# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.config_db import _invoke
from zato.admin.web.views.settings.config import redis_page_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpResponse
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    HttpResponse = HttpResponse

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    # The current values of the default Redis connection
    redis_values = {}

    try:
        response = req.zato.client.invoke('zato.config-db.redis.get', {})
        if response.ok:
            redis_values = response.data['values']
        else:
            logger.error('redis index: invoke failed: %s', response)
    except Exception:
        logger.error('redis index: %s', format_exc())

    return TemplateResponse(req, 'zato/redis.html', {
        'page_config': redis_page_config,
        'redis_values': redis_values,
    })

# ################################################################################################################################

@method_allowed('POST')
def test(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.test')
    return out

# ################################################################################################################################

@method_allowed('POST')
def save(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.save')
    return out

# ################################################################################################################################
# ################################################################################################################################
