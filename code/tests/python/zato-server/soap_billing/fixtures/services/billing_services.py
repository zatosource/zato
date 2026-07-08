# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import date, decimal_
from zato.server.service import Model, RESTAdapter, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

# The environment segment of the ERP's URL paths
_Default_Environment = 'production'

# Maps company codes from the query string to the percent-encoded names the ERP's URL paths expect
_Company_North = 'North%20Trading%20Ltd.'
_Company_South = 'South%20Retail%20Group'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Invoice(Model):
    invoiceNo: str
    customerNo: str
    notes: str
    paymentTerms: str
    documentDate: date
    dueDate: date
    currencyCode: str
    contactEmail: str
    yourReference: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateInvoiceHeaderDomainRequest(Model):
    invoiceNo: str
    customerNo: str
    notes: str
    paymentTerms: str
    documentDate: date
    dueDate: date
    currencyCode: str
    contactEmail: str
    yourReference: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateInvoiceLinesDomainRequest(Model):
    invoiceNo: str
    lineNo: int
    itemNo: str
    description: str
    quantity: decimal_
    unitOfMeasure: str
    unitPrice: decimal_
    vatGroup: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Payment(Model):
    paymentNo: str
    invoiceNo: str
    amount: decimal_
    currencyCode: str
    paymentDate: date
    payerReference: str

# ################################################################################################################################
# ################################################################################################################################

class CreateInvoiceHeader(Service):

    # Our name
    name = 'test.soap.billing.invoice-header.create.main'

    # I/O definition
    input = Invoice

    # Connection to use
    conn_name = 'Billing.Invoice.Create.Header.Main'

# ################################################################################################################################

    def map_data(self, data:'Invoice') -> 'CreateInvoiceHeaderDomainRequest':

        # Build a request to invoke the domain system with ..
        invoice = CreateInvoiceHeaderDomainRequest()

        # .. and populate it ..
        invoice.invoiceNo    = data.invoiceNo
        invoice.customerNo   = data.customerNo
        invoice.notes        = data.notes
        invoice.paymentTerms = data.paymentTerms
        invoice.documentDate = data.documentDate
        invoice.dueDate      = data.dueDate
        invoice.currencyCode = data.currencyCode
        invoice.contactEmail = data.contactEmail
        invoice.yourReference = data.yourReference

        # .. and return it
        return invoice

