# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from hashlib import sha256

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import SOAPFault, SOAPVersion
from zato.common.soap.message import SOAPMessage
from soap_channel import create_soap_channel, delete_soap_channel, wait_for_channel_fixture_services
from soap_outconn import create_soap_outconn, delete_soap_outconn, invoke_soap_outconn_from_ide, \
    wait_for_soap_invoker_service
from wss_definition import change_wss_password, create_wss_definition, delete_wss_definition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.channel.live.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture services this suite's channels point to, deployed during server boot
_Registry_Service  = 'test.soap.channel.registry'
_Documents_Service = 'test.soap.channel.documents'
_Echo_Service      = 'test.soap.channel.echo'
_Protected_Service = 'test.soap.channel.protected'
_Faulty_Service    = 'test.soap.channel.faulty'

# The fault code local names of each SOAP version, keyed by the version-independent names
_Sender_Code_By_Version   = {SOAPVersion.V11: 'Client', SOAPVersion.V12: 'Sender'}
_Receiver_Code_By_Version = {SOAPVersion.V11: 'Server', SOAPVersion.V12: 'Receiver'}

# Log patterns produced by the server when WS-Security enforcement rejects a message
_WSS_Log_Patterns = ('401 Unauthorized path_info',)

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _new_channel_client(server_port:'int', url_path:'str', config:'anydict | None'=None) -> 'SOAPClient':
    """ Returns a SOAP client pointed at a channel of the server under test - exactly
    what an external SOAP counterparty is.
    """

    client_config = {
        'address': f'http://127.0.0.1:{server_port}{url_path}',
        'timeout': 10,
    } # type: anydict

    if config:
        client_config.update(config)

    out = SOAPClient(client_config)
    return out

# ################################################################################################################################

def _invoke_with_retry(client:'SOAPClient', operation:'str', message:'SOAPMessage') -> 'any_':
    """ Invokes a channel, retrying while the configuration made a moment ago in the browser
    propagates to the server - until then the URL is unknown or stale credentials are
    still in effect, so both parse errors and faults are retried.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = client.invoke(operation, message)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            return out

    raise Exception(f'Could not invoke `{client.address}` within {_Propagation_Timeout}s, last error: {last_error!r}')

# ################################################################################################################################

def _invoke_expecting_fault(client:'SOAPClient', operation:'str', message:'SOAPMessage') -> 'SOAPFault':
    """ Invokes a channel and returns the SOAP fault it answered with, retrying other errors
    while the channel configured a moment ago in the browser propagates to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            response = client.invoke(operation, message)
        except SOAPFault as fault:
            return fault
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            raise Exception(f'Expected a fault from `{client.address}`, got: {response!r}')

    raise Exception(f'No fault from `{client.address}` within {_Propagation_Timeout}s, last error: {last_error!r}')

# ################################################################################################################################

