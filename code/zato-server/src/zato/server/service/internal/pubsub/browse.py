# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services the queue and DLQ pages of an outgoing connection read from.

# stdlib
from datetime import timedelta
from json import dumps, loads
from urllib.parse import urlencode

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.pubsub.dlq import Header_Attempts, Header_Error, Header_Moved_Time, Header_Pub_Time, Header_Reason, \
    Header_Rounds, Header_Source_Msg_ID, Header_Source_Topic, Key_DLQ
from zato.common.pubsub.outgoing import find_outgoing_conn, get_dlq_settings, get_outgoing_topic_name, Key_Attempts, Key_CID, \
    Key_Conn_ID, Key_Conn_Name, Key_Conn_Type, Key_Data, Key_DLQ_Rounds, Key_Headers, Key_Method, Key_Msg_ID, Key_Params, \
    Key_Pub_Time, Key_Request
from zato.common.util.time_ import utcnow
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

_default_page_size = 50
_default_page = 1

Kind_Queue = 'queue'
Kind_DLQ   = 'dlq'

_topic_list = ['orders.failed', 'orders.manual-review', 'ops.escalations']

# The moment the test messages are dated against - fixed once, so their ages grow the way real ones do
_time_anchor = utcnow()

# ################################################################################################################################
# ################################################################################################################################

_order_json = """{
  "order_id": "ORD-2026-041877",
  "customer": {
    "id": "C-88213",
    "name": "Maria Johnson",
    "email": "maria.johnson@example.com"
  },
  "lines": [
    {"sku": "AX-2201", "qty": 2, "unit_price": 149.90},
    {"sku": "BQ-7710", "qty": 1, "unit_price": 899.00}
  ],
  "currency": "USD",
  "total": 1198.80,
  "requested_delivery": "2026-09-24"
}"""

_invoice_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:example:billing:v2">
  <InvoiceNumber>INV-2026-009312</InvoiceNumber>
  <IssueDate>2026-09-18</IssueDate>
  <Supplier>
    <Name>Northwind Components Inc.</Name>
    <TaxId>US-77-1029384</TaxId>
  </Supplier>
  <Customer>
    <Name>John Smith</Name>
    <AccountId>ACC-55120</AccountId>
  </Customer>
  <Lines>
    <Line number="1"><Description>Pressure sensor PS-40</Description><Quantity>12</Quantity><Amount>2148.00</Amount></Line>
    <Line number="2"><Description>Mounting bracket</Description><Quantity>12</Quantity><Amount>216.00</Amount></Line>
  </Lines>
  <Total currency="USD">2364.00</Total>
