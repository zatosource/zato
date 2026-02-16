# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.common import get_api_key, is_valid_provider
from zato.admin.web.views.ai.llm.core import get_llm_client
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads

if 0:
    from zato.common.typing_ import any_, generator_

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

def _stream_response(model_id:'str', messages:'list', zato_client:'any_'=None, cluster_id:'int'=None, cluster:'any_'=None, session_id:'str'='') -> 'generator_':
    """ Generator that yields SSE events for a chat stream.
    """
    provider = _get_provider_for_model(model_id)

    if not provider:
        error_data = {'message': f'Unknown model: {model_id}'}
        error_event = _format_sse_event('error', error_data)
        yield error_event
        return

    api_key = get_api_key(provider)

    if not api_key:
        error_data = {'message': f'No API key configured for {provider}'}
        error_event = _format_sse_event('error', error_data)
        yield error_event
        return

    try:
        client = get_llm_client(provider, api_key, zato_client, cluster_id, cluster, session_id)
    except ValueError as e:
        error_msg = str(e)
        error_data = {'message': error_msg}
        error_event = _format_sse_event('error', error_data)
        yield error_event
        return

    try:
        for llm_response in client.stream_chat(model_id, messages):
            response_type = llm_response.get('type', '')
            content = llm_response.get('content', '')

            if response_type == 'chunk':
                chunk_data = {'text': content}
                chunk_event = _format_sse_event('chunk', chunk_data)
                yield chunk_event

            elif response_type == 'done':
                done_data = {
                    'input_tokens': llm_response.get('input_tokens', 0),
                    'output_tokens': llm_response.get('output_tokens', 0)
                }
                done_event = _format_sse_event('done', done_data)
                yield done_event
                return

            elif response_type == 'error':
                error_data = {'message': content}
                error_event = _format_sse_event('error', error_data)
                yield error_event
                return

            elif response_type == 'object_changed':
                keys = ['action', 'object_id', 'object_name', 'object_type']
                changed_data = {key: llm_response[key] for key in keys}
                changed_event = _format_sse_event('object_changed', changed_data)
                yield changed_event

            elif response_type == 'tool_progress':
                progress_data = {
                    'status': llm_response.get('status', ''),
                    'total': llm_response.get('total', 0),
                    'completed': llm_response.get('completed', 0),
                    'message': llm_response.get('message', ''),
                    'items': llm_response.get('items', [])
                }
                progress_event = _format_sse_event('tool_progress', progress_data)
                yield progress_event

            elif response_type == 'browser_tool':
                browser_data = {
                    'request_id': llm_response.get('request_id', ''),
                    'tool_name': llm_response.get('tool_name', ''),
                    'params': llm_response.get('params', {})
                }
                browser_event = _format_sse_event('browser_tool', browser_data)
                yield browser_event

    except Exception as e:
        logger.warning('Stream error: %s', format_exc())
        error_msg = str(e)
        error_data = {'message': error_msg}
        error_event = _format_sse_event('error', error_data)
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

    zato_obj = getattr(req, 'zato', None)
    cluster_id = None
    cluster = None
    zato_client = None
    if zato_obj:
        cluster_id = zato_obj.cluster_id
        cluster = getattr(zato_obj, 'cluster', None)
        zato_client = zato_obj.client

    session_id = body.get('session_id', '') or req.session.session_key or ''
    is_new_conversation = body.get('is_new_conversation', False)

    if is_new_conversation and session_id:
        from zato.admin.web.views.ai.llm.execution import clear_session_state
        clear_session_state(session_id)
        logger.info('Cleared session state for new conversation: %s', session_id)

    response = StreamingHttpResponse(_stream_response(model_id, messages, zato_client, cluster_id, cluster, session_id), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'

    return response

# ################################################################################################################################

@method_allowed('POST')
def browser_tool_result(req):
    """ Callback endpoint for browser tool results.
    """
    from django.http import JsonResponse
    from zato.admin.web.views.ai.browser_tools import submit_browser_tool_result

    try:
        body = loads(req.body)
        request_id = body.get('request_id', '')
        result = body.get('result', {})

        if not request_id:
            return JsonResponse({'success': False, 'error': 'Missing request_id'})

        submit_browser_tool_result(request_id, result)

        return JsonResponse({'success': True})

    except Exception as e:
        logger.warning('Browser tool result error: %s', format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

# ################################################################################################################################

@method_allowed('POST')
def fetch_page(req):
    """ Proxy endpoint for fetching web pages server-side using curl_cffi.
    """
    from django.http import JsonResponse
    from curl_cffi import requests as curl_requests
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.skip_tags = {'script', 'style', 'noscript', 'head', 'meta', 'link'}
            self.current_tag = None

        def handle_starttag(self, tag, attrs):
            self.current_tag = tag

        def handle_endtag(self, tag):
            self.current_tag = None

        def handle_data(self, data):
            if self.current_tag not in self.skip_tags:
                text = data.strip()
                if text:
                    self.text_parts.append(text)

        def get_text(self):
            return ' '.join(self.text_parts)

    try:
        body = loads(req.body)
        url = body.get('url', '')

        if not url:
            return JsonResponse({'success': False, 'error': 'Missing url'})

        if not url.startswith(('http://', 'https://')):
            return JsonResponse({'success': False, 'error': 'Invalid url'})

        response = curl_requests.get(
            url,
            impersonate='chrome',
            timeout=30,
            allow_redirects=True
        )

        html = response.text
        title = ''

        title_start = html.lower().find('<title>')
        if title_start != -1:
            title_end = html.lower().find('</title>', title_start)
            if title_end != -1:
                title = html[title_start + 7:title_end].strip()

        extractor = TextExtractor()
        extractor.feed(html)
        content = extractor.get_text()

        if len(content) > 15000:
            content = content[:15000] + '...'

        return JsonResponse({
            'success': True,
            'url': url,
            'title': title,
            'content': content,
            'status_code': response.status_code
        })

    except Exception as e:
        logger.warning('Fetch page error: %s', format_exc())
        return JsonResponse({'success': False, 'url': url, 'error': str(e)})

# ################################################################################################################################
# ################################################################################################################################
