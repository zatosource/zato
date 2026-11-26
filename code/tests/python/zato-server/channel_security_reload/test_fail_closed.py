# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.exception import Forbidden
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.channel import logger as channel_logger, RequestDispatcher

# Local
from .helpers import Channel_Name, make_channel_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_cid = 'zcid-test-fail-closed-0001'

# ################################################################################################################################
# ################################################################################################################################

def _make_dispatcher(url_data:'MagicMock') -> 'RequestDispatcher':
    """ A dispatcher with everything but the security check itself mocked away.
    """
    out = RequestDispatcher(
        server=MagicMock(),
        url_data=url_data,
        request_handler=MagicMock(),
        return_tracebacks=False,
        default_error_message='Internal server error',
        http_methods_allowed=['GET', 'POST'],
    )

    return out

# ################################################################################################################################

def _check_security(dispatcher:'RequestDispatcher', channel_item:'Bunch') -> 'None':
    """ Runs the security check of one request without credentials against the channel.
    """
    meta = cast_('any_', MagicMock())
    config_manager = cast_('any_', MagicMock())
    request_ctx:'stranydict' = {}

    dispatcher._check_security(_cid, meta, channel_item, request_ctx, b'', {}, config_manager)

# ################################################################################################################################
# ################################################################################################################################

class FailClosedTestCase(TestCase):
    """ A channel with security groups whose security groups context is not in place.
    """

    def test_channel_with_groups_and_no_context_is_refused(self) -> 'None':

        url_data = MagicMock()
        dispatcher = _make_dispatcher(url_data)
        channel_item = make_channel_item()

        with expected_records(channel_logger.name):
            with self.assertLogs(channel_logger, level='ERROR') as captured:
                with self.assertRaises(Forbidden):
                    _check_security(dispatcher, channel_item)

        # The record names the channel and the request ..
        record = captured.records[0]
        message = record.getMessage()

        self.assertIn(Channel_Name, message)
        self.assertIn(_cid, message)

        # .. and the check did not get as far as the credentials.
        url_data.check_security.assert_not_called()

# ################################################################################################################################

    def test_service_that_handles_rejections_does_not_receive_the_request(self) -> 'None':

        url_data = MagicMock()
        dispatcher = _make_dispatcher(url_data)
        channel_item = make_channel_item()

        with patch.object(dispatcher, '_service_handles_auth_rejection', return_value=True):
            with expected_records(channel_logger.name):
                with self.assertRaises(Forbidden):
                    _check_security(dispatcher, channel_item)

# ################################################################################################################################

    def test_channel_with_an_empty_group_list_is_not_refused(self) -> 'None':

        url_data = MagicMock()
        dispatcher = _make_dispatcher(url_data)

        channel_item = make_channel_item()
        channel_item.security_groups = []

        _check_security(dispatcher, channel_item)

        # The security definition of the channel is what the request is checked against.
        url_data.check_security.assert_called_once()

# ################################################################################################################################

    def test_channel_with_groups_and_a_context_is_checked_against_the_groups(self) -> 'None':

        url_data = MagicMock()
        dispatcher = _make_dispatcher(url_data)

        security_groups_ctx = MagicMock()
        security_groups_ctx.has_members.return_value = True

        channel_item = make_channel_item()
        channel_item.security_groups_ctx = security_groups_ctx

        with patch.object(dispatcher, 'check_security_via_groups') as check_security_via_groups:
            _check_security(dispatcher, channel_item)

        check_security_via_groups.assert_called_once()

        # The context of the channel's groups is what the request is checked against.
        call_args = check_security_via_groups.call_args
        self.assertIs(call_args.args[2], security_groups_ctx)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
