# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import joinall, sleep, spawn

# humanize
from humanize import intcomma

# Zato
from common import get_min_delivery_rate, get_min_publish_rate, set_progress_context
from documents import get_document_mix
from load import consume_until_done
from seeding import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The business-to-business pattern - many API clients publish documents of very different sizes,
# from small receipts to large batch files, each to the queue of one trading partner.
_partner_count = 10

# How many API clients publish concurrently.
_publisher_greenlet_count = 100

# How many documents each API client publishes.
_documents_per_publisher = 20

# How many documents are published in the measured run.
_document_count = _publisher_greenlet_count * _documents_per_publisher

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 2000

# How long the whole run may take at most before it is declared hung, in seconds.
_deadline_seconds = 120

# How often the run checks whether the last document has been delivered, in seconds.
_delivery_poll_seconds = 0.01

# How many bytes one megabyte has.
_bytes_per_mb = 1_000_000

# ################################################################################################################################
# ################################################################################################################################

def _publish_share(
    backend:'SQLPubSubBackend',
    topic_names:'strlist',
    documents:'strlist',
    publisher_index:'int',
    counters:'anydict',
    ) -> 'None':
    """ What one API client runs - its share of the documents, each one to the next partner,
    with every client starting at a different point of the mix.
    """
    for document_index in range(_documents_per_publisher):

        position = publisher_index + document_index
        topic_name = topic_names[position % _partner_count]
        document = documents[position % len(documents)]

        _ = backend.publish(topic_name, document)

        counters['published_bytes'] += len(document)

# ################################################################################################################################

def run_document_mix_scenario() -> 'None':
    """ A mix of business documents - 40 percent delivery receipts of 1 KB, 30 percent HL7 lab results of 10 KB,
    20 percent XML purchase orders of 100 KB and 10 percent X12 batches of 1 MB - published by one hundred
    concurrent API clients to the queues of ten partners, while the partners consume them.
    Both the publish and the delivery floors must hold.
    """
    set_progress_context('document mix', _publisher_greenlet_count, _partner_count)

    delete_all_rows()

    backend = SQLPubSubBackend()
    documents = get_document_mix()

    # Each partner has a queue of its own ..
    topic_names:'strlist' = []
    sub_keys:'strlist' = []

    for partner_index in range(_partner_count):

        topic_name = f'perf.documents.{partner_index:04d}'
        sub_key = f'zpsk.perf.documents.{partner_index:04d}'

        topic_names.append(topic_name)
        sub_keys.append(sub_key)

        backend.subscribe(sub_key, topic_name)

    counters:'anydict' = {
        'delivered': 0,
        'expected': _document_count,
        'published_bytes': 0,
    }

    start = monotonic()

    # .. the partners are already waiting when the first document lands ..
    consumer_greenlets:'anylist' = []

    for sub_key in sub_keys:
        consumer_greenlets.append(spawn(consume_until_done, backend, sub_key, counters, _consumer_block_ms))

    # .. the API clients publish concurrently with them ..
    publisher_greenlets:'anylist' = []

    for publisher_index in range(_publisher_greenlet_count):
        greenlet = spawn(_publish_share, backend, topic_names, documents, publisher_index, counters)
        publisher_greenlets.append(greenlet)

    # .. the publish rate is measured over the clients' own window ..
    _ = joinall(publisher_greenlets, timeout=_deadline_seconds)

    publish_elapsed = monotonic() - start

    # .. the delivery rate is measured up to the last delivery, because after it the other partners
    # .. remain in a blocking fetch until its block time ends ..
    deadline = start + _deadline_seconds

    while counters['delivered'] < _document_count:
        if monotonic() > deadline:
            break
        sleep(_delivery_poll_seconds)

    elapsed = monotonic() - start

    # .. and every document must reach its partner.
    _ = joinall(consumer_greenlets, timeout=_deadline_seconds)

    delivered = counters['delivered']
    assert delivered == _document_count, f'Expected {intcomma(_document_count)} deliveries, got {intcomma(delivered)}'

    publish_rate = _document_count / publish_elapsed
    delivery_rate = delivered / elapsed

    published_mb = counters['published_bytes'] / _bytes_per_mb
    publish_mb_rate = published_mb / publish_elapsed
    average_kb = counters['published_bytes'] / _document_count / 1000

    assert publish_rate >= get_min_publish_rate(), f'Document mix publish rate too low: {intcomma(int(publish_rate))}/s'
    assert delivery_rate >= get_min_delivery_rate(), f'Document mix delivery rate too low: {intcomma(int(delivery_rate))}/s'

    message = f'Document mix: {intcomma(int(publish_rate))} publishes/s at {intcomma(int(publish_mb_rate))} MB/s,'
    message += f' {intcomma(int(delivery_rate))} deliveries/s, average document {intcomma(int(average_kb))} KB'
    print(message)

# ################################################################################################################################
# ################################################################################################################################
