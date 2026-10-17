# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The get_queue_response hook of a service - how deployment learns whether a service has one
# and what an invocation of the hook alone runs and does not run.

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT
from zato.common.typing_ import cast_
from zato.common.util.json_ import BasicParser
from zato.server.service import Invoke_Mode, Service
from zato.server.service.store import ServiceStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_cid = 'test-cid-0001'
_msg_id = 'zpsm-0000000000000001'

# The hook's and the handler's names, as the services below record them
_call_before_handle = 'before_handle'
_call_handle = 'handle'
_call_after_handle = 'after_handle'
_call_get_queue_response = 'get_queue_response'

# ################################################################################################################################
# ################################################################################################################################

class _TestService(Service):
    """ The class-level boilerplate a deployed service carries, which ServiceStore would otherwise set up.
    """
    _config_manager = MagicMock()
    _config_store = MagicMock()
    amqp = MagicMock()

    has_io = False
    component_enabled_email = False
    component_enabled_odoo = False

# ################################################################################################################################

class _HandleOnlyService(_TestService):
    """ A service without the hook - the common case.
    """
    _Service__service_name = 'orders.handle-only'
    _Service__service_impl_name = 'orders.api.HandleOnlyService'

    def handle(self) -> 'None':
        pass

# ################################################################################################################################

class _AfterHandleService(_TestService):
    """ A service with after_handle and without the hook - the two are not the same thing.
    """
    _Service__service_name = 'orders.after-handle'
    _Service__service_impl_name = 'orders.api.AfterHandleService'

    def handle(self) -> 'None':
        pass

    def after_handle(self) -> 'None':
        pass

# ################################################################################################################################

class _HookService(_TestService):
    """ A service with every hook, each of them recording that it ran and what it saw.
    """
    _Service__service_name = 'orders.with-hook'
    _Service__service_impl_name = 'orders.api.HookService'

    # Each instance records into the list of the test that created it
    calls:'anylist'

    def before_handle(self) -> 'None':
        self.calls.append(_call_before_handle)

    def handle(self) -> 'None':
        self.calls.append(_call_handle)
        self.response.payload = {'handled': True, 'msg_id': self.request.queue.msg_id}

    def after_handle(self) -> 'None':
        self.calls.append(_call_after_handle)

    def get_queue_response(self) -> 'None':
        self.calls.append(_call_get_queue_response)
        self.response.payload = {'queued': True, 'msg_id': self.request.queue.msg_id}

# ################################################################################################################################
# ################################################################################################################################

def _set_up_class(class_:'type[Service]') -> 'None':
    """ Runs the part of deployment that computes a class's attributes - the store itself is not needed for that.
    """
    store = cast_('any_', MagicMock())
    ServiceStore.set_up_class_attributes(store, class_, cast_('any_', None))

# ################################################################################################################################

def _invoke(service_class:'type[_HookService]', **kwargs:'any_') -> 'tuple[any_, _HookService]':
    """ Runs one service through update_handle the way a channel does, returning the response and the instance.
    """
    service = service_class()
    service.calls = []

    server = MagicMock()
    server.json_parser = BasicParser()

    request_ctx:'stranydict' = {}

    response = service.update_handle(
        service.set_response_data, service, {'order_id': 1}, CHANNEL.INVOKE, DATA_FORMAT.DICT, '', server,
        None, MagicMock(), _cid, {}, request_ctx=request_ctx, **kwargs)

    return response, service

# ################################################################################################################################
# ################################################################################################################################

class HookFlagTestCase(unittest.TestCase):
    """ The flag a channel reads instead of calling the hook to find out whether there is one.
    """

    def test_a_class_without_the_override_reads_false(self) -> 'None':
        _set_up_class(_HandleOnlyService)
        self.assertFalse(_HandleOnlyService.has_get_queue_response)

# ################################################################################################################################

    def test_a_class_with_the_override_reads_true(self) -> 'None':
        _set_up_class(_HookService)
        self.assertTrue(_HookService.has_get_queue_response)

# ################################################################################################################################

    def test_after_handle_alone_does_not_count(self) -> 'None':
        _set_up_class(_AfterHandleService)
        self.assertFalse(_AfterHandleService.has_get_queue_response)

# ################################################################################################################################

    def test_the_flag_is_false_before_deployment(self) -> 'None':
        """ A class that deployment has not seen yet is one without the hook, never one with it.
        """
        class _NotDeployed(_TestService):
            def get_queue_response(self) -> 'None':
                pass

        self.assertFalse(_NotDeployed.has_get_queue_response)

# ################################################################################################################################
# ################################################################################################################################

class InvokeModeTestCase(unittest.TestCase):
    """ What an invocation runs in each of its modes.
    """

    def test_the_queue_response_mode_runs_the_hook_alone(self) -> 'None':

        response, service = _invoke(_HookService, invoke_mode=Invoke_Mode.Queue_Response_Only, queue_msg_id=_msg_id)

        self.assertEqual(service.calls, [_call_get_queue_response])
        self.assertEqual(response, {'queued': True, 'msg_id': _msg_id})

# ################################################################################################################################

    def test_the_hook_reads_the_message_id(self) -> 'None':

        _, service = _invoke(_HookService, invoke_mode=Invoke_Mode.Queue_Response_Only, queue_msg_id=_msg_id)

        self.assertEqual(service.request.queue.msg_id, _msg_id)

# ################################################################################################################################

    def test_the_full_mode_runs_the_handlers_and_never_the_hook(self) -> 'None':

        response, service = _invoke(_HookService)

        self.assertEqual(service.calls, [_call_before_handle, _call_handle, _call_after_handle])
        self.assertEqual(response, {'handled': True, 'msg_id': ''})

# ################################################################################################################################

    def test_the_full_mode_is_the_default(self) -> 'None':

        _, explicit = _invoke(_HookService, invoke_mode=Invoke_Mode.Full)
        _, implicit = _invoke(_HookService)

        self.assertEqual(explicit.calls, implicit.calls)

# ################################################################################################################################

    def test_the_message_id_is_empty_in_the_full_mode(self) -> 'None':

        _, service = _invoke(_HookService)

        self.assertEqual(service.request.queue.msg_id, '')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
