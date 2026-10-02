# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.common.audit_log.common import AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What every data attribute name starts with
    Data_Prefix = 'zato.audit.data'

    # What every payload attribute name starts with
    Payload_Prefix = 'zato.audit.payload'

    # Set on a record whose payload was cut to the configured size
    Payload_Truncated = 'zato.audit.payload.truncated'

    # How long a single data string can be
    Max_Value_Length = 4096

# ################################################################################################################################
# ################################################################################################################################

# A source whose whole data document is exported
All_Keys = None

# The data keys each source exports
_data_keys_by_source:'stranydict' = {
    AuditSource.MCP:           All_Keys,
    AuditSource.Config:        All_Keys,
    AuditSource.File_Outgoing: All_Keys,
    AuditSource.SQL_Outgoing:  ('statement', 'row_count', 'error'),
    AuditSource.FHIR:          ('resource_type', 'method', 'path'),
    AuditSource.Email_IMAP:    ('sent_from', 'sent_to'),
    AuditSource.AS2:           ('mic', 'disposition'),
}

# The sources whose data column is a payload, or has nothing worth exporting, and so leaves only under the payload flag
_sources_without_data = {
    AuditSource.PubSub,
    AuditSource.REST_Channel,
    AuditSource.SOAP_Channel,
    AuditSource.REST_Outgoing,
    AuditSource.SOAP_Outgoing,
    AuditSource.Email_SMTP,
    AuditSource.AS4,
    AuditSource.X12,
    AuditSource.MLLP_Channel,
    AuditSource.MLLP_Outgoing,
    AuditSource.Kafka_Channel,
    AuditSource.Kafka_Outgoing,
    AuditSource.Scheduler,
    AuditSource.LLM,
    AuditSource.Odoo,
    AuditSource.Service,
    AuditSource.Microsoft_Cloud,
    AuditSource.REST_Outgoing_Health,
    AuditSource.SOAP_Outgoing_Health,
    AuditSource.FHIR_Health,
    AuditSource.Email_SMTP_Health,
    AuditSource.Certificate,
    AuditSource.Microsoft_Health,
    AuditSource.Test_Transfer,
}

# The data keys of event types that export the same keys whatever their source
_data_keys_by_event_type:'stranydict' = {
    AuditEvent.Alert_Raised: ('kind', 'message', 'rule', 'count'),
}

# The scalar types OTLP carries as they are
_scalar_types = (str, bool, int, float)

# ################################################################################################################################
# ################################################################################################################################

def has_data_export(source:'str', event_type:'str') -> 'bool':
    """ Whether the data document of an event of this source and type is exported at all.
    """
    if source in _data_keys_by_source:
        out = True
    else:
        out = event_type in _data_keys_by_event_type

    return out

# ################################################################################################################################

def get_sources_with_data() -> 'strset':
    """ Returns the sources whose data document is exported.
    """
    out = set(_data_keys_by_source)
    return out

# ################################################################################################################################

def get_sources_without_data() -> 'strset':
    """ Returns the sources whose data document is not exported.
    """
    out = set(_sources_without_data)
    return out

# ################################################################################################################################

def _cap(value:'str', max_length:'int') -> 'str':
    """ Cuts a string to the maximum length a single value can have.
    """
    if len(value) > max_length:
        value = value[:max_length]

    return value

# ################################################################################################################################

def _flatten_list(items:'anylist') -> 'any_':
    """ Turns a list into an OTLP array value - scalars of one type stay as they are, mixed scalars become strings,
    and a list holding objects or lists is serialized, since OTLP arrays hold scalars only.
    """

    # An array of objects has no OTLP form of its own ..
    for item in items:
        if not isinstance(item, _scalar_types):
            out = _cap(dumps(items), ModuleCtx.Max_Value_Length)
            return out

    # .. scalars of one type travel as they are ..
    types = set()
    for item in items:
        types.add(type(item))

    type_count = len(types)
    is_one_type = type_count <= 1

    if is_one_type:
        out = tuple(items)

    # .. and mixed ones as strings.
    else:
        as_strings = []
        for item in items:
            as_strings.append(str(item))
        out = tuple(as_strings)

    return out

# ################################################################################################################################

def flatten(prefix:'str', value:'any_', out:'stranydict') -> 'None':
    """ Flattens a document into attributes, joining the keys of nested objects with a dot at every level.
    """

    # Nested objects add a level to the name ..
    if isinstance(value, dict):
        for key, item in value.items():
            flatten(f'{prefix}.{key}', item, out)

    # .. lists become arrays ..
    elif isinstance(value, list):
        out[prefix] = _flatten_list(value)

    # .. strings are capped, and empty ones are left out like empty columns are ..
    elif isinstance(value, str):
        if value:
            out[prefix] = _cap(value, ModuleCtx.Max_Value_Length)

    # .. other scalars go as they are ..
    elif isinstance(value, _scalar_types):
        out[prefix] = value

    # .. nulls are left out ..
    elif value is None:
        pass

    # .. and anything else travels as its text.
    else:
        out[prefix] = _cap(str(value), ModuleCtx.Max_Value_Length)

# ################################################################################################################################

def build_data_attributes(source:'str', event_type:'str', data:'str', out:'stranydict') -> 'None':
    """ Adds the exported keys of an event's data document to the attributes of its record.
    """

    # An event without a document has nothing to add ..
    if not data:
        return

    # .. find which keys this event exports ..
    if event_type in _data_keys_by_event_type:
        keys = _data_keys_by_event_type[event_type]
    else:
        keys = _data_keys_by_source[source]

    # .. a document that is not JSON, or not an object, has no keys to export ..
    try:
        document = loads(data)
    except Exception:
        return

    if not isinstance(document, dict):
        return

    # .. a source exporting everything flattens the whole document ..
    if keys is All_Keys:
        flatten(ModuleCtx.Data_Prefix, document, out)

    # .. and any other only the keys it names.
    else:
        for key in keys:
            if key in document:
                flatten(f'{ModuleCtx.Data_Prefix}.{key}', document[key], out)

# ################################################################################################################################

def build_payload_attributes(data:'str', bodies:'stranydict', max_size:'int', out:'stranydict') -> 'None':
    """ Adds an event's payload and bodies to the attributes of its record, each cut to the configured size.
    """
    is_truncated = False

    # The payload kept in the data column ..
    if data:
        if len(data) > max_size:
            is_truncated = True
        out[f'{ModuleCtx.Payload_Prefix}.data'] = data[:max_size]

    # .. and each body under its kind.
    for kind, body in bodies.items():
        if len(body) > max_size:
            is_truncated = True
        out[f'{ModuleCtx.Payload_Prefix}.{kind}'] = body[:max_size]

    if is_truncated:
        out[ModuleCtx.Payload_Truncated] = True

# ################################################################################################################################
# ################################################################################################################################
