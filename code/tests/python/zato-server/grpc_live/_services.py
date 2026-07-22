# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Generated stubs - the test suite puts their directory on the server's PYTHONPATH
import billing_pb2

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestGetInvoice(Service):
    """ Invokes the unary GetInvoice method through a named outgoing connection.
    """
    name = 'test.grpc.get-invoice'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        invoice_id = self.request.raw_request['invoice_id']

        client = self.grpc[conn_name]
        request = billing_pb2.InvoiceRequest(invoice_id=invoice_id)
        invoice = client.GetInvoice(request)

        self.response.payload = json.dumps({
            'invoice_id': invoice.invoice_id,
            'customer': invoice.customer,
            'amount_cents': invoice.amount_cents,
        })

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestListInvoices(Service):
    """ Invokes the server-streaming ListInvoices method, confirming the response
    arrives as a generator and collecting what it yields.
    """
    name = 'test.grpc.list-invoices'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        max_items = self.request.raw_request['max_items']

        client = self.grpc[conn_name]
        request = billing_pb2.InvoiceListRequest(max_items=max_items)
        response = client.ListInvoices(request)

        # The response streams - it is a generator, not a list
        is_generator = hasattr(response, '__next__')

        invoices = []

        for invoice in response:
            invoices.append({
                'invoice_id': invoice.invoice_id,
                'amount_cents': invoice.amount_cents,
            })

        self.response.payload = json.dumps({
            'is_generator': is_generator,
            'invoices': invoices,
        })

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestSubmitPayments(Service):
    """ Invokes the client-streaming SubmitPayments method with a generator of requests.
    """
    name = 'test.grpc.submit-payments'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        payments = self.request.raw_request['payments']

        def _payment_stream():
            for payment in payments:
                yield billing_pb2.Payment(invoice_id=payment['invoice_id'], amount_cents=payment['amount_cents'])

        client = self.grpc[conn_name]
        summary = client.SubmitPayments(_payment_stream())

        self.response.payload = json.dumps({
            'payment_count': summary.payment_count,
            'total_cents': summary.total_cents,
        })

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestReconcilePayments(Service):
    """ Invokes the bidirectional-streaming ReconcilePayments method.
    """
    name = 'test.grpc.reconcile-payments'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        payments = self.request.raw_request['payments']

        def _payment_stream():
            for payment in payments:
                yield billing_pb2.Payment(invoice_id=payment['invoice_id'], amount_cents=payment['amount_cents'])

        client = self.grpc[conn_name]
        response = client.ReconcilePayments(_payment_stream())

        receipts = []

        for receipt in response:
            receipts.append({
                'invoice_id': receipt.invoice_id,
                'is_settled': receipt.is_settled,
            })

        self.response.payload = json.dumps({'receipts': receipts})

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestPing(Service):
    """ Pings a gRPC connection through its wrapper and returns the result.
    """
    name = 'test.grpc.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        wrapper = self.server.config_manager.outconn_grpc[conn_name]['conn']
        wrapper.ping()

        self.response.payload = json.dumps({'alive': True})

# ################################################################################################################################
# ################################################################################################################################

class GRPCTestChannelGetInvoice(Service):
    """ Mounted on a REST channel - invokes GetInvoice without handling any exceptions,
    so gRPC failures bubble up and the channel maps them to HTTP statuses.
    """
    name = 'test.grpc.channel.get-invoice'

    def handle(self) -> 'None':

        # The channel hands the body over as raw bytes
        data = json.loads(self.request.raw_request)
        invoice_id = data['invoice_id']

        client = self.grpc['test.grpc.stubs']
        request = billing_pb2.InvoiceRequest(invoice_id=invoice_id)
        invoice = client.GetInvoice(request)

        self.response.payload = json.dumps({'invoice_id': invoice.invoice_id})

# ################################################################################################################################
# ################################################################################################################################
