# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import intnone
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class Wait(ZatoCommand):

    opts = [
        {'name':'--path', 'help':'Path to a local Zato server', 'default':''},
        {'name':'--address', 'help':'Address of a remote Zato server', 'default':''},
        {'name':'--url-path', 'help':'URL path of an endpoint to invoke', 'default':'/zato/ping'},
        {'name':'--timeout', 'help':'How many seconds to wait for the server', 'default':'60'},
        {'name':'--interval', 'help':'How often to check if the server is up, in seconds', 'default':'0.1'},
        {'name':'--silent', 'help':'Whether to log details of connection attempts', 'action':'store_true'},
    ]

    def execute(self, args:'Namespace', needs_sys_exit:'bool'=True) -> 'intnone':

        # stdlib
        import sys

        # Zato
        from zato.common.util.api import get_client_from_server_conf
        from zato.common.util.tcp import wait_for_zato

        # We need to have a local or remote server on input ..
        if not (args.path or args.address):
            self.logger.warning('Exactly one of --path or --address is required (#1)')
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # .. but we cannot have both of them at the same time.
        if args.path and args.address:
            self.logger.warning('Exactly one of --path or --address is required (#2)')
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # We need to look up the server's address through its client ..
        if args.path:
            client = get_client_from_server_conf(args.path, False)
            address = client.address # type: str

        # .. unless we are given it explicitly.
        else:
            address = args.address # type: str

        # Check whether we should log progress
        silent = getattr(args, 'silent', False)
        if silent:
            needs_log = False
        else:
            needs_log = True

        # We can now wait for the server to respond
        is_success = wait_for_zato(address, args.url_path, int(args.timeout), float(args.interval), needs_log=needs_log)

        if not is_success:
            if needs_sys_exit:
                sys.exit(self.SYS_ERROR.SERVER_TIMEOUT)
            else:
                raise Exception('No response from `{}{}` after {}s'.format(address, args.url_path, args.timeout))
        else:
            return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']
    args.address = ''
    args.url_path = ''
    args.timeout = 60
    args.interval = 0.1

    command = Wait(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
