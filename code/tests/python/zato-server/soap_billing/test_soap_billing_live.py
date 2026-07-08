# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from base64 import b64encode
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The paths the SOAP connections point at, exactly as the server receives them,
# with the space in the company name arriving percent-encoded.
_Path_Header_Main  = '/erp/WS/North%20Trading%20Ltd./Codeunit/InvoiceEntryService'
_Path_Header_Branch = '/erp/WS/South%20Retail%20Group/Codeunit/InvoiceEntryService'
_Path_Slow = '/erp/slow/Codeunit/InvoiceEntryService'
_Path_Payment = '/erp/WS/North%20Trading%20Ltd./Codeunit/PaymentEntryService'

# The paths the REST connections build from their {env} and {company} parameters
_Path_Rest_Invoice = '/v2.0/production/WS/North%20Trading%20Ltd./Codeunit/InvoiceEntryService'
_Path_Rest_Payment_Status = '/v2.0/production/WS/North%20Trading%20Ltd./Page/PaymentStatus'

# The SOAPAction values from the connection definitions
_Action_Create_Header = 'urn:example-erp/codeunit/InvoiceEntryService:CreateInvoiceHeader'
_Action_Create_Lines  = 'urn:example-erp/codeunit/InvoiceEntryService:CreateInvoiceLines'
_Action_Register_Payment = 'urn:example-erp/codeunit/PaymentEntryService:RegisterPayment'
_Action_Rest_Invoice = 'urn:example-erp/codeunit/InvoiceEntryService'
_Action_Payment_Status = 'urn:example-erp/page/PaymentStatus:GetPaymentStatus'

# The static bodies the ERP answers with - consumed by the services as raw strings
_Raw_Header_Result = b'<CreateInvoiceHeader_Result xmlns="urn:example-erp/codeunit/InvoiceEntryService">' \
    b'<return_value>INV-2026-0001</return_value></CreateInvoiceHeader_Result>'

_Raw_Lines_Result = b'<CreateInvoiceLines_Result xmlns="urn:example-erp/codeunit/InvoiceEntryService">' \
    b'<return_value>2</return_value></CreateInvoiceLines_Result>'

_Raw_Payment_Result = b'<RegisterPayment_Result xmlns="urn:example-erp/codeunit/PaymentEntryService">' \
    b'<return_value>PAY-2026-0001</return_value></RegisterPayment_Result>'

_Raw_Invoice_Ack = b'<InvoiceImport_Result xmlns="urn:example-erp/codeunit/InvoiceEntryService">' \
    b'<status>Accepted</status></InvoiceImport_Result>'

_Raw_Payment_Status = b'<GetPaymentStatus_Result xmlns="urn:example-erp/page/PaymentStatus">' \
    b'<status>Settled</status></GetPaymentStatus_Result>'

# A complete invoice the tests post to the JSON channels
_Invoice_Request = {
    'invoiceNo': 'INV-2026-0007',
    'customerNo': 'CUST-0042',
    'notes': 'Quarterly maintenance services',
    'paymentTerms': '30D',
    'documentDate': '2026-01-15',
    'dueDate': '2026-02-14',
    'currencyCode': 'EUR',
    'contactEmail': 'billing@example.com',
    'yourReference': 'REF-2026-0007',
}

# Invoice lines with characters that must survive only because of the CDATA section
_Lines_Request = {
    'invoiceNo': 'INV-2026-0007',
    'lineNo': 10,
    'itemNo': 'ITEM-100',
    'description': 'Spare parts <B-42> for pumps & valves',
    'quantity': '3',
    'unitOfMeasure': 'PCS',
    'unitPrice': '125.50',
    'vatGroup': 'STANDARD',
}

_Payment_Request = {
    'paymentNo': 'PAY-2026-0031',
    'invoiceNo': 'INV-2026-0007',
    'amount': '376.50',
    'currencyCode': 'EUR',
    'paymentDate': '2026-02-10',
    'payerReference': 'WIRE-2026-4411',
}

# The SOAP 1.1 envelope the external submitter posts to the invoice channel
_Submitted_Invoice_Envelope = b"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:inv="urn:example-erp/codeunit/InvoiceEntryService">
    <soapenv:Header/>
    <soapenv:Body>
        <inv:ImportInvoice>
            <inv:invoiceNo>INV-2026-0011</inv:invoiceNo>
            <inv:customerNo>CUST-0042</inv:customerNo>
            <inv:currencyCode>EUR</inv:currencyCode>
        </inv:ImportInvoice>
    </soapenv:Body>
