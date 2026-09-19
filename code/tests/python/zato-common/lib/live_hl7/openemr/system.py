# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.http import Session, encode_form, expect_status, parse_json, request
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The service name in the compose file
Service = 'openemr'

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
Client_Admin_Page = '/interface/smart/admin-client.php'

# API paths
Registration_Path = f'/oauth2/{Site}/registration'
Token_Path = f'/oauth2/{Site}/token'
API_Root = f'/apis/{Site}/api'

# What the API client asks for
API_Scopes = 'openid offline_access api:oemr user/patient.read user/patient.write user/encounter.read user/encounter.write'

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

        if result.status != 200:
            return False

        out = b'name="authUser"' in result.body
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
    if result.status != 200 or b'name="authUser"' in result.body:
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
    expect_status(result, 200, 'API client registration')

    out = parse_json(result)
    return out

# ################################################################################################################################

def enable_api_client(session:'Session', client_id:'str') -> 'None':
    """ A registered client is disabled until an administrator enables it in the browser - this is that click.
    """
    fields:'strstrdict' = {'action': 'enable', 'client_id': client_id}
    result = session.post_form(Client_Admin_Page, fields)
    expect_status(result, 200, f'enabling API client {client_id}')

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
    expect_status(result, 200, 'API token')

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
    expect_status(result, 201, 'patient creation')

    data = parse_json(result)
    out = data['data']

    return out

# ################################################################################################################################

def create_encounter(api:'Session', patient_uuid:'str', encounter:'anydict') -> 'anydict':
    result = api.post_json(API_Root + f'/patient/{patient_uuid}/encounter', encounter)
    expect_status(result, 201, 'encounter creation')

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
    expect_status(result, 200, f'procedure provider {name}')

# ################################################################################################################################

def poll_results(session:'Session') -> 'None':
    """ Makes OpenEMR fetch and file whatever results wait in every provider's results directory now.
    """
    fields:'strstrdict' = {'form_external_refresh': '1', 'form_refresh': 'true'}
    result = session.post_form(Reports_Page, fields)
    expect_status(result, 200, 'result polling')

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
