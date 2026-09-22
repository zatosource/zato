# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from http.client import BAD_GATEWAY, CREATED, OK
from string import Template

# Live HL7
from live_hl7.compose import Host_Gateway
from live_hl7.credentials import PasswordRules
from live_hl7.extension import Extension_Root_Env, extension_directory
from live_hl7.fetch import work_directory
from live_hl7.http import Session, expect_status, is_http_ok, parse_json, request
from live_hl7.messages import Patient
from live_hl7.seed import Seed_Patients
from live_hl7.system import Handle, LiveSystem
from live_hl7.zato import Zato_MLLP_Port_Env, zato_mllp_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strintdict, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Service names in the compose file
Webapp_Service = 'oe.openelis.org'
Bridge_Service = 'bridge.openelis.org'
DB_Service = 'db.openelis.org'

# The database the image installs and the account the container's own psql connects as, without a password
Database_Name = 'clinlims'
Database_User = 'postgres'

# The administrator and the password baked into the image when it was built - DEFAULT_PW is a build argument
# and does nothing at runtime, so the password is changed to ours once the webapp is up.
Admin_Username = 'admin'
Image_Admin_Password = 'adminADMIN!'

# The bridge's own account for its /input endpoint
Bridge_Username = 'bridge'

# The webapp's context, as served by the webapp itself rather than the project's proxy
Context_Path = '/OpenELIS-Global'

# Where the bridge posts what it receives, on the stack's own network
Webapp_Analyzer_URI = f'https://{Webapp_Service}:8443{Context_Path}/analyzer'

# The bridge configuration's template next to this file and where the rendered one lives
Bridge_Config_Template_Name = 'bridge-configuration.yml'
Bridge_Config_Dir_Name = 'openelis-bridge'
Bridge_Config_File_Name = 'configuration.yml'

# Analyzer protocols, modes and states, as the webapp names them - a result from a sender the laboratory does not
# know is staged under an analyzer the webapp creates for it, named after MSH-3 and MSH-4 and waiting to be registered
Protocol_HL7_V25 = 'HL7_V2_5'
Mode_Both = 'BOTH'
Status_Active = 'ACTIVE'
Status_Pending_Registration = 'PENDING_REGISTRATION'

# What the webapp says of an order it handed to the bridge - delivered and acknowledged, or not
Dispatch_Delivered = 'DISPATCHED'
Dispatch_Failed = 'FAILED'

# How the bridge names itself in MSH-3 of the orders it sends, and the type of those orders
Order_Sending_Application = 'OE2'
Order_Message_Type = 'ORM'

# How the webapp names an analyzer it created for an unknown sender - MSH-3 and MSH-4 joined
Stub_Name_Separator = '-'

# How a result that reached an order is marked in the order's results
Analysis_Method_Analyzer = 'AUTO'

# Dates as the order entry form takes them
Form_Date_Format = '%d/%m/%Y'
HL7_Date_Format = '%Y%m%d'

# The identifier type the laboratory's own patient identifiers are issued under, and the entry form's words for
# a patient who is new and for an order that is not urgent
Patient_ID_Type = 'NID'
Patient_Update_Add = 'ADD'
Priority_Routine = 'ROUTINE'

# Haemoglobin, the one test every haematology analyzer reports - the test every seed patient has one order for
Haemoglobin_LOINC = '718-7'
Seed_LOINC = Haemoglobin_LOINC

# Whether a patient is already in the laboratory, by the identifier the seed gave it
Patient_Exists_SQL = "select count(*) from clinlims.patient where national_id = '{national_id}'"

# The webapp takes HL7 results through analyzer plugins only and its image ships none - the plugin directory comes
# from the extension when there is one and is empty otherwise, and this is the name the webapp registers the generic
# plugin under.
Plugins_Directory_Name = 'openelis_plugins'
Plugins_Cache_Dir_Name = 'openelis-plugins'
Plugin_Suffix = '.jar'
Generic_HL7_Type_Name = 'Generic HL7'

