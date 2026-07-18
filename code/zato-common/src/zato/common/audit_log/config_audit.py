# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config-change and view-access audit events. A config change records who changed what,
# with a before/after summary of only the fields that differ, whether the change was
# persistent or runtime-only, and both the original and the effective principal,
# so escalation never hides the actor. A view event records who opened which message body
# from which screen - access logging for content that may carry PHI.

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.defaults import secret_fields_exact, secret_fields_prefix, secret_fields_suffix
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import intnone, stranydict, strdictnone

    AuditLog = AuditLog

# ################################################################################################################################
# ################################################################################################################################

# What replaces the value of a secret field in a change summary
Secret_Mask = '******'

# ################################################################################################################################
# ################################################################################################################################

class ConfigScope:
    """ Whether a change was written to configuration or applied to the runtime only,
    e.g. a channel suspend that will not survive a restart.
    """
    Persistent = 'persistent'
    Ephemeral  = 'ephemeral'

# ################################################################################################################################
# ################################################################################################################################

def is_secret_field(name:'str') -> 'bool':
    """ Tells whether a field's value must be masked in change summaries.
    """

    # The comparison is case-insensitive so Password and password are both matched
    name = name.lower()

    # Exact names are the primary match ..
    if name in secret_fields_exact:
        return True

    # .. and the prefix and suffix sets extend it.
    for prefix in secret_fields_prefix:
        if name.startswith(prefix):
            return True

    for suffix in secret_fields_suffix:
        if name.endswith(suffix):
            return True

    return False

# ################################################################################################################################

def mask_secrets(config:'stranydict') -> 'stranydict':
    """ Returns a copy of a config dict with every secret value replaced by the mask.
    """

    # Our response to produce
    out:'stranydict' = {}

    for name, value in config.items():
        if is_secret_field(name):
            out[name] = Secret_Mask
        else:
            out[name] = value

    return out

# ################################################################################################################################

def build_change_summary(before:'stranydict', after:'stranydict') -> 'stranydict':
    """ Builds the before/after summary of a config change - only the fields
    whose values differ are included, with secrets masked on both sides.
    A creation has an empty before and a deletion has an empty after.
    """

    # Only the fields that actually changed make it into the summary
    summary_before:'stranydict' = {}
    summary_after:'stranydict'  = {}

    all_names = set(before) | set(after)

    for name in sorted(all_names):

        # A field missing on one side is a marker of addition or removal
        in_before = name in before
        in_after  = name in after

        if in_before and in_after:

            # Unchanged fields stay out of the summary
            if before[name] == after[name]:
                continue

        if in_before:
            summary_before[name] = before[name]

        if in_after:
            summary_after[name] = after[name]

    # Our response to produce
    out:'stranydict' = {
        'before': mask_secrets(summary_before),
        'after':  mask_secrets(summary_after),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def record_config_change(
    audit_log:'AuditLog',
    *,
    action:'str',
    object_type:'str',
    object_name:'str',
    actor:'str',
    cid:'str' = '',
    effective_actor:'str' = '',
    scope:'str' = ConfigScope.Persistent,
    before:'strdictnone' = None,
    after:'strdictnone' = None,
    ) -> 'intnone':
    """ Writes one config-change event - who changed what, the before/after summary,
    the persistent-vs-ephemeral scope, and both identities. The action is one of
    AuditEvent.Config_Created, Config_Edited or Config_Deleted. The effective actor
    defaults to the original one when no escalation took place. Returns the event id.
    """

    # A creation has no before and a deletion has no after
    if before is None:
        before = {}

    if after is None:
        after = {}

    # With no escalation, the change ran as the person who made it
    if not effective_actor:
        effective_actor = actor

    # The summary carries only the fields that differ, with secrets masked
    summary = build_change_summary(before, after)
    summary['object_type'] = object_type

    # The identity and scope fields are searchable attributes -
    # "everything this person changed" and "all ephemeral changes" are one query each.
    attrs = {
        'actor': actor,
        'effective_actor': effective_actor,
        'scope': scope,
        'object_type': object_type,
    }

    # Our response to produce
    out = audit_log.insert(
        AuditSource.Config,
        action,
        object_name,
        cid=cid,
        outcome=AuditOutcome.OK,
        data=dumps(summary),
        attrs=attrs,
    )

    return out

# ################################################################################################################################

def record_view_event(
    audit_log:'AuditLog',
    *,
    actor:'str',
    viewed_event_id:'int',
    screen:'str',
    cid:'str' = '',
    ) -> 'intnone':
    """ Writes one view-access event - who opened which event's message body
    and from which screen. This is access logging, not access control -
    the view already happened, this records it. Returns the event id.
    """

    # The viewer and the viewed event are searchable attributes -
    # "who looked at this message" and "everything this person viewed" are one query each.
    attrs = {
        'actor': actor,
        'viewed_event_id': viewed_event_id,
        'screen': screen,
    }

    data = dumps({
        'viewed_event_id': viewed_event_id,
        'screen': screen,
    })

    # Our response to produce
    out = audit_log.insert(
        AuditSource.Config,
        AuditEvent.Content_Viewed,
        screen,
        cid=cid,
        outcome=AuditOutcome.OK,
        data=data,
        attrs=attrs,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
