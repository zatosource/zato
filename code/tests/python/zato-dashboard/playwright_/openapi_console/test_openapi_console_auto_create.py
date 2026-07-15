# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import find_channel_row, get_row_cell_texts, open_channel_page, wait_for_channel_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# All auto channels of this suite share this name fragment, which the list page filters by
_Query = 'api.test.openapi'

# Row cell indexes for REST channel rows
_Cell_Name      = 2
_Cell_Is_Active = 3
_Cell_Url_Path  = 4
_Cell_Service   = 5
_Cell_Security  = 6

# What the security cell shows for a channel with no security definition
_No_Security = '---'

# Every auto channel the server must have created at boot, with its expected activity flag -
# the names double as service names and the URL paths follow from them by convention.
_Expected_Channels = {
    'api.test.openapi.typed.get-user':     {'is_active': 'No',  'url_path': '/api/api/test/openapi/typed/get-user'},
    'api.test.openapi.untyped.echo':       {'is_active': 'No',  'url_path': '/api/api/test/openapi/untyped/echo'},
    'api.test.openapi.methods.multi':      {'is_active': 'No',  'url_path': '/api/api/test/openapi/methods/multi'},
    'api.test.openapi.prestarted.ping':    {'is_active': 'Yes', 'url_path': '/api/api/test/openapi/prestarted/ping'},
    'api.test.openapi.diffing.contract':   {'is_active': 'No',  'url_path': '/api/api/test/openapi/diffing/contract'},
}

# Services that must have no channel at all - the first one matches an exclude pattern,
# the second one matches no include pattern.
_Excluded_Channel = 'api.test.openapi.excluded.hidden'
_No_Match_Channel = 'api.other.no-match'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleAutoCreate:
    """ Verifies that REST channels are auto-created at server boot for the services matching
    the include patterns, named and pathed by convention, inactive by default except for
    the active-pattern matches, with no security, and never created for excluded services.
    """

# ################################################################################################################################

    def test_auto_created_channels(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Checks every expected auto channel row and the absence of the excluded ones.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the REST channels page filtered down to this suite's channels ..
        open_channel_page(page, base_url, query=_Query)

        # .. verify each expected auto channel row ..
        for name, expected in _Expected_Channels.items():

            row = wait_for_channel_row(page, name)
            cells = get_row_cell_texts(row)

            # .. the name and the URL path follow from the service name by convention ..
            assert cells[_Cell_Name] == name, f'Expected name `{name}`, got: {cells}'
            assert cells[_Cell_Url_Path] == expected['url_path'], \
                f'Expected url_path `{expected["url_path"]}` for `{name}`, got: {cells}'

            # .. the channel serves the service it was created for ..
            assert cells[_Cell_Service] == name, f'Expected service `{name}`, got: {cells}'

            # .. only the active-pattern match boots active ..
            assert cells[_Cell_Is_Active] == expected['is_active'], \
                f'Expected is_active `{expected["is_active"]}` for `{name}`, got: {cells}'

            # .. and no auto channel carries any security definition at creation.
            assert cells[_Cell_Security] == _No_Security, f'Expected no security for `{name}`, got: {cells}'

        # .. the excluded service matches an include and an exclude pattern, the exclude wins ..
        excluded_row = find_channel_row(page, _Excluded_Channel)
        assert excluded_row is None, f'Expected no channel for `{_Excluded_Channel}`'

        # .. and a service matching no include pattern gets no channel either.
        open_channel_page(page, base_url, query=_No_Match_Channel)

        no_match_row = find_channel_row(page, _No_Match_Channel)
        assert no_match_row is None, f'Expected no channel for `{_No_Match_Channel}`'

# ################################################################################################################################
# ################################################################################################################################
