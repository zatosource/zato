# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################
# ################################################################################################################################

internal_patterns = [
    'zato.*',
    'pub.zato.*',
    'helpers.*',
]

# ################################################################################################################################
# ################################################################################################################################

class OpenAPI(ZatoCommand):
    """OpenAPI specification generator."""
    opts = [
        {'name':'--include', 'help':'A comma-separated list of patterns to include services by', 'default':'*'},
        {'name':'--with-internal', 'help':'Whether internal services should be included on output', 'action':'store_true'},
        {'name':'--exclude', 'help':'A comma-separated list of patterns to exclude services by',
            'default':','.join(internal_patterns)},
        {'name':'--file', 'help':'Directory to save the output to', 'default':'openapi.yaml'},
        {'name':'--delete-file', 'help':'If given, --dir will be deleted before the output is saved', 'action':'store_true'},
        {'name':'--with-api-invoke', 'help':'If given, OpenAPI spec for --api-invoke-path endpoints will be generated',
         'action':'store_true', 'default':True},
        {'name':'--with-rest-channels', 'help':'If given, OpenAPI spec for individual REST endpoints will be generated',
         'action':'store_true', 'default':True},
        {'name':'--api-invoke-path', 'help':'A comma-separated list of URL paths to invoke API services through'},
        {'name':'--tags', 'help':'A comma-separated list of docstring tags to generate documentation for',
            'default':'public'},
    ]

# ################################################################################################################################
# ################################################################################################################################

    def execute(self, args:'any_') -> 'None':

        # stdlib
        import os

        # Zato
        from zato.common.util.api import get_client_from_server_conf
        from zato.common.util.file_system import fs_safe_now

        client = get_client_from_server_conf(args.path)

        exclude = args.exclude.split(',') or []
        exclude = [elem.strip() for elem in exclude]

        tags = args.tags.split(',')
        tags = [elem.strip() for elem in tags]

        if args.with_internal:
            for item in internal_patterns:
                try:
                    exclude.remove(item)
                except ValueError:
                    pass

        request = {
            'return_internal': args.with_internal,
            'include': args.include,
            'exclude': ','.join(exclude),
            'needs_api_invoke': args.with_api_invoke,
            'needs_rest_channels': args.with_rest_channels,
            'needs_sphinx': True,
            'tags': tags,
        }

        if args.with_api_invoke:
            request['api_invoke_path'] = args.api_invoke_path if args.api_invoke_path else '/zato/api/invoke/{service_name}'

        if not args.file:
            now = fs_safe_now()
            out_file = '{}.{}'.format('apispec', now)
        else:
            out_file = args.file

        out_file = os.path.abspath(out_file)

        if os.path.exists(out_file):
            if args.delete_file:
                self.logger.info('Deleting %s', out_file)
                os.remove(out_file)
            else:
                self.logger.warning('Output file %s already exists and --delete-file was not provided', out_file)
                return

        # We are expecting for this file to be returned by the server
        def_name = 'openapi.yaml'

        # Invoke the server ..
        response = client.invoke('zato.apispec.get-api-spec', request)

        # .. get all specifications ..
        data = response.data['response']['data']

        # .. check all the files the server returned ..
        for file_path, contents in data.items():

            # .. save the OpenAPI definition if it is found ..
            if def_name in file_path:
                f = open_w(out_file)
                f.write(contents)
                f.close()
                self.logger.info('Output saved to %s', out_file)
                break

        # .. otherwise, report an error.
        else:
            self.logger.warning('No OpenAPI definition (%s) found among files received -> %s', def_name, sorted(data))

# ################################################################################################################################
# ################################################################################################################################
