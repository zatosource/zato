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
MLLP_Outgoing_Type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP
MLLP_Outgoing_Name = 'lab.results'
MLLP_Outgoing_Address = 'lab.example.com:2575'
LLM_Type = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
LLM_Name = 'support.assistant'
LLM_Address = 'https://api.openai.com/v1'
LLM_Model = 'gpt-4o'
MCP_Type = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
MCP_Name = 'orders.gateway'
MCP_URL_Path = '/mcp/orders'
MCP_Services = ['orders.get', 'orders.list']

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
    def generate_secret() -> 'bytes':
        return b'auto-secret'

    def evaluate(key:'str', value:'any_', encrypt:'bool') -> 'any_':
        out = value
        return out

    def get_config_session(**kwargs:'any_') -> 'any_':
        out = session_factory()
        return out

    def identity(value:'any_') -> 'any_':
        out = value
        return out

    service:'any_' = object.__new__(class_)

    service.cid = 'cid-generic-alerts'
    service.request = SimpleNamespace(input=full_input(class_, input_data), raw=dict(input_data), payload={})
    service.response = SimpleNamespace(payload=Bunch())
    service.odb = SimpleNamespace(session=session_factory)
    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test-generic-alerts')
    service.invoke = MagicMock(return_value={'id': Job_Id})
    service.crypto = SimpleNamespace(encrypt=_encrypt, generate_secret=generate_secret)

    # The declared input of Create and Edit is empty, so every raw value is evaluated through here
    service._io = SimpleNamespace(eval_=evaluate)

    server = SimpleNamespace(
        name='test-server',
        cluster_id=Cluster_Id,
        odb=service.odb,
        get_config_session=get_config_session,
        encrypt=identity,
        decrypt=identity,
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

def mllp_outgoing_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an outgoing MLLP connection sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': MLLP_Outgoing_Name,
        'type_': MLLP_Outgoing_Type,
        'is_active': True,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'address': MLLP_Outgoing_Address,
        'pool_size': HL7.Default.pool_size,
        'is_audit_log_active': True,
        'cluster_id': Cluster_Id,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def llm_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an outgoing LLM connection sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': LLM_Name,
        'type_': LLM_Type,
        'is_active': True,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'address': LLM_Address,
        'model': LLM_Model,
        'pool_size': 1,
        'timeout': 60,
        'max_tokens': 4096,
        'max_history_turns': 20,
        'chat_expiry': 86400,
        'cluster_id': Cluster_Id,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def mcp_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an MCP gateway sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': MCP_Name,
        'type_': MCP_Type,
        'is_active': True,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
        'url_path': MCP_URL_Path,
        'services': MCP_Services,
        'security_groups': [],
        'is_audit_log_active': True,
        'validate_input': True,
        'cluster_id': Cluster_Id,
    }
    out.update(overrides)

    return out

# ##############################################################################################################################

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

# ##############################################################################################################################

def create_mllp_outgoing(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one outgoing MLLP connection and returns its id.
    """
    service = new_service(Create, session_factory, mllp_outgoing_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ##############################################################################################################################

def create_llm(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one outgoing LLM connection and returns its id.
    """
    service = new_service(Create, session_factory, llm_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ##############################################################################################################################

def create_mcp(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one MCP gateway and returns its id - the REST channel the gateway rides on is created through
    the stand-in invoke, so nothing but the generic connection lands in the database.
    """
    service = new_service(Create, session_factory, mcp_input(**overrides))
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
