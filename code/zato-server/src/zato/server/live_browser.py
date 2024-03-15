# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# gevent
from gevent import spawn

# SQLAlchemy
from sqlalchemy import and_

# TextBlob
from textblob import TextBlob

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.odb.model import Server, WebSocketClient, WebSocketSubscription

# ################################################################################################################################

_wsgi_ignore = (
    'HTTP_ACCEPT', 'zato.oauth.post_data', 'zato.channel_item', 'zato.http.response.headers', 'zato.http.GET', 'zato.http.POST'
)
_wsgi_sub_dicts = ('zato.http.response.headers', 'zato.http.GET', 'zato.http.POST')

# ################################################################################################################################

def match_pattern(text, pattern):
    """ Returns True if every element in pattern is contained in words extracted ouf of text,
    pattern is assumed to be a set of lower-cased string elements.
    """
    return pattern <= {elem.lower() for elem in TextBlob(text).words}

# ################################################################################################################################

def live_browser_patterns(session, cluster_id):
    return session.query(WebSocketClient.ext_client_id, WebSocketSubscription.pattern).\
        filter(WebSocketSubscription.client_id==WebSocketClient.id).\
        filter(Server.cluster_id==cluster_id).\
        filter(and_(
            WebSocketSubscription.is_by_ext_id.is_(False),
            WebSocketSubscription.is_by_channel.is_(False))).\
        outerjoin(Server, Server.id==WebSocketClient.server_id).\
        all()

# ################################################################################################################################

def notify_msg_browser(service, step):

    with closing(service.odb.session()) as session:

        subs = {}
        for ext_client_id, pattern in live_browser_patterns(session, service.server.cluster_id):
            pattern = pattern.replace(WEB_SOCKET.PATTERN.MSG_BROWSER_PREFIX, '', 1)
            patterns = subs.setdefault(ext_client_id, set())
            patterns.add(pattern)

    # All metadata
    meta = []

    # WSGI keys and values of interest
    wsgi = []

    for key, value in sorted(service.wsgi_environ.items()):

        if key.startswith('SERVER_'):
            continue

        if key.startswith('wsgi.'):
            continue

        if key.startswith('gunicorn.'):
            continue

        if key in _wsgi_ignore:
            continue

        if not isinstance(key, basestring):
            key = str(key)

        if not isinstance(value, basestring):
            value = str(value)

        wsgi.append('{} {}'.format(key.lower(), value.lower()))

    for _sub_dict in _wsgi_sub_dicts:
        for key, value in iteritems(service.wsgi_environ[_sub_dict]):
            wsgi.append('{} {}'.format(key.lower(), value.lower()))

    channel_name = service.channel.name or 'invoker'
    wsgi_text = ' '.join(wsgi).strip() or ''
    meta = ' '.join([step, service.channel.type, channel_name, wsgi_text])

    # Concatenation of input data + WSGI + other metadata
    text = ('{} {}'.format(meta, service.request.raw_request.lower())).strip()

    # Match all data against each subscription
    for ext_client_id, pattern in subs.items():

        # Ok, something matched, send that client a notification
        if match_pattern(text, pattern):
            spawn(service.out.websockets.invoke, {'meta':meta, 'request':service.request.raw_request}, id=ext_client_id)

# ################################################################################################################################
