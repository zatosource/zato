# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Zato
from zato.common import SEARCH
from zato.common.util.search import SearchResults
from zato.common.util.time_ import datetime_from_ms
from zato.server.service.internal import AdminService

# ################################################################################################################################

_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value

# ################################################################################################################################

class NonGDSearchService(AdminService):
    """ A base class for services that produce a list of paginated non-GD messages.
    """
    def set_non_gd_msg_list_response(self, msg_list, cur_page, _sort_key=itemgetter('pub_time')):
        """ Paginates a list of non-GD messages (from topics or queues) and returns results.
        """
        cur_page = cur_page - 1 if cur_page else 0 # We index lists from 0

        # Set it here because later on it may be shortened to the page_size of elements
        total = len(msg_list)

        # If we get here, we must have collected some data at all
        if msg_list:

            # Sort the output before it is returned - messages last published (youngest) come first
            msg_list.sort(key=_sort_key, reverse=True)
            start = cur_page * _page_size
            end = start + _page_size
            msg_list = msg_list[start:end]

        for msg in msg_list:

            # Convert float timestamps in all the remaining messages to ISO-8601
            msg['pub_time'] = datetime_from_ms(msg['pub_time'] * 1000.0)
            if msg.get('expiration_time'):
                msg['expiration_time'] = datetime_from_ms(msg['expiration_time'] * 1000.0)

            # Return endpoint information in the same format GD messages are returned in
            msg['endpoint_id'] = msg.pop('published_by_id')
            msg['endpoint_name'] = self.pubsub.get_endpoint_by_id(msg['endpoint_id']).name

        search_results = SearchResults(None, None, None, total)
        search_results.set_data(cur_page, _page_size)

        # This goes to the service's response payload object
        self.response.payload.response = msg_list
        self.response.payload._meta = search_results.to_dict()

# ################################################################################################################################
