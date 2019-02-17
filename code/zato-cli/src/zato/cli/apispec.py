# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from shutil import rmtree

# Zato
from zato.cli import ZatoCommand
from zato.common.util import fs_safe_now, get_client_from_server_conf

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2


# ################################################################################################################################

internal_patterns = [
    'zato.*',
    'pub.zato.*',
    'helpers.*',
]

# ################################################################################################################################

class APISpec(ZatoCommand):
    """API specifications generator."""
    opts = [
        {'name':'--include', 'help':'A comma-separated list of patterns to include services by', 'default':'*'},
        {'name':'--with-internal', 'help':'Whether internal services should be included on output', 'action':'store_true'},
        {'name':'--exclude', 'help':'A comma-separated list of patterns to exclude services by',
            'default':','.join(internal_patterns)},
        {'name':'--dir', 'help':'Directory to save the output to', 'default':''},
        {'name':'--delete-dir', 'help':'If given, --dir will be deleted before the output is saved', 'action':'store_true'},
        {'name':'--with-api-invoke', 'help':'If given, OpenAPI spec for --api-invoke-path endpoints will be generated',
         'action':'store_true'},
        {'name':'--with-rest-channels', 'help':'If given, OpenAPI spec for individual REST endpoints will be generated',
         'action':'store_true'},
        {'name':'--api-invoke-path', 'help':'A comma-separated list of URL paths to invoke API services through'},
    ]

# ################################################################################################################################

    def execute(self, args):
        client = get_client_from_server_conf(args.path)

        exclude = args.exclude.split(',') or []
        exclude = [elem.strip() for elem in exclude]

        if args.with_internal:
            for item in internal_patterns:
                try:
                    exclude.remove(item)
                except ValueError:
                    pass

        if args.with_api_invoke:
            api_invoke_path = args.api_invoke_path if args.api_invoke_path else '/zato/api/invoke/{service_name}'

        request = {
            'return_internal': args.with_internal,
            'include': args.include,
            'exclude': ','.join(exclude),
            'needs_api_invoke': args.with_api_invoke,
            'needs_rest_channels': args.with_rest_channels,
            'api_invoke_path': api_invoke_path
        }

        if not args.dir:
            now = fs_safe_now()
            out_dir = '{}.{}'.format('apispec', now)
        else:
            out_dir = args.dir

        out_dir = os.path.abspath(out_dir)

        if os.path.exists(out_dir):
            if args.delete_dir:
                self.logger.info('Deleting %s', out_dir)
                rmtree(out_dir)
            else:
                self.logger.warn('Output directory %s already exists and --delete-dir was not provided', out_dir)
                return

        os.mkdir(out_dir)

        response = client.invoke('zato.apispec.get-api-spec', request)
        data = response.data['response']['data']

        for file_path, contents in data.items():
            full_file_path = os.path.join(out_dir, file_path)
            file_dir = os.path.abspath(os.path.dirname(full_file_path))
            try:
                os.makedirs(file_dir)
            except OSError:
                pass # Must have been already created
            finally:
                if contents:
                    f = open(full_file_path, 'w')
                    f.write(contents)
                    f.close()

        self.logger.info('Output saved to %s', out_dir)
        self.logger.info('To build the documentation, run:\ncd %s\nmake html', out_dir)
