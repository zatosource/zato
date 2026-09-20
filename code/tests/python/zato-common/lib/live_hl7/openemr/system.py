# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import CREATED, OK
from json import dumps
from urllib.parse import urlencode

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.http import Session, encode_form, expect_status, parse_json, request
from live_hl7.seed import Seed_Patients, SeedPatient
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The service names in the compose file
Service = 'openemr'
DB_Service = 'db'

# The database the image installs and its root account, whose password is the one every service is started with
Database_Name = 'openemr'
Database_Root_User = 'root'

# The account the image creates from OE_USER and OE_PASS
Admin_Username = 'admin'

# The site every path is qualified with
Site = 'default'

# Browser paths
Login_Page = f'/interface/login/login.php?site={Site}'
Login_Action = f'/interface/main/main_screen.php?auth=login&site={Site}'
Provider_Edit_Page = '/interface/orders/procedure_provider_edit.php'
Order_Form_Page = '/interface/forms/procedure_order/new.php'
Reports_Page = '/interface/orders/list_reports.php'

# API paths
Registration_Path = f'/oauth2/{Site}/registration'
Token_Path = f'/oauth2/{Site}/token'
API_Root = f'/apis/{Site}/api'

# What the API client asks for
API_Scopes = 'openid offline_access api:oemr user/patient.read user/patient.write user/encounter.read user/encounter.write'

# What the instance's seed patients are created through, and how HL7's sex codes read in OpenEMR
Seed_Client_Name = 'zato-seed'
Sex_Names = {'F': 'Female', 'M': 'Male'}

# The transport the procedure provider uses - what makes OpenEMR upload orders over SFTP and poll for results
Protocol_SFTP = 'SFTP'
Direction_Bidirectional = 'B'
Provider_Type_Lab = '1'

# ################################################################################################################################
# ################################################################################################################################

class OpenEMR(LiveSystem):
    """ OpenEMR - lab orders out as HL7 files over sFTP, lab results in from the same drop.
    """

    name = 'openemr'
    block_number = 5
    purposes = ('web', 'mariadb')
    password_rules = PasswordRules(8, True, True, True, False)
    images = {
        'db':      'mariadb:11.4',
        'openemr': 'openemr/openemr:7.0.3',
    }
    directory = os.path.dirname(__file__)
    summary = 'OpenEMR with its REST API enabled, sending procedure orders and reading results over sFTP.'
    ui_purpose = 'web'
    ui_path = '/'
    ui_username = Admin_Username
    kept_volumes = ('zato-hl7-openemr-db', 'zato-hl7-openemr-app')

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the login form is served - the image runs its own setup before that.
        """
        url = handle.http_url('web') + Login_Page
        result = request('GET', url)

        if result.status != OK:
            return False

        out = b'name="authUser"' in result.body
        return out

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ The instance gets the seed patients, unless an earlier run on the kept volumes already added them.
        """
        seed_patients(handle)

# ################################################################################################################################
# ################################################################################################################################

def seed_patients(handle:'Handle') -> 'None':
    api = admin_api(handle)

    for patient in Seed_Patients:
        payload = _seed_payload(patient)
        query = urlencode({'lname': payload['lname'], 'fname': payload['fname'], 'DOB': payload['DOB']})
        found = find_patients(api, query)

        if not found:
            _ = create_patient(api, payload)

# ################################################################################################################################

def admin_api(handle:'Handle') -> 'Session':
    """ An API session for the administrator - a client is registered and enabled for it first.
    """
    client = register_api_client(handle, Seed_Client_Name)
    enable_api_client(handle, client['client_id'])
    token = api_token(handle, client)

    out = api_session(handle, token)
    return out

# ################################################################################################################################