</soapenv:Envelope>"""

# The SOAP 1.1 envelope the external submitter posts to the payment-status channel
_Payment_Status_Envelope = b"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pay="urn:example-erp/page/PaymentStatus">
    <soapenv:Header/>
    <soapenv:Body>
        <pay:GetPaymentStatus>
            <pay:paymentNo>PAY-2026-0031</pay:paymentNo>
        </pay:GetPaymentStatus>
    </soapenv:Body>
</soapenv:Envelope>"""

_Request_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _basic_auth_header(username:'str', password:'str') -> 'str':
    """ Builds the value of a basic-auth Authorization header.
    """
    token = b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')
    out = f'Basic {token}'
    return out

# ################################################################################################################################

def _post(url:'str', body:'bytes', headers:'anydict') -> 'any_':
    """ Posts a request and returns (status, headers, body-bytes), turning HTTP errors
    into regular results so tests can assert on 4xx and 5xx responses. The headers come
    back as the case-insensitive message object because the server sends lowercase names.
    """
    request = Request(url, data=body, headers=headers, method='POST')

    try:
        with urlopen(request, timeout=_Request_Timeout) as response:
            out = (response.status, response.headers, response.read())
    except HTTPError as http_error:
        out = (http_error.code, http_error.headers, http_error.read())

    return out

# ################################################################################################################################

def _post_json(server_port:'int', path:'str', data:'anydict') -> 'any_':
    """ Posts a JSON document to one of the application channels.
    """
    url = f'http://127.0.0.1:{server_port}{path}'
    body = dumps(data).encode('utf-8')
    out = _post(url, body, {'Content-Type': 'application/json'})
    return out

# ################################################################################################################################

