# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand
from zato.client import CID_NO_CLIP, DEFAULT_MAX_CID_REPR, DEFAULT_MAX_RESPONSE_REPR
from zato.common.api import BROKER, ZATO_INFO_FILE
from zato.common.const import ServiceConst

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
        {'name':'--channel', 'help':'Channel the service will be invoked through', 'default':'invoke'},
        {'name':'--data-format', 'help':"Payload's data format", 'default': 'json'},
        {'name':'--transport', 'help':'Transport to invoke the service over'},
        {'name':'--url-path', 'help':'URL path zato.service.invoke is exposed on',
            'default':ServiceConst.API_Admin_Invoke_Url_Path},
        {'name':'--max-cid-repr',
         'help':'How many characters of each end of a CID to print out in verbose mode, defaults to {}, use {} to print the whole of it'.format(
            DEFAULT_MAX_CID_REPR, CID_NO_CLIP), 'default':DEFAULT_MAX_CID_REPR},
        {'name':'--max-response-repr', 'help':'How many characters of a response to print out in verbose mode, defaults to {}'.format(
            DEFAULT_MAX_RESPONSE_REPR), 'default':DEFAULT_MAX_RESPONSE_REPR},
        {'name':'--is-async', 'help':'If given, the service will be invoked asynchronously', 'action':'store_true'},
        {'name':'--expiration', 'help':'In async mode, after how many seconds the message should expire, defaults to {} seconds'.format(
            BROKER.DEFAULT_EXPIRATION), 'default':BROKER.DEFAULT_EXPIRATION},
    ]

# ################################################################################################################################

    def execute(self, args):

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.util.api import get_client_from_server_conf

        client = get_client_from_server_conf(args.path, stdin_data=self.stdin_data)

        headers = {}
        if args.headers:
            for pair in args.headers.strip().split(';'):
                k, v = pair.strip().split('=', 1)
                headers[k] = v

        # Prevents attempts to convert/escape XML into JSON
        to_json = True if args.data_format == DATA_FORMAT.JSON else False

        func = client.invoke_async if args.is_async else client.invoke
        response = func(args.name, args.payload, headers, args.channel, args.data_format, args.transport, to_json=to_json)

        if response.ok:
            self.logger.info(response.data or '(None)')
        else:
            self.logger.error(response.details)

        if args.verbose:
            self.logger.debug('inner.text:[{}]'.format(response.inner.text))
            self.logger.debug('response:[{}]'.format(response))

# ################################################################################################################################
