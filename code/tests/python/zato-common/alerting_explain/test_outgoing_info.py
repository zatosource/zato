# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object lines of an outgoing REST or SOAP connection - the transport it speaks, the SOAP action and version a
# SOAP one calls with, how often its health check runs or that it has none, read from the row of the transport
# the alert's source names, be it the connection's own traffic or its check.

# stdlib
import json

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.outgoing_info import describe_outgoing_http
from zato.common.api import CONNECTION, HTTP_SOAP, URL_TYPE
from zato.common.audit_log.api import AuditSource
from zato.common.odb.model import Base, Cluster, HTTPSOAP, SecurityBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_cluster_id = 1
_conn_name = 'crm.api'
_conn_host = 'https://crm.example.com'
_conn_url_path = '/orders'
_soap_action = 'urn:orders'
_soap_version = '1.1'

_health_check = HTTP_SOAP.HealthCheck

# ################################################################################################################################
# ################################################################################################################################

def _new_session() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the describer reads.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    out = sessionmaker(bind=engine)

    session = out()
    session.add(Cluster(_cluster_id, 'test-cluster', '', 'sqlite'))
    session.commit()
    session.close()

    return out

# ################################################################################################################################

def _seed_connection(session_maker:'any_', transport:'str', opaque:'anydict', *, url_path:'str'=_conn_url_path) -> 'None':
    """ One outgoing connection of the transport, with the given opaque attributes.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    row = HTTPSOAP()
    row.name = _conn_name
    row.is_active = True
    row.is_internal = False
    row.connection = CONNECTION.OUTGOING
    row.transport = transport
    row.host = _conn_host
    row.url_path = url_path
    row.method = 'POST'
    row.ping_method = 'HEAD'
    row.timeout = 10
    row.pool_size = 20
    row.data_format = 'xml' if transport == URL_TYPE.SOAP else 'json'
    row.soap_action = _soap_action if transport == URL_TYPE.SOAP else ''
    row.soap_version = _soap_version if transport == URL_TYPE.SOAP else None
    row.security = None
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _describe(session_maker:'any_', source:'str') -> 'anylist':
    """ The label and value pairs of the connection the source names.
    """
    session = session_maker()
    out = describe_outgoing_http(session, _cluster_id, source, _conn_name)
    session.close()

    assert out is not None
    return out

# ################################################################################################################################

def _labels(lines:'anylist') -> 'list':
    return [label for label, _ in lines]

# ################################################################################################################################

def _value(lines:'anylist', wanted:'str') -> 'any_':
    for label, value in lines:
        if label == wanted:
            return value
    raise KeyError(wanted)

# ################################################################################################################################
# ################################################################################################################################

class TestTransportLines:

    def test_a_rest_connection_says_rest_and_carries_no_soap_lines(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {})

        lines = _describe(session_maker, AuditSource.REST_Outgoing)
        labels = _labels(lines)

        assert _value(lines, 'Transport') == 'REST'
        assert 'SOAP action' not in labels
        assert 'SOAP version' not in labels

        # The transport comes right after the name
        assert labels[:2] == ['Name', 'Transport']

# ################################################################################################################################

    def test_a_soap_connection_says_soap_with_its_action_and_version(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.SOAP, {})

        lines = _describe(session_maker, AuditSource.SOAP_Outgoing)
        labels = _labels(lines)

        assert _value(lines, 'Transport') == 'SOAP'
        assert _value(lines, 'SOAP action') == _soap_action
        assert _value(lines, 'SOAP version') == _soap_version

        # The SOAP lines sit between the address and the method
        assert labels.index('Address') < labels.index('SOAP action') < labels.index('SOAP version') < labels.index('Method')

# ################################################################################################################################

    def test_each_transport_is_read_from_its_own_row(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {}, url_path='/rest')
        _seed_connection(session_maker, URL_TYPE.SOAP, {}, url_path='/soap')

        rest_lines = _describe(session_maker, AuditSource.REST_Outgoing)
        soap_lines = _describe(session_maker, AuditSource.SOAP_Outgoing)

        assert _value(rest_lines, 'Address') == f'{_conn_host}/rest'
        assert _value(soap_lines, 'Address') == f'{_conn_host}/soap'

# ################################################################################################################################

    def test_a_health_check_source_reads_the_row_of_its_transport(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.SOAP, {})

        lines = _describe(session_maker, AuditSource.SOAP_Outgoing_Health)

        assert _value(lines, 'Transport') == 'SOAP'
        assert _value(lines, 'SOAP action') == _soap_action

        # There is no REST row of that name, so the REST check has nothing to describe
        session = session_maker()
        assert describe_outgoing_http(session, _cluster_id, AuditSource.REST_Outgoing_Health, _conn_name) is None
        session.close()

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheckLine:

    def test_a_connection_without_a_check_says_off(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {})

        lines = _describe(session_maker, AuditSource.REST_Outgoing)
        assert _value(lines, 'Health check') == 'off'

# ################################################################################################################################

    def test_a_run_every_of_zero_says_off_too(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {
            _health_check.Field_Run_Every: 0,
            _health_check.Field_Run_Unit: 'minutes',
        })

        lines = _describe(session_maker, AuditSource.REST_Outgoing)
        assert _value(lines, 'Health check') == 'off'

# ################################################################################################################################

    def test_a_check_reads_how_often_it_runs_in_the_singular_or_plural(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.SOAP, {
            _health_check.Field_Run_Every: 1,
            _health_check.Field_Run_Unit: 'seconds',
        })

        lines = _describe(session_maker, AuditSource.SOAP_Outgoing_Health)
        assert _value(lines, 'Health check') == 'every 1 second'

        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {
            _health_check.Field_Run_Every: 5,
            _health_check.Field_Run_Unit: 'minutes',
        })

        lines = _describe(session_maker, AuditSource.REST_Outgoing)
        assert _value(lines, 'Health check') == 'every 5 minutes'

# ################################################################################################################################

    def test_the_health_check_line_sits_after_the_audit_log_and_before_the_alerts(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {})

        labels = _labels(_describe(session_maker, AuditSource.REST_Outgoing))
        assert labels.index('Audit log') < labels.index('Health check') < labels.index('Alert settings of its own')

# ################################################################################################################################
# ################################################################################################################################

class TestQueueLines:

    def test_a_connection_saved_before_the_switches_existed_carries_their_defaults(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.PLAIN_HTTP, {})

        lines = _describe(session_maker, AuditSource.REST_Outgoing)

        # The queue is off and the DLQ on by default
        assert _value(lines, 'Use queue') == 'off'
        assert _value(lines, 'Use DLQ') == 'on'

        # The two sit after the retries, before the audit log
        labels = _labels(lines)
        assert labels.index('Use queue') + 1 == labels.index('Use DLQ')
        assert labels.index('Use DLQ') < labels.index('Audit log')

# ################################################################################################################################

    def test_the_switches_read_as_stored_for_rest_and_soap_alike(self) -> 'None':
        session_maker = _new_session()
        _seed_connection(session_maker, URL_TYPE.SOAP, {
            HTTP_SOAP.Queue.Field_Use_Queue: True,
            HTTP_SOAP.DLQ.Field_Use_DLQ: False,
        })

        lines = _describe(session_maker, AuditSource.SOAP_Outgoing)

        assert _value(lines, 'Use queue') == 'on'
        assert _value(lines, 'Use DLQ') == 'off'

# ################################################################################################################################
# ################################################################################################################################