# What Zato is to the laboratory - an analyzer whose results carry this MSH-3 and which takes orders
# at the Zato MLLP channel on this machine, known to the bridge by the address the host has on its network.
Zato_Analyzer_Name = 'Zato'
Zato_Sending_Application = 'ZATO'
Zato_Identifier_Pattern = f'^{Zato_Sending_Application}'

# The laboratory's LOINC-coded tests, one per code, each becoming a test of the Zato analyzer under its code,
# and the sample type a test is ordered on
LOINC_Tests_SQL = (
    "select id, loinc from clinlims.test where is_active = 'Y' and loinc is not null and loinc <> '' order by id"
)
Sample_Type_SQL = (
    'select sample_type_id from clinlims.sampletype_test where test_id = {test_id} order by sample_type_id limit 1'
)

# The one sample of an order, as the entry form describes it - the frontend's own template, the type, the tests
# and the collection date and time filled in
Sample_XML = (
    '<?xml version="1.0" encoding="utf-8"?><samples>'
    "<sample sampleID='{sample_type_id}' sampleItemId='' date='{date}' time='{time}' collector='' "
    "collectionConditions='' quantity='' uom='' receivedDate='' receivedTime='' tests='{test_id}' testSectionMap='' "
    "testSampleTypeMap='' panels='' rejected='false' rejectReasonId='' initialConditionIds='' storageLocationId='' "
    "storageLocationType='' storagePositionCoordinate='' gpsLatitude='' gpsLongitude='' gpsAccuracy='' "
    "gpsCaptureMethod=''/></samples>"
)

# ################################################################################################################################
# ################################################################################################################################

class OpenELIS(LiveSystem):
    """ OpenELIS Global 2 with its analyzer bridge - results in over MLLP, LIS-initiated orders out over MLLP.
    """

    name = 'openelis'
    block_number = 2
    purposes = ('web', 'postgres', 'bridge_api', 'mllp')
    password_rules = PasswordRules(8, True, True, True, True)
    images = {
        'certs':               'itechuw/certgen:main',
        'db.openelis.org':     'itechuw/openelis-global-2-database:3.2.2.0',
        'oe.openelis.org':     'itechuw/openelis-global-2:3.2.2.0',
        'fhir.openelis.org':   'itechuw/openelis-global-2-fhir:3.2.2.0',
        'bridge.openelis.org': 'itechuw/openelis-analyzer-bridge:3.0.5',
    }
    one_off_services = ('certs',)
    directory = os.path.dirname(__file__)
    summary = (
        'OpenELIS Global 2 with its FHIR store and analyzer bridge, MLLP in on the bridge, orders out from the webapp.'
    )
    ui_purpose = 'web'
    ui_path = Context_Path + '/'
    ui_is_https = True
    ui_username = Admin_Username

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out['OPENELIS_BRIDGE_CONFIG'] = _bridge_config_path()
        out['OPENELIS_PLUGINS_DIR'] = _plugins_directory()

        return out

# ################################################################################################################################

    def prepare(self, handle:'Handle') -> 'None':
        """ Renders the bridge configuration with the webapp's address and our credentials, having made sure
        the laboratory has the plugin its connection to Zato needs.
        """
        _require_plugin()

        template_path = os.path.join(self.directory, Bridge_Config_Template_Name)

        with open(template_path, encoding='utf8') as f:
            template = Template(f.read())

        values:'strstrdict' = {
            'BRIDGE_USERNAME':     Bridge_Username,
            'BRIDGE_PASSWORD':     handle.password,
            'WEBAPP_ANALYZER_URI': Webapp_Analyzer_URI,
            'WEBAPP_USERNAME':     Admin_Username,
            'WEBAPP_PASSWORD':     handle.password,
        }

        rendered = template.substitute(values)

        with open(_bridge_config_path(), 'w', encoding='utf8') as f:
            _ = f.write(rendered)

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the webapp serves its login page and the bridge reports itself up.
        """
        webapp_url = handle.https_url('web') + Context_Path + '/LoginPage'

        if not is_http_ok(webapp_url, verify_tls=False):
            return False

        bridge_url = handle.https_url('bridge_api') + '/actuator/health'
        result = request('GET', bridge_url, verify_tls=False)

        if result.status != OK:
            return False

        data = parse_json(result)
        out = data['status'] == 'UP'

        return out

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ The administrator gets our password, the laboratory gets Zato as its analyzer, in both directions,
        and the seed patients, each with one order, unless an earlier run on the kept volumes already added them.
        """
        change_admin_password(handle)

        session = login(handle)
        connect_to_zato(handle, session)
        seed_orders(handle, session)

