# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import NotFound
from zato.server.service import Bool, Service

# ################################################################################################################################

class _CacheService(Service):
    pass

# ################################################################################################################################

class Get(_CacheService):

    class SimpleIO:
        response_elem = None
        input_required = ('key',)
        input_optional = ('cache', 'default', Bool('details'),)
        output_required = ('value',)
        output_optional = ('key', 'last_read', 'prev_read', 'last_write', 'prev_write', 'expiry', 'expires_at', 'hits',
            'position')
        skip_empty = True
        ignore_skip_empty = ('value',)
        allow_empty_required = True

# ################################################################################################################################

    def handle(self):
        input = self.request.input
        cache_name = input['cache']

        if cache_name:
            try:
                cache = self.cache.builtin[cache_name]
            except KeyError:
                raise NotFound(self.cid, 'No such cache `{}`'.format(cache_name))
        else:
            cache = self.cache.default

        kwargs = {
            'key': input['key'],
            'details': input.get('details'),
        }
        if input.get('default'):
            kwargs['default'] = input['default']

        cache.set(input['key'], None)

        item = cache.get(**kwargs)

        if item is not None:
            self.response.payload = item.to_dict() if input['details'] else {'value': item}
        else:
            raise NotFound(self.cid, 'No such key `{}`'.format(input['key']))

# ################################################################################################################################
