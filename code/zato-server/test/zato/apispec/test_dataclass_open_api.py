# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import main

# Zato
from zato.common.test.apispec_ import run_common_apispec_assertions, service_name, sio_config
from zato.common.api import APISPEC, URL_TYPE
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase
from zato.server.apispec.spec.core import Generator
from zato.server.apispec.spec.openapi import OpenAPIGenerator
from zato.server.service.internal.helpers import MyDataclassService

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################

class _MatchTestCompiled:
    group_names = ['phone_number']

# ################################################################################################################################
# ################################################################################################################################

class DataClassOpenAPITestCase(BaseSIOTestCase):

    def test_dataclass_generate_open_api(self):

        MyClass = deepcopy(MyDataclassService)
        DataClassSimpleIO.attach_sio(None, self.get_server_config(), MyClass)

        service_store_services = {
            'my.impl.name': {
                'name': service_name,
                'service_class': MyClass,
            }
        }
        include = ['*']
        exclude = []
        query   = ''
        tags    = ['public']

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        initial_info = generator.get_info() # type: any_

        channel_data = [{
            'service_name': service_name,
            'transport':    URL_TYPE.PLAIN_HTTP,
            'url_path':     '/test/{phone_number}',
            'match_target_compiled': _MatchTestCompiled()
        }]

        needs_api_invoke = True
        needs_rest_channels = True
        api_invoke_path = APISPEC.GENERIC_INVOKE_PATH

        open_api_generator = OpenAPIGenerator(initial_info, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)

        result = open_api_generator.generate()
        run_common_apispec_assertions(self, result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
