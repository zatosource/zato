# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from uuid import uuid4

# Zato
from zato.admin.web.views.ai.common import get_redis_client
from zato.common.json_internal import dumps, loads

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

Redis_Key_Prefix_Browser_Tool = 'zato.ai.browser-tool.'
Browser_Tool_Timeout = 60

# ################################################################################################################################
# ################################################################################################################################

class BrowserToolExecutor:
    """ Executes tools in the browser via SSE events and Redis callbacks.
    """

    def __init__(self, yield_event:'callable'):
        self.yield_event = yield_event
        self.redis_client = get_redis_client()

# ################################################################################################################################

    def _format_browser_tool_event(self, request_id:'str', tool_name:'str', params:'anydict') -> 'anydict':
        """ Formats a browser_tool SSE event.
        """
        return {
            'type': 'browser_tool',
            'request_id': request_id,
            'tool_name': tool_name,
            'params': params
        }

# ################################################################################################################################

    def execute(self, tool_name:'str', params:'anydict') -> 'anydict':
        """ Executes a browser tool and waits for the result.
        """
        request_id = uuid4().hex
        redis_key = Redis_Key_Prefix_Browser_Tool + request_id

        logger.info('Executing browser tool %s with request_id %s, params: %s', tool_name, request_id, params)

        event = self._format_browser_tool_event(request_id, tool_name, params)

        for item in self.yield_event(event):
            yield item

        logger.info('Waiting for browser tool result on key %s', redis_key)

        result = self.redis_client.blpop(redis_key, timeout=Browser_Tool_Timeout)

        if result is None:
            logger.warning('Browser tool %s timed out after %s seconds', tool_name, Browser_Tool_Timeout)
            return {'success': False, 'error': f'Browser tool timed out after {Browser_Tool_Timeout} seconds'}

        _, result_json = result
        result_data = loads(result_json)

        self.redis_client.delete(redis_key)

        logger.info('Browser tool %s completed with result: %s', tool_name, result_data)

        return result_data

# ################################################################################################################################
# ################################################################################################################################

def submit_browser_tool_result(request_id:'str', result:'anydict') -> 'None':
    """ Called by the callback endpoint to submit a browser tool result.
    """
    redis_client = get_redis_client()
    redis_key = Redis_Key_Prefix_Browser_Tool + request_id

    logger.info('Submitting browser tool result for request_id %s: %s', request_id, result)

    result_json = dumps(result)
    redis_client.lpush(redis_key, result_json)
    redis_client.expire(redis_key, 120)

# ################################################################################################################################
# ################################################################################################################################

Browser_Tool_Schemas = {
    'search_internet': {
        'name': 'search_internet',
        'description': 'Search the internet using a search engine. The search is performed by the user\'s browser.',
        'input_schema': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'The search query'
                }
            },
            'required': ['query']
        }
    },
    'visit_page': {
        'name': 'visit_page',
        'description': 'Visit a web page and retrieve its content. The page is fetched by the user\'s browser.',
        'input_schema': {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'description': 'The URL to visit'
                }
            },
            'required': ['url']
        }
    }
}

# ################################################################################################################################

def get_browser_tool_schemas() -> 'list':
    """ Returns the list of browser tool schemas for LLM.
    """
    return list(Browser_Tool_Schemas.values())

# ################################################################################################################################

def is_browser_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is a browser tool.
    """
    return tool_name in Browser_Tool_Schemas

# ################################################################################################################################
# ################################################################################################################################