</Invoice>"""

_shipment_csv = """shipment_id,order_id,carrier,tracking_number,shipped_at,weight_kg
SHP-771201,ORD-2026-041502,UPS,1Z999AA10123456784,2026-09-18T14:02:11Z,3.4
SHP-771202,ORD-2026-041510,FedEx,449044304137821,2026-09-18T14:05:40Z,1.1
SHP-771203,ORD-2026-041533,USPS,9400111899223197428490,2026-09-18T14:09:03Z,0.6"""

_payment_json = """{
  "payment_id": "PAY-5c1f8e",
  "order_id": "ORD-2026-041790",
  "method": "card",
  "amount": 249.00,
  "currency": "USD",
  "card": {"brand": "visa", "last4": "4242", "expiry": "08/28"},
  "captured": true
}"""

_customer_update_json = """{
  "customer_id": "C-10922",
  "name": "Anna Miller",
  "email": "anna.miller@example",
  "phone": "+1 555 0100",
  "address": {
    "line1": "1200 Market St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "9410"
  }
}"""

_stock_json = """{
  "warehouse": "WH-EAST-2",
  "sku": "AX-2201",
  "delta": -2,
  "reason": "order",
  "reference": "ORD-2026-041877"
}"""

_validation_error = '422 Unprocessable Entity: {"detail": [{"loc": ["address", "postal_code"], "msg": "must be 5 digits"}, ' + \
    '{"loc": ["email"], "msg": "value is not a valid email address"}]}'

_json_headers = {'Content-Type': 'application/json', 'X-Request-Source': 'zato'}
_xml_headers  = {'Content-Type': 'application/xml', 'X-Request-Source': 'zato'}
_csv_headers  = {'Content-Type': 'text/csv', 'X-Request-Source': 'zato'}

# ################################################################################################################################
# ################################################################################################################################

def _seconds_ago(seconds:'int') -> 'str':
    """ An ISO timestamp this many seconds before the anchor.
    """
    delta = timedelta(seconds=seconds)
    when = _time_anchor - delta

    out = when.isoformat()
    return out

# ################################################################################################################################

def _new_envelope(
    conn_type:'str',
    conn_id:'int',
    conn_name:'str',
    *,
    suffix:'str',
    age:'int',
    attempts:'int',
    rounds:'int',
    method:'str',
    data:'str',
    headers:'stranydict',
    params:'stranydict',
    ) -> 'stranydict':
    """ One envelope.
    """
    out = {
        Key_Conn_Type: conn_type,
        Key_Conn_ID: conn_id,
        Key_Conn_Name: conn_name,
        Key_CID: f'0d5b2c1a7e{suffix}',
        Key_Msg_ID: f'zpsm.f4e1c9a2b7d3{suffix}',
        Key_Pub_Time: _seconds_ago(age),
        Key_Attempts: attempts,
        Key_DLQ_Rounds: rounds,
        Key_Request: {
            Key_Method: method,
            Key_Data: data,
            Key_Headers: headers,
            Key_Params: params,
        },
    }

    return out

# ################################################################################################################################

def _with_dlq_header(envelope:'stranydict', *, moved_ago:'int', error:'str', attempts:'int', source_topic:'str') -> 'stranydict':
    """ One envelope with a DLQ header.
    """
    out = dict(envelope)

    out[Key_DLQ] = {
        Header_Reason: PubSub.Outgoing.DLQ_Reason_Retries_Exhausted,
        Header_Error: error,
        Header_Attempts: attempts,
        Header_Moved_Time: _seconds_ago(moved_ago),
        Header_Source_Topic: source_topic,
        Header_Source_Msg_ID: envelope[Key_Msg_ID],
        Header_Pub_Time: envelope[Key_Pub_Time],
        Header_Rounds: envelope[Key_DLQ_Rounds],
    }

    return out

# ################################################################################################################################

def _build_queue_documents(conn_type:'str', conn_id:'int', conn_name:'str') -> 'anylist':
    """ The messages of a queue.
    """
    out = [
        _new_envelope(conn_type, conn_id, conn_name, suffix='0001', age=41, attempts=1, rounds=0,
            method='POST', data=_order_json, headers=_json_headers, params={}),
        _new_envelope(conn_type, conn_id, conn_name, suffix='0002', age=27, attempts=0, rounds=0,
            method='POST', data=_stock_json, headers=_json_headers, params={'source': 'wms'}),
        _new_envelope(conn_type, conn_id, conn_name, suffix='0003', age=9, attempts=0, rounds=0,
            method='PUT', data=_invoice_xml, headers=_xml_headers, params={}),
    ]

    return out

# ################################################################################################################################

def _build_dlq_documents(conn_type:'str', conn_id:'int', conn_name:'str') -> 'anylist':
    """ The messages of a DLQ.
    """
    source_topic = get_outgoing_topic_name(conn_type, conn_name)

    order = _new_envelope(conn_type, conn_id, conn_name, suffix='1001', age=1010, attempts=4, rounds=0,
        method='POST', data=_order_json, headers=_json_headers, params={})

    invoice = _new_envelope(conn_type, conn_id, conn_name, suffix='1002', age=6300, attempts=4, rounds=2,
        method='PUT', data=_invoice_xml, headers=_xml_headers, params={'validate': 'true'})

    shipments = _new_envelope(conn_type, conn_id, conn_name, suffix='1003', age=15200, attempts=4, rounds=3,
        method='POST', data=_shipment_csv, headers=_csv_headers, params={})

    payment = _new_envelope(conn_type, conn_id, conn_name, suffix='1004', age=180500, attempts=4, rounds=1,
        method='POST', data=_payment_json, headers=_json_headers, params={})

    customer = _new_envelope(conn_type, conn_id, conn_name, suffix='1005', age=95, attempts=4, rounds=0,
        method='PATCH', data=_customer_update_json, headers=_json_headers, params={})

    out = [
        _with_dlq_header(customer, moved_ago=31, attempts=4, source_topic=source_topic, error=_validation_error),
        _with_dlq_header(order, moved_ago=380, attempts=4, source_topic=source_topic,
            error='503 Service Unavailable'),
        _with_dlq_header(invoice, moved_ago=2520, attempts=4, source_topic=source_topic,
            error='Connection refused: billing.internal.example.com:8443'),
        _with_dlq_header(shipments, moved_ago=10900, attempts=4, source_topic=source_topic,
            error='Read timed out (10 seconds)'),
        _with_dlq_header(payment, moved_ago=175000, attempts=4, source_topic=source_topic,
            error='401 Unauthorized'),
    ]

    return out

# ################################################################################################################################

_document_builders = {
    Kind_Queue: _build_queue_documents,
    Kind_DLQ: _build_dlq_documents,
}

# ################################################################################################################################
# ################################################################################################################################

def _matches(document:'stranydict', query:'str') -> 'bool':
    """ Whether a message has the query anywhere in it.
    """
    text = dumps(document)
    text = text.lower()

    out = query in text
    return out

# ################################################################################################################################

def _to_row(document:'stranydict', conn_address:'str') -> 'stranydict':
    """ What the listing shows of one message.
    """
    request = document[Key_Request]
    data = request[Key_Data]
    data_bytes = data.encode('utf8')

    # The address the message goes to - the connection's own with the message's query string
    address = conn_address

    if params := request[Key_Params]:
        address = f'{address}?{urlencode(params)}'

    out = {
        'msg_id': document[Key_Msg_ID],
        'cid': document[Key_CID],
        'pub_time_iso': document[Key_Pub_Time],
        'attempts': document[Key_Attempts],
        'rounds': document[Key_DLQ_Rounds],
        'method': request[Key_Method],
        'address': address,
        'content_type': request[Key_Headers]['Content-Type'],
        'size': len(data_bytes),
    }

    if dlq_header := document.get(Key_DLQ):
        out['moved_time_iso'] = dlq_header[Header_Moved_Time]
        out['error'] = dlq_header[Header_Error]
        out['reason'] = dlq_header[Header_Reason]
    else:
        out['moved_time_iso'] = ''
        out['error'] = ''
        out['reason'] = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class _BrowseService(AdminService):
    """ What the browsing services share.
    """

    def _get_conn(self, conn_type:'str', conn_id:'int') -> 'tuple[str, anydict]':
        """ The connection by its id, as its name and its wrapper.
        """
        found = find_outgoing_conn(self.server, conn_type, conn_id)

        if not found:
            raise Exception(f'No such outgoing connection `{conn_type}` `{conn_id}`')

        conn_name, wrapper = found

        out = (conn_name, wrapper)
        return out

# ################################################################################################################################

    def _get_documents(self, kind:'str', conn_type:'str', conn_id:'int', conn_name:'str') -> 'anylist':
        """ Every message the queue or the DLQ holds, oldest first.
        """
        builder = _document_builders[kind]

        out = builder(conn_type, conn_id, conn_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class GetMessageList(_BrowseService):
    """ One page of the messages an outgoing connection's queue or DLQ holds.
    """
    name  = 'zato.pubsub.outgoing.get-message-list'
    input = 'conn_type', Int('conn_id'), 'kind', '-query', Int('-cur_page'), Int('-page_size')

    def handle(self) -> 'None':
        input = self.request.input

        conn_type = input.conn_type
        conn_id = input.conn_id
        kind = input.kind

        cur_page = input.cur_page or _default_page
        page_size = input.page_size or _default_page_size

        conn_name, wrapper = self._get_conn(conn_type, conn_id)

        # A queue on a broker cannot be browsed
        topic_name = get_outgoing_topic_name(conn_type, conn_name)
        topic_backend = self.server.config_manager.get_pubsub_topic_backend(topic_name)
        is_queue_browsable = topic_backend is None

        queue_documents = self._get_documents(Kind_Queue, conn_type, conn_id, conn_name)
        dlq_documents = self._get_documents(Kind_DLQ, conn_type, conn_id, conn_name)

        if kind == Kind_Queue:
            documents = queue_documents
        else:
            documents = dlq_documents

        if query := input.query:
            query = query.lower()
            matching:'anylist' = []

            for document in documents:
                if _matches(document, query):
                    matching.append(document)

            documents = matching

        total = len(documents)
        start = (cur_page - 1) * page_size
        end = start + page_size
        page_documents = documents[start:end]

        num_pages, remainder = divmod(total, page_size)
        if remainder:
            num_pages += 1

        items:'anylist' = []

        for document in page_documents:
            items.append(_to_row(document, wrapper.address))

        dlq_settings = get_dlq_settings(conn_type, wrapper)

        self.response.payload = {
            'conn_name': conn_name,
            'is_queue_browsable': is_queue_browsable,
            'queue_depth': len(queue_documents),
            'dlq_depth': len(dlq_documents),
            'dlq_settings': dlq_settings,
            'topic_list': _topic_list,
            'items': items,
            'total': total,
            'cur_page': cur_page,
            'num_pages': num_pages,
            'page_size': page_size,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetMessage(_BrowseService):
    """ One message in full.
    """
    name  = 'zato.pubsub.outgoing.get-message'
    input = 'conn_type', Int('conn_id'), 'kind', 'msg_id'

    def handle(self) -> 'None':
        input = self.request.input

        conn_name, wrapper = self._get_conn(input.conn_type, input.conn_id)
        documents = self._get_documents(input.kind, input.conn_type, input.conn_id, conn_name)

        for document in documents:
            if document[Key_Msg_ID] == input.msg_id:
                out = document
                break
        else:
            raise Exception(f'No such message `{input.msg_id}`')

        # The settings go along with the message because the details window states what the rule will do with it
        dlq_settings = get_dlq_settings(input.conn_type, wrapper)

        self.response.payload = {'document': out, 'dlq_settings': dlq_settings}

# ################################################################################################################################
# ################################################################################################################################

class GetMessageTimeList(_BrowseService):
    """ When each of the messages named entered the queue or the DLQ - what the pages' refreshes read.
    """
    name  = 'zato.pubsub.outgoing.get-message-time-list'
    input = 'conn_type', Int('conn_id'), 'kind', AsIs('msg_id_list')

    def handle(self) -> 'None':
        input = self.request.input
        kind = input.kind

        conn_name, _ = self._get_conn(input.conn_type, input.conn_id)
        documents = self._get_documents(kind, input.conn_type, input.conn_id, conn_name)

        wanted = set(loads(input.msg_id_list))
        items:'stranydict' = {}

        for document in documents:
            msg_id = document[Key_Msg_ID]

            if msg_id not in wanted:
                continue

            if kind == Kind_DLQ:
                items[msg_id] = document[Key_DLQ][Header_Moved_Time]
            else:
                items[msg_id] = document[Key_Pub_Time]

        self.response.payload = {'items': items}

# ################################################################################################################################
# ################################################################################################################################

class MessageAction(_BrowseService):
    """ Runs one action on the messages named by their ids or on all the messages matching a query.
    """
    name  = 'zato.pubsub.outgoing.message-action'
    input = 'conn_type', Int('conn_id'), 'kind', 'action', AsIs('-msg_id_list'), '-query', '-forward_to', Bool('-keep_header')

    def handle(self) -> 'None':
        input = self.request.input

        conn_name, _ = self._get_conn(input.conn_type, input.conn_id)
        documents = self._get_documents(input.kind, input.conn_type, input.conn_id, conn_name)

        if msg_id_list := input.msg_id_list:
            msg_id_list = loads(msg_id_list)
            count = len(msg_id_list)

        else:
            query = input.query.lower()
            count = 0

            for document in documents:
                if _matches(document, query):
                    count += 1

        self.response.payload = {
            'action': input.action,
            'count': count,
            'forward_to': input.forward_to,
            'keep_header': input.keep_header,
        }

# ################################################################################################################################
# ################################################################################################################################

class UpdateMessage(_BrowseService):
    """ Replaces the data of one message.
    """
    name  = 'zato.pubsub.outgoing.update-message'
    input = 'conn_type', Int('conn_id'), 'kind', 'msg_id', 'data'

    def handle(self) -> 'None':
        input = self.request.input

        _ = self._get_conn(input.conn_type, input.conn_id)
        data_bytes = input.data.encode('utf8')

        self.response.payload = {
            'msg_id': input.msg_id,
            'size': len(data_bytes),
        }

# ################################################################################################################################
# ################################################################################################################################
