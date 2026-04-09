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
    ]

# ################################################################################################################################

    def execute(self, args):

        # stdlib
        from json import loads as json_loads

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        client = get_client_from_server_conf(args.path, stdin_data=self.stdin_data)

        payload = args.payload or '{}'
        if isinstance(payload, str):
            try:
                payload = json_loads(payload)
            except Exception:
                payload = {'payload': payload}

        response = client.invoke(args.name, payload)

        if response.ok:
            self.logger.info(response.data or '(None)')
        else:
            self.logger.error(response.details)

        if args.verbose:
            self.logger.debug('inner.text:[{}]'.format(response.inner.text))

# ################################################################################################################################
