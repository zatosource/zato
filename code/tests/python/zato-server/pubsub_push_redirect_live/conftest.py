# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# The support module of the suite is in its own directory, and the definition of the suite, the test endpoint
# and the test services are shared with other suites
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, '..', '..', 'zato-common', 'lib'))

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture # noqa: E402

# Test support
from http_endpoint.addresses import get_non_loopback_address # noqa: E402
from http_endpoint.endpoint import Host, TestEndpoint # noqa: E402
from pubsub_rest.definition import Definition # noqa: E402
from pubsub_rest.server import Services_Path # noqa: E402
from redirect_live_support import All_Scenarios, get_name, get_source_base, get_source_path, LiveConfig, \
    Loopback_First, Loopback_Second, Remote_First # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The name of the copy of the server log that remains after the suite
_server_log_copy_name = 'server-logs-pubsub-push-redirect.txt'

# ################################################################################################################################
# ################################################################################################################################

def _start_endpoint(state:'SessionState', data_directory:'str', key:'str', host:'str') -> 'None':
    """ Starts an endpoint that the server pushes to, which the fixture stops together with the server.
    """
    certificates_directory = os.path.join(data_directory, 'endpoints', key)

    endpoint = TestEndpoint(certificates_directory, host)
    endpoint.start()

    state.receivers.append(endpoint)
    LiveConfig.endpoints[key] = endpoint

# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    data_directory = tempfile.mkdtemp(prefix='zato_pubsub_push_redirect_data_')
    state.test_data_directory = data_directory

    # Two endpoints on the loopback address and one on the address outside of it ..
    non_loopback_address = get_non_loopback_address()

    _start_endpoint(state, data_directory, Loopback_First, Host)
    _start_endpoint(state, data_directory, Loopback_Second, Host)
    _start_endpoint(state, data_directory, Remote_First, non_loopback_address)

    endpoint_count = len(LiveConfig.endpoints)
    logger.info('Endpoints started: %d', endpoint_count)

    # .. each scenario has a subscriber of its own, subscribed to a topic of its own ..
    definition = Definition()

    for scenario in All_Scenarios:
        name = get_name(scenario)
        source_base = get_source_base(scenario)
        source_path = get_source_path(scenario)

        _ = definition.add_push_subscriber_at(name, [name], source_base, source_path)

    # .. and the server trusts the CA of the TLS listeners of the first endpoint.
    first = LiveConfig.endpoints[Loopback_First]

    server_env:'strstrdict' = {
        'REQUESTS_CA_BUNDLE': first.certificates.ca_path,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        LiveConfig.base_url        = f'http://{host}:{server_port}'
        LiveConfig.invoke_password = invoke_password
        LiveConfig.server_log_path = os.path.join(server_directory, 'logs', 'server.log')

    enmasse_yaml = definition.to_yaml()

    out:'anydict' = {
        'placeholders': {},
        'enmasse_yaml': enmasse_yaml,
        'populate_callback': _populate,
        'server_env': server_env,
        'hot_deploy_sources': [Services_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_push_redirect_live.conftest',
    server_log_copy_name=_server_log_copy_name,
    template_path='',
    quickstart_prefix='zato_pubsub_push_redirect_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
