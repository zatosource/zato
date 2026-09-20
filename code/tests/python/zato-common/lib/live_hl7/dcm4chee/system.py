# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import shutil
import tempfile
from http.client import NO_CONTENT, OK
from io import BytesIO
from json import dumps
from time import sleep
from zipfile import ZIP_DEFLATED, ZipFile
from typing import NamedTuple
from urllib.parse import quote

# Live containers
from live_containers.ready import StartupFailed, wait_until

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.openhim.system import Host_Address
from live_hl7.http import expect_status, is_http_ok, parse_json, request
from live_hl7.seed import Seed_Patients
from live_hl7.system import Handle, LiveSystem
from live_hl7.zato import Zato_MLLP_Port_Env, zato_mllp_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_hl7.http import HTTPResult
    from live_hl7.tls import Authority, Identity
    from zato.common.typing_ import any_, anydict, anylist, strintdict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Service names in the compose file
Archive_Service = 'arc'
LDAP_Service = 'ldap'

# The archive's own identities
Archive_AET = 'DCM4CHEE'
Archive_Device = 'dcm4chee-arc'

# The application entity the image serves the modality worklist through - a REST client asking the
# archive's own entity for worklist items is turned away, since that entity has no worklist service class
Worklist_AET = 'WORKLIST'

# Every HL7 message the archive sends carries this in MSH-3 and MSH-4 unless told otherwise
Archive_HL7_Application = 'DCM4CHEE|DCM4CHEE'

# Where everything is in the directory
Base_DN = 'dc=dcm4che,dc=org'
Config_DN = f'cn=DICOM Configuration,{Base_DN}'
Devices_DN = f'cn=Devices,{Config_DN}'
Archive_Device_DN = f'dicomDeviceName={Archive_Device},{Devices_DN}'
HL7_Registry_DN = f'cn=Unique HL7 Application Names Registry,{Config_DN}'
Archive_HL7_Application_DN = f'hl7ApplicationName={Archive_HL7_Application},{Archive_Device_DN}'
LDAP_Admin_DN = f'cn=admin,{Base_DN}'

# The archive's own HL7 listeners, the TLS one being where a sender has to present a certificate
HL7_TLS_Connection_DN = f'cn=hl7-tls,{Archive_Device_DN}'

# The queue the archive's outgoing HL7 messages wait on
HL7_Send_Queue = 'HL7Send'
HL7_Send_Queue_DN = f'dcmQueueName={HL7_Send_Queue},{Archive_Device_DN}'

# The archive's web root and its REST paths
Web_Root = '/dcm4chee-arc'
AETs_Path = Web_Root + '/aets'
Reload_Path = Web_Root + '/ctrl/reload'
Archive_RS_Path = f'{AETs_Path}/{Archive_AET}/rs'
Worklist_RS_Path = f'{AETs_Path}/{Worklist_AET}/rs'
Patients_Path = f'{Archive_RS_Path}/patients'
HL7_Apps_Path = Web_Root + '/hl7apps'
Tasks_Path = f'{Web_Root}/queue/{HL7_Send_Queue}'

# How the procedure status update leaves - a notification, not a worklist status change
PSU_Action_Send = 'SEND_NOTIFICATION'
PSU_Trigger_Study_Received = 'STUDY_RECEIVED'
PSU_Message_Type_ORU = 'ORU_R01'

# What a task of the send queue ends in - AA completes it, any other acknowledgment is a warning, and a connection
# that could not be made fails it once its retries are used up
Task_Completed = 'COMPLETED'
Task_Warning = 'WARNING'
Task_Failed = 'FAILED'

# The cipher suites the archive's TLS listener and senders are switched to, the image's own being ones a current OpenSSL no longer offers
TLS_Cipher_Suites = (
    'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
    'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
)

# Where the archive's container sees the certificates issued to it, readable to the user it runs as
Container_TLS_Directory = '/opt/zato-tls'
_Mount_Directory_Mode = 0o755
_Mount_File_Mode = 0o644