def _build_header_envelope(invoice:'anydict') -> 'bytes':
    """ Rebuilds the exact envelope the CreateInvoiceHeader service produces so tests
    can assert the connection passed it through byte-for-byte.
    """
    out = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:inv="urn:example-erp/codeunit/InvoiceEntryService">
            <soapenv:Header/>
            <soapenv:Body>
                <inv:CreateInvoiceHeader>
                    <inv:invoiceNo>{invoice['invoiceNo']}</inv:invoiceNo>
                    <inv:customerNo>{invoice['customerNo']}</inv:customerNo>
                    <inv:notes>{invoice['notes']}</inv:notes>
                    <inv:paymentTerms>{invoice['paymentTerms']}</inv:paymentTerms>
                    <inv:documentDate>{invoice['documentDate']}</inv:documentDate>
                    <inv:dueDate>{invoice['dueDate']}</inv:dueDate>
                    <inv:currencyCode>{invoice['currencyCode']}</inv:currencyCode>
                    <inv:contactEmail>{invoice['contactEmail']}</inv:contactEmail>
                    <inv:yourReference>{invoice['yourReference']}</inv:yourReference>
                </inv:CreateInvoiceHeader>
            </soapenv:Body>
            </soapenv:Envelope>
            """.encode('utf8')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPBillingLive:
    """ Live tests for the three SOAP usage patterns of the billing application - envelopes
    sent through conn.send, plain channels carrying SOAP, and RESTAdapters posting SOAP.
    """

# ################################################################################################################################

    def test_invoice_header_send(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # Prepare the ERP's static answer for this operation ..
        soap_test_server.configure(_Path_Header_Main, respond_raw=(OK, _Raw_Header_Result, 'text/xml; charset=utf-8'))
        soap_test_server.clear_requests()

        # .. invoke the service through its JSON channel ..
        status, _, body = _post_json(zato_server['server_port'], '/billing/invoice-header/main', _Invoice_Request)

        # .. the caller received the ERP's raw response string back ..
        assert status == OK
        assert body == _Raw_Header_Result

        # .. and the ERP received exactly what the service built.
        record = soap_test_server.last_request

        assert record['path'] == _Path_Header_Main
        assert record['headers']['SOAPAction'] == _Action_Create_Header
        assert record['headers']['Content-Type'].startswith('text/xml')

        # The basic-auth credentials from the connection's security definition
        expected_auth = _basic_auth_header(billing_config['gateway_username'], billing_config['gateway_password'])
        assert record['headers']['Authorization'] == expected_auth

        # The envelope went through byte-for-byte - no double-wrapping, no rewriting
        assert record['raw_body'] == _build_header_envelope(_Invoice_Request)
        assert record['raw_body'].count(b'<soapenv:Envelope') == 1

# ################################################################################################################################

    def test_invoice_header_branch_connection(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # The same inherited service works through a different connection ..
        soap_test_server.configure(_Path_Header_Branch, respond_raw=(OK, _Raw_Header_Result, 'text/xml; charset=utf-8'))
        soap_test_server.clear_requests()

        status, _, body = _post_json(zato_server['server_port'], '/billing/invoice-header/branch', _Invoice_Request)

        assert status == OK
        assert body == _Raw_Header_Result

        # .. and it is the branch endpoint that was invoked.
        record = soap_test_server.last_request

        assert record['path'] == _Path_Header_Branch
        assert record['headers']['SOAPAction'] == _Action_Create_Header
        assert record['raw_body'] == _build_header_envelope(_Invoice_Request)

# ################################################################################################################################

    def test_invoice_lines_cdata(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        soap_test_server.configure(_Path_Header_Main, respond_raw=(OK, _Raw_Lines_Result, 'text/xml; charset=utf-8'))
        soap_test_server.clear_requests()

        status, _, body = _post_json(zato_server['server_port'], '/billing/invoice-lines', _Lines_Request)

        assert status == OK
        assert body == _Raw_Lines_Result

        record = soap_test_server.last_request

        # This operation shares the endpoint but carries its own action
        assert record['path'] == _Path_Header_Main
        assert record['headers']['SOAPAction'] == _Action_Create_Lines

        # The CDATA section arrived intact, with the markup characters unescaped inside it
        description = _Lines_Request['description']
        expected_cdata = f'<inv:description><![CDATA[{description}]]></inv:description>'.encode('utf8')
        assert expected_cdata in record['raw_body']

        # The parsed body confirms the CDATA text is readable on the receiving side
        assert record['body'].CreateInvoiceLines.description == description

# ################################################################################################################################

    def test_payment_register_tls(
        self,
        zato_server:'anydict',
        soap_test_server_tls:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # The payments endpoint runs over TLS with a self-signed certificate,
        # which the connection accepts because its tls_verify is off.
        soap_test_server_tls.configure(_Path_Payment, respond_raw=(OK, _Raw_Payment_Result, 'text/xml; charset=utf-8'))
        soap_test_server_tls.clear_requests()

        status, _, body = _post_json(zato_server['server_port'], '/billing/payment-register', _Payment_Request)

        assert status == OK
        assert body == _Raw_Payment_Result

        record = soap_test_server_tls.last_request

        assert record['path'] == _Path_Payment
        assert record['headers']['SOAPAction'] == _Action_Register_Payment
        assert b'<pay:paymentNo>PAY-2026-0031</pay:paymentNo>' in record['raw_body']

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Read timed out', 'ReadTimeout', 'Traceback', 'Caught an exception')
    def test_timeout(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # The slow connection has a one-second timeout, so a three-second delay must
        # surface as an error - the connection wrapper turns the read timeout
        # into a backend-invocation error the caller sees as a 400.
        soap_test_server.configure(_Path_Slow, delay=3)
        soap_test_server.clear_requests()

        status, _, body = _post_json(zato_server['server_port'], '/billing/invoice-header/slow', _Invoice_Request)

        assert status == BAD_REQUEST
        assert b'timed out' in body

# ################################################################################################################################

    def test_channel_chain_invoice(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # The full chain the application runs in production - a SOAP envelope enters
        # a plain channel, which forwards it through a RESTAdapter to the ERP.
        soap_test_server.configure(_Path_Rest_Invoice, respond_raw=(OK, _Raw_Invoice_Ack, 'application/xml'))
        soap_test_server.clear_requests()

        url = f'http://127.0.0.1:{zato_server["server_port"]}/billing/erp/invoice?company=north'

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': _Action_Rest_Invoice,
            'Authorization': _basic_auth_header(billing_config['submitter_username'], billing_config['submitter_password']),
        }

        status, response_headers, body = _post(url, _Submitted_Invoice_Envelope, headers)

        # The caller received the ERP's XML verbatim, marked as XML
        assert status == OK
        assert response_headers['Content-Type'].startswith('application/xml')
        assert body == _Raw_Invoice_Ack

        record = soap_test_server.last_request

        # The {env} and {company} parameters were substituted into the path,
        # with the pre-encoded company name preserved
        assert record['path'] == _Path_Rest_Invoice

        # The adapter's static headers arrived
        assert record['headers']['SOAPAction'] == _Action_Rest_Invoice
        assert record['headers']['Content-Type'] == 'application/xml'

        # The envelope travelled through the whole chain untouched
        assert record['raw_body'] == _Submitted_Invoice_Envelope

# ################################################################################################################################

    def test_channel_chain_payment_status(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # This chain forwards the caller's own SOAPAction instead of a static one
        soap_test_server.configure(_Path_Rest_Payment_Status, respond_raw=(OK, _Raw_Payment_Status, 'application/xml'))
        soap_test_server.clear_requests()

        url = f'http://127.0.0.1:{zato_server["server_port"]}/billing/erp/payment-status'

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': _Action_Payment_Status,
            'Authorization': _basic_auth_header(billing_config['submitter_username'], billing_config['submitter_password']),
        }

        status, response_headers, body = _post(url, _Payment_Status_Envelope, headers)

        assert status == OK
        assert response_headers['Content-Type'].startswith('application/xml')
        assert body == _Raw_Payment_Status

        record = soap_test_server.last_request

        assert record['path'] == _Path_Rest_Payment_Status

        # The action the caller sent is the action the ERP received
        assert record['headers']['SOAPAction'] == _Action_Payment_Status
        assert record['raw_body'] == _Payment_Status_Envelope

# ################################################################################################################################

    def test_channel_chain_bad_company(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        soap_test_server.clear_requests()

        # A company outside the channel's map must be rejected before anything is forwarded
        url = f'http://127.0.0.1:{zato_server["server_port"]}/billing/erp/invoice?company=west'

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': _Action_Rest_Invoice,
            'Authorization': _basic_auth_header(billing_config['submitter_username'], billing_config['submitter_password']),
        }

        status, _, body = _post(url, _Submitted_Invoice_Envelope, headers)

        assert status == BAD_REQUEST

        response_data = loads(body.decode('utf-8'))
        assert response_data['error'] == 'parameter company is not valid'

        # Nothing reached the ERP
        assert soap_test_server.last_request is None

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Invalid Basic Auth', '401', 'Unauthorized')
    def test_channel_chain_wrong_credentials(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        soap_test_server.clear_requests()

        url = f'http://127.0.0.1:{zato_server["server_port"]}/billing/erp/invoice?company=north'

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': _Action_Rest_Invoice,
            'Authorization': _basic_auth_header(billing_config['submitter_username'], 'not-the-password'),
        }

        status, _, _ = _post(url, _Submitted_Invoice_Envelope, headers)

        assert status == UNAUTHORIZED

        # Nothing reached the ERP
        assert soap_test_server.last_request is None

# ################################################################################################################################

    def test_enmasse_reimport(
        self,
        zato_server:'anydict',
        soap_test_server:'any_',
        billing_config:'anydict',
    ) -> 'None':

        # Importing the same YAML again must be a no-op for every billing object ..
        result = subprocess.run(
            billing_config['enmasse_command'],
            capture_output=True,
            text=True,
            timeout=120,
            env=billing_config['enmasse_env'],
        )

        output = result.stdout + result.stderr

        assert result.returncode == 0, output
        assert 'Enmasse OK' in output

        # .. nothing was created ..
        assert 'not found in DB, will create new' not in output
        assert 'Creating outgoing SOAP connection' not in output
        assert 'Creating REST channel' not in output

        # .. none of the connections or channels was updated ..
        assert 'Will update Billing.' not in output
        assert 'Will update billing.' not in output

        # .. and the configuration still works afterwards.
        soap_test_server.configure(_Path_Header_Main, respond_raw=(OK, _Raw_Header_Result, 'text/xml; charset=utf-8'))
        soap_test_server.clear_requests()

        status, _, body = _post_json(zato_server['server_port'], '/billing/invoice-header/main', _Invoice_Request)

        assert status == OK
        assert body == _Raw_Header_Result

# ################################################################################################################################
# ################################################################################################################################
