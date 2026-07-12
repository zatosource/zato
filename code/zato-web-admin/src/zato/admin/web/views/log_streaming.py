# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Redis
import redis

# Django
from django.http import HttpResponse, HttpResponseBadRequest

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The Redis stream that the servers write log entries to
_log_stream_key = 'zato.logs'

# A cursor meaning "start from the very beginning of the stream"
_stream_start_id = '0-0'

# The most entries a single poll may return
_max_entries_per_poll = 500

# One client per worker process, redis-py clients are connection pools and are thread-safe
_redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def toggle_streaming(req):

    logger.info('toggle_streaming: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    response = req.zato.client.invoke('zato.log.streaming.toggle', {})
    logger.info('toggle_streaming: service response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_status(req):

    logger.info('get_status: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    response = req.zato.client.invoke('zato.log.streaming.status', {})
    logger.info('get_status: service response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def read_log_entries(req):
    """ Single-shot endpoint for log streaming.
    The client sends the id of the last stream entry it has seen, the server reads everything
    newer than that from the capped Redis stream and returns it as one JSON document.
    The client polls this endpoint periodically for as long as the page is open, so a worker
    is only ever occupied for the duration of one read, never for the lifetime of the page.
    """
    stream_logger = getLogger('zato.sse_stream')

    try:
        request_data = loads(req.body.decode('utf-8'))
    except Exception:
        stream_logger.error(f'read_log_entries: failed to parse request body: {format_exc()}')
        return HttpResponseBadRequest('Invalid JSON in request body')

    last_id = request_data['last_id']

    # A client with no cursor starts at the current end of the stream, receiving only
    # what is logged after its page opened - the same semantics the pubsub channel had.
    if not last_id:

        newest = _redis_client.xrevrange(_log_stream_key, count=1)

        if newest:
            newest_entry = newest[0]
            last_id = newest_entry[0]
        else:
            last_id = _stream_start_id

        out = {'last_id': last_id, 'entries': []}
        response = HttpResponse(dumps(out), content_type='application/json')
        response['Cache-Control'] = 'no-cache'

        return response

    # Read everything that arrived after the client's cursor - the '(' prefix makes the range exclusive
    raw_entries = _redis_client.xrange(_log_stream_key, min=f'({last_id}', count=_max_entries_per_poll)

    entries = []

    for entry_id, entry_fields in raw_entries:
        log_entry = loads(entry_fields['data'])
        entries.append(log_entry)
        last_id = entry_id

    if entries:
        entry_count = len(entries)
        suffix = 'entry' if entry_count == 1 else 'entries'
        stream_logger.info(f'read_log_entries: returning {entry_count} {suffix}, new last_id={last_id}')

    out = {'last_id': last_id, 'entries': entries}
    response = HttpResponse(dumps(out), content_type='application/json')
    response['Cache-Control'] = 'no-cache'

    return response

# ################################################################################################################################
# ################################################################################################################################
