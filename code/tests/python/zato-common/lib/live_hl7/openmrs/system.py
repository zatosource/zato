# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK
from urllib.parse import quote
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.fetch import cached_path, fetch_once, work_directory
from live_hl7.http import Session, basic_auth, expect_status, parse_json, request
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strintdict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The service names in the compose file
Service = 'openmrs'
DB_Service = 'db'

# The database the compose file creates, as the application connects to it
DB_Name = 'openmrs'
DB_Username = 'openmrs'

# The account the distribution ships with - the password is replaced at first start
Admin_Username = 'admin'
Admin_Initial_Password = 'Admin123'

# Everything the application serves sits under this path
Context_Path = '/openmrs'
REST_Path = Context_Path + '/ws/rest/v1'

# The module rendering ORU^R01 on request, fetched once into the cache
HL7_Query_Module_ID = 'org.openmrs.module.hl7query'
HL7_Query_Module_URL = 'https://openmrs.jfrog.io/artifactory/modules/org/openmrs/module/hl7query-omod/1.0/hl7query-omod-1.0.jar'
HL7_Query_Module_File = 'hl7query-1.0.omod'
HL7_Query_RefApp_Module_File = 'hl7query-1.0-refapp.omod'

# The module's login controller, removed from it
HL7_Query_Login_Controller_Class = 'org/openmrs/module/hl7query/web/controller/SessionController.class'

# The modules directory mounted into the container
Modules_Dir_Name = 'openmrs-modules'

# The application's service in the compose file, where its installation writes the runtime properties once done
# and where the marker of the one restart the installation calls for goes
Web_Service = 'openmrs'
Application_Data_Dir = '/usr/local/tomcat/.OpenMRS'
Runtime_Properties_File = Application_Data_Dir + '/openmrs-runtime.properties'
Restarted_Marker_File = Application_Data_Dir + '/zato-restarted-after-install'

# What has the hl7query module loaded
HL7_Query_Variable = 'OPENMRS_HL7_QUERY'
HL7_Query_Wanted = '1'

# The scheduler task moving hl7_in_queue into encounters and patients
Process_HL7_Task = 'Process HL7 Task'

# What MSH-3 carries in everything the application renders
Implementation_ID = 'ZATOTEST'
Implementation_Name = 'Zato test implementation'
Implementation_Passphrase = 'zato-test'

# ################################################################################################################################
# ################################################################################################################################

class OpenMRS(LiveSystem):
    """ The OpenMRS Reference Application - HL7 in through the REST queue and, for a suite that asks for the hl7query
    module, HL7 out through it.
    """

    name = 'openmrs'
    block_number = 1
    purposes = ('web', 'mysql')
    password_rules = PasswordRules(8, True, True, True, False)
    images = {
        'db':      'mysql:5.6',
        'openmrs': 'openmrs/openmrs-reference-application-distro:2.12.2',
    }
    directory = os.path.dirname(__file__)
    summary = 'The OpenMRS Reference Application, HL7 in through REST, HL7 out through the hl7query module when asked for.'
    ui_purpose = 'web'
    ui_path = Context_Path + '/login.htm'
    ui_username = Admin_Username
    kept_volumes = ('zato-hl7-openmrs-db', 'zato-hl7-openmrs-data')

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out['OPENMRS_MODULES_DIR'] = work_directory(Modules_Dir_Name)
        out[HL7_Query_Variable] = ''

        return out

# ################################################################################################################################

    def prepare(self, handle:'Handle') -> 'None':
        """ Puts the hl7query module where the container loads modules from when asked for it, and takes it away when not.
        """
        target = os.path.join(work_directory(Modules_Dir_Name), HL7_Query_Module_File)

        if _wants_hl7_query(handle):
            source = _refapp_module()

            if not os.path.exists(target):
                _ = shutil.copyfile(source, target)

        elif os.path.exists(target):
            os.remove(target)

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the REST module authenticates, with the initial password or with ours. A fresh start installs
        the application first and has to be restarted once afterwards before it serves anything, which is done here.
        """
        url = handle.http_url('web') + REST_Path + '/session'

        for password in (Admin_Initial_Password, handle.password):
            headers = {'Authorization': basic_auth(Admin_Username, password)}
            result = request('GET', url, headers=headers)

            if result.status == OK:
                data = parse_json(result)
                if data['authenticated']:
                    return True

            if result.status == NOT_FOUND:
                _restart_once_after_install(handle)

        return False

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ Replaces the shipped administrator password, confirms the module started when it was asked for and sets
        the Implementation ID.
        """
        _change_initial_password(handle)

        session = login(handle)

        if _wants_hl7_query(handle):
            _require_module_started(session, HL7_Query_Module_ID)

        set_implementation_id(session)

