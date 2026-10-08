# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# The test doubles live next to the tests and are imported flat, the live helpers under zato-common.
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# Django
import django
from django.conf import settings

# The views build responses and read the request the way Django hands it over, so Django is configured
# before anything imports them - with nothing behind it, no database and no templates, because a view
# is called here directly rather than through a URL and a list page's response is read without rendering it.
# The list pages build their forms, which is what the application registry is set up for, without translations.
if not settings.configured:
    settings.configure(
        DEBUG=False,
        DATABASES={},
        INSTALLED_APPS=[],
        USE_TZ=True,
        USE_I18N=False,
        DEFAULT_CHARSET='utf-8',
    )
    django.setup()

# pytest
import pytest

# Zato
from zato.common.api import GENERIC
from zato.common.util.mcp_oauth import Server_Address_Env_Key

# Live environment
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import find_free_port, Host, ZatoEnvironment

# Live SMS
from live_sms.redis_server import start_redis
from live_sms.suite import SimulatorSuite

# Test support
from _suite import DashboardSuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import iterator_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def dashboard() -> 'iterator_':
    """ The simulators, a Redis and one server with no SMS connections on it, for the whole session.
    """
    parts = Parts()

    try:
        simulators = SimulatorSuite()
        simulators.start()
        parts.add('SMS simulators', simulators.stop)

        # The Redis the channels remember seen events in
        redis_port = find_free_port()
        redis_process = start_redis(redis_port)
        parts.add('redis-server', redis_process.kill)

        directory = tempfile.mkdtemp(prefix='zato_sms_views_')
        zato = ZatoEnvironment(directory, password_prefix='test.sms.views')
        parts.add('Zato', zato.stop)
        zato.create(redis_port=redis_port)

        # The server and the Dashboard's list page build each channel's webhook URL from this address
        server_address = f'http://{Host}:{zato.server_port}'
        os.environ[Server_Address_Env_Key] = server_address

        zato.start({Server_Address_Env_Key: server_address})

        suite = DashboardSuite(simulators, zato)

    # A setup cut short tears down what it started
    except BaseException:
        tear_down(parts)
        raise

    yield suite

    tear_down(parts)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_connections(dashboard:'DashboardSuite') -> 'iterator_':
    """ Every test starts with simulators that recorded nothing and leaves no SMS connections of the tests on the server.
    """
    dashboard.simulators.reset()

    yield

    dashboard.delete_connections(GENERIC.CONNECTION.TYPE.CHANNEL_SMS, 'test.views.')
    dashboard.delete_connections(GENERIC.CONNECTION.TYPE.OUTCONN_SMS, 'test.views.')

# ################################################################################################################################
# ################################################################################################################################