# What the image itself ships, used when nothing else was issued
_Image_Keystore = '/opt/wildfly/standalone/configuration/keystores/key.p12'
_Image_Keystore_Password = 'secret'
_Image_Truststore = '/opt/wildfly/standalone/configuration/keystores/cacerts.p12'
_Image_Truststore_Password = 'secret'

# The DICOM JSON tags of a patient
Tag_Patient_Name = '00100010'
Tag_Patient_ID = '00100020'
Tag_Patient_Birth_Date = '00100030'
Tag_Patient_Sex = '00100040'

# ################################################################################################################################
# ################################################################################################################################

class PatientRecord(NamedTuple):
    """ One patient as the archive's REST takes them.
    """
    patient_id: 'str'
    family_name: 'str'
    given_name: 'str'
    birth_date: 'str'
    sex: 'str'

# ################################################################################################################################
# ################################################################################################################################

# Where the server keeps what it deploys, what the UI's war is called, where the UI is served from and how the UI's
# stylesheet paints its photograph behind every page
Deployments_Dir = '/opt/wildfly/standalone/deployments'
UI_War_Prefix = 'dcm4chee-arc-ui2-'
UI_Path = Web_Root + '/ui2'
UI_Background_Rule_Start = b'body .background{'
UI_Background_Rule_Hidden = b'body .background{display:none}'
UI_Redeploy_Grace = 3.0

# The server's own log file, how its management port is reached, which loggers carry HL7 and what of the file a
# person following it sees - HL7 and anything at warning level or above. An entry is one line that opens with a
# date plus every line up to the next such one, which is how a message arrives with all its segments, less the
# frames of a Java stack trace, and the connection writes each message twice, its first line at info and the
# whole of it at debug, so the first goes. A task of the send queue is announced with its number, which is its
# key in the task table of the database.
Server_Log = '/opt/wildfly/standalone/log/server.log'
Log_Entry_Start = '^[0-9]{4}-[0-9]{2}-[0-9]{2} '
Log_Entry_Wanted = 'hl7|HL7|WARN|ERROR'
Log_Entry_Unwanted = 'INFO  \\[org.dcm4che3.hl7.MLLPConnection\\]'
Log_Stack_Frame = '^\\tat '
Task_Created = re.compile(r"Create Task\{taskID=(\d+), .*queueName='HL7Send'")
Database_Service = 'db'
Database_Name = 'pacsdb'
Database_User = 'pacs'
Management_Controller = 'remote+https://localhost:9993'
Management_Client = '/opt/wildfly/bin/jboss-cli.sh -c'
Management_Login = '--user=$WILDFLY_ADMIN_USER --password=$WILDFLY_ADMIN_PASSWORD'
HL7_Log_Categories = ('org.dcm4che3.hl7', 'org.dcm4che3.net.hl7', 'org.dcm4chee.arc.hl7')
Follow_Log_Entry = f'/{Log_Entry_Start}/ {{is_shown = /{Log_Entry_Wanted}/ && !/{Log_Entry_Unwanted}/}}'
Follow_Log_Line = f'is_shown && !/{Log_Stack_Frame}/ {{print; fflush()}}'
Follow_Log_Filter = f"awk '{Follow_Log_Entry} {Follow_Log_Line}'"
Follow_Log_Command = f'tail -F -n 0 {Server_Log} | {Follow_Log_Filter}'

# What the server writes when a deployment failed, and how the causes are read out of the log, each once
Startup_Failed_Marker = 'WFLYSRV0026'
Startup_Causes_Command = f"grep '^Caused by' {Server_Log} | sort -u"

# What Zato is to the archive - this device and application
Zato_Device = 'zato'
Zato_Application = 'ZATO|HOSPITAL'

# ################################################################################################################################
# ################################################################################################################################

