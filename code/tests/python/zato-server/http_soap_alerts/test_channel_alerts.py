# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.object_config import alert_type_channels, get_defaults, get_field_names, storage_name
from zato.common.alerting.time_slots import TimeSlotsError
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import dumps
from zato.common.odb.model import Base, Cluster, HTTPSOAP, SecurityBase, Service
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal.http_soap import Create, Edit, Get, GetList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_cluster_id = 1
_service_name = 'orders.get'
_channel_name = 'orders.api'
_outgoing_name = 'crm.api'
_url_path = '/orders'

# The names the settings are stored under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_channels)]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session_factory() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the services touch.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    factory = sessionmaker(bind=engine)

    session = factory()
    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.add(Service(None, _service_name, True, 'orders.OrdersGet', False, cluster))
    session.commit()
    session.close()

    yield factory

    engine.dispose()

# ################################################################################################################################
# ################################################################################################################################

def _full_input(class_:'any_', input_data:'stranydict') -> 'Bunch':
    """ The input as SimpleIO hands it to a service - every declared name is there, the ones the caller
    did not send as None.
    """
    out = Bunch()

    for elem in class_.input:

        if isinstance(elem, str):
            name = elem
        else:
            name = elem.name

        out[name.lstrip('-')] = None

    out.update(input_data)

    return out

# ################################################################################################################################

def _new_service(class_:'any_', session_factory:'any_', input_data:'stranydict') -> 'any_':
    """ A service with its collaborators standing in - the sessions are real, the server is not.
    """
    service:'any_' = object.__new__(class_)

    service.request = SimpleNamespace(input=_full_input(class_, input_data))
    service.response = SimpleNamespace(payload=Bunch())
    service.odb = SimpleNamespace(session=session_factory)
    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test-channel-alerts')
    service.invoke = MagicMock(return_value={})

    server = SimpleNamespace(
        cluster_id=_cluster_id,
        get_config_session=lambda **kwargs: session_factory(),
        encrypt=lambda value: value,
        fs_server_config=SimpleNamespace(misc=SimpleNamespace(return_internal_objects='True')),
    )
    service.server = server

    return service

# ################################################################################################################################

