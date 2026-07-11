# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# jsonata-python
from jsonata import Jsonata

# lxml
from lxml import etree

# Zato
from zato.common.api import HTTP_SOAP, SchedulerLink
from zato.common.odb.model import HTTPSOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, dictlist, stranydict, strlist

    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck

# ################################################################################################################################
# ################################################################################################################################

def validate_jsonata(expression:'str') -> 'None':
    """ Compiles a JSONata expression, raising an exception if its syntax is invalid.
    """
    _ = Jsonata(expression)

# ################################################################################################################################

def validate_xpath(expression:'str') -> 'None':
    """ Compiles an XPath expression, raising an exception if its syntax is invalid.
    """
    _ = etree.XPath(expression)

# ################################################################################################################################

def evaluate_jsonata(expression:'str', data:'any_') -> 'any_':
    """ Evaluates a JSONata expression against the given data.
    """
    compiled = Jsonata(expression)

    out = compiled.evaluate(data)
    return out

# ################################################################################################################################

def evaluate_xpath(expression:'str', xml_text:'str | bytes') -> 'any_':
    """ Evaluates an XPath expression against an XML document given as text.
    Element results are turned into their text content so callers receive plain values.
    """
    if isinstance(xml_text, str):
        xml_text = xml_text.encode('utf8')

    document = etree.fromstring(xml_text)
    result = document.xpath(expression)

    # A node-set is turned into the text of each node ..
    if isinstance(result, list):
        out:'anylist' = []
        for node in result:
            if isinstance(node, etree._Element):
                out.append(node.text)
            else:
                out.append(node)

        # .. a single-element list reads more naturally as a scalar.
        if len(out) == 1:
            out = out[0]

        return out

    # .. anything else - a string, a number or a boolean - is already a plain value.
    return result

# ################################################################################################################################
# ################################################################################################################################

def parse_param_rows(text:'str') -> 'dictlist':
    """ Parses the JSON rows of request parameters - each row is a dict of key, value and mode.
    """
    if not text:
        return []

    out = loads(text)
    return out

# ################################################################################################################################

def evaluate_param_rows(rows:'dictlist', context:'any_') -> 'stranydict':
    """ Turns the rows of request parameters into a dict, evaluating each JSONata-mode value at call time.
    The context is the request data the calling service passed in - it is empty for scheduled calls.
    """

    # Our response to produce
    out:'stranydict' = {}

    for row in rows:
        key = row['key']
        value = row['value']
        mode = row['mode']

        # JSONata values are evaluated each time this runs - text values are sent exactly as typed
        if mode == _invocation.ValueMode.JSONata:
            value = evaluate_jsonata(value, context)

        out[key] = value

    return out

# ################################################################################################################################

def evaluate_request_data(data:'str', data_mode:'str', context:'any_') -> 'str':
    """ Returns the request body to send - either exactly as typed or built by a JSONata expression.
    The context is the request data the calling service passed in - it is empty for scheduled calls.
    """
    if data_mode == _invocation.ValueMode.JSONata:
        result = evaluate_jsonata(data, context)

        # A structural result is serialized to JSON so it can travel as the request body
        if isinstance(result, (dict, list)):
            out = dumps(result)
        else:
            out = result

        return out

    # The body is sent exactly as typed
    return data

# ################################################################################################################################

def map_response(response_data:'any_', response_map:'str', response_map_mode:'str') -> 'any_':
    """ Reshapes a response through the connection's response map. JSONata maps receive parsed JSON,
    XPath maps receive the raw XML text.
    """
    if response_map_mode == _invocation.ResponseMapMode.XPath:
        out = evaluate_xpath(response_map, response_data)
        return out

    # JSONata operates on parsed data so text is parsed first
    if isinstance(response_data, (str, bytes)):
        response_data = loads(response_data)

    out = evaluate_jsonata(response_map, response_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

def update_connection_opaque_fields(session:'SASession', conn_id:'int', values:'stranydict') -> 'None':
    """ Writes the given opaque attributes back to an outgoing connection.
    """

    # The connection may no longer exist, e.g. its linked job outlived it
    row = session.query(HTTPSOAP).filter_by(id=conn_id).first()
    if not row:
        return

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. reflect the new values ..
    opaque.update(values)

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################

def clear_connection_opaque_fields(session:'SASession', conn_id:'int', field_names:'strlist') -> 'None':
    """ Removes the given opaque attributes from an outgoing connection, e.g. when its linked job was deleted.
    """

    # The connection may no longer exist, e.g. the job is being deleted because the connection itself is
    row = session.query(HTTPSOAP).filter_by(id=conn_id).first()
    if not row:
        return

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. remove everything that was asked for ..
    for name in field_names:
        opaque.pop(name, None)

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################
# ################################################################################################################################

def update_linked_job_fields(
    session,    # type: SASession
    conn_id,    # type: int
    kind,       # type: str
    run_every,  # type: int
    run_unit,   # type: str
    start_date, # type: str
    job_id,     # type: int
    ) -> 'None':
    """ Writes the current state of a connection-linked scheduler job back to the opaque fields
    of the connection, no matter if the job describes scheduled invocations or health checks.
    """

    # Health check jobs describe their own field set, without a start date ..
    if kind == SchedulerLink.KindType.HealthCheck:
        values = {
            _health_check.Field_Run_Every: run_every,
            _health_check.Field_Run_Unit: run_unit,
            _health_check.Field_Job_ID: job_id,
        }

    # .. scheduled invocations use the connection's scheduler tab fields.
    else:
        values = {
            _invocation.Field_Run_Every: run_every,
            _invocation.Field_Run_Unit: run_unit,
            _invocation.Field_Start_Date: start_date,
            _invocation.Field_Job_ID: job_id,
        }

    update_connection_opaque_fields(session, conn_id, values)

# ################################################################################################################################

def clear_linked_job_fields(session:'SASession', conn_id:'int', kind:'str') -> 'None':
    """ Removes the fields describing a connection-linked scheduler job after the job was deleted,
    so the connection does not describe a job that no longer exists.
    """
    if kind == SchedulerLink.KindType.HealthCheck:
        field_names = list(_health_check.FieldList)
    else:
        field_names = list(_invocation.SchedulerFieldList)

    clear_connection_opaque_fields(session, conn_id, field_names)

# ################################################################################################################################
# ################################################################################################################################
