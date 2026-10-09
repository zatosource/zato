# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# Django
import django
from django.conf import settings

# Django is configured before the views are imported - without a database and without templates, as each view
# is called directly and a list page's response is read without rendering. The application registry is set up
# for the list pages' forms.
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

        # The Redis in which the channels record received events
        redis_port = find_free_port()
        redis_process = start_redis(redis_port)
        parts.add('redis-server', redis_process.kill)

        directory = tempfile.mkdtemp(prefix='zato_sms_views_')
        zato = ZatoEnvironment(directory, password_prefix='test.sms.views')
        parts.add('Zato', zato.stop)
        zato.create(redis_port=redis_port)

        # The server's address, from which the server and the Dashboard build each channel's webhook URL
        server_address = f'http://{Host}:{zato.server_port}'
        os.environ[Server_Address_Env_Key] = server_address

        zato.start({Server_Address_Env_Key: server_address})

        suite = DashboardSuite(simulators, zato)

    # An incomplete setup stops what it started
    except BaseException:
        tear_down(parts)
        raise

    yield suite

    tear_down(parts)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_connections(dashboard:'DashboardSuite') -> 'iterator_':
    """ Each test starts with cleared simulators and ends with its SMS connections removed from the server.
    """
    dashboard.simulators.reset()

    yield

    dashboard.delete_connections(GENERIC.CONNECTION.TYPE.CHANNEL_SMS, 'test.views.')
    dashboard.delete_connections(GENERIC.CONNECTION.TYPE.OUTCONN_SMS, 'test.views.')

# ################################################################################################################################
# ################################################################################################################################
