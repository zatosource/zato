# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_channel, open_channel_page, wait_for_channel_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.internal.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

# The built-in pub/sub channels are internal and must never expose Invoke or Audit log links
_Internal_Channels = ('pubsub.rest.publish', 'pubsub.rest.get-messages')

# ################################################################################################################################
# ################################################################################################################################

def _get_link(row:'any_', text:'str') -> 'any_':
    """ Returns the anchor with the given text in a row or None if there is no such anchor.
    """
    out = row.query_selector(f'a:text-is("{text}")')
    return out

# ################################################################################################################################

def _get_disabled_hint(row:'any_', text:'str') -> 'any_':
    """ Returns the grayed-out placeholder with the given text in a row or None if there is no such placeholder.
    """
    out = row.query_selector(f'span.form_hint:text-is("{text}")')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelInternal:
    """ Internal REST channels, e.g. the built-in pub/sub ones, are skipped by the audit log entirely,
    which is why their Invoke and Audit log links must be disabled in the channel list.
    """

    def test_internal_channel_links_disabled(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the channel list filtered down to the built-in pub/sub channels ..
        open_channel_page(page, base_url, query='pubsub.rest')

        for channel_name in _Internal_Channels:

            # .. each of them is listed ..
            row = wait_for_channel_row(page, channel_name)

            # .. neither the Invoke nor the Audit log link exists for it ..
            invoke_link = _get_link(row, 'Invoke')
            audit_log_link = _get_link(row, 'Audit log')

            assert invoke_link is None, f'Expected no Invoke link for `{channel_name}`'
            assert audit_log_link is None, f'Expected no Audit log link for `{channel_name}`'

            # .. while both cells still show their grayed-out placeholders.
            invoke_hint = _get_disabled_hint(row, 'Invoke')
            audit_log_hint = _get_disabled_hint(row, 'Audit log')

            assert invoke_hint is not None, f'Expected a disabled Invoke placeholder for `{channel_name}`'
            assert audit_log_hint is not None, f'Expected a disabled Audit log placeholder for `{channel_name}`'

# ################################################################################################################################

    def test_user_channel_links_enabled(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a user-defined channel ..
        channel_name = _Test_Name_Prefix + 'enabled'
        url_path = '/test/rest/internal/' + rand_string()

        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        # .. its row is listed ..
        row = wait_for_channel_row(page, channel_name)

        # .. and both links are active for it.
        invoke_link = _get_link(row, 'Invoke')
        audit_log_link = _get_link(row, 'Audit log')

        assert invoke_link is not None, f'Expected an Invoke link for `{channel_name}`'
        assert audit_log_link is not None, f'Expected an Audit log link for `{channel_name}`'

# ################################################################################################################################
# ################################################################################################################################