class DCM4CHEE(LiveSystem):
    """ dcm4chee-arc-light - a PACS taking ADT, ORM and ORU over MLLP and sending HL7 out through forward rules
    and procedure status updates.
    """

    name = 'dcm4chee'
    block_number = 3
    purposes = ('web', 'dicom', 'hl7', 'hl7_tls', 'ldap', 'postgres')
    password_rules = PasswordRules(8, False, False, False, False)
    images = {
        'ldap': 'dcm4che/slapd-dcm4chee:2.6.14-35.2',
        'db':   'dcm4che/postgres-dcm4chee:17.9-35',
        'arc':  'dcm4che/dcm4chee-arc-psql:5.35.2',
    }
    directory = os.path.dirname(__file__)
    summary = 'dcm4chee-arc-light with its LDAP and PostgreSQL, HL7 on 2575 and 12575, DICOM on 11112.'
    ui_purpose = 'web'
    ui_path = UI_Path
    ui_username = 'no login, the image runs without Keycloak'
    kept_volumes = ('zato-hl7-dcm4chee-ldap-config', 'zato-hl7-dcm4chee-ldap-data')

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        """ The ports and the password, then the image's own certificates - a suite that issued the archive
        certificates of its own hands them over through tls_environment, which overrides these.
        """
        out = super().environment(ports, password)

        # The compose file mounts this whether or not anything is in it
        tls_directory = tempfile.mkdtemp(prefix='zato_hl7_dcm4chee_tls_')

        out['DCM4CHEE_TLS_DIR'] = tls_directory
        out['DCM4CHEE_KEYSTORE'] = _Image_Keystore
        out['DCM4CHEE_KEYSTORE_PASSWORD'] = _Image_Keystore_Password
        out['DCM4CHEE_TRUSTSTORE'] = _Image_Truststore
        out['DCM4CHEE_TRUSTSTORE_PASSWORD'] = _Image_Truststore_Password

        return out

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the archive's REST answers. A server that finished its startup with errors is a server
        whose deployment failed, and it stays that way - the wait ends with what the server's log says caused it.
        """
        url = handle.http_url('web') + AETs_Path

        if is_http_ok(url):
            return True

        _raise_if_startup_failed(handle)

        return False

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ The image's only HL7 application is the wildcard one, which nothing can send as - the archive looks its
        sending application up by its exact name, so it gets one of its own, unless the directory already has it.
        The archive gets a few patients too, and Zato as where its ADT notifications go.
        """
        if not ldap_entry_exists(handle, Archive_HL7_Application_DN):
            add_archive_hl7_application(handle)

        strip_ui_background(handle)
        enable_hl7_logging(handle)
        seed_patients(handle)
        publish_to_zato(handle)

# ################################################################################################################################

    def follow_logs(self, handle:'Handle') -> 'None':
        """ The server logs to a file of its own, its container's output ends with the startup - the HL7 lines and
        anything at warning level or above from that file are streamed, from now on. The server writes an outgoing
        message to its log only once it is connected, so the message a task was created for is read from the
        task itself, which is what carries it to the sender, and shown whole the moment the task appears.
        """
        for line in handle.stack.follow_exec(Archive_Service, ['sh', '-c', Follow_Log_Command]):
            print(line, flush=True)

            match = Task_Created.search(line)

            if match:
                print(queued_message(handle, match.group(1)), flush=True)
                print('', flush=True)

# ################################################################################################################################
# ################################################################################################################################