def _seed_payload(patient:'SeedPatient') -> 'anydict':
    birth_date = f'{patient.birth_date[:4]}-{patient.birth_date[4:6]}-{patient.birth_date[6:]}'

    out:'anydict' = {
        'pubpid': patient.mrn,
        'fname': patient.given_name,
        'lname': patient.family_name,
        'DOB': birth_date,
        'sex': Sex_Names[patient.sex],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ A browser session logged in as the administrator.
    """
    out = Session(handle.http_url('web'))

    _ = out.get(Login_Page)

    fields:'strstrdict' = {
        'new_login_session_management': '1',
        'authProvider': 'Default',
        'authUser': Admin_Username,
        'clearPass': handle.password,
        'languageChoice': '1',
    }

    result = out.post_form(Login_Action, fields)

    # The main screen answers 200 when logged in, the login page comes back otherwise
    if result.status != OK or b'name="authUser"' in result.body:
        raise Exception(f'OpenEMR login failed, status {result.status}')

    return out

# ################################################################################################################################

def register_api_client(handle:'Handle', name:'str') -> 'anydict':
    """ Registers a confidential API client, returning what the server assigned it.
    """
    payload = {
        'application_type': 'private',
        'redirect_uris': [handle.http_url('web') + '/callback'],
        'client_name': name,
        'token_endpoint_auth_method': 'client_secret_post',
        'scope': API_Scopes,
    }

    url = handle.http_url('web') + Registration_Path
    result = request('POST', url, body=_json_bytes(payload), headers={'Content-Type': 'application/json'})
    expect_status(result, OK, 'API client registration')

    out = parse_json(result)
    return out

# ################################################################################################################################

def enable_api_client(handle:'Handle', client_id:'str') -> 'None':
    """ A registered client is disabled until an administrator enables it, which is this one row.
    """
    statement = f"update oauth_clients set is_enabled = 1 where client_id = '{client_id}'"
    arguments = ['mariadb', f'-u{Database_Root_User}', f'-p{handle.password}', Database_Name, '-e', statement]

    _ = handle.stack.exec(DB_Service, arguments)

# ################################################################################################################################

def api_token(handle:'Handle', client:'anydict') -> 'str':
    """ A bearer token for the administrator through the password grant.
    """
    fields:'strstrdict' = {
        'grant_type': 'password',
        'client_id': client['client_id'],
        'client_secret': client['client_secret'],
        'scope': API_Scopes,
        'user_role': 'users',
        'username': Admin_Username,
        'password': handle.password,
    }

    url = handle.http_url('web') + Token_Path
    result = request('POST', url, body=_form_bytes(fields), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    expect_status(result, OK, 'API token')

    data = parse_json(result)
    out = data['access_token']

    return out

# ################################################################################################################################

def api_session(handle:'Handle', token:'str') -> 'Session':
    out = Session(handle.http_url('web'))
    out.headers['Authorization'] = f'Bearer {token}'

    return out

# ################################################################################################################################

def create_patient(api:'Session', patient:'anydict') -> 'anydict':
    result = api.post_json(API_Root + '/patient', patient)
    expect_status(result, CREATED, 'patient creation')

    data = parse_json(result)
    out = data['data']

    return out

# ################################################################################################################################

def create_encounter(api:'Session', patient_uuid:'str', encounter:'anydict') -> 'anydict':
    result = api.post_json(API_Root + f'/patient/{patient_uuid}/encounter', encounter)
    expect_status(result, CREATED, 'encounter creation')

    data = parse_json(result)
    out = data['data']

    return out

# ################################################################################################################################

def find_patients(api:'Session', query:'str') -> 'any_':
    data = api.get_json(API_Root + f'/patient?{query}')
    out = data['data']

    return out

# ################################################################################################################################

def create_procedure_provider(
    session:'Session',
    *,
    name:'str',
    sending_application:'str',
    sending_facility:'str',
    receiving_application:'str',
    receiving_facility:'str',
    remote_host:'str',
    login_name:'str',
    password:'str',
    orders_path:'str',
    results_path:'str',
    ) -> 'None':
    """ A lab OpenEMR sends orders to over SFTP and reads results from - the remote host has to resolve
    from inside the container on port 22, and only a password logs in.
    """
    fields:'strstrdict' = {
        'form_name': name,
        'form_npi': '',
        'form_send_app_id': sending_application,
        'form_send_fac_id': sending_facility,
        'form_recv_app_id': receiving_application,
        'form_recv_fac_id': receiving_facility,
        'form_DorP': 'P',
        'form_direction': Direction_Bidirectional,
        'form_protocol': Protocol_SFTP,
        'form_remote_host': remote_host,
        'form_login': login_name,
        'form_password': password,
        'form_orders_path': orders_path,
        'form_results_path': results_path,
        'form_notes': '',
        'form_lab_director': '',
        'form_type': Provider_Type_Lab,
        'form_active': '1',
        'bn_save': 'Save',
    }

    result = session.post_form(Provider_Edit_Page, fields)
    expect_status(result, OK, f'procedure provider {name}')

# ################################################################################################################################

def poll_results(session:'Session') -> 'None':
    """ Makes OpenEMR fetch and file whatever results wait in every provider's results directory now.
    """
    fields:'strstrdict' = {'form_external_refresh': '1', 'form_refresh': 'true'}
    result = session.post_form(Reports_Page, fields)
    expect_status(result, OK, 'result polling')

# ################################################################################################################################

def _json_bytes(payload:'any_') -> 'bytes':
    out = dumps(payload).encode('utf8')
    return out

# ################################################################################################################################

def _form_bytes(fields:'strstrdict') -> 'bytes':
    out = encode_form(fields)
    return out

# ################################################################################################################################
# ################################################################################################################################
