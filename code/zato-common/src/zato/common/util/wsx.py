# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import WEB_SOCKET

# ################################################################################################################################

_on_disconnected = WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED

# ################################################################################################################################

def find_wsx_environ(service, raise_if_not_found=True):
    wsx_environ = service.wsgi_environ.get('zato.request_ctx.async_msg', {}).get('environ')
    if not wsx_environ:
        if raise_if_not_found:
            raise Exception('Could not find `[\'zato.request_ctx.async_msg\'][\'environ\']` in WSGI environ `{}`'.format(
                service.wsgi_environ))
    else:
        return wsx_environ

# ################################################################################################################################

def cleanup_wsx_client(service_invoker, sub_keys, hook, hook_service, hook_request, _on_disconnected=_on_disconnected):
    """ Cleans up information about a WSX client that has disconnected.
    """
    '''
    if self.has_session_opened:

        # Deletes state from SQL
        self.invoke_service('zato.channel.web-socket.client.delete-by-pub-id', {
            'pub_client_id': self.pub_client_id,
        })

        if self.pubsub_tool.sub_keys:

            # Deletes across all workers the in-RAM pub/sub state about the client that is disconnecting
            self.invoke_service('zato.channel.web-socket.client.unregister-ws-sub-key', {
                'sub_key_list': list(self.pubsub_tool.sub_keys),
            })

            # Clears out our own delivery tasks
            self.pubsub_tool.remove_all_sub_keys()

    # Run the relevant on_connected hook, if any is available (even if the session was never opened)
    hook = self.get_on_disconnected_hook()
    if hook:
        hook(WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED, self.config.hook_service, **self._get_hook_request())
        '''

# ################################################################################################################################
