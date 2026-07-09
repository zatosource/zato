# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# Zato
from zato.common.as2.duplicates import duplicate_table, DuplicateStore
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

def _make_store(tmp_path:'os.PathLike') -> 'DuplicateStore':
    """ Points the audit database at a per-test SQLite file and builds a duplicate store on it.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

    out = DuplicateStore()
    return out

# ################################################################################################################################

def _cleanup_env() -> 'None':
    _ = os.environ.pop(AuditLogCtx.Env_Type, None)
    _ = os.environ.pop(AuditLogCtx.Env_Name, None)

# ################################################################################################################################
# ################################################################################################################################

def test_unseen_message_is_not_a_duplicate(tmp_path:'os.PathLike') -> 'None':
    try:
        store = _make_store(tmp_path)

        assert store.get('PartnerCorp', 'ZatoRetail', 'abc@partnercorp') is None

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_stored_mdn_comes_back_byte_for_byte(tmp_path:'os.PathLike') -> 'None':
    try:
        store = _make_store(tmp_path)

        body = b'MIME-Version: 1.0\r\n\r\nThis is the stored MDN'
        headers = {'Content-Type': 'multipart/report; report-type=disposition-notification'}

        created = store.store('PartnerCorp', 'ZatoRetail', 'abc@partnercorp', 200, body, headers)
        assert created is True

        stored = store.get('PartnerCorp', 'ZatoRetail', 'abc@partnercorp')

        assert stored is not None
        assert stored.status_code == 200
        assert stored.body == body
        assert stored.headers == headers

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_only_the_first_store_wins(tmp_path:'os.PathLike') -> 'None':
    try:
        store = _make_store(tmp_path)

        first = store.store('PartnerCorp', 'ZatoRetail', 'abc@partnercorp', 200, b'first', {})
        second = store.store('PartnerCorp', 'ZatoRetail', 'abc@partnercorp', 200, b'second', {})

        assert first is True
        assert second is False

        # The bytes of the first delivery are what a replay gets back.
        stored = store.get('PartnerCorp', 'ZatoRetail', 'abc@partnercorp')
        assert stored.body == b'first'

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_identity_triple_is_the_key(tmp_path:'os.PathLike') -> 'None':
    try:
        store = _make_store(tmp_path)

        _ = store.store('PartnerCorp', 'ZatoRetail', 'abc@partnercorp', 200, b'first', {})

        # The same Message-ID from another pair is a different message.
        assert store.get('OtherCorp', 'ZatoRetail', 'abc@partnercorp') is None
        assert store.get('PartnerCorp', 'OtherRetail', 'abc@partnercorp') is None

        # And another Message-ID from the same pair is one too.
        assert store.get('PartnerCorp', 'ZatoRetail', 'def@partnercorp') is None

    finally:
        _cleanup_env()

# ################################################################################################################################

def test_retention_deletes_entries_outside_the_window(tmp_path:'os.PathLike') -> 'None':
    try:
        store = _make_store(tmp_path)

        # One entry from long before the detection window and one fresh.
        old_iso = (utcnow() - timedelta(days=store.window_days + 1)).isoformat()

        insert_stmt = duplicate_table.insert().values(
            as2_from='PartnerCorp',
            as2_to='ZatoRetail',
            message_id='old@partnercorp',
            status_code=200,
            body=b'old',
            headers='{}',
            created_iso=old_iso,
        )

        with store.engine.begin() as connection:
            _ = connection.execute(insert_stmt)

        _ = store.store('PartnerCorp', 'ZatoRetail', 'fresh@partnercorp', 200, b'fresh', {})

        store._run_retention(utcnow())

        # The old entry is gone, so its message is no longer a duplicate ..
        assert store.get('PartnerCorp', 'ZatoRetail', 'old@partnercorp') is None

        # .. while the fresh one still is.
        assert store.get('PartnerCorp', 'ZatoRetail', 'fresh@partnercorp') is not None

    finally:
        _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
