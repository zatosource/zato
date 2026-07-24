# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.rule_engine.sql.constants import Chat_Kind_Slack, Chat_Kind_Teams, Chat_Kinds
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The Fernet key that credentials are encrypted with at rest - shared by the dashboard and the jobs.
Env_Secret_Key = 'Zato_Rule_Engine_Secret_Key'

# What each platform's credentials must carry before anything can be sent through it.
Teams_Fields = ('tenant_id', 'client_id', 'client_secret')
Slack_Fields = ('token',)

_required_fields = {
    Chat_Kind_Teams: Teams_Fields,
    Chat_Kind_Slack: Slack_Fields,
}

# ################################################################################################################################
# ################################################################################################################################

class NotifyConfigError(Exception):
    """ A notification credentials or destination configuration problem, always with a readable message.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_crypto_manager() -> 'CryptoManager':
    """ Returns the crypto manager built from the environment's secret key.
    """
    # The key is the one piece of state that lives outside the database ..
    if secret_key := os.environ.get(Env_Secret_Key):
        pass
    else:
        message = f'Environment variable {Env_Secret_Key} is not set - ' + \
            'generate a key with zato.common.crypto.api.CryptoManager.generate_key and export it'
        raise NotifyConfigError(message)

    # .. and everything else derives from it.
    out = CryptoManager.from_secret_key(secret_key)
    return out

# ################################################################################################################################

def save_credentials(backend:'RuleSQLBackend', *, kind:'str', values:'anydict', actor:'str') -> 'None':
    """ Encrypts one platform's credentials and stores them in the rule engine database.
    """
    # Reject platforms this module does not deliver to ..
    if kind not in Chat_Kinds:
        message = f'Unknown chat kind -> {kind}'
        raise NotifyConfigError(message)

    # .. every required field has to be present and non-empty ..
    for field_name in _required_fields[kind]:
        field_value = values.get(field_name)
        if not field_value:
            message = f'Missing required {kind} credentials field -> {field_name}'
            raise NotifyConfigError(message)

    # .. serialize and encrypt the complete credentials document ..
    crypto_manager = get_crypto_manager()
    payload_clear = json.dumps(values)
    encrypted = crypto_manager.encrypt(payload_clear, needs_str=True)
    payload = cast_('str', encrypted)

    # .. and store the ciphertext, never the clear text.
    backend.notifications.set_chat_config(kind=kind, payload=payload, actor=actor)

# ################################################################################################################################

def load_credentials(backend:'RuleSQLBackend', kind:'str') -> 'anydict | None':
    """ Returns one platform's decrypted credentials or None when the platform is not configured.
    """
    record = backend.notifications.get_chat_config(kind)

    # An unconfigured platform is a valid state, not an error ..
    if record is None:
        out = None

    # .. while a configured one decrypts back into its original document.
    else:
        crypto_manager = get_crypto_manager()
        payload_clear = crypto_manager.decrypt(record.payload)
        out = json.loads(payload_clear)

    return out

# ################################################################################################################################

def credentials_status(backend:'RuleSQLBackend') -> 'dictlist':
    """ Returns each platform's configuration state without ever exposing any secrets.
    """
    # Index the stored rows by platform ..
    records = backend.notifications.list_chat_configs()
    by_kind = {}

    for record in records:
        by_kind[record.kind] = record

    # .. and report every known platform in its fixed order, configured or not.
    out = []

    for kind in Chat_Kinds:
        if record := by_kind.get(kind):
            row = {
                'kind':          kind,
                'is_configured': True,
                'updated_at':    record.updated_at.isoformat(),
                'updated_by':    record.updated_by,
            }
        else:
            row = {
                'kind':          kind,
                'is_configured': False,
                'updated_at':    None,
                'updated_by':    None,
            }

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################
