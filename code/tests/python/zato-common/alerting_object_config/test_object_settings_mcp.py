# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from datetime import datetime

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.object_config import alert_type_channels, alert_type_llm, alert_type_mcp, alert_type_rest, \
    get_defaults, to_storage
from zato.common.alerting.object_settings import get_muted_rule_names, get_silence_expected_names, load_object_settings
from zato.common.api import GENERIC
from zato.common.json_internal import dumps
from zato.common.odb.model import Base, Cluster, GenericConn, HTTPSOAP
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    sessiongen = Iterator[SASession]
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The moment the muting resolves against - ten in the morning UTC
_now = datetime(2026, 9, 12, 10, 0, 0)

# The cluster the gateway belongs to
_cluster_id = 1

# The gateway the tests store and a channel listed next to it
_mcp_name = 'orders.gateway'
_rest_channel_name = 'orders.api'

# The gateway's own thresholds - each off its default
_own_invalid_calls = 2
_own_repeat_calls = 30
_own_volume_budget = 2000000000
_own_max_tools = 30

# The rule a gateway that does not expect traffic keeps quiet
_silence_rule_name = 'Gateway_Silent'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _session() -> 'sessiongen':
    """ An in-memory SQLite database with the tables the settings are read from and one cluster.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConn.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.add(Cluster(_cluster_id, 'test-cluster', '', 'sqlite'))
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

def _add_gateway(session:'SASession', opaque:'stranydict') -> 'None':
    """ Stores one MCP gateway with the given opaque attributes.
    """
    item = cast_('any_', GenericConn())
    item.name = _mcp_name
    item.type_ = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
    item.is_active = True
    item.is_internal = False
    item.is_channel = True
    item.is_outconn = False
    item.cluster_id = _cluster_id
    item.opaque1 = dumps(opaque)

    session.add(item)
    session.commit()

# ################################################################################################################################
# ################################################################################################################################

class TestLoadGatewaySettings:

    def test_an_mcp_gateway_loads_under_mcp_with_its_own_thresholds(self) -> 'None':
        stored = to_storage(alert_type_mcp, {
            'invalid_calls': _own_invalid_calls,
            'repeat_calls': _own_repeat_calls,
            'volume_budget': _own_volume_budget,
            'max_tools': _own_max_tools,
        })

        with _session() as session:
            _add_gateway(session, stored)
            settings = load_object_settings(session, _cluster_id)

        by_object = settings[alert_type_mcp]

        assert list(by_object) == [_mcp_name]
        assert by_object[_mcp_name]['invalid_calls'] == _own_invalid_calls
        assert by_object[_mcp_name]['repeat_calls'] == _own_repeat_calls
        assert by_object[_mcp_name]['volume_budget'] == _own_volume_budget
        assert by_object[_mcp_name]['max_tools'] == _own_max_tools

        # What was not stored is still at its default, and no other type sees the row
        assert by_object[_mcp_name]['rejections'] == get_defaults(alert_type_mcp)['rejections']
        assert by_object[_mcp_name]['warning_latency'] == get_defaults(alert_type_mcp)['warning_latency']
        assert by_object[_mcp_name]['traffic_expected'] is False
        assert settings[alert_type_llm] == {}
        assert settings[alert_type_rest] == {}

# ################################################################################################################################

    def test_a_gateway_with_nothing_stored_reads_at_the_defaults(self) -> 'None':
        with _session() as session:
            _add_gateway(session, {})
            settings = load_object_settings(session, _cluster_id)

        assert settings[alert_type_mcp] == {_mcp_name: get_defaults(alert_type_mcp)}

# ################################################################################################################################
# ################################################################################################################################

class TestGatewaySilence:

    def test_a_gateway_expecting_traffic_is_muted_and_unmuted_by_its_own_switch(self) -> 'None':
        values = get_defaults(alert_type_mcp)

        # A gateway that does not say it expects traffic has its silence rule muted, and that rule alone
        assert values['traffic_expected'] is False
        assert get_muted_rule_names(alert_type_mcp, values, _now) == [_silence_rule_name]

        values['traffic_expected'] = True
        assert get_muted_rule_names(alert_type_mcp, values, _now) == []

# ################################################################################################################################

    def test_a_gateway_expecting_traffic_is_listed_next_to_the_channels_expecting_it(self) -> 'None':
        expecting = get_defaults(alert_type_mcp)
        expecting['traffic_expected'] = True

        object_settings = {
            alert_type_mcp: {_mcp_name: expecting},
            alert_type_channels: {_rest_channel_name: get_defaults(alert_type_channels)},
        }

        # The channel keeps its default of not expecting traffic, so the gateway is the one name listed
        assert get_silence_expected_names(object_settings, _now) == {_mcp_name}

# ################################################################################################################################
# ################################################################################################################################
