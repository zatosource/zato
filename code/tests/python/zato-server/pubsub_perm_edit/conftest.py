# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    publisher_password    = 'test.pub.' + os.urandom(8).hex()
    subscriber_a_password = 'test.suba.' + os.urandom(8).hex()
    subscriber_b_password = 'test.subb.' + os.urandom(8).hex()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'subscriber_a_password': subscriber_a_password,
        'subscriber_b_password': subscriber_b_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_perm_edit import TestConfig
        from zato.common.test.client import AdminClient

        TestConfig.base_url              = f'http://{host}:{server_port}'
        TestConfig.invoke_password       = invoke_password
        TestConfig.publisher_username    = 'test.perm.edit.publisher'
        TestConfig.publisher_password    = publisher_password
        TestConfig.subscriber_a_username = 'test.perm.edit.subscriber.a'
        TestConfig.subscriber_a_password = subscriber_a_password
        TestConfig.subscriber_b_username = 'test.perm.edit.subscriber.b'
        TestConfig.subscriber_b_password = subscriber_b_password
        TestConfig.server_directory      = server_directory
        TestConfig.zato_bin              = zato_bin

        # .. look up sec_base_id values and the permission id ..
        admin = AdminClient(TestConfig.base_url, invoke_password)

        sec_list = admin.invoke('zato.security.get-list', {'cluster_id': 1})

        if isinstance(sec_list, list):
            sec_items = sec_list
        else:
            sec_items = sec_list['zato_security_get_list_response']

        for sec_item in sec_items:
            if sec_item['name'] == 'test.perm.edit.subscriber.a':
                TestConfig.subscriber_a_sec_base_id = sec_item['id']
            elif sec_item['name'] == 'test.perm.edit.subscriber.b':
                TestConfig.subscriber_b_sec_base_id = sec_item['id']

        # .. look up the permission id for subscriber.a's sub permission ..
        perm_list = admin.invoke('zato.pubsub.permission.get-list', {'cluster_id': 1})

        if isinstance(perm_list, list):
            perm_items = perm_list
        else:
            perm_items = perm_list['zato_pubsub_permission_get_list_response']

        for perm_item in perm_items:
            if perm_item['name'] == 'test.perm.edit.subscriber.a' and 'sub=' in perm_item['pattern']:
                TestConfig.permission_id = perm_item['id']
                break

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_perm_edit.conftest',
    server_log_copy_name='server-logs-pubsub-perm-edit.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_perm_edit_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