def add_archive_hl7_application(handle:'Handle') -> 'None':
    """ The archive's named HL7 application - what it sends ADT notifications, forwarded messages and
    procedure status updates as, on the same connections as its wildcard receiver, taking any message type.
    """
    ldif = f"""dn: {Archive_HL7_Application_DN}
changetype: add
objectClass: hl7Application
objectClass: dcmArchiveHL7Application
hl7ApplicationName: {Archive_HL7_Application}
dicomAETitle: {Archive_AET}
dicomDescription: The archive as a sender
hl7DefaultCharacterSet: 8859/1
hl7SendingCharacterSet: 8859/1
hl7AcceptedMessageType: *
dicomNetworkConnectionReference: cn=hl7,{Archive_Device_DN}
dicomNetworkConnectionReference: {HL7_TLS_Connection_DN}

dn: hl7ApplicationName={Archive_HL7_Application},{HL7_Registry_DN}
changetype: add
objectClass: hl7UniqueApplicationName
hl7ApplicationName: {Archive_HL7_Application}
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################
# ################################################################################################################################

def tls_environment(authority:'Authority', identity:'Identity') -> 'strstrdict':
    """ What the archive is started with so that its TLS listener presents the identity issued to it and verifies
    senders against the authority - the two stores copied where the user the archive runs as can read them.
    """
    directory = os.path.join(authority.directory, 'dcm4chee')
    os.makedirs(directory, mode=_Mount_Directory_Mode, exist_ok=True)

    keystore_name = os.path.basename(identity.keystore_path)
    truststore_name = os.path.basename(authority.truststore_path)

    for source, name in ((identity.keystore_path, keystore_name), (authority.truststore_path, truststore_name)):
        target = os.path.join(directory, name)
        _ = shutil.copyfile(source, target)
        os.chmod(target, _Mount_File_Mode)

    out = {
        'DCM4CHEE_TLS_DIR': directory,
        'DCM4CHEE_KEYSTORE': f'{Container_TLS_Directory}/{keystore_name}',
        'DCM4CHEE_KEYSTORE_PASSWORD': identity.store_password,
        'DCM4CHEE_TRUSTSTORE': f'{Container_TLS_Directory}/{truststore_name}',
        'DCM4CHEE_TRUSTSTORE_PASSWORD': authority.truststore_password,
    }

    return out

# ################################################################################################################################

def configure_hl7_tls(handle:'Handle') -> 'None':
    """ Switches the archive's TLS listener to cipher suites a current sender offers.
    """
    lines = [
        f'dn: {HL7_TLS_Connection_DN}',
        'changetype: modify',
        'replace: dicomTLSCipherSuite',
    ]

    for cipher_suite in TLS_Cipher_Suites:
        lines.append(f'dicomTLSCipherSuite: {cipher_suite}')

    ldif = '\n'.join(lines) + '\n'
    ldap_modify(handle, ldif)

# ################################################################################################################################
# ################################################################################################################################

def ldap_entry_exists(handle:'Handle', dn:'str') -> 'bool':
    """ Whether the directory has an entry - the search's exit code says, 0 for one found and 32 for no such object.
    """
    arguments = [
        'ldapsearch',
        '-x',
        '-H', 'ldap://localhost:389',
        '-D', LDAP_Admin_DN,
        '-w', handle.password,
        '-b', dn,
        '-s', 'base',
        'dn',
    ]

    status = handle.stack.exec_status(LDAP_Service, arguments)

    out = status == 0
    return out

# ################################################################################################################################

def ldap_modify(handle:'Handle', ldif:'str') -> 'None':
    """ Applies one LDIF through the directory's own client, then tells the archive to reread its configuration.
    """
    arguments = [
        'ldapmodify',
        '-x',
        '-H', 'ldap://localhost:389',
        '-D', LDAP_Admin_DN,
        '-w', handle.password,
        '-c',
    ]

    _ = handle.stack.exec(LDAP_Service, arguments, input_data=ldif.encode('utf8'))
    reload_config(handle)

# How many times a reload is tried and how long each failed one waits before the next, in seconds
Reload_Attempts = 5
Reload_Retry_Wait = 1.0

# ################################################################################################################################

def reload_config(handle:'Handle') -> 'None':
    """ Tells the archive to reread its configuration, which rebinds its listeners - a rebind finding a port still
    held fails with a 500 and the next one is tried.
    """
    url = handle.http_url('web') + Reload_Path

    for attempt in range(Reload_Attempts):

        result = request('POST', url)

        if result.status == NO_CONTENT:
            return

        is_last = attempt == Reload_Attempts - 1

        if is_last:
            expect_status(result, NO_CONTENT, 'configuration reload')

        sleep(Reload_Retry_Wait)

# ################################################################################################################################

def add_hl7_receiver(
    handle:'Handle',
    device:'str',
    application:'str',
    host:'str',
    port:'int',
    *,
    is_tls:'bool'=False,
    ) -> 'None':
    """ A foreign HL7 application the archive may send to - a device, one HL7 network connection,
    the application on it and its entry in the unique names registry. The application is `NAME|FACILITY`.
    A connection with cipher suites on it is one the archive connects to over TLS, presenting its own
    certificate and verifying the receiver's against its trust store. An entry of the same name from an earlier
    run is replaced.
    """
    device_dn = f'dicomDeviceName={device},{Devices_DN}'
    connection_dn = f'cn=hl7,{device_dn}'

    if ldap_entry_exists(handle, device_dn):
        remove_hl7_receiver(handle, device, application)

    tls_lines:'strlist' = []

    if is_tls:
        for cipher_suite in TLS_Cipher_Suites:
            tls_lines.append(f'dicomTLSCipherSuite: {cipher_suite}\n')

    tls = ''.join(tls_lines)

    ldif = f"""dn: {device_dn}
