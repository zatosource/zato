# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the HTTP/SOAP services are exercised with offline - a service whose collaborators stand in,
# the input a create or an edit of each kind of object sends, and the readers of what was stored.

# stdlib
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.ext.bunch import Bunch
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal.http_soap.create import Create
from zato.server.service.internal.http_soap.get import Get, GetList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

Cluster_Id = 1
Service_Name = 'orders.get'
Channel_Name = 'orders.api'
Outgoing_Name = 'crm.api'
Outgoing_Host = 'https://crm.example.com'
URL_Path = '/orders'

# What the SOAP objects answer to and speak
SOAP_Action = 'urn:orders'
SOAP_Version = '1.1'

# ################################################################################################################################
# ################################################################################################################################

def full_input(class_:'any_', input_data:'stranydict') -> 'Bunch':
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

def new_service(class_:'any_', session_factory:'any_', input_data:'stranydict') -> 'any_':
    """ A service with its collaborators standing in - the sessions are real, the server is not.
    """
    def get_config_session(**kwargs:'any_') -> 'any_':
        out = session_factory()
        return out

    def encrypt(value:'any_') -> 'any_':
        out = value
        return out

    service:'any_' = object.__new__(class_)

    service.cid = 'cid-http-soap-alerts'
    service.request = SimpleNamespace(input=full_input(class_, input_data))
    service.response = SimpleNamespace(payload=Bunch())
    service.odb = SimpleNamespace(session=session_factory)
    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test-http-soap-alerts')
    service.invoke = MagicMock(return_value={})

    server = SimpleNamespace(
        cluster_id=Cluster_Id,
        get_config_session=get_config_session,
        encrypt=encrypt,
        fs_server_config=SimpleNamespace(misc=SimpleNamespace(return_internal_objects='True')),
    )
    service.server = server

    return service

# ################################################################################################################################

def base_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of a REST channel sends - the alert settings are not among these.
    """
    out:'stranydict' = {
        'name': Channel_Name,
        'url_path': URL_Path,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'service': Service_Name,
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
        'cluster_id': Cluster_Id,
        'is_wrapper': False,
        'wrapper_type': None,
        'username': None,
        'password': None,
        'is_audit_log_active': True,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def soap_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of a SOAP channel sends - the REST one with the SOAP transport, action and version.
    """
    out = base_input(transport=URL_TYPE.SOAP, soap_action=SOAP_Action, soap_version=SOAP_Version)
    out.update(overrides)

    return out

# ################################################################################################################################

def outgoing_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an outgoing REST connection sends - a host in place of a service.
    """
    out = base_input(name=Outgoing_Name, connection=CONNECTION.OUTGOING, host=Outgoing_Host, service=None)
    out.update(overrides)

    return out

# ################################################################################################################################

def soap_outgoing_input(**overrides:'any_') -> 'stranydict':
    """ What every create and edit of an outgoing SOAP connection sends.
    """
    out = outgoing_input(transport=URL_TYPE.SOAP, soap_action=SOAP_Action, soap_version=SOAP_Version)
    out.update(overrides)

    return out

# ################################################################################################################################

def create(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one HTTPSOAP object and returns its id.
    """
    service = new_service(Create, session_factory, base_input(**overrides))
    service.handle()

    out = service.response.payload.id
    return out

# ################################################################################################################################

def stored_opaque(session_factory:'any_', item_id:'int') -> 'anydict':
    """ The opaque attributes an object has in the database.
    """
    session = session_factory()
    item = session.query(HTTPSOAP).filter(HTTPSOAP.id==item_id).one()
    out = parse_instance_opaque_attr(item)
    session.close()

    return out

# ################################################################################################################################

def get_list(session_factory:'any_', connection:'str', transport:'str') -> 'list':
    """ What GetList returns for one connection and transport pair.
    """
    input_data = {
        'cluster_id': Cluster_Id,
        'connection': connection,
        'transport': transport,
        'paginate': False,
    }
    service = new_service(GetList, session_factory, input_data)

    session = session_factory()
    out = service.get_data(session)
    session.close()

    return out

# ################################################################################################################################

def get(session_factory:'any_', item_id:'int') -> 'anydict':
    """ What Get returns for one object.
    """
    def require_any(*names:'str') -> 'None':
        pass

    service = new_service(Get, session_factory, {'cluster_id': Cluster_Id, 'id': item_id, 'name': None})
    service.request.input.require_any = require_any
    service.handle()

    out = service.response.payload
    return out

# ################################################################################################################################
# ################################################################################################################################
