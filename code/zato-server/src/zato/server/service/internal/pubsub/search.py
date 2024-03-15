# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import SEARCH
from zato.common.util.search import SearchResults
from zato.common.util.time_ import datetime_from_ms
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE

# ################################################################################################################################
# ################################################################################################################################

class NonGDSearchService(AdminService):
    """ A base class for services that produce a list of paginated non-GD messages.
    """
    def _post_process_msg_list(self, msg_list) -> 'None':

        for msg in msg_list:

            # Convert float timestamps in all the remaining messages to ISO-8601
            msg['pub_time'] = datetime_from_ms(msg['pub_time'] * 1000.0)
            if msg.get('expiration_time'):
                msg['expiration_time'] = datetime_from_ms(msg['expiration_time'] * 1000.0)

            # Return endpoint information in the same format GD messages are returned in
            msg['endpoint_id'] = msg.pop('published_by_id')
            msg['endpoint_name'] = self.pubsub.get_endpoint_by_id(msg['endpoint_id']).name

# ################################################################################################################################

    def set_non_gd_msg_list_response(self, msg_list, cur_page) -> 'None':
        """ Paginates a list of non-GD messages (from topics or queues) and returns results.
        """
        # Build the results metadata
        search_results = SearchResults.from_list(
            msg_list, cur_page, _page_size, needs_sort=True, post_process_func=self._post_process_msg_list)

        # This goes to the service's response payload object ..
        self.response.payload.response = msg_list

        # .. and this is metadata so it goes to _meta.
        self.response.payload._meta = search_results.to_dict()

# ################################################################################################################################
# ################################################################################################################################
