# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the generic connection services are exercised with offline - a service whose collaborators stand in,
# the input a create or an edit of an outgoing FHIR connection or of an MLLP channel sends, and the readers of what was stored.

# stdlib
import logging
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

# Zato
from zato.common.api import GENERIC, HL7, SCHEDULER
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import loads
from zato.common.odb.model import Cluster, GenericConn, Job, Service
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal.generic.connection import Create
from zato.server.service.internal.generic.get_list import GetList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    any_ = any_
    anydict = anydict
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

Cluster_Id = 1
Service_Name = 'zato.connection.health-check.run'
FHIR_Type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR
FHIR_Name = 'ehr.fhir'
FHIR_Address = 'https://fhir.example.com/r4'
MLLP_Type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
MLLP_Name = 'adt.intake'
MLLP_Service = 'adt.process'

# The id the scheduler stand-in gives every job it is asked to create
Job_Id = 4321

# ################################################################################################################################
# ################################################################################################################################

def full_input(class_:'any_', input_data:'stranydict') -> 'Bunch':
    """ The input as SimpleIO hands it to a service - every declared name is there, the ones the caller
    did not send as None. A service with no declared input, e.g. Create, is handed everything as raw input instead.
    """
    out = Bunch()

    for elem in getattr(class_, 'input', ()):

        if isinstance(elem, str):
            name = elem
        else:
            name = elem.name

        out[name.lstrip('-')] = None

    # What was sent lands in the declared input when there is one and in the raw request otherwise
    if out:
        out.update(input_data)

    return out

# ################################################################################################################################

def new_service(class_:'any_', session_factory:'any_', input_data:'stranydict') -> 'any_':
    """ A service with its collaborators standing in - the sessions are real, the server is not.
    """
    service:'any_' = object.__new__(class_)

    service.cid = 'cid-generic-alerts'
    service.request = SimpleNamespace(input=full_input(class_, input_data), raw=dict(input_data), payload={})
    service.response = SimpleNamespace(payload=Bunch())
    service.odb = SimpleNamespace(session=session_factory)
    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test-generic-alerts')
    service.invoke = MagicMock(return_value={'id': Job_Id})
    service.crypto = SimpleNamespace(encrypt=_encrypt, generate_secret=lambda: b'auto-secret')

    # The declared input of Create and Edit is empty, so every raw value is evaluated through here
    service._io = SimpleNamespace(eval_=lambda key, value, encrypt: value)

    server = SimpleNamespace(
        name='test-server',
        cluster_id=Cluster_Id,
        get_config_session=lambda **kwargs: session_factory(),
        encrypt=lambda value: value,
        decrypt=lambda value: value,
        config_manager=SimpleNamespace(sdk_connector_types={}),
        fs_server_config=SimpleNamespace(misc=SimpleNamespace(return_internal_objects='True')),
    )
    service.server = server

    return service

# ################################################################################################################################

def _encrypt(value:'str') -> 'bytes':
    out = value.encode('utf8')
    return out

# ################################################################################################################################

def fhir_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an outgoing FHIR connection sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': FHIR_Name,
        'type_': FHIR_Type,
        'is_active': True,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'address': FHIR_Address,
        'pool_size': HL7.Default.pool_size,
        'security_id': 0,
        'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
        'is_audit_log_active': True,
        'cluster_id': Cluster_Id,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def mllp_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an MLLP channel sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': MLLP_Name,
        'type_': MLLP_Type,
        'is_active': True,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
        'service': MLLP_Service,
        'is_audit_log_active': True,
        'cluster_id': Cluster_Id,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def create(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one outgoing FHIR connection and returns its id.
    """
    service = new_service(Create, session_factory, fhir_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ################################################################################################################################

def create_mllp(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one MLLP channel and returns its id.
    """
    service = new_service(Create, session_factory, mllp_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ################################################################################################################################

def stored_opaque(session_factory:'any_', item_id:'int') -> 'anydict':
    """ The opaque attributes a connection has in the database.
    """
    session = session_factory()
    item = session.query(GenericConn).filter(GenericConn.id==item_id).one()
    out = parse_instance_opaque_attr(item)
    session.close()

    return out

# ################################################################################################################################

def count_connections(session_factory:'any_') -> 'int':
    """ How many connections the database holds.
    """
    session = session_factory()
    out = session.query(GenericConn).count()
    session.close()

    return out

# ################################################################################################################################

def add_job(session_factory:'any_', job_id:'int', name:'str') -> 'None':
    """ Puts the job the scheduler stand-in reported into the database, the way the real scheduler would have.
    """
    session = session_factory()
    cluster = session.query(Cluster).filter(Cluster.id==Cluster_Id).one()
    service = session.query(Service).filter(Service.name==Service_Name).one()
    job = Job(job_id, name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, datetime(2026, 1, 1), '', cluster, service=service)
    session.add(job)
    session.commit()
    session.close()

# ################################################################################################################################

def get_list(session_factory:'any_', type_:'str'=FHIR_Type) -> 'anylist':
    """ What GetList returns for the connections of one type, outgoing FHIR ones unless told otherwise.
    """
    input_data = {
        'cluster_id': Cluster_Id,
        'type_': type_,
        'paginate': False,
    }
    service = new_service(GetList, session_factory, input_data)
    service.handle()

    out = loads(service.response.payload)
    return out

# ################################################################################################################################
# ################################################################################################################################
