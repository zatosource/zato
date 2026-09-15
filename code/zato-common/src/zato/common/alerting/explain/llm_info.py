# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an outgoing LLM connection's evidence - what the connection is, read off the ODB as every
# other object's is, so the model reads which provider and which model the calls went to before it reads how they
# went. The API key never appears.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines
from zato.common.alerting.object_config import alert_type_llm
from zato.common.api import GENERIC, LLM
from zato.common.odb.model import GenericConn
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist
    anylist = anylist
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

# The connection's numbers the Object section names, each with its label and the default a connection stored
# before the key existed reads at
_number_keys = (
    ('timeout',    'Timeout',    LLM.DEFAULT.TIMEOUT),
    ('max_tokens', 'Max tokens', LLM.DEFAULT.MAX_TOKENS),
)

# ################################################################################################################################
# ################################################################################################################################

def describe_outgoing_llm(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one outgoing LLM connection - its address, model, pool size,
    timeout, max tokens and the alert thresholds it sets of its own. None when no outgoing LLM connection
    goes by the name in the cluster.
    """
    row = session.query(GenericConn).\
        filter(GenericConn.cluster_id==cluster_id).\
        filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.OUTCONN_LLM).\
        filter(GenericConn.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Type', 'LLM'))
    out.append(('Active', 'yes' if row.is_active else 'no'))
    out.append(('Address', row.address))

    # The model is what selects the provider, so it is named right after where the calls go
    if 'model' in opaque:
        out.append(('Model', opaque['model']))

    if row.pool_size:
        out.append(('Pool size', row.pool_size))

    for key, label, default in _number_keys:
        if key in opaque:
            value = opaque[key]
        else:
            value = default
        out.append((label, value))

    # The settings are the LLM type's - the completion and token ones on top of the REST-like ones
    out.extend(settings_lines(alert_type_llm, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
