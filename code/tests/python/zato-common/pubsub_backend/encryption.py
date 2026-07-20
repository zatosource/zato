# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import delete_all_rows, get_message_rows
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

# The topic and subscriber all the encryption assertions share.
_topic = 'pubsub.backend.test.encryption'
_sub_key = 'zpsk.test.encryption.1'

# The payload whose plaintext must never appear in the database.
_plaintext = 'this-payload-must-be-encrypted-at-rest'

# ################################################################################################################################
# ################################################################################################################################

def run_encryption_scenario() -> 'None':
    """ Encryption at rest - payloads are stored encrypted, read back decrypted
    and dropped like any other payload once fully delivered.
    """
    delete_all_rows()

    # A throwaway key is all the backend needs.
    secret_key = CryptoManager.generate_key()
    crypto_manager = CryptoManager(secret_key=secret_key)

    backend = SQLPubSubBackend(crypto_manager=crypto_manager, encrypt_at_rest=True)
    backend.subscribe(_sub_key, _topic)

    result = backend.publish(_topic, _plaintext, correl_id='correlation-encryption-1')

    # What sits in the database is not the plaintext ..
    rows = get_message_rows(_topic)

    assert len(rows) == 1
    assert rows[0].payload_encrypted
    assert rows[0].payload != _plaintext
    assert _plaintext not in rows[0].payload

    # .. but the preview and size describe the plaintext ..
    assert rows[0].data_size == len(_plaintext)
    assert rows[0].data_preview == _plaintext

    # .. every read path decrypts transparently ..
    messages = backend.fetch_messages(_sub_key)

    assert len(messages) == 1
    assert messages[0]['data'] == _plaintext

    details = backend.get_message_details(_topic, result.msg_id)

    assert details is not None
    assert details['data'] == _plaintext

    browsed, _ignored = backend.browse_messages(_topic, _sub_key, state='pending', needs_data=True)

    assert browsed[0]['data'] == _plaintext

    # .. and the acknowledgement drops the encrypted payload like any other.
    _ = backend.ack_message(_sub_key, result.msg_id)

    rows = get_message_rows(_topic)

    assert rows[0].payload is None
    assert not rows[0].payload_encrypted

# ################################################################################################################################
# ################################################################################################################################
