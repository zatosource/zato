# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.cli import ZatoCommand
from zato.common.util import fs_safe_now, get_client_from_server_conf

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

class APISpec(ZatoCommand):
    """API specifications generator."""

    opts = [
        {'name':'--sphinx', 'help':'Whether Sphinx docs should be generated'},
        {'name':'--with-wsdl', 'help':'Whether Sphinx docs should contain WSDL spec'},
        {'name':'--with-openapi', 'help':'Whether Sphinx docs should contain OpenAPI spec'},
        {'name':'--with-raml', 'help':'Whether Sphinx docs should contain RAML spec'},
        {'name':'--wsdl', 'help':'Whether WSDL spec should be generated'},
        {'name':'--openapi', 'help':'Whether OpenAPI spec should be generated'},
        {'name':'--raml', 'help':'Whether RAML spec should be generated'},
    ]

# ################################################################################################################################

    def execute(self, args):
        client = get_client_from_server_conf(args.path)
        request = {
            'return_internal': False
        }

        response = client.invoke('zato.apispec.get-api-spec', request)
        data = response.data['response']['data']

        now = fs_safe_now()
        out_dir = '{}.{}'.format('apispec', now)
        out_dir = os.path.abspath(out_dir)
        os.mkdir(out_dir)

        for file_path, contents in data.items():
            full_file_path = os.path.join(out_dir, file_path)
            file_dir = os.path.abspath(os.path.dirname(full_file_path))
            try:
                os.makedirs(file_dir)
            except OSError:
                pass # Must have been already created
            finally:
                f = open(full_file_path, 'w')
                f.write(contents)
                f.close()

        print()
        print(now, data.keys())
        self.logger.info('Output saved to %s', out_dir)
        print()