# ################################################################################################################################
# ################################################################################################################################

def _restart_once_after_install(handle:'Handle') -> 'None':
    """ Restarts the container once the installation has written its runtime properties, and only once - a marker
    next to them says it was done.
    """
    check = ['sh', '-c', f'test -f {Runtime_Properties_File} && ! test -f {Restarted_Marker_File} && echo yes']
    output = handle.stack.exec(Web_Service, check).strip()

    if output != 'yes':
        return

    _ = handle.stack.exec(Web_Service, ['touch', Restarted_Marker_File])
    print(f'Installed {handle.system}, restarting it once as the application requires', flush=True)

    handle.stack.restart(Web_Service)

# ################################################################################################################################

def _wants_hl7_query(handle:'Handle') -> 'bool':
    out = handle.stack.environment[HL7_Query_Variable] == HL7_Query_Wanted
    return out

# ################################################################################################################################
# ################################################################################################################################

def _refapp_module() -> 'str':
    """ The module as published, without its login controller, whose bean name the Reference Application already
    uses. The rewritten module is kept in the cache next to the published one.
    """
    out = cached_path(HL7_Query_RefApp_Module_File)

    if os.path.exists(out):
        return out

    source = fetch_once(HL7_Query_Module_URL, HL7_Query_Module_File)
    partial = out + '.partial'
    is_removed = False

    with ZipFile(source) as published, ZipFile(partial, 'w', ZIP_DEFLATED) as rewritten:

        for item in published.infolist():

            if item.filename == HL7_Query_Login_Controller_Class:
                is_removed = True
                continue

            rewritten.writestr(item, published.read(item.filename))

    if not is_removed:
        raise Exception(f'{HL7_Query_Login_Controller_Class} not found in {source}')

    os.replace(partial, out)

    return out

# ################################################################################################################################

def _change_initial_password(handle:'Handle') -> 'None':
    """ Replaces the shipped password, when it is still the one in use.
    """
    session = Session(handle.http_url('web'))
    session.headers['Authorization'] = basic_auth(Admin_Username, Admin_Initial_Password)

    result = session.get(REST_Path + '/session')
    data = parse_json(result)

    if not data['authenticated']:
        return

    payload = {'oldPassword': Admin_Initial_Password, 'newPassword': handle.password}
    result = session.post_json(REST_Path + '/password', payload)
    expect_status(result, OK, 'password change')

# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ A session authenticated as the administrator, for REST and the legacy pages alike.
    """
    out = Session(handle.http_url('web'))
    out.headers['Authorization'] = basic_auth(Admin_Username, handle.password)

    result = out.get(REST_Path + '/session')
    expect_status(result, OK, 'login')

    data = parse_json(result)
    if not data['authenticated']:
        raise Exception('OpenMRS did not authenticate the administrator')

    return out

# ################################################################################################################################

def _require_module_started(session:'Session', module_id:'str') -> 'None':
    """ Fails with the module's own state when it is there but did not start, since nothing works without it.
    """
    result = session.get(REST_Path + f'/module/{module_id}?v=full')
    expect_status(result, OK, f'module {module_id}')

    data = parse_json(result)

    if not data['started']:
        raise Exception(f'Module {module_id} is not started: {data}')

# ################################################################################################################################

def set_implementation_id(session:'Session') -> 'None':
    """ Stores the Implementation ID as the global property the application deserializes it from, so no call
    leaves for the public implementation id server.
    """
    value = (
        '<org.openmrs.ImplementationId>'
        f'<name>{escape(Implementation_Name)}</name>'
        f'<description>{escape(Implementation_Name)}</description>'
        f'<implementationId>{escape(Implementation_ID)}</implementationId>'
        f'<passphrase>{escape(Implementation_Passphrase)}</passphrase>'
        '</org.openmrs.ImplementationId>'
    )

    set_global_property(session, 'implementation_id', value)

# ################################################################################################################################

def set_global_property(session:'Session', name:'str', value:'str') -> 'None':
    """ Creates or updates one global property.
    """
    result = session.get(REST_Path + f'/systemsetting/{name}')

    if result.status == OK:
        result = session.post_json(REST_Path + f'/systemsetting/{name}', {'value': value})
    else:
        result = session.post_json(REST_Path + '/systemsetting', {'property': name, 'value': value})

    if result.status not in (OK, CREATED):
        body = result.body.decode('utf8', 'replace')
        raise Exception(f'Could not set global property {name}, status {result.status}, body: {body}')

# ################################################################################################################################

def post_hl7(session:'Session', message:'str') -> 'anydict':
    """ Puts one ER7 message into hl7_in_queue.
    """
    result = session.post_json(REST_Path + '/hl7', {'hl7': message})
    expect_status(result, CREATED, 'HL7 post')

    out = parse_json(result)
    return out

# ################################################################################################################################

def run_hl7_task(session:'Session') -> 'None':
    """ Runs the queue processor now instead of waiting for the scheduler.
    """
    payload = {'action': 'runtask', 'tasks': [Process_HL7_Task]}
    result = session.post_json(REST_Path + '/taskaction', payload)

    if result.status not in (OK, CREATED, NO_CONTENT):
        body = result.body.decode('utf8', 'replace')
        raise Exception(f'Could not run {Process_HL7_Task}, status {result.status}, body: {body}')

# ################################################################################################################################

def render_oru_r01(session:'Session', patient_uuid:'str', encounter_uuid:'str') -> 'str':
    """ The ORU^R01 the hl7query module renders for one encounter.
    """
    path = Context_Path + f'/hl7query/orur01?patient={patient_uuid}&encounter={encounter_uuid}'
    result = session.get(path)
    expect_status(result, OK, 'ORU^R01 rendering')

    out = result.body.decode('utf8')
    return out

# ################################################################################################################################

def find_patients(session:'Session', query:'str') -> 'any_':
    out = session.get_json(REST_Path + f'/patient?q={quote(query)}&v=full')
    return out['results']

# ################################################################################################################################

def find_encounters(session:'Session', patient_uuid:'str') -> 'any_':
    out = session.get_json(REST_Path + f'/encounter?patient={patient_uuid}&v=full')
    return out['results']

# ################################################################################################################################

def hl7_queue(session:'Session') -> 'any_':
    """ What is still waiting in hl7_in_queue.
    """
    out = session.get_json(REST_Path + '/hl7?v=full')
    return out['results']

# ################################################################################################################################

def ensure_hl7_source(session:'Session', name:'str') -> 'None':
    """ Registers a sending facility - the REST queue takes a message only when MSH-4 names a source it knows.
    """
    sources = session.get_json(REST_Path + f'/hl7source?q={quote(name)}')

    for source in sources['results']:
        if source['display'] == name:
            return

    payload = {'name': name, 'description': f'Facility {name}'}
    result = session.post_json(REST_Path + '/hl7source', payload)
    expect_status(result, CREATED, f'HL7 source {name}')

# ################################################################################################################################

def ensure_identifier_type(session:'Session', name:'str') -> 'None':
    """ Registers a patient identifier type - the ADT^A28 handler files PID-3 under the type whose name
    is the identifier's assigning authority, and leaves a patient without one it cannot find.
    """
    types = session.get_json(REST_Path + f'/patientidentifiertype?q={quote(name)}')

    for identifier_type in types['results']:
        if identifier_type['display'] == name:
            return

    payload = {'name': name, 'description': f'Identifier {name}', 'required': False}
    result = session.post_json(REST_Path + '/patientidentifiertype', payload)
    expect_status(result, CREATED, f'identifier type {name}')

# ################################################################################################################################

def make_identifier_types_optional(session:'Session') -> 'None':
    """ Turns every required identifier type into an optional one - a patient filed from an HL7 message
    carries the identifiers the message had, and saving one is refused while a required type is missing.
    """
    types = session.get_json(REST_Path + '/patientidentifiertype?v=full')

    for identifier_type in types['results']:
        if identifier_type['required']:
            uuid = identifier_type['uuid']
            result = session.post_json(REST_Path + f'/patientidentifiertype/{uuid}', {'required': False})
            expect_status(result, OK, f'identifier type {uuid}')

# ################################################################################################################################

def _query_rows(handle:'Handle', query:'str') -> 'anylist':
    """ Rows of one query against the application's own database, each a list of column values as text.
    """
    arguments = ['mysql', '-u', DB_Username, f'-p{handle.password}', DB_Name, '-N', '-B', '-e', query]
    output = handle.stack.exec(DB_Service, arguments)

    out:'anylist' = []

    for line in output.splitlines():
        if line:
            out.append(line.split('\t'))

    return out

# ################################################################################################################################

def hl7_errors(handle:'Handle') -> 'anylist':
    """ What the queue processor could not handle - the control id of each message and the error it was filed with.
    """
    out = _query_rows(handle, 'SELECT hl7_source_key, error FROM hl7_in_error')
    return out

# ################################################################################################################################

def hl7_archive(handle:'Handle') -> 'anylist':
    """ The control ids of the messages the queue processor handled.
    """
    out = _query_rows(handle, 'SELECT hl7_source_key FROM hl7_in_archive')
    return out

# ################################################################################################################################
# ################################################################################################################################
