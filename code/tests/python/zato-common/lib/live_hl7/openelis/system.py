# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from string import Template

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.fetch import work_directory
from live_hl7.http import Session, expect_status, is_http_ok, parse_json, request
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strintdict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Service names in the compose file
Webapp_Service = 'oe.openelis.org'
Bridge_Service = 'bridge'

# The administrator the image creates with DEFAULT_PW
Admin_Username = 'admin'

# The bridge's own account for its /input endpoint
Bridge_Username = 'bridge'

# The webapp's context, as served by the webapp itself rather than the project's proxy
Context_Path = '/OpenELIS-Global'

# Where the bridge posts what it receives, on the stack's own network
Webapp_Analyzer_URI = f'https://{Webapp_Service}:8443{Context_Path}/analyzer'

# The rendered bridge configuration lives here
Bridge_Config_Dir_Name = 'openelis-bridge'
Bridge_Config_File_Name = 'configuration.yml'
Bridge_Config_Template = os.path.join(os.path.dirname(__file__), 'bridge-configuration.yml')

# Analyzer protocols and modes, as the webapp names them
Protocol_HL7 = 'HL7'
Mode_Both = 'BOTH'

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
        'certs':            'itechuw/certgen:main',
        'db.openelis.org':  'itechuw/openelis-global-2-database:3.2.2.0',
        'oe.openelis.org':  'itechuw/openelis-global-2:3.2.2.0',
        'fhir.openelis.org': 'itechuw/openelis-global-2-fhir:3.2.2.0',
        'bridge':           'itechuw/openelis-analyzer-bridge:3.0.5',
    }
    directory = os.path.dirname(__file__)
    summary = 'OpenELIS Global 2 with its FHIR store and analyzer bridge, MLLP in on the bridge, orders out from the webapp.'
    ui_purpose = 'web'
    ui_path = Context_Path + '/'
    ui_is_https = True
    ui_username = Admin_Username

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out['OPENELIS_BRIDGE_CONFIG'] = _bridge_config_path()

        return out

# ################################################################################################################################

    def prepare(self, handle:'Handle') -> 'None':
        """ Renders the bridge configuration with the webapp's address and our credentials.
        """
        with open(Bridge_Config_Template, encoding='utf8') as f:
            template = Template(f.read())

        values:'strstrdict' = {
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

        if result.status != 200:
            return False

        data = parse_json(result)
        out = data['status'] == 'UP'

        return out

# ################################################################################################################################
# ################################################################################################################################

def _bridge_config_path() -> 'str':
    out = os.path.join(work_directory(Bridge_Config_Dir_Name), Bridge_Config_File_Name)
    return out

# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ A session logged in the way the frontend logs in - a CSRF token first, then the credentials.
    """
    out = Session(handle.https_url('web') + Context_Path, verify_tls=False)

    result = out.get('/csrf')
    expect_status(result, 200, 'CSRF token')

    data = parse_json(result)
    out.headers['X-CSRF-Token'] = data['token']

    result = out.post_json('/ValidateLogin', {'loginName': Admin_Username, 'password': handle.password})
    expect_status(result, 200, 'login')

    return out

# ################################################################################################################################

def register_analyzer(
    session:'Session',
    *,
    name:'str',
    identifier_pattern:'str',
    host:'str',
    port:'int',
    test_mappings:'anylist',
    ) -> 'anydict':
    """ An HL7 analyzer the webapp recognises by MSH-3 and sends orders to at the host and port.
    """
    payload = {
        'name':                  name,
        'protocol':              Protocol_HL7,
        'identifierPattern':     identifier_pattern,
        'mode':                  Mode_Both,
        'supportsLisInitiated':  True,
        'destinationHost':       host,
        'destinationPort':       port,
        'active':                True,
        'testMappings':          test_mappings,
    }

    result = session.post_json('/rest/analyzer/analyzers', payload)

    if result.status not in (200, 201):
        body = result.body.decode('utf8', 'replace')
        raise Exception(f'Could not register analyzer {name}, status {result.status}, body: {body}')

    out = parse_json(result)
    return out

# ################################################################################################################################

def analyzers(session:'Session') -> 'any_':
    out = session.get_json('/rest/analyzer/analyzers')
    return out

# ################################################################################################################################

def send_order(session:'Session', analyzer_id:'str', accession:'str') -> 'anydict':
    """ Makes the webapp hand an order for one accession to the bridge, which delivers it over MLLP.
    """
    result = session.post_json(f'/rest/analyzer/analyzers/{analyzer_id}/send-order', {'accessionNumber': accession})

    if result.status not in (200, 201, 202):
        body = result.body.decode('utf8', 'replace')
        raise Exception(f'Could not send an order for {accession}, status {result.status}, body: {body}')

    out = parse_json(result)
    return out

# ################################################################################################################################

def tests(session:'Session') -> 'any_':
    """ The laboratory's test catalogue, for picking a test an analyzer code maps to.
    """
    out = session.get_json('/rest/tests')
    return out

# ################################################################################################################################

def create_sample_patient_entry(session:'Session', entry:'anydict') -> 'anydict':
    """ One patient with one sample and its tests, the way the order entry form posts it.
    """
    result = session.post_json('/rest/SamplePatientEntry', entry)

    if result.status not in (200, 201):
        body = result.body.decode('utf8', 'replace')
        raise Exception(f'Could not create the sample patient entry, status {result.status}, body: {body}')

    out = parse_json(result)
    return out

# ################################################################################################################################

def analyzer_results(session:'Session') -> 'any_':
    """ Results received from analyzers, waiting to be accepted.
    """
    out = session.get_json('/rest/AnalyzerResults')
    return out

# ################################################################################################################################

def results_for_validation(session:'Session', test_section_id:'str') -> 'any_':
    out = session.get_json(f'/rest/ResultValidation?testSectionId={test_section_id}')
    return out

# ################################################################################################################################
# ################################################################################################################################
