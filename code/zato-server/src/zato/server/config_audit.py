# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config-audit producers for the service layer - every create, edit and delete
# of a configuration object lands in the audit trail with the acting user,
# a before/after summary of only the fields that changed and secrets masked.
# The core lives in zato.common.audit_log.config_audit, this module binds it
# to what a running service knows - its server, its cid and its channel's identity.

# Zato
from zato.common.api import GENERIC
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.config_audit import record_config_change, ConfigScope
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strdictnone
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################
# ################################################################################################################################

# What a change is recorded under when no channel identity exists,
# e.g. when a service was invoked internally rather than through a channel.
Internal_Actor = 'internal'

# The header a caller may forward the original principal in - e.g. the Dashboard
# forwards its logged-in user this way while authenticating as its own API account.
Original_Principal_Header = 'HTTP_X_ZATO_USER'

# The environ key the service invoker propagates its channel's authenticated
# identity under - the inner service has no channel security of its own.
Invoker_Security_Username = 'zato.channel_security_username'

# ################################################################################################################################
# ################################################################################################################################

def get_model_snapshot(model:'any_') -> 'stranydict':
    """ Returns the configuration one ODB model row carries as a flat dict -
    the SQL columns plus everything from the opaque attribute, which is where
    generic objects and connections keep most of their fields.
    """

    # Our response to produce
    out:'stranydict' = {}

    for column in model.__table__.columns:
        out[column.name] = getattr(model, column.name)

    # The opaque attribute is a JSON dict of further fields - flattened here
    # so the change summary compares them field by field.
    opaque = out.pop(GENERIC.ATTR_NAME, None)

    if opaque:
        out.update(loads(opaque))

    return out

# ################################################################################################################################

def resolve_actors(service:'Service') -> 'tuple':
    """ Returns (actor, effective_actor) for one running service. The effective actor
    is the authenticated identity the call ran under - the channel's own security
    or the one the service invoker propagated. The actor is the original principal
    when a caller forwarded one, otherwise the two are the same.
    """
    wsgi_environ = service.wsgi_environ

    # The identity the call actually ran under
    effective = service.channel.security.username

    if not effective:
        effective = wsgi_environ.get(Invoker_Security_Username)

    if not effective:
        effective = Internal_Actor

    # The forwarded original principal - e.g. the Dashboard's logged-in user -
    # takes precedence as the actor when present
    actor = wsgi_environ.get(Original_Principal_Header)

    if not actor:
        actor = effective

    out = actor, effective
    return out

# ################################################################################################################################

def record_service_config_change(
    service:'Service',
    *,
    action:'str',
    object_type:'str',
    object_name:'str',
    before:'strdictnone' = None,
    after:'strdictnone' = None,
    scope:'str' = ConfigScope.Persistent,
    ) -> 'None':
    """ Writes one config-change event on behalf of a running service - the actor
    is whoever made the call and the effective actor is the identity it ran under,
    so escalation never hides the person behind it.
    """
    audit_log = AuditLog(service.server.name)

    actor, effective_actor = resolve_actors(service)

    _ = record_config_change(
        audit_log,
        action=action,
        object_type=object_type,
        object_name=object_name,
        actor=actor,
        effective_actor=effective_actor,
        cid=service.cid,
        scope=scope,
        before=before,
        after=after,
    )

# ################################################################################################################################
# ################################################################################################################################
