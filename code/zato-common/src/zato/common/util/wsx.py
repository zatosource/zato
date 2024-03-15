# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from logging import getLogger
from tempfile import gettempdir

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.util.file_system import fs_safe_name
from zato.common.util.open_ import open_r, open_rw

# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.server.service import Service

# ################################################################################################################################

logger_zato = getLogger('zato')
logger_wsx = getLogger('zato_web_socket')

# ################################################################################################################################

msg_cleanup_error = 'WSX cleanup error, wcr:`%d`, si:`%s`, pci:`%s`, sk_list:`%s`, h:`%r`, hs:`%r`, hr:`%r`, ofl:`%s`, e:`%s`'

# ################################################################################################################################

_on_disconnected = WEB_SOCKET.HOOK_TYPE.ON_DISCONNECTED

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, textio_

# ################################################################################################################################

def find_wsx_environ(service:'Service', raise_if_not_found:'bool'=True) -> 'stranydict':
    wsx_environ = service.wsgi_environ.get('zato.request_ctx.async_msg', {}).get('environ') or {}
    if not wsx_environ:
        if raise_if_not_found:
            raise Exception('Could not find `[\'zato.request_ctx.async_msg\'][\'environ\']` in WSGI environ `{}`'.format(
                service.wsgi_environ))
    else:
        return wsx_environ

# ################################################################################################################################

def cleanup_wsx_client(wsx_cleanup_required, service_invoker, pub_client_id, sub_keys, hook, hook_service, hook_request,
    opaque_func_list=None):
    """ Cleans up information about a WSX client that has disconnected.
    """
    try:
        # Sometime it will not be needed at all, e.g. when we clean up a half-opened connection that never
        # succesfully authenticated.
        if wsx_cleanup_required:

            # Deletes state from SQL
            service_invoker('zato.channel.web-socket.client.delete-by-pub-id', {
                'pub_client_id': pub_client_id,
            })

            if sub_keys:

                # Deletes across all workers the in-RAM pub/sub state about the client that is disconnecting
                service_invoker('zato.channel.web-socket.client.unregister-ws-sub-key', {
                    'sub_key_list': sub_keys,
                })

                # An opaque list of functions to invoke - each caller may decide what else should be carried out here
                for func in opaque_func_list or []:
                    func()

        # Run the relevant on_disconnected hook, if any is available (even if the session was never opened)

        if hook:
            hook(_on_disconnected, hook_service, **hook_request)

    except Exception as e:
        for logger in logger_zato, logger_wsx:
            logger.info(msg_cleanup_error, wsx_cleanup_required, service_invoker, pub_client_id, sub_keys, hook,
                hook_service, hook_request, opaque_func_list, e)

# ################################################################################################################################

class ContextHandler:

    _file: 'textio_'

    def __init__(self, *, ctx_container_name:'str', is_read_only:'bool') -> 'None':

        # Prepare metadata
        self.ctx_container_name = ctx_container_name
        self.is_read_only = is_read_only
        self.open_func = open_r if self.is_read_only else open_rw
        self.ctx_file_path = '<not-set-yet-ContextHandler-ctx_file_path>'

        # And open the context file now either for reading or r/w
        self.init()

# ################################################################################################################################

    def init(self):

        # Store context in a temporary directory ..
        tmp_dir = gettempdir()

        # .. under the same file as our channel's name ..
        name_safe = fs_safe_name(self.ctx_container_name)
        self.ctx_file_path = os.path.join(tmp_dir, 'zato-' + name_safe + '.txt')

        # .. create and return the file now.
        self._file = self.open_func(self.ctx_file_path)

# ################################################################################################################################

    def store(self, data:'any_') -> 'None':
        if not isinstance(data, dict):
            data = {'data':str(data)}
        data = dumps(data)

        self._file.write(f'{data}\n')
        self._file.flush()

# ################################################################################################################################
# ################################################################################################################################