def _base_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of a REST channel sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': _channel_name,
        'url_path': _url_path,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'service': _service_name,
        'service_id': None,
        'security_id': None,
        'security_groups': None,
        'method': '',
        'soap_action': '',
        'soap_version': None,
        'data_format': 'json',
        'host': None,
        'ping_method': None,
        'pool_size': None,
        'merge_url_params_req': True,
        'url_params_pri': None,
        'params_pri': None,
        'timeout': 10,
        'content_type': None,
        'match_slash': True,
        'http_accept': None,
        'is_active': True,
        'is_internal': False,
        'cluster_id': _cluster_id,
        'is_wrapper': False,
        'wrapper_type': None,
        'username': None,
        'password': None,
        'is_audit_log_active': True,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def _create(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one HTTPSOAP object and returns its id.
    """
    service = _new_service(Create, session_factory, _base_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ################################################################################################################################

def _stored_opaque(session_factory:'any_', item_id:'int') -> 'anydict':
    """ The opaque attributes an object has in the database.
    """
    session = session_factory()
    item = session.query(HTTPSOAP).filter(HTTPSOAP.id==item_id).one()
    out = parse_instance_opaque_attr(item)
    session.close()

    return out

# ################################################################################################################################

def _get_list(session_factory:'any_', connection:'str', transport:'str') -> 'list':
    """ What GetList returns for one connection and transport pair.
    """
    input_data = {
        'cluster_id': _cluster_id,
        'connection': connection,
        'transport': transport,
        'paginate': False,
    }
    service = _new_service(GetList, session_factory, input_data)

    session = session_factory()
    out = service.get_data(session)
    session.close()

    return out

# ################################################################################################################################

def _get(session_factory:'any_', item_id:'int') -> 'anydict':
    """ What Get returns for one object.
    """
    service = _new_service(Get, session_factory, {'cluster_id': _cluster_id, 'id': item_id, 'name': None})
    service.request.input.require_any = lambda *names: None
    service.handle()

    out = service.response.payload
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_a_rest_channel_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_max_latency=2500,
            alert_traffic_expected=True,
            alert_silence_window=1800,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_traffic_expected'] is True
        assert opaque['alert_silence_window'] == 1800
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

    def test_a_rest_channel_fills_in_the_defaults_for_what_it_was_not_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_channels)

        for name in get_field_names(alert_type_channels):
            assert storage_name(name) in opaque

        assert opaque['alert_consecutive_failures'] == defaults['consecutive_failures']
        assert opaque['alert_silence_slots'] == '[]'
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_an_outgoing_connection_stores_no_settings(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            name=_outgoing_name,
            connection=CONNECTION.OUTGOING,
            host='https://crm.example.com',
            service=None,
            alert_max_latency=2500,
        )

        opaque = _stored_opaque(session_factory, item_id)

        for name in _storage_names:
            assert name not in opaque

    def test_a_soap_channel_stores_no_settings(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, transport=URL_TYPE.SOAP, soap_action='urn:orders', soap_version='1.1')

        opaque = _stored_opaque(session_factory, item_id)

        for name in _storage_names:
            assert name not in opaque

    def test_bad_silence_slots_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':
        bad_slots = dumps([{'time_from': '09:00', 'is_on': True, 'silence_seconds': 900}])

        with pytest.raises(TimeSlotsError) as ctx:
            _ = _create(session_factory, alert_silence_slots=bad_slots)

        assert 'Time slot 1 has no time_to' in str(ctx.value)

        session = session_factory()
        assert session.query(HTTPSOAP).count() == 0
        session.close()

    def test_good_silence_slots_are_stored_as_the_string_they_arrived_as(self, session_factory:'any_') -> 'None':
        slots = dumps([{'time_from': '09:00', 'time_to': '17:00', 'is_on': True, 'silence_seconds': 900}])

        item_id = _create(session_factory, alert_silence_slots=slots)

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_silence_slots'] == slots

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500, alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _base_input(id=item_id, data_format='xml'))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        service = _new_service(Edit, session_factory, _base_input(id=item_id, alert_max_latency=750, alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 750
        assert opaque['alert_is_active'] is False

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        service = _new_service(Edit, session_factory, _base_input(id=item_id))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]
        assert message['alert_max_latency'] == 2500

    def test_a_get_then_edit_round_trip_keeps_the_settings(self, session_factory:'any_') -> 'None':
        slots = dumps([{'time_from': '22:00', 'time_to': '06:00', 'is_on': False, 'silence_seconds': 3600}])
        item_id = _create(session_factory, alert_max_latency=2500, alert_silence_slots=slots, alert_llm_connection='ops.llm')

        # What the listing's inline edit does - read the object, change one field, save it whole
        item_dict = _get(session_factory, item_id)
        item_dict['id'] = item_id
        item_dict['cluster_id'] = _cluster_id
        item_dict['service'] = item_dict['service_name']
        item_dict['is_active'] = False
        item_dict['security_groups'] = None

        service = _new_service(Edit, session_factory, item_dict)
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_silence_slots'] == slots
        assert opaque['alert_llm_connection'] == 'ops.llm'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_a_rest_channel_lists_every_setting_with_the_defaults_filled_in(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_max_latency=2500)

        # A channel stored before a setting existed has nothing under that name
        session = session_factory()
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name==_channel_name).one()
        opaque = parse_instance_opaque_attr(item)
        del opaque['alert_client_errors']
        item.opaque1 = dumps(opaque)
        session.commit()
        session.close()

        rows = _get_list(session_factory, CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP)
        row = rows[0]

        defaults = get_defaults(alert_type_channels)

        for name in _storage_names:
            assert name in row

        assert row['alert_max_latency'] == 2500
        assert row['alert_client_errors'] == defaults['client_errors']

    def test_an_outgoing_connection_lists_no_settings(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory,
            name=_outgoing_name,
            connection=CONNECTION.OUTGOING,
            host='https://crm.example.com',
            service=None,
        )

        rows = _get_list(session_factory, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP)
        row = rows[0]

        for name in _storage_names:
            assert name not in row

# ################################################################################################################################
# ################################################################################################################################
