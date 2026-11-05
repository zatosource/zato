# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import Counter
from hashlib import sha256
from time import monotonic

# gevent
from gevent import joinall, sleep, spawn

# humanize
from humanize import intcomma

# Zato
from common import set_progress_context
from production_documents import get_production_documents
from seeding import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The partners, each with a queue of its own.
_partner_count = 10

# How many API clients publish concurrently.
_publisher_greenlet_count = 25

# How many documents each API client publishes.
_documents_per_publisher = 40

# How many documents are published in the run.
_document_count = _publisher_greenlet_count * _documents_per_publisher

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 2000

# How long the whole run may take at most, in seconds.
_deadline_seconds = 600

# How often the run checks whether the last document has been delivered, in seconds.
_delivery_poll_seconds = 0.05

# How many bytes one megabyte has.
_bytes_per_mb = 1_000_000

# ################################################################################################################################
# ################################################################################################################################

def _digest(document:'str') -> 'str':
    out = sha256(document.encode('utf8')).hexdigest()
    return out

# ################################################################################################################################

def _publish_share(
    backend:'SQLPubSubBackend',
    topic_names:'strlist',
    documents:'strlist',
    publisher_index:'int',
    state:'anydict',
    ) -> 'None':
    """ What one API client runs - its share of the documents, each one to the next partner,
    with every client starting at a different point of the mix.
    """
    for document_index in range(_documents_per_publisher):

        position = publisher_index + document_index
        topic_name = topic_names[position % _partner_count]
        document = documents[position % len(documents)]

        _ = backend.publish(topic_name, document)

        state['published'][topic_name][_digest(document)] += 1
        state['published_bytes'] += len(document.encode('utf8'))

# ################################################################################################################################

def _consume(backend:'SQLPubSubBackend', sub_key:'str', topic_name:'str', state:'anydict') -> 'None':
    """ What one partner runs - blocking fetches and one acknowledgement per batch, recording the digest
    of each document it receives.
    """
    received = state['received'][topic_name]

    while state['delivered'] < _document_count:

        messages = backend.fetch_messages(sub_key, block_ms=_consumer_block_ms)

        if not messages:
            continue

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])
            received[_digest(message['data'])] += 1

        _ = backend.ack_messages(sub_key, msg_ids)

        state['delivered'] += len(messages)
        sleep(0)

# ################################################################################################################################

def run_production_mix_scenario() -> 'None':
    """ The production mix of documents from 1 KB to 10 MB - receipts, HL7 lab results and admissions, XML and EDIFACT
    orders, FHIR bundles, X12 orders and ship notices and PDF invoices - published by API clients to the queues
    of the partners while the partners consume them. Every partner must receive exactly the documents published
    to it, each one unchanged, within the deadline.
    """
    set_progress_context('production mix', _publisher_greenlet_count, _partner_count)

    delete_all_rows()

    backend = SQLPubSubBackend()
    documents = get_production_documents()

    topic_names:'strlist' = []
    state:'anydict' = {
        'published': {},
        'received': {},
        'published_bytes': 0,
        'delivered': 0,
    }

    for partner_index in range(_partner_count):

        topic_name = f'perf.production.{partner_index:04d}'
        sub_key = f'zpsk.perf.production.{partner_index:04d}'

        topic_names.append(topic_name)
        state['published'][topic_name] = Counter()
        state['received'][topic_name] = Counter()

        backend.subscribe(sub_key, topic_name)

    start = monotonic()

    # The partners wait for their documents before the first one is published ..
    consumer_greenlets:'anylist' = []

    for partner_index, topic_name in enumerate(topic_names):
        sub_key = f'zpsk.perf.production.{partner_index:04d}'
        consumer_greenlets.append(spawn(_consume, backend, sub_key, topic_name, state))

    # .. the API clients publish concurrently with them ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        greenlet = spawn(_publish_share, backend, topic_names, documents, publisher_index, state)
        publisher_greenlets.append(greenlet)

    _ = joinall(publisher_greenlets, timeout=_deadline_seconds, raise_error=True)
    publish_elapsed = monotonic() - start

    # .. every document must reach its partner before the deadline ..
    deadline = start + _deadline_seconds

    while state['delivered'] < _document_count:
        assert monotonic() < deadline, f'Delivered {intcomma(state["delivered"])} of {intcomma(_document_count)} documents'
        sleep(_delivery_poll_seconds)

    elapsed = monotonic() - start
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds, raise_error=True)

    # .. and each partner received exactly what was published to it, byte for byte.
    for topic_name in topic_names:
        published = state['published'][topic_name]
        received = state['received'][topic_name]
        assert received == published, f'Documents of {topic_name} differ from the ones published'

    published_mb = state['published_bytes'] / _bytes_per_mb

    message = f'Production mix: {intcomma(int(_document_count / publish_elapsed))} publishes/s'
    message += f' at {intcomma(int(published_mb / publish_elapsed))} MB/s,'
    message += f' {intcomma(int(_document_count / elapsed))} deliveries/s at {intcomma(int(published_mb / elapsed))} MB/s,'
    message += f' {intcomma(int(published_mb))} MB in total'
    print(message)

# ################################################################################################################################
# ################################################################################################################################