# ################################################################################################################################

    def handle(self) -> 'None':

        # Get the domain data
        invoice = self.map_data(self.request.input)

        # Data string to use when invoking the SOAP system
        data = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:inv="urn:example-erp/codeunit/InvoiceEntryService">
            <soapenv:Header/>
            <soapenv:Body>
                <inv:CreateInvoiceHeader>
                    <inv:invoiceNo>{invoice.invoiceNo}</inv:invoiceNo>
                    <inv:customerNo>{invoice.customerNo}</inv:customerNo>
                    <inv:notes>{invoice.notes}</inv:notes>
                    <inv:paymentTerms>{invoice.paymentTerms}</inv:paymentTerms>
                    <inv:documentDate>{invoice.documentDate}</inv:documentDate>
                    <inv:dueDate>{invoice.dueDate}</inv:dueDate>
                    <inv:currencyCode>{invoice.currencyCode}</inv:currencyCode>
                    <inv:contactEmail>{invoice.contactEmail}</inv:contactEmail>
                    <inv:yourReference>{invoice.yourReference}</inv:yourReference>
                </inv:CreateInvoiceHeader>
            </soapenv:Body>
            </soapenv:Envelope>
            """.encode('utf8')

        # Name of the SOAP connection to use..
        conn:'HTTPSOAPWrapper' = self.out.soap[self.conn_name].conn # type: ignore

        # ..send the SOAP request..
        response = conn.send(self.cid, data) # type: ignore

        # ..and return the response
        self.response.payload = response.data

# ################################################################################################################################
# ################################################################################################################################

class CreateInvoiceHeaderBranch(CreateInvoiceHeader):

    # Our name
    name = 'test.soap.billing.invoice-header.create.branch'
    conn_name = 'Billing.Invoice.Create.Header.Branch'

# ################################################################################################################################
# ################################################################################################################################

class CreateInvoiceHeaderSlow(CreateInvoiceHeader):

    # Our name
    name = 'test.soap.billing.invoice-header.create.slow'
    conn_name = 'Billing.Invoice.Create.Header.Slow'

# ################################################################################################################################
# ################################################################################################################################

class CreateInvoiceLines(Service):

    # Our name
    name = 'test.soap.billing.invoice-lines.create'

    # I/O definition
    input = CreateInvoiceLinesDomainRequest

    # Connection to use
    conn_name = 'Billing.Invoice.Create.Lines.Main'

# ################################################################################################################################

    def map_data(self, data:'CreateInvoiceLinesDomainRequest') -> 'CreateInvoiceLinesDomainRequest':

        # Build a request to invoke the domain system with ..
        lines = CreateInvoiceLinesDomainRequest()

        # .. and populate it ..
        lines.invoiceNo     = data.invoiceNo
        lines.lineNo        = data.lineNo
        lines.itemNo        = data.itemNo
        lines.description   = data.description
        lines.quantity      = data.quantity
        lines.unitOfMeasure = data.unitOfMeasure
        lines.unitPrice     = data.unitPrice
        lines.vatGroup      = data.vatGroup

        # .. and return it
        return lines

# ################################################################################################################################

    def handle(self) -> 'None':

        # Get the domain data
        lines = self.map_data(self.request.input)

        # Data string to use when invoking the SOAP system
        data = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:inv="urn:example-erp/codeunit/InvoiceEntryService">
            <soapenv:Header/>
            <soapenv:Body>
                <inv:CreateInvoiceLines>
                    <inv:invoiceNo>{lines.invoiceNo}</inv:invoiceNo>
                    <inv:lineNo>{lines.lineNo}</inv:lineNo>
                    <inv:itemNo>{lines.itemNo}</inv:itemNo>
                    <inv:description><![CDATA[{lines.description}]]></inv:description>
                    <inv:quantity>{lines.quantity}</inv:quantity>
                    <inv:unitOfMeasure>{lines.unitOfMeasure}</inv:unitOfMeasure>
                    <inv:unitPrice>{lines.unitPrice}</inv:unitPrice>
                    <inv:vatGroup>{lines.vatGroup}</inv:vatGroup>
                </inv:CreateInvoiceLines>
            </soapenv:Body>
            </soapenv:Envelope>
            """.encode('utf8')

        # Name of the SOAP connection to use..
        conn:'HTTPSOAPWrapper' = self.out.soap[self.conn_name].conn # type: ignore

        # ..send the SOAP request..
        response = conn.send(self.cid, data) # type: ignore

        # ..and return the response
        self.response.payload = response.data

# ################################################################################################################################
# ################################################################################################################################