def _invoke_outconn_with_retry(page:'Page', base_url:'str', outconn_name:'str', operation:'str', **kwargs:'any_') -> 'anydict':
    """ Invokes an outgoing connection through the pre-deployed service, driven from the IDE
    in the browser, retrying while the pair configured a moment ago propagates to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_soap_outconn_from_ide(page, base_url, outconn_name, operation, **kwargs)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            # The service reports errors as a reply field, e.g. while the connection
            # or the channel it points back at is still propagating to the server.
            if error := (out.get('error') or out.get('fault_code')):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return out

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelEndToEnd:
    """ End-to-end scenarios for SOAP channels - every channel is configured through
    the browser and then exercised by real SOAP traffic over HTTP, which is what
    a SOAP counterparty sends, with assertions on what came back over the wire.
    """

# ################################################################################################################################

    def test_cdc_style_channel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A CDC IIS-style channel - the pre-deployed service reads the HL7 message
        through dot access and the caller receives the HL7 ACK it built.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        name = _Test_Name_Prefix + 'cdc'
        url_path = '/' + name

        # Create the channel through the browser ..
        channel_id = create_soap_channel(page, base_url, name, _Registry_Service, url_path, {
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
            'soap_version': '1.2',
        })

        # .. build a real submitSingleMessage envelope, the way a counterparty does ..
        message_control_id = 'MSG-' + CryptoManager.generate_hex_string()

        message = SOAPMessage()
        message.namespace = 'urn:cdc:iisb:2014'
        message.username = 'registry-client'
        message.facilityID = 'FAC-01'
        message.hl7Message = f'MSH|^~\\&|MYAPP|FAC-01|IIS|STATE|20260115||VXU^V04^VXU_V04|{message_control_id}|P|2.5.1'

        # .. post it over HTTP ..
        client = _new_channel_client(server_port, url_path, {
            'soap_version': '1.2',
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
        })

        response = _invoke_with_retry(client, 'submitSingleMessage', message)

        # .. and the reply is the HL7 ACK the service built, echoing the control id.
        acknowledgment = getattr(response.submitSingleMessageResponse, 'return')

        assert acknowledgment.startswith('MSH|'), f'Expected an HL7 ACK, got: {acknowledgment}'
        assert f'MSA|AA|{message_control_id}' in acknowledgment, \
            f'Expected the control id echoed in MSA, got: {acknowledgment}'

        # Clean up.
        client.close()
        delete_soap_channel(page, channel_id)

# ################################################################################################################################

    def test_loopback_both_versions(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Loopback - an outgoing SOAP connection pointed back at a channel of the same
        server, so one invocation crosses the whole stack twice, in both SOAP versions.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        for soap_version in (SOAPVersion.V11, SOAPVersion.V12):

            version_tag = soap_version.replace('.', '')
            name = _Test_Name_Prefix + 'loopback-' + version_tag
            url_path = '/' + name

            # A channel with the echo service behind it ..
            channel_id = create_soap_channel(page, base_url, name, _Echo_Service, url_path, {
                'soap_action': 'urn:cdc:iisb:2014:connectivityTest',
                'soap_version': soap_version,
            })

            # .. and an outgoing connection pointed back at that channel.
            outconn_id = create_soap_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
                'url_path': url_path,
                'soap_version': soap_version,
                'soap_action': 'urn:cdc:iisb:2014:connectivityTest',
            })

            # One call now goes service -> outgoing connection -> channel -> service and back.
            result = _invoke_outconn_with_retry(page, base_url, name, 'connectivityTest',
                namespace='urn:cdc:iisb:2014',
                fields={'echoBack': 'round trip ' + version_tag},
                response_fields=['echoed', 'observedVersion', 'observedOperation'],
            )

            fields = result['fields']

            assert fields['echoed'] == 'round trip ' + version_tag, f'Expected the echo back, got: {result}'
            assert fields['observedVersion'] == soap_version, \
                f'Expected the channel to see SOAP {soap_version}, got: {result}'
            assert fields['observedOperation'] == 'connectivityTest', \
                f'Expected the channel to see the operation, got: {result}'

            # Clean up this version's pair.
            delete_soap_outconn(page, outconn_id)
            delete_soap_channel(page, channel_id)

# ################################################################################################################################

    def test_mtom_channel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An IHE-style MTOM channel - a multipart document submission goes in,
        the service reads plain bytes, and the reply leaves as an MTOM package.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        name = _Test_Name_Prefix + 'mtom'
        url_path = '/' + name

        # The channel has MTOM responses enabled in the browser form ..
        channel_id = create_soap_channel(page, base_url, name, _Documents_Service, url_path, {
            'soap_action': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
            'soap_version': '1.2',
            'use_mtom': True,
        })

        # .. the submission carries the document as an MTOM part ..
        document_bytes = ('BINARY-DOCUMENT-' + CryptoManager.generate_hex_string()).encode()

        message = SOAPMessage()
        message.namespace = 'urn:ihe:iti:xds-b:2007'
        message.Document = document_bytes

        client = _new_channel_client(server_port, url_path, {
            'soap_version': '1.2',
            'soap_action': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
            'use_mtom': True,
        })

        response = _invoke_with_retry(client, 'ProvideAndRegisterDocumentSet', message)
        operation_response = response.ProvideAndRegisterDocumentSetResponse

        # .. the service saw the document as plain bytes, delivered as one MIME part ..
        assert operation_response.status == 'urn:ihe:iti:2007:ResponseStatusType:Success', \
            f'Expected a success status, got: {operation_response!r}'
        assert operation_response.documentLength == str(len(document_bytes)), \
            f'Expected the document length, got: {operation_response!r}'
        assert operation_response.partCount == '1', f'Expected one MIME part, got: {operation_response!r}'

        # .. the receipt reads as the digest bytes, which proves the xop:Include
        # reference in the reply was resolved from a real MTOM part ..
        assert operation_response.receipt == sha256(document_bytes).digest(), \
            f'Expected the document digest, got: {operation_response!r}'

        # .. and the reply really was a multipart package on the wire.
        assert len(response.attachments) == 1, f'Expected one response attachment, got: {response.attachments!r}'

        # Clean up.
        client.close()
        delete_soap_channel(page, channel_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_WSS_Log_Patterns)
    def test_wss_username_token(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A UsernameToken-protected channel admits the correct token and rejects
        a wrong or missing one with a fault of the request's SOAP version.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        name = _Test_Name_Prefix + 'wss'
        url_path = '/' + name
        username = 'user.' + name
        password = 'password.' + CryptoManager.generate_hex_string(32)

        # Create the security definition in the browser and give it a known password ..
        wss_id = create_wss_definition(page, base_url, name, username, 'username_token')
        change_wss_password(page, wss_id, password)

        # .. and the channel with that definition attached.
        channel_id = create_soap_channel(page, base_url, name, _Protected_Service, url_path, {
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
            'security': f'WS-Security/{name}',
        })

        for soap_version in (SOAPVersion.V11, SOAPVersion.V12):

            message = SOAPMessage()
            message.namespace = 'urn:cdc:iisb:2014'
            message.facilityID = 'FAC-01'

            # The correct token is admitted and the service sees the verified user ..
            client = _new_channel_client(server_port, url_path, {
                'soap_version': soap_version,
                'security': {
                    'mode': 'username_token',
                    'username': username,
                    'password': password,
                    'use_digest': False,
                },
            })

            response = _invoke_with_retry(client, 'submitSingleMessage', message)
            operation_response = response.submitSingleMessageResponse

            assert operation_response.status == 'ok', f'Expected an ok response, got: {operation_response!r}'
            assert operation_response.verifiedMode == 'username_token', \
                f'Expected the verified mode, got: {operation_response!r}'
            assert operation_response.verifiedUser == username, \
                f'Expected the verified user, got: {operation_response!r}'

            client.close()

            # .. a wrong password is rejected with a Sender fault of this version ..
            wrong_client = _new_channel_client(server_port, url_path, {
                'soap_version': soap_version,
                'security': {
                    'mode': 'username_token',
                    'username': username,
                    'password': 'wrong.' + CryptoManager.generate_hex_string(32),
                    'use_digest': False,
                },
            })

            fault = _invoke_expecting_fault(wrong_client, 'submitSingleMessage', message)
            expected_code = _Sender_Code_By_Version[soap_version]

            assert fault.code == expected_code, f'Expected a {expected_code} fault, got: {fault.code} {fault.reason}'

            wrong_client.close()

            # .. and so is a message with no token at all.
            anonymous_client = _new_channel_client(server_port, url_path, {
                'soap_version': soap_version,
            })

            fault = _invoke_expecting_fault(anonymous_client, 'submitSingleMessage', message)

            assert fault.code == expected_code, f'Expected a {expected_code} fault, got: {fault.code} {fault.reason}'

            anonymous_client.close()

        # Clean up.
        delete_soap_channel(page, channel_id)
        delete_wss_definition(page, wss_id)

# ################################################################################################################################

    def test_fault_propagation(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Service exceptions surface as well-formed faults of the request's SOAP version -
        client errors as Sender faults with their message, everything else as Receiver
        faults with no internals ever reaching the wire.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        registry_name = _Test_Name_Prefix + 'fault-sender'
        registry_url_path = '/' + registry_name

        faulty_name = _Test_Name_Prefix + 'fault-receiver'
        faulty_url_path = '/' + faulty_name

        # One channel whose service rejects bad input, one whose service always breaks.
        registry_channel_id = create_soap_channel(
            page, base_url, registry_name, _Registry_Service, registry_url_path, {
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
        })

        faulty_channel_id = create_soap_channel(
            page, base_url, faulty_name, _Faulty_Service, faulty_url_path, {
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
        })

        for soap_version in (SOAPVersion.V11, SOAPVersion.V12):

            # A submission without the required field - the BadRequest the service
            # raises becomes a Sender fault carrying its message ..
            message = SOAPMessage()
            message.namespace = 'urn:cdc:iisb:2014'
            message.hl7Message = 'MSH|^~\\&|MYAPP|FAC-01|IIS|STATE|20260115||VXU^V04^VXU_V04|MSG-01|P|2.5.1'

            client = _new_channel_client(server_port, registry_url_path, {'soap_version': soap_version})
            fault = _invoke_expecting_fault(client, 'submitSingleMessage', message)
            client.close()

            expected_code = _Sender_Code_By_Version[soap_version]

            assert fault.code == expected_code, f'Expected a {expected_code} fault, got: {fault.code} {fault.reason}'
            assert fault.reason == 'facilityID is required', f'Expected the rejection message, got: {fault.reason}'

            # .. while an ordinary exception becomes a Receiver fault whose reason
            # is the generic message - never the exception's own details.
            client = _new_channel_client(server_port, faulty_url_path, {'soap_version': soap_version})
            fault = _invoke_expecting_fault(client, 'submitSingleMessage', message)
            client.close()

            expected_code = _Receiver_Code_By_Version[soap_version]

            assert fault.code == expected_code, f'Expected a {expected_code} fault, got: {fault.code} {fault.reason}'
            assert 'internal detail' not in fault.reason, f'The exception leaked to the wire: {fault.reason}'
            assert 'RuntimeError' not in fault.reason, f'The exception leaked to the wire: {fault.reason}'
            assert 'Traceback' not in fault.reason, f'A traceback leaked to the wire: {fault.reason}'

        # Clean up.
        delete_soap_channel(page, registry_channel_id)
        delete_soap_channel(page, faulty_channel_id)

# ################################################################################################################################
# ################################################################################################################################