changetype: add
objectClass: dicomDevice
objectClass: dcmDevice
dicomDeviceName: {device}
dicomInstalled: TRUE

dn: {connection_dn}
changetype: add
objectClass: dicomNetworkConnection
objectClass: dcmNetworkConnection
cn: hl7
dicomHostname: {host}
dicomPort: {port}
dcmProtocol: HL7
{tls}
dn: hl7ApplicationName={application},{device_dn}
changetype: add
objectClass: hl7Application
hl7ApplicationName: {application}
dicomNetworkConnectionReference: {connection_dn}
dicomInstalled: TRUE

dn: hl7ApplicationName={application},{HL7_Registry_DN}
changetype: add
objectClass: hl7UniqueApplicationName
hl7ApplicationName: {application}
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def remove_hl7_receiver(handle:'Handle', device:'str', application:'str') -> 'None':
    device_dn = f'dicomDeviceName={device},{Devices_DN}'

    ldif = f"""dn: hl7ApplicationName={application},{HL7_Registry_DN}
changetype: delete

dn: hl7ApplicationName={application},{device_dn}
changetype: delete

dn: cn=hl7,{device_dn}
changetype: delete

dn: {device_dn}
changetype: delete
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def add_forward_rule(handle:'Handle', name:'str', receiver:'str', conditions:'strlist') -> 'None':
    """ Every received message matching the conditions, `MSH-9=ADT.*` and the like, is forwarded to the receiver.
    An entry of the same name from an earlier run is replaced.
    """
    rule_dn = f'cn={name},{Archive_Device_DN}'

    if ldap_entry_exists(handle, rule_dn):
        remove_forward_rule(handle, name)

    lines = [
        f'dn: {rule_dn}',
        'changetype: add',
        'objectClass: hl7ForwardRule',
        f'cn: {name}',
        f'hl7FwdApplicationName: {receiver}',
    ]

    for condition in conditions:
        lines.append(f'dcmProperty: {condition}')

    ldif = '\n'.join(lines) + '\n'
    ldap_modify(handle, ldif)

# ################################################################################################################################

def remove_forward_rule(handle:'Handle', name:'str') -> 'None':
    ldif = f'dn: cn={name},{Archive_Device_DN}\nchangetype: delete\n'
    ldap_modify(handle, ldif)

# ################################################################################################################################

def enable_procedure_status_update(handle:'Handle', receiver:'str', delay:'str') -> 'None':
    """ Once a study has been quiet for the delay, an ISO-8601 duration such as `PT10S`, the archive sends
    an ORU^R01 about it to the receiver.
    """
    ldif = f"""dn: {Archive_Device_DN}
