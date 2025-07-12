# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import asdict
from datetime import timedelta
from json import dumps, loads
from logging import getLogger
from uuid import uuid4

# Zato
from zato.common.typing_ import any_, anydict, dict_, list_, strnone
from zato.common.util.api import utcnow
from zato.common.util.auth import check_basic_auth, extract_basic_auth

# gevent
from gevent.pywsgi import WSGIServer

# gunicorn
from gunicorn.app.base import BaseApplication

# werkzeug
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request
from werkzeug.middleware.proxy_fix import ProxyFix

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import PubSub
from zato.common.util.api import new_cid, new_sub_key
from zato.common.pubsub.models import PubMessage, PubResponse, SimpleResponse
from zato.common.pubsub.models import Subscription, Topic
from zato.common.pubsub.models import topic_subscriptions
from zato.common.pubsub.models import APIResponse, BadRequestResponse, HealthCheckResponse, NotFoundResponse, \
    NotImplementedResponse, UnauthorizedResponse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, dictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_prefix = PubSub.Prefix
_rest_server = PubSub.REST_Server

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class Backend:
    """ Backend implementation of pub/sub, irrespective of the actual REST server.
    """

# ################################################################################################################################
# ################################################################################################################################
