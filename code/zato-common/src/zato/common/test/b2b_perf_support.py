# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from random import Random
from time import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# cryptography
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate

# SQLAlchemy
from sqlalchemy import event as sa_event

# Zato
from zato.common.b2b.common.keys import LocalKeys
from zato.common.b2b.ebms2.common import Direction
from zato.common.b2b.ebms2.cpa.parse import parse_cpa
from zato.common.b2b.ebms2.inbound_common import HTTPResponse
from zato.common.b2b.ebms2.packaging import Payload
from zato.common.test.b2b_documents import new_line_items

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_perf_common import PartyConfig
    from zato.common.typing_ import any_, stranydict, strstrdict
    Agreement = Agreement
    any_ = any_
    Binding = Binding
    Engine = Engine
    party_id_list = party_id_list
    PartyConfig = PartyConfig
    payload_list = payload_list
    stranydict = stranydict
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

strpartyidsdict = dict[str, 'party_id_list']

# ################################################################################################################################
# ################################################################################################################################

# How long a party waits for the response to one of its posts, in seconds.
_post_timeout = 30

# The verbs of the statements that are counted, as opposed to the transaction control the driver sends.
_counted_verbs = ('SELECT', 'INSERT', 'UPDATE', 'DELETE')

# A select that reads the stored bytes of a message names the table of message bodies.
_body_table_marker = 'event_body'

# The business document of each message, filled up to the size of the run with order lines
# that follow the same sequence in every run.
_document_start = b'<OrderDocument xmlns="urn:zato:b2b:perf"><Lines>'
_document_end   = b'</Lines></OrderDocument>'
_document_type  = 'application/xml'
_document_seed  = 20261028

_json_content_type = 'application/json'

_method_post = 'POST'

# ################################################################################################################################
# ################################################################################################################################

def new_payloads(size:'int') -> 'payload_list':
    """ Returns the payload of a business document of at least the given size, made of whole order lines.
    """
    frame_size = len(_document_start) + len(_document_end)
    lines_size = size - frame_size

    draw = Random(_document_seed)
    lines = new_line_items(draw, lines_size)

    payload = Payload()
    payload.content_id = ''
    payload.content_type = _document_type
    payload.data = _document_start + lines + _document_end

    out = [payload]
    return out

# ################################################################################################################################

def load_agreement(path:'str') -> 'Agreement':

    with open(path, 'rb') as agreement_file:
        data = agreement_file.read()

    out = parse_cpa(data)
    return out

# ################################################################################################################################

def load_keys(config:'PartyConfig') -> 'LocalKeys':

    with open(config.key_path, 'rb') as key_file:
        key_data = key_file.read()

    with open(config.certificate_path, 'rb') as certificate_file:
        certificate_data = certificate_file.read()

    certificate = load_pem_x509_certificate(certificate_data)

    out = LocalKeys()
    out.signing_key = load_pem_private_key(key_data, None)
    out.signing_certificate_chain = [certificate]

    return out

# ################################################################################################################################

def resolve_binding(agreement:'Agreement', from_name:'str', to_name:'str', service:'str', action:'str') -> 'Binding':
    """ Returns the binding of a message that one named party of an agreement sends to the other.
    """
    party_ids:'strpartyidsdict' = {}

    for party in agreement.parties:
        party_ids[party.party_name] = party.party_ids

    from_ids = party_ids[from_name]
    to_ids = party_ids[to_name]

    out = agreement.resolve(from_ids, to_ids, service, '', action, Direction.Send)
    return out

# ################################################################################################################################

def http_post(url:'str', headers:'strstrdict', body:'bytes') -> 'HTTPResponse | None':
    """ Posts a message and returns the response whatever its status code, or None when no response arrived.
    """
    request = Request(url, data=body, headers=headers, method=_method_post)

    # Our response to produce
    out = HTTPResponse()

    # A response with an error status code is a response like any other ..
    try:
        with urlopen(request, timeout=_post_timeout) as response:
            out.status_code = response.status
            content_type = response.headers['Content-Type']
            out.body = response.read()

    except HTTPError as e:
        out.status_code = e.code
        content_type = e.headers['Content-Type']
        out.body = e.read()

    # .. while a refused connection, a timeout or a connection closed before the response is no response at all.
    except OSError:
        return None

    # A response without a body may come without a Content-Type.
    if content_type is not None:
        out.content_type = content_type

    return out

# ################################################################################################################################

def json_response(data:'stranydict') -> 'HTTPResponse':

    text = dumps(data)

    out = HTTPResponse()
    out.content_type = _json_content_type
    out.body = text.encode('utf8')

    return out

# ################################################################################################################################
# ################################################################################################################################

class StatementCounter:
    """ Counts the statements and the commits of an engine, all of them and those within the measurement window.
    """

    def __init__(self, engine:'Engine') -> 'None':

        # The measurement window, as seconds since the epoch, empty until the run starts.
        self.window_start = 0.0
        self.window_end = 0.0

        self.statements = 0
        self.commits = 0
        self.total_statements = 0
        self.body_selects = 0

        sa_event.listen(engine, 'before_cursor_execute', self._on_execute)
        sa_event.listen(engine, 'commit', self._on_commit)

# ################################################################################################################################

    def _is_in_window(self) -> 'bool':

        now = time()

        if now < self.window_start:
            out = False
        else:
            out = now < self.window_end

        return out

# ################################################################################################################################

    def _on_execute(self, conn:'any_', cursor:'any_', sql:'str', parameters:'any_', context:'any_', executemany:'bool') -> 'None':

        words = sql.split(maxsplit=1)
        verb = words[0].upper()

        if verb not in _counted_verbs:
            return

        self.total_statements += 1

        if verb == 'SELECT':
            if _body_table_marker in sql:
                self.body_selects += 1

        if self._is_in_window():
            self.statements += 1

# ################################################################################################################################

    def _on_commit(self, conn:'any_') -> 'None':
        if self._is_in_window():
            self.commits += 1

# ################################################################################################################################
# ################################################################################################################################