changetype: modify
replace: hl7PSUSendingApplication
hl7PSUSendingApplication: {Archive_HL7_Application}
-
replace: hl7PSUReceivingApplication
hl7PSUReceivingApplication: {receiver}
-
replace: hl7PSUDelay
hl7PSUDelay: {delay}
-
replace: hl7PSUTrigger
hl7PSUTrigger: {PSU_Trigger_Study_Received}
-
replace: hl7PSUAction
hl7PSUAction: {PSU_Action_Send}
-
replace: hl7PSUMessageType
hl7PSUMessageType: {PSU_Message_Type_ORU}
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def disable_procedure_status_update(handle:'Handle') -> 'None':
    ldif = f"""dn: {Archive_Device_DN}
changetype: modify
delete: hl7PSUSendingApplication
-
delete: hl7PSUReceivingApplication
-
delete: hl7PSUDelay
-
delete: hl7PSUTrigger
-
delete: hl7PSUAction
-
delete: hl7PSUMessageType
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def enable_adt_notifications(handle:'Handle', receiver:'str') -> 'None':
    """ Every patient created, updated, merged or re-identified through the archive's REST or UI is announced
    to the receiver with an ADT message, composed and queued by the archive itself.
    """
    ldif = f"""dn: {Archive_Device_DN}
changetype: modify
replace: hl7ADTSendingApplication
hl7ADTSendingApplication: {Archive_HL7_Application}
-
replace: hl7ADTReceivingApplication
hl7ADTReceivingApplication: {receiver}
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def disable_adt_notifications(handle:'Handle') -> 'None':
    ldif = f"""dn: {Archive_Device_DN}
changetype: modify
delete: hl7ADTSendingApplication
-
delete: hl7ADTReceivingApplication
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################

def set_hl7_send_retries(handle:'Handle', max_retries:'int') -> 'None':
    """ How many times the archive tries a message its receiver could not be reached for before the task fails -
    the image ships with ten tries, half a minute and more apart.
    """
    ldif = f"""dn: {HL7_Send_Queue_DN}
