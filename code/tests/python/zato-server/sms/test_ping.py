# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import GENERIC, SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import SMSSuite

# ################################################################################################################################
# ################################################################################################################################

Providers = SMS.ProviderList

# The service the Dashboard's Ping button invokes
Generic_Ping_Service = 'zato.generic.connection.ping'

# The request path of each provider's ping
Ping_Path = {
    SMS.Provider.Twilio: '/2010-04-01/Accounts/',
    SMS.Provider.Vonage: '/v2/reports/records',
    SMS.Provider.Infobip: '/account/1/balance',
    SMS.Provider.Africas_Talking: '/version1/user',
}

# ################################################################################################################################
# ################################################################################################################################

def _connection_id(sms:'SMSSuite', provider:'str') -> 'int':
    """ The ID of a provider's outgoing connection, as the Dashboard lists it.
    """
    items, _ = sms.client.get_list('zato.generic.connection.get-list', cluster_id=1, type_=GENERIC.CONNECTION.TYPE.OUTCONN_SMS)

    for item in items:
        if item['name'] == sms.outgoing(provider):
            out = item['id']
            break
    else:
        raise AssertionError(f'No connection `{sms.outgoing(provider)}` among {items}')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPing:

    @pytest.mark.parametrize('provider', Providers)
    def test_a_ping_is_an_authenticated_read_and_sends_nothing(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)

        response = sms.ping(provider)
        assert response['is_ok'] is True, response

        assert simulator.sends == []
        assert simulator.rejections == []

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_a_ping_with_a_wrong_credential_fails(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        password = simulator.password
        simulator.password = password + '-changed'

        try:
            response = sms.ping(provider)
        finally:
            simulator.password = password

        assert response['is_ok'] is False, response
        assert len(simulator.rejections) == 1, simulator.rejections
        assert simulator.rejections[0].path.startswith(Ping_Path[provider]), simulator.rejections

# ################################################################################################################################

    @pytest.mark.parametrize('provider', Providers)
    def test_the_dashboard_ping_service_reaches_the_provider(self, sms:'SMSSuite', provider:'str') -> 'None':

        simulator = sms.simulator(provider)
        conn_id = _connection_id(sms, provider)

        response = sms.client.invoke(Generic_Ping_Service, {'id': conn_id})

        assert response['is_success'] is True, response
        assert simulator.sends == []

# ################################################################################################################################
# ################################################################################################################################
