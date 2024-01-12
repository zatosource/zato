# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# Zato
from zato.url_dispatcher import Matcher

# ################################################################################################################################
# ################################################################################################################################

class Response:
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data

# ################################################################################################################################
# ################################################################################################################################

class RequestsAdapter:

    def __init__(self):
        self._get_handlers = []
        self._post_handlers = []

# ################################################################################################################################

    def _on_request(self, path, config, args, kwargs):
        # type: (str, list) -> Response
        for item in config:
            matcher = item['matcher'] # type: Matcher
            if matcher.match(path) is not None:
                func = item['func']
                data = func(path, args=args, kwargs=bunchify(kwargs))
                return Response(data)
        else:
            raise KeyError(path)

# ################################################################################################################################

    def get(self, path, *args, **kwargs):
        # type: (...) -> Response
        return self._on_request(path, self._get_handlers, args, kwargs)

# ################################################################################################################################

    def post(self, path, *args, **kwargs):
        # type: (...) -> Response
        return self._on_request(path, self._post_handlers, args, kwargs)

# ################################################################################################################################

    def _add_handler(self, path, func, config):
        # type: (str, object, list)
        config.append({
            'path': path,
            'matcher': Matcher(path),
            'func': func,
        })

# ################################################################################################################################

    def add_get_handler(self, path, func):
        self._add_handler(path, func, self._get_handlers)

# ################################################################################################################################

    def add_post_handler(self, path, func):
        self._add_handler(path, func, self._post_handlers)

# ################################################################################################################################
# ################################################################################################################################