# ################################################################################################################################
# ################################################################################################################################

def _bridge_config_path() -> 'str':
    out = os.path.join(work_directory(Bridge_Config_Dir_Name), Bridge_Config_File_Name)
    return out

# ################################################################################################################################

def _plugins_directory() -> 'str':
    out = extension_directory(Plugins_Directory_Name, work_directory(Plugins_Cache_Dir_Name))
    return out

# ################################################################################################################################

def _require_plugin() -> 'None':
    """ Fails before any container starts when the plugin directory has no plugin in it.
    """
    directory = _plugins_directory()

    for name in os.listdir(directory):
        if name.endswith(Plugin_Suffix):
            break
    else:
        raise Exception(
            f'No analyzer plugin in {directory}, so OpenELIS would take no HL7 results - is {Extension_Root_Env} set?'
        )

# ################################################################################################################################

def change_admin_password(handle:'Handle') -> 'None':
    """ The image's password gives way to ours - the form the login page offers for it, no session needed.
    """
    session = Session(handle.https_url('web') + Context_Path, verify_tls=False)

    fields = {
        'loginName':       Admin_Username,
        'password':        Image_Admin_Password,
        'newPassword':     handle.password,
        'confirmPassword': handle.password,
    }

    result = session.post_form('/ChangePasswordLogin?apiCall=true', fields)
    expect_status(result, OK, 'password change')

# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ A session logged in the way the frontend logs in - the credentials as a form, then the CSRF token
    from the session.
    """
    out = Session(handle.https_url('web') + Context_Path, verify_tls=False)

    fields = {'loginName': Admin_Username, 'password': handle.password}
    result = out.post_form('/ValidateLogin?apiCall=true', fields)
    expect_status(result, OK, 'login')

    data = out.get_json('/session')
    out.headers['X-CSRF-Token'] = data['csrf']

    return out

# ################################################################################################################################

def connect_to_zato(handle:'Handle', session:'Session') -> 'None':
    """ Zato becomes an analyzer of the laboratory - its results come in over the bridge's MLLP port and orders
    to it go out to the Zato MLLP channel on this machine as ORM^O01.
    """
    host_address = host_address_of(handle)
    port = zato_mllp_port()

    analyzer = register_analyzer(
        session,
        name=Zato_Analyzer_Name,
        identifier_pattern=Zato_Identifier_Pattern,
        host=host_address,
        port=port,
    )
    analyzer_id = analyzer['id']

    mapped = map_loinc_tests(session, handle, analyzer_id)
    codes = f'{mapped} LOINC code' if mapped == 1 else f'{mapped} LOINC codes'

    # The mappings went in after the bridge learned of the analyzer, so it learns of it again, this time with them
    update_analyzer(session, analyzer_id, analyzer)

    mllp_address = handle.address('mllp')
    sends_to = f'{host_address}:{port}, the Zato MLLP channel on this machine ({Zato_MLLP_Port_Env} to change it)'
    receives_on = f'{mllp_address}, MSH-3 {Zato_Sending_Application}, OBR-3 the accession, OBX-3 one of {codes}'

    print(f'  Sends to       {sends_to}', flush=True)
    print(f'  Receives on    {receives_on}', flush=True)

# ################################################################################################################################

def host_address_of(handle:'Handle') -> 'str':
    """ The address this machine has on the bridge's network - the webapp takes analyzers by IPv4 address only.
    """
    hosts = handle.stack.exec(Bridge_Service, ['cat', '/etc/hosts'])

    for line in hosts.splitlines():
        fields = line.split()
        if Host_Gateway in fields[1:]:
            out = fields[0]
            break
    else:
        raise Exception(f'{Host_Gateway} is not in the hosts of {Bridge_Service}:\n{hosts}')

    return out

# ################################################################################################################################

def generic_hl7_type_id(session:'Session') -> 'str':
    """ The analyzer type the webapp created for the plugin when it loaded it on startup.
    """
    data = session.get_json('/rest/analyzer-types')

    for analyzer_type in data:
        if analyzer_type['name'] == Generic_HL7_Type_Name:
            out = analyzer_type['id']
            break
    else:
        raise Exception(
            f'No {Generic_HL7_Type_Name} analyzer type - there is no such plugin in the plugin directory, data: {data}'
        )

    return out

# ################################################################################################################################

def _analyzer_payload(
    name:'str',
    plugin_type_id:'str',
    identifier_pattern:'str',
    host:'str',
    port:'int',
    ) -> 'anydict':
    out = {
        'name':              name,
        'analyzerType':      Generic_HL7_Type_Name,
        'pluginTypeId':      plugin_type_id,
        'identifierPattern': identifier_pattern,
        'ipAddress':         host,
        'port':              port,
        'protocolVersion':   Protocol_HL7_V25,
        'communicationMode': Mode_Both,
        'status':            Status_Active,
    }

    return out

# ################################################################################################################################

def register_analyzer(
    session:'Session',
    *,
    name:'str',
    identifier_pattern:'str',
    host:'str',
    port:'int',
    ) -> 'anydict':
    """ An HL7 analyzer of the generic plugin - recognised by MSH-3 through the pattern and sent orders at the host
    and port.
    """
    plugin_type_id = generic_hl7_type_id(session)
    payload = _analyzer_payload(name, plugin_type_id, identifier_pattern, host, port)

    result = session.post_json('/rest/analyzer/analyzers', payload)
    expect_status(result, CREATED, f'registration of analyzer {name}')

    out = parse_json(result)

    if not out['bridgeRegistered']:
        raise Exception(f'The webapp did not register analyzer {name} with the bridge: {out}')

    return out

# ################################################################################################################################

def update_analyzer(session:'Session', analyzer_id:'str', analyzer:'anydict') -> 'None':
    """ Saves the analyzer as it is, which makes the webapp register it with the bridge again.
    """
    _save_analyzer(session, analyzer_id, analyzer, analyzer['ipAddress'], analyzer['port'])

# ################################################################################################################################

def point_analyzer_at(session:'Session', handle:'Handle', analyzer:'anydict', port:'int') -> 'None':
    """ The analyzer's orders go to this port on this machine from now on - the webapp takes analyzers by IPv4
    address only, so this machine is the address it has on the bridge's network.
    """
    _save_analyzer(session, analyzer['id'], analyzer, host_address_of(handle), port)

# ################################################################################################################################

def _save_analyzer(session:'Session', analyzer_id:'str', analyzer:'anydict', host:'str', port:'int') -> 'None':
    payload = _analyzer_payload(
        analyzer['name'],
        analyzer['pluginTypeId'],
        analyzer['identifierPattern'],
        host,
        port,
    )

    result = session.put_json(f'/rest/analyzer/analyzers/{analyzer_id}', payload)
    expect_status(result, OK, f'update of analyzer {analyzer_id}')

    data = parse_json(result)

    if not data['bridgeRegistered']:
        raise Exception(f'The webapp did not register analyzer {analyzer_id} with the bridge again: {data}')

# ################################################################################################################################

def analyzers(session:'Session') -> 'anylist':
    """ Every analyzer the laboratory knows, the stubs it created for unknown senders included.
    """
    data = session.get_json('/rest/analyzer/analyzers')

    out = data['analyzers']
    return out

# ################################################################################################################################

def analyzer_named(session:'Session', name:'str') -> 'anydict':
    for analyzer in analyzers(session):
        if analyzer['name'] == name:
            out = analyzer
            break
    else:
        raise Exception(f'No analyzer named {name}')

    return out

# ################################################################################################################################

def zato_analyzer(session:'Session') -> 'anydict':
    """ Zato as the laboratory registered it on startup.
    """
    out = analyzer_named(session, Zato_Analyzer_Name)
    return out

# ################################################################################################################################

def stub_name(sending_application:'str', sending_facility:'str') -> 'str':
    """ What the webapp calls the analyzer it creates for a sender it does not know.
    """
    out = f'{sending_application}{Stub_Name_Separator}{sending_facility}'
    return out

# ################################################################################################################################

def map_loinc_tests(session:'Session', handle:'Handle', analyzer_id:'str') -> 'int':
    """ The laboratory's LOINC-coded tests become the analyzer's tests under their LOINC codes - an order for one
    of them goes out with that code in OBR-4, and a result naming it in OBX-3 lands on that test. Returns how many.
    """
    out = 0

    for test_id, loinc in loinc_tests(handle).items():
        map_test(session, analyzer_id, loinc, test_id)
        out += 1

    return out

# ################################################################################################################################

def loinc_tests(handle:'Handle') -> 'strstrdict':
    """ Test ID to LOINC code, the first test of each code - the catalogue has the same code on a test per sample type,
    and an analyzer knows one test under one code.
    """
    output = _query(handle, LOINC_Tests_SQL)

    out:'strstrdict' = {}
    seen:'strset' = set()

    for line in output.splitlines():
        test_id, loinc = line.split('|')

        if loinc in seen:
            continue

        seen.add(loinc)
        out[test_id] = loinc

    return out

# ################################################################################################################################

def map_test(session:'Session', analyzer_id:'str', analyzer_test_name:'str', test_id:'str') -> 'None':
    payload = {
        'analyzerId':       analyzer_id,
        'analyzerTestName': analyzer_test_name,
        'testId':           test_id,
        'newMapping':       True,
    }

    result = session.post_json('/rest/AnalyzerTestName', payload)
    expect_status(result, CREATED, f'mapping of {analyzer_test_name} to test {test_id}')

# ################################################################################################################################

def send_order(session:'Session', analyzer_id:'str', accession:'str') -> 'anydict':
    """ Makes the webapp hand an order for one accession to the bridge, which delivers it over MLLP - what the webapp
    says of the dispatch, delivered with 200 and failed with 502, either way with the outcome in `status`.
    """
    result = session.post_json(f'/rest/analyzer/analyzers/{analyzer_id}/send-order', {'accessionNumber': accession})
    expect_status(result, (OK, BAD_GATEWAY), f'dispatch of an order for {accession}')

    out = parse_json(result)
    return out

# ################################################################################################################################

def loinc_test_id(handle:'Handle', loinc:'str') -> 'str':
    """ The test the Zato analyzer knows under one LOINC code.
    """
    for test_id, code in loinc_tests(handle).items():
        if code == loinc:
            out = test_id
            break
    else:
        raise Exception(f'No active test with LOINC {loinc}')

    return out

# ################################################################################################################################

def sample_type_of(handle:'Handle', test_id:'str') -> 'str':
    """ The sample type a test is ordered on.
    """
    out = _query(handle, Sample_Type_SQL.format(test_id=test_id))

    if not out:
        raise Exception(f'Test {test_id} is ordered on no sample type')

    return out

# ################################################################################################################################

def new_accession(session:'Session') -> 'str':
    """ The next accession number of the laboratory's own sequence.
    """
    data = session.get_json('/rest/SampleEntryGenerateScanProvider')

    out = data['body']
    return out

# ################################################################################################################################

def seed_order(session:'Session', handle:'Handle', patient:'Patient', test_id:'str') -> 'str':
    """ One new patient with one sample and one test ordered on it, entered the way the order entry form enters
    it - the accession the laboratory gave the order.
    """
    accession = new_accession(session)

    form = session.get_json('/rest/SamplePatientEntry')
    order_items = form['sampleOrderItems']

    birth_date = datetime.strptime(patient.birth_date, HL7_Date_Format).strftime(Form_Date_Format)

    sample_xml = Sample_XML.format(
        sample_type_id=sample_type_of(handle, test_id),
        date=order_items['receivedDateForDisplay'],
        time=order_items['receivedTime'],
        test_id=test_id,
    )

    payload = {
        'sampleXML': sample_xml,
        'referralItems': [],
        'useReferral': False,
        'orderEntryOnly': False,
        'patientUpdateStatus': Patient_Update_Add,
        'customNotificationLogic': False,
        'patientEmailNotificationTestIds': [],
        'patientSMSNotificationTestIds': [],
        'providerEmailNotificationTestIds': [],
        'providerSMSNotificationTestIds': [],
        'rememberSiteAndRequester': False,
        'patientProperties': {
            'patientUpdateStatus': Patient_Update_Add,
            'patientPK': '',
            'nationalId': patient.patient_id,
            'lastName': patient.family_name,
            'firstName': patient.given_name,
            'gender': patient.sex,
            'birthDateForDisplay': birth_date,
            'patientType': '',
            'readOnly': False,
        },
        'sampleOrderItems': {
            'labNo': accession,
            'requestDate': order_items['requestDate'],
            'receivedDateForDisplay': order_items['receivedDateForDisplay'],
            'receivedTime': order_items['receivedTime'],
            'priority': Priority_Routine,
            'modified': True,
            'readOnly': False,
            'isEQASample': False,
            'externalOrderNumber': '',
            'sampleId': '',
            'programId': '',
        },
        'initialSampleConditionList': [],
        'testSectionList': [],
    }

    result = session.post_json('/rest/SamplePatientEntry', payload)
    expect_status(result, (OK, CREATED), f'entry of the order {accession}')

    out = accession
    return out

# ################################################################################################################################

def seed_orders(handle:'Handle', session:'Session') -> 'None':
    """ The seed patients, each with one haemoglobin order - something for a person to dispatch from the UI.
    """
    test_id = loinc_test_id(handle, Seed_LOINC)

    for seed in Seed_Patients:

        if patient_exists(handle, seed.mrn):
            continue

        patient = Patient(seed.mrn, Patient_ID_Type, seed.family_name, seed.given_name, seed.birth_date, seed.sex)
        _ = seed_order(session, handle, patient, test_id)

# ################################################################################################################################

def patient_exists(handle:'Handle', national_id:'str') -> 'bool':
    count = _query(handle, Patient_Exists_SQL.format(national_id=national_id))

    out = count != '0'
    return out

# ################################################################################################################################

def _query(handle:'Handle', sql:'str') -> 'str':
    """ One statement through the container's own psql, its rows as bare lines without a header.
    """
    arguments = ['psql', '-U', Database_User, '-At', '-c', sql, Database_Name]
    output = handle.stack.exec(DB_Service, arguments)

    out = output.strip()
    return out

# ################################################################################################################################

def _results_form(session:'Session', analyzer_id:'str') -> 'anydict':
    """ The results page of one analyzer as the webapp serves it - the form the page posts back with its decisions.
    """
    out = session.get_json(f'/rest/AnalyzerResults?id={analyzer_id}')
    return out

# ################################################################################################################################

def analyzer_results(session:'Session', analyzer_id:'str') -> 'anylist':
    """ The results of one analyzer waiting to be accepted into their orders.
    """
    form = _results_form(session, analyzer_id)

    out = form['resultList']
    return out

# ################################################################################################################################

def results_with_accession(session:'Session', analyzer_id:'str', accession:'str') -> 'anylist':
    out:'anylist' = []

    for result in analyzer_results(session, analyzer_id):
        if result['accessionNumber'] == accession:
            out.append(result)

    return out

# ################################################################################################################################

def accept_results(session:'Session', analyzer_id:'str', accession:'str') -> 'None':
    """ Accepts every waiting result of one accession into its order, the way the results page saves them.
    """
    form = _results_form(session, analyzer_id)

    for item in form['resultList']:
        if item['accessionNumber'] == accession:
            item['isAccepted'] = True

    result = session.post_json('/rest/AnalyzerResults', form)
    expect_status(result, OK, f'acceptance of the results of {accession}')

# ################################################################################################################################

def accession_results(session:'Session', accession:'str') -> 'anylist':
    """ The tests of one order with the results they have so far.
    """
    data = session.get_json(f'/rest/accession-results?accessionNumber={accession}')

    out = data['testResult']
    return out

# ################################################################################################################################
# ################################################################################################################################
