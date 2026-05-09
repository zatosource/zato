# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand
from zato.common.api import ZATO_INFO_FILE

# ################################################################################################################################

class Invoke(ZatoCommand):
    """ Invokes a service by its name
    """
    file_needed = ZATO_INFO_FILE

    opts = [
        {'name':'path', 'help':'Path in the file-system to a server the service is deployed on'},
        {'name':'name', 'help':'Name of the service to invoke'},
        {'name':'--payload', 'help':'Payload to invoke the service with'},
        {'name':'--headers',
         'help':'Additional HTTP headers the service invoker will receive in format of header-name=header-value; header2-name=header2-value'},
        {'name':'--is-async', 'help':'If given, the service will be invoked asynchronously', 'action':'store_true'},
    ]

# ################################################################################################################################

    def execute(self, args):

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        client = get_client_from_server_conf(args.path, stdin_data=self.stdin_data)

        headers = {}
        if args.headers:
            for pair in args.headers.strip().split(';'):
                k, v = pair.strip().split('=', 1)
                headers[k] = v

        func = client.invoke_async if args.is_async else client.invoke
        response = func(args.name, args.payload, headers)

        if response.ok:
            self.logger.info(response.data or '(None)')
        else:
            self.logger.error(response.details)

        if args.verbose:
            self.logger.debug('inner.text:[{}]'.format(response.inner.text))
            self.logger.debug('response:[{}]'.format(response))

# ################################################################################################################################
