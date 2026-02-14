# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.http import StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.common import get_api_key, is_valid_provider
from zato.admin.web.views.ai.llm.factory import get_llm_client
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads

if 0:
    from zato.common.typing_ import generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _get_provider_for_model(model_id:'str') -> 'str | None':
    """ Returns the provider for a given model ID.
    """
    all_models = get_all_models()

    for provider, models in all_models.items():
        for model in models:
            if model['id'] == model_id:
                return provider

    return None

# ################################################################################################################################

def _format_sse_event(event_type:'str', data:'dict') -> 'str':
    """ Formats an SSE event.
    """
    data_json = dumps(data)
    out = f'event: {event_type}\ndata: {data_json}\n\n'
    return out

# ################################################################################################################################

def _stream_response(model_id:'str', messages:'list') -> 'generator_':
    """ Generator that yields SSE events for a chat stream.
    """
    provider = _get_provider_for_model(model_id)

    if not provider:
        error_event = _format_sse_event('error', {'message': f'Unknown model: {model_id}'})
        yield error_event
        return

    api_key = get_api_key(provider)

    if not api_key:
        error_event = _format_sse_event('error', {'message': f'No API key configured for {provider}'})
        yield error_event
        return

    try:
        client = get_llm_client(provider, api_key)
    except ValueError as e:
        error_event = _format_sse_event('error', {'message': str(e)})
        yield error_event
        return

    try:
        for response in client.stream_chat(model_id, messages):
            response_type = response.get('type', '')
            content = response.get('content', '')

            if response_type == 'chunk':
                chunk_event = _format_sse_event('chunk', {'text': content})
                yield chunk_event

            elif response_type == 'done':
                done_event = _format_sse_event('done', {})
                yield done_event
                return

            elif response_type == 'error':
                error_event = _format_sse_event('error', {'message': content})
                yield error_event
                return

    except Exception as e:
        logger.warning('Stream error: %s', e)
        error_event = _format_sse_event('error', {'message': str(e)})
        yield error_event

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke(req) -> 'StreamingHttpResponse':
    """ SSE endpoint for streaming chat responses.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)

        def error_gen():
            error_event = _format_sse_event('error', {'message': 'Invalid request body'})
            yield error_event

        response = StreamingHttpResponse(error_gen(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    model_id = body.get('model', '')
    messages = body.get('messages', [])

    if not model_id:
        def error_gen():
            error_event = _format_sse_event('error', {'message': 'Model ID is required'})
            yield error_event

        response = StreamingHttpResponse(error_gen(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    if not messages:
        def error_gen():
            error_event = _format_sse_event('error', {'message': 'Messages are required'})
            yield error_event

        response = StreamingHttpResponse(error_gen(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    response = StreamingHttpResponse(_stream_response(model_id, messages), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'

    return response

# ################################################################################################################################
# ################################################################################################################################