changetype: modify
replace: dcmMaxRetries
dcmMaxRetries: {max_retries}
"""

    ldap_modify(handle, ldif)

# ################################################################################################################################
# ################################################################################################################################

def patient_json(patient:'PatientRecord') -> 'anydict':
    """ A patient in the DICOM JSON the archive's REST takes.
    """
    out = {
        Tag_Patient_ID: {'vr': 'LO', 'Value': [patient.patient_id]},
        Tag_Patient_Name: {'vr': 'PN', 'Value': [{'Alphabetic': f'{patient.family_name}^{patient.given_name}'}]},
        Tag_Patient_Birth_Date: {'vr': 'DA', 'Value': [patient.birth_date]},
        Tag_Patient_Sex: {'vr': 'CS', 'Value': [patient.sex]},
    }

    return out

# ################################################################################################################################

def _send_patient_json(handle:'Handle', method:'str', path:'str', patient:'PatientRecord') -> 'HTTPResult':
    url = handle.http_url('web') + path
    body = dumps(patient_json(patient)).encode('utf8')

    out = request(method, url, body=body, headers={'Content-Type': 'application/dicom+json'})
    return out

# ################################################################################################################################

def strip_ui_background(handle:'Handle') -> 'None':
    """ The UI paints a blurred photograph behind every page - the rule is taken out of every language's
    stylesheet inside the deployed war, which the server then redeploys on its own.
    """
    war_path = _ui_war_path(handle)
    war_bytes = handle.stack.exec_raw(Archive_Service, ['cat', war_path])

    published = ZipFile(BytesIO(war_bytes))
    rewritten_bytes = BytesIO()
    is_stripped = False

    with ZipFile(rewritten_bytes, 'w', ZIP_DEFLATED) as rewritten:

        for item in published.infolist():
            data = published.read(item.filename)

            if item.filename.endswith('.css') and UI_Background_Rule_Start in data:
                data = _without_background_rule(data)
                is_stripped = True

            rewritten.writestr(item, data)

    if not is_stripped:
        raise Exception(f'No background rule found in the stylesheets of {war_path}')

    _ = handle.stack.exec_raw(Archive_Service, ['sh', '-c', f'cat > {war_path}'], input_data=rewritten_bytes.getvalue())
    _wait_for_ui(handle)

# ################################################################################################################################

def _ui_war_path(handle:'Handle') -> 'str':
    listing = handle.stack.exec(Archive_Service, ['ls', Deployments_Dir])

    for name in listing.split():
        if name.startswith(UI_War_Prefix) and name.endswith('.war'):
            out = f'{Deployments_Dir}/{name}'
            return out

    raise Exception(f'No UI war under {Deployments_Dir}, the image was started with WILDFLY_DEPLOY_UI off')

# ################################################################################################################################

def _without_background_rule(css:'bytes') -> 'bytes':
    """ The whole `body .background{...}` rule replaced with one that hides the element.
    """
    start = css.index(UI_Background_Rule_Start)
    end = css.index(b'}', start) + 1

    out = css[:start] + UI_Background_Rule_Hidden + css[end:]
    return out

# ################################################################################################################################

def _wait_for_ui(handle:'Handle') -> 'None':
    """ The server notices the rewritten war and redeploys it - until it is back, the UI answers with an error.
    """
    url = handle.http_url('web') + UI_Path + '/'

    def is_back() -> 'bool':
        return is_http_ok(url)

    # It takes a moment for the redeployment to begin, before which the old one still answers
    sleep(UI_Redeploy_Grace)
    wait_until(is_back, 'the archive UI redeploying')

# ################################################################################################################################

def _raise_if_startup_failed(handle:'Handle') -> 'None':
    """ Ends the wait when the server says it started with errors, with the causes from its log.
    """
    status = handle.stack.exec_status(Archive_Service, ['grep', '-q', Startup_Failed_Marker, Server_Log])

    if status != 0:
        return

    causes = handle.stack.exec(Archive_Service, ['sh', '-c', Startup_Causes_Command])

    raise StartupFailed(f'The archive started with errors, its deployment failed:\n{causes}')

# ################################################################################################################################

def queued_message(handle:'Handle', task_id:'str') -> 'str':
    """ The HL7 message a task of the send queue carries, segment per line.
    """
    statement = f"select convert_from(payload, 'UTF8') from task where pk = {int(task_id)}"
    arguments = ['psql', '-U', Database_User, '-d', Database_Name, '-At', '-c', statement]

    output = handle.stack.exec(Database_Service, arguments)

    out = output.replace('\r', '\n').strip()
    return out

# ################################################################################################################################

def enable_hl7_logging(handle:'Handle') -> 'None':
    """ The server logs nothing of HL7 by default - the HL7 loggers go to debug, which is where every message sent
    and received, and every acknowledgment, is written with its content.
    """
    commands:'strlist' = []

    for category in HL7_Log_Categories:
        commands.append(f'/subsystem=logging/logger={category}:add(level=DEBUG)')

    joined_commands = ','.join(commands)

    # The management port speaks TLS with the image's own certificate, which the client is told to accept
    # for this one connection
    shell_command = f'echo T | {Management_Client} --controller={Management_Controller} {Management_Login} --commands="{joined_commands}"'

    arguments = ['sh', '-c', shell_command]

    output = handle.stack.exec(Archive_Service, arguments)

    if output.count('"outcome" => "success"') != len(commands):
        raise Exception(f'Could not enable HL7 logging:\n{output}')

# ################################################################################################################################

def publish_to_zato(handle:'Handle') -> 'None':
    """ The archive learns about Zato's MLLP channel on this machine and announces every patient created, edited
    or merged in its UI to it - a person clicks the pencil on a patient, saves, and the channel has the message.
    """
    port = zato_mllp_port()

    add_hl7_receiver(handle, Zato_Device, Zato_Application, Host_Address, port)
    enable_adt_notifications(handle, Zato_Application)

    print(f'  Sends to       {Host_Address}:{port}, the Zato MLLP channel on this machine ({Zato_MLLP_Port_Env} to change it)', flush=True)

# ################################################################################################################################

def seed_patients(handle:'Handle') -> 'None':
    """ A few patients for a person to find in the UI of the archive.
    """
    for patient in Seed_Patients:
        record = PatientRecord(patient.mrn, patient.family_name, patient.given_name, patient.birth_date, patient.sex)
        create_patient(handle, record)

# ################################################################################################################################

def create_patient(handle:'Handle', patient:'PatientRecord') -> 'None':
    """ A new patient through the archive's REST - with the notifications on, this brings an ADT^A28.
    """
    result = _send_patient_json(handle, 'POST', Patients_Path, patient)
    expect_status(result, OK, 'create patient')

# ################################################################################################################################

def update_patient(handle:'Handle', patient:'PatientRecord') -> 'None':
    """ A patient's demographics change - an ADT^A31 with the notifications on.
    """
    result = _send_patient_json(handle, 'PUT', f'{Patients_Path}/{patient.patient_id}', patient)
    expect_status(result, NO_CONTENT, 'update patient')

# ################################################################################################################################

def merge_patients(handle:'Handle', surviving_id:'str', prior_id:'str') -> 'None':
    """ The prior patient's records go under the surviving one - an ADT^A40 with the notifications on.
    """
    url = handle.http_url('web') + f'{Patients_Path}/{prior_id}/merge/{surviving_id}'

    result = request('POST', url)
    expect_status(result, NO_CONTENT, 'merge patients')

# ################################################################################################################################

def change_patient_id(handle:'Handle', prior_id:'str', new_id:'str') -> 'None':
    """ A patient gets a new identifier - an ADT^A47 with the notifications on.
    """
    url = handle.http_url('web') + f'{Patients_Path}/{prior_id}/changeid/{new_id}'

    result = request('POST', url)
    expect_status(result, NO_CONTENT, 'change patient id')

# ################################################################################################################################

def send_adt(handle:'Handle', receiver:'str', patient:'PatientRecord', *, is_queued:'bool'=False) -> 'HTTPResult':
    """ The archive composes an ADT^A28 about the patient and sends it to the receiver - 204 on AA, 409 with the MSA
    and ERR fields in JSON on anything else, or 202 when queued, the send queue telling the rest.
    """
    path = f'{HL7_Apps_Path}/{quote(Archive_HL7_Application)}/hl7/{quote(receiver)}/patients'

    if is_queued:
        path += '?queue=true'

    out = _send_patient_json(handle, 'POST', path, patient)
    return out

# ################################################################################################################################

def hl7_tasks(handle:'Handle') -> 'anylist':
    """ Every task of the send queue, as the tasks monitor lists them - each with its status, the message
    it carried in errorMessage or outcomeMessage and when it was processed.
    """
    url = handle.http_url('web') + Tasks_Path + '?dicomDeviceName=' + Archive_Device
    result = request('GET', url)
    expect_status(result, OK, 'HL7 send tasks')

    out = parse_json(result)
    return out

# ################################################################################################################################

def _query(handle:'Handle', resource:'str', query:'str', *, rs_path:'str'=Archive_RS_Path) -> 'any_':
    url = handle.http_url('web') + f'{rs_path}/{resource}?{query}'
    result = request('GET', url, headers={'Accept': 'application/dicom+json'})

    # No matches is an empty answer, not an empty list
    if result.status == NO_CONTENT:
        return []

    expect_status(result, OK, resource)

    out = parse_json(result)
    return out

# ################################################################################################################################

def patients(handle:'Handle', patient_id:'str') -> 'any_':
    out = _query(handle, 'patients', f'PatientID={patient_id}')
    return out

# ################################################################################################################################

def mwl_items(handle:'Handle', accession:'str') -> 'any_':
    out = _query(handle, 'mwlitems', f'AccessionNumber={accession}', rs_path=Worklist_RS_Path)
    return out

# ################################################################################################################################

def studies(handle:'Handle', accession:'str') -> 'any_':
    out = _query(handle, 'studies', f'AccessionNumber={accession}')
    return out

# ################################################################################################################################

def study_by_uid(handle:'Handle', study_uid:'str') -> 'any_':
    out = _query(handle, 'studies', f'StudyInstanceUID={study_uid}')
    return out

# ################################################################################################################################

def aets(handle:'Handle') -> 'anydict':
    url = handle.http_url('web') + AETs_Path
    result = request('GET', url)
    expect_status(result, OK, 'AE titles')

    out = parse_json(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