class RegisterPayment(Service):

    # Our name
    name = 'test.soap.billing.payment.register'

    # I/O definition
    input = Payment

    # Connection to use
    conn_name = 'Billing.Payment.Register'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Get the payment data
        payment = self.request.input

        # Data string to use when invoking the SOAP system
        data = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pay="urn:example-erp/codeunit/PaymentEntryService">
            <soapenv:Header/>
            <soapenv:Body>
                <pay:RegisterPayment>
                    <pay:paymentNo>{payment.paymentNo}</pay:paymentNo>
                    <pay:invoiceNo>{payment.invoiceNo}</pay:invoiceNo>
                    <pay:amount>{payment.amount}</pay:amount>
                    <pay:currencyCode>{payment.currencyCode}</pay:currencyCode>
                    <pay:paymentDate>{payment.paymentDate}</pay:paymentDate>
                    <pay:payerReference>{payment.payerReference}</pay:payerReference>
                </pay:RegisterPayment>
            </soapenv:Body>
            </soapenv:Envelope>
            """.encode('utf8')

        # Name of the SOAP connection to use..
        conn:'HTTPSOAPWrapper' = self.out.soap[self.conn_name].conn # type: ignore

        # ..send the SOAP request..
        response = conn.send(self.cid, data) # type: ignore

        # ..and return the response
        self.response.payload = response.data

# ################################################################################################################################
# ################################################################################################################################

class ReceiveInvoice(Service):

    # Our name
    name = 'test.soap.billing.channel.invoice-receive'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Get the data from the payload ..
        data = self.request.payload.decode('utf-8') # type: ignore

        # Services to Invoke
        forward_to_erp_service = 'test.soap.billing.erp.invoice-post'

        # get the company from the channel parameters
        if self.request.channel_params['company'] == 'north':
            company = _Company_North
        elif self.request.channel_params['company'] == 'south':
            company = _Company_South
        else:
            # Return an error if the company is not valid
            self.response.payload = {'error':'parameter company is not valid'}
            self.response.status_code = 400
            return

        self.logger.info(company)

        # Invoke the service
        response = self.invoke(forward_to_erp_service, env=_Default_Environment, company=company, data=data)

        # return the response
        self.response.content_type = 'application/xml'
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class GetPaymentStatus(Service):

    # Our name
    name = 'test.soap.billing.channel.payment-status'

# ################################################################################################################################

    def handle(self) -> 'None':

        # get the company and environment
        company = _Company_North
        env = _Default_Environment

        # Get the data from the payload ..
        data = self.request.payload.decode('utf-8') # type: ignore
        soap_action = str(self.request.http._wsgi_environ.get('HTTP_SOAPACTION', ''))

        # Services to Invoke
        forward_to_erp_service = 'test.soap.billing.erp.payment-status'

        # set the content type to application/xml
        self.response.content_type = 'application/xml'

        try:
            # Invoke the service
            response = self.invoke(forward_to_erp_service, company=company, env=env, data=data, soap_action=soap_action)

            # return the response
            self.response.payload = response

        except Exception as e:
            self.logger.error(f'Error invoking service: {e}')
            self.response.payload = str(e)
            self.response.status_code = 500
            return

# ################################################################################################################################
# ################################################################################################################################

class ErpPostInvoice(RESTAdapter):

    # Our name
    name = 'test.soap.billing.erp.invoice-post'

    # I/O definition
    input = 'env', 'company'

    # Connection to use
    conn_name = 'Billing.ERP.Invoice.REST'

    # REST method to use
    method = 'POST'

# ################################################################################################################################

    def get_path_params(self, params:'strdict') -> 'strdict':

        # Local variables
        env = self.request.input.env
        company = self.request.input.company

        # return the values
        return {'env': env, 'company': company}

# ################################################################################################################################

    def get_headers(self) -> 'strdict':

        # Return the headers
        return {
            'Content-Type': 'application/xml',
            'SOAPAction': 'urn:example-erp/codeunit/InvoiceEntryService'
        }

# ################################################################################################################################

    def get_request(self) -> 'str':

        # Get the data from the payload ..
        payload = self.request.payload

        # Extract the data
        data = payload['data'] # type: ignore

        return data

# ################################################################################################################################
# ################################################################################################################################

class ErpGetPaymentStatus(RESTAdapter):

    # Our name
    name = 'test.soap.billing.erp.payment-status'

    # I/O definition
    input = 'env', 'company', '-soap_action'

    # Connection to use
    conn_name = 'Billing.ERP.PaymentStatus.REST'

    # REST method to use
    method = 'POST'

# ################################################################################################################################

    def get_path_params(self, params:'strdict') -> 'strdict':

        # Local variables
        env = self.request.input.env
        company = self.request.input.company

        # return the values
        return {'env': env, 'company': company}

# ################################################################################################################################

    def get_request(self) -> 'str':

        # Get the data from the payload ..
        payload = self.request.payload

        # Extract the data
        data = payload['data'] # type: ignore

        return data

# ################################################################################################################################

    def get_headers(self) -> 'strdict':

        # Get the SOAPAction from the input
        soap_action = self.request.input.soap_action

        # Return the headers
        return {
            'Content-Type': 'application/xml',
            'SOAPAction': soap_action
        }

# ################################################################################################################################
# ################################################################################################################################
