# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The describers of the generic outgoing connections, FHIR and MLLP - each names the connection's queue delivery
# switches, at their defaults for a connection saved before the switches existed and as stored otherwise, and
# neither names a connection that is not there.

# stdlib
import json

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.fhir_info import describe_outgoing_fhir
from zato.common.alerting.explain.mllp_outgoing_info import describe_mllp_outgoing
from zato.common.api import GENERIC, HTTP_SOAP
from zato.common.odb.model import Base, Cluster, GenericConn, SecurityBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_
    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

_cluster_id = 1
_conn_name = 'lab.results'
_conn_address = '10.0.0.7:2575'

# Each describer with the type of row it reads
_describers = {
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: describe_outgoing_fhir,
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: describe_mllp_outgoing,
}

# ################################################################################################################################
# ################################################################################################################################

def _new_session() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the describers read.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        SecurityBase.__table__,
        GenericConn.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    out = sessionmaker(bind=engine)

    session = out()
    session.add(Cluster(_cluster_id, 'test-cluster', '', 'sqlite'))
    session.commit()
    session.close()

    return out

# ################################################################################################################################

def _seed_connection(session_maker:'any_', type_:'str', opaque:'anydict') -> 'None':
    """ One generic outgoing connection of the type, with the given opaque attributes.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    row = GenericConn()
    row.name = _conn_name
    row.type_ = type_
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.address = _conn_address
    row.pool_size = 5
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _describe(session_maker:'any_', type_:'str') -> 'anylist':
    """ The label and value pairs of the connection of the type.
    """
    session = session_maker()
    out = _describers[type_](session, _cluster_id, _conn_name)
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

class TestQueueLines:

    def test_a_connection_saved_before_the_switches_existed_carries_their_defaults(self) -> 'None':

        for type_ in _describers:
            session_maker = _new_session()
            _seed_connection(session_maker, type_, {})

            lines = _describe(session_maker, type_)

            # The queue is off and the DLQ on by default
            assert _value(lines, 'Use queue') == 'off', type_
            assert _value(lines, 'Use DLQ') == 'on', type_

            # The two sit next to each other, before the audit log and the alert settings
            labels = _labels(lines)
            assert labels.index('Use queue') + 1 == labels.index('Use DLQ'), type_
            assert labels.index('Use DLQ') < labels.index('Audit log') < labels.index('Alert settings of its own'), type_

# ################################################################################################################################

    def test_the_switches_read_as_stored(self) -> 'None':

        for type_ in _describers:
            session_maker = _new_session()
            _seed_connection(session_maker, type_, {
                HTTP_SOAP.Queue.Field_Use_Queue: True,
                HTTP_SOAP.DLQ.Field_Use_DLQ: False,
            })

            lines = _describe(session_maker, type_)

            assert _value(lines, 'Use queue') == 'on', type_
            assert _value(lines, 'Use DLQ') == 'off', type_

# ################################################################################################################################

    def test_a_connection_that_is_not_there_is_none(self) -> 'None':

        for type_, describer in _describers.items():
            session_maker = _new_session()
            session = session_maker()

            assert describer(session, _cluster_id, 'no.such.connection') is None, type_
            session.close()

# ################################################################################################################################
# ################################################################################################################################
