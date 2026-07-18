# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import config_db_redis_page_config, config_db_sql_page_config
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    HttpRequest = HttpRequest

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The databases the SQL screen knows about, in their display order
_sql_databases = ['audit-log', 'analytics']

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_', success:'bool'=True) -> 'HttpResponse':
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################

def _invoke(req:'any_', service_name:'str') -> 'HttpResponse':
    """ Forwards the JSON body of a request to a config DB service and returns its response as JSON.
    """
    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        response = req.zato.client.invoke(service_name, config_data)

        if response.ok:
            data = response.data
            return _json_response(data, success=data['success'])
        else:
            return _json_response({'success': False, 'error': str(response)}, success=False)

    except Exception as e:
        logger.error('config_db `%s`: %s', service_name, format_exc())
        return _json_response({'success': False, 'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def sql_index(req:'any_') -> 'TemplateResponse':

    # The current values of each database, keyed by its identifier
    sql_values = {}

    try:
        for database in _sql_databases:
            response = req.zato.client.invoke('zato.config-db.sql.get', {'database': database})
            if response.ok:
                sql_values[database] = response.data['values']
            else:
                logger.error('config_db sql_index: invoke failed: %s', response)
    except Exception:
        logger.error('config_db sql_index: %s', format_exc())

    return TemplateResponse(req, 'zato/config-db/sql/index.html', {
        'page_config': config_db_sql_page_config,
        'sql_values': sql_values,
    })

# ################################################################################################################################

@method_allowed('POST')
def sql_test(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.sql.test')
    return out

# ################################################################################################################################

@method_allowed('POST')
def sql_save(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.sql.save')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def redis_index(req:'any_') -> 'TemplateResponse':

    # The current values of the default Redis connection
    redis_values = {}

    try:
        response = req.zato.client.invoke('zato.config-db.redis.get', {})
        if response.ok:
            redis_values = response.data['values']
        else:
            logger.error('config_db redis_index: invoke failed: %s', response)
    except Exception:
        logger.error('config_db redis_index: %s', format_exc())

    return TemplateResponse(req, 'zato/config-db/redis/index.html', {
        'page_config': config_db_redis_page_config,
        'redis_values': redis_values,
    })

# ################################################################################################################################

@method_allowed('POST')
def redis_test(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.test')
    return out

# ################################################################################################################################

@method_allowed('POST')
def redis_save(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.save')
    return out

# ################################################################################################################################
# ################################################################################################################################
