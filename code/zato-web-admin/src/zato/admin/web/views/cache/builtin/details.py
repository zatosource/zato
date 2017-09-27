# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.views import Index as _Index

logger = logging.getLogger(__name__)

class CacheEntry(object):
    def __init__(self, key, value, last_read, prev_read, prev_write, expiry, expires_at, hits, position):
        self.key = key
        self.value = value
        self.last_read = last_read
        self.prev_read = prev_read
        self.prev_write = prev_write
        self.expiry = expiry
        self.expires_at = expires_at
        self.hits = hits
        self.position = position

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cache-builtin-details'
    template = 'zato/cache/builtin/details.html'
    service_name = 'cache3.details' #'zato.cache.builtin.details.get-list'
    output_class = CacheEntry
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'id')
        output_required = ('key', 'value', 'position', 'hits', 'expiry', 'expires_at', 'last_read', 'prev_read', 'prev_write')
        output_repeated = True

    def handle(self):
        return {
            'show_search_form': True
        }

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import AsIs
from zato.server.service.internal import AdminService

class Details(AdminService):
    name = 'cache3.details'

    class SimpleIO:
        input_required = (AsIs('id'),)
        output_required = ('key', 'value', 'position', 'hits', 'expiry', 'expires_at', 'last_read', 'prev_read', 'prev_write')
        output_repeated = True

    def _get_data(self, _ignored_session, _ignored_cluster_id, *args, **kwargs):
        print(333, args, kwargs)
        return []

    def handle(self):
        self.response.payload[:] = self._search(self._get_data)
'''