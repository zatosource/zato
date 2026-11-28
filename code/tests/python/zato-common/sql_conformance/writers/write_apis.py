# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The write APIs of the Zato database, each with the rows that its write leaves behind. Each API runs against
# the database that the environment configures, and the rows are read back through a connection of their own.

# stdlib
from datetime import datetime, timezone
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.store import raise_alert
from zato.common.audit_log.api import AuditLog, AuditSource
from zato.common.audit_log.common import alert_table, event_table
from zato.common.common_db.schema import shared_object_table
from zato.common.common_db.store import SharedObjectStore
from zato.common.db_env.database import get_database_engine, new_unshared_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pending import new_pending_attempts
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.rule_engine.sql.schema import rule_version_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from zato.common.typing_ import any_

    any_ = any_
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server that the audit events are written by
    Server_Name = 'durability-writers'

    # The topic of the publications
    Topic_Name = 'durability.writers'

    # The payload of each publication
    Data = 'Durability of the write'

    # The attempt of a delivery row after its first lease or its first push attempt
    Attempt_Recorded = 1

    # How many messages and how many bytes of payloads a claim of a push batch may take
    Claim_Max_Messages = 10
    Claim_Max_Len = 1024 * 1024

    # The type of the shared objects
    Shared_Object_Type = 'durability-writers'

    # The kind, the source and the object of the findings that the alerts are raised for
    Finding_Kind = 'durability-check'
    Finding_Source = 'durability'
    Finding_Object = 'durability-writers'

    # The event type and the object of the audit events
    Audit_Event_Type = 'durability.write'
    Audit_Object = 'durability-writers'

    # The author of the rulesets and the rule that each of their versions holds
    Author = 'durability.writers'
    Rule_ID = 'durability-rule'

# ################################################################################################################################
# ################################################################################################################################

class WriteCheck(NamedTuple):
    """ The rows that a write leaves behind - the rows of a table whose column has a value,
    which the write creates or, if is_present is False, removes.
    """
    column: 'Column'
    value: 'any_'
    is_present: 'bool'

# ################################################################################################################################

def count_rows(check:'WriteCheck') -> 'int':
    """ Returns how many rows of a write's check a connection of an engine of its own finds.
    """
    column = check.column
    query = select(func.count()).select_from(column.table).where(column == check.value)

    engine = new_unshared_database_engine()

    try:
        with engine.connect() as connection:
            out = connection.execute(query).scalar_one()
    finally:
        engine.dispose()

    return out

# ################################################################################################################################

def is_written(check:'WriteCheck') -> 'bool':
    """ Returns whether a connection of an engine of its own finds what a write leaves behind.
    """
    count = count_rows(check)

    if check.is_present:
        out = count > 0
    else:
        out = count == 0

    return out

# ################################################################################################################################
# ################################################################################################################################

class WriteAPI:
    """ One write API, with the writes that it needs before it and the rows that it leaves behind.
    The identifiers of the rows are built from a token, which a test and the process that writes share.
    """

    def __init__(self, token:'str') -> 'None':
        self.token = token

    def prepare(self) -> 'None':
        """ Writes what the write of the API needs before it.
        """

    def write(self) -> 'None':
        raise NotImplementedError()

    def get_check(self) -> 'WriteCheck':
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class _PubSubAPI(WriteAPI):
    """ The base of the pub/sub APIs, with a subscriber and a message of its own.
    """

    def __init__(self, token:'str') -> 'None':
        super().__init__(token)

        self.sub_key = f'zpsk.durability.{token}'
        self.msg_id = f'zpsm.durability.{token}'

    def prepare(self) -> 'None':
        audit_log = AuditLog(ModuleCtx.Server_Name)
        self.backend = SQLPubSubBackend(audit_log=audit_log)

    def subscribe(self) -> 'None':
        self.backend.subscribe(self.sub_key, ModuleCtx.Topic_Name)

    def publish(self) -> 'None':
        _ = self.backend.publish(ModuleCtx.Topic_Name, ModuleCtx.Data, msg_id=self.msg_id)

# ################################################################################################################################

class PublishAPI(_PubSubAPI):

    def prepare(self) -> 'None':
        super().prepare()
        self.subscribe()

    def write(self) -> 'None':
        self.publish()

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(message_table.c.msg_id, self.msg_id, True)
        return out

# ################################################################################################################################

class AckAPI(_PubSubAPI):

    def prepare(self) -> 'None':
        super().prepare()
        self.subscribe()
        self.publish()

    def write(self) -> 'None':
        _ = self.backend.ack_messages(self.sub_key, [self.msg_id])

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(delivery_table.c.sub_key, self.sub_key, False)
        return out

# ################################################################################################################################

class AckAtomicAPI(AckAPI):

    def write(self) -> 'None':
        self.backend.ack_with_publications(self.sub_key, [self.msg_id], [], [])

# ################################################################################################################################

class LeaseAPI(AckAPI):

    def write(self) -> 'None':
        _ = self.backend.pull_messages(self.sub_key)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(delivery_table.c.attempt, ModuleCtx.Attempt_Recorded, True)
        return out

# ################################################################################################################################

class RecordAttemptsAPI(AckAPI):
    """ The push attempts of a batch, written through the writer.
    """

    def prepare(self) -> 'None':
        super().prepare()

        query = select(delivery_table.c.id).where(delivery_table.c.sub_key == self.sub_key)

        with get_database_engine().connect() as connection:
            self.delivery_ids = list(connection.execute(query).scalars())

    def write(self) -> 'None':
        pending = new_pending_attempts(self.delivery_ids)
        self.backend._writer.record_attempts(pending)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(delivery_table.c.attempt, ModuleCtx.Attempt_Recorded, True)
        return out

# ################################################################################################################################

class ClaimAPI(AckAPI):
    """ The claim of the next push batch of a subscriber, which records the first attempt of each of its messages.
    """

    def write(self) -> 'None':
        _ = self.backend.claim(self.sub_key, ModuleCtx.Claim_Max_Messages, ModuleCtx.Claim_Max_Len)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(delivery_table.c.attempt, ModuleCtx.Attempt_Recorded, True)
        return out

# ################################################################################################################################

class AckAndClaimAPI(AckAPI):
    """ The commit of a push batch, which acknowledges its messages together with the claim of the next batch.
    """

    def write(self) -> 'None':
        _ = self.backend.ack_and_claim(self.sub_key, [self.msg_id], [], [], ModuleCtx.Claim_Max_Messages,
            ModuleCtx.Claim_Max_Len)

# ################################################################################################################################

class AuditInsertAPI(WriteAPI):

    def write(self) -> 'None':
        audit_log = AuditLog(ModuleCtx.Server_Name)
        _ = audit_log.insert(AuditSource.PubSub, ModuleCtx.Audit_Event_Type, ModuleCtx.Audit_Object, cid=self.token)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(event_table.c.cid, self.token, True)
        return out

# ################################################################################################################################

class SharedObjectAPI(WriteAPI):

    def write(self) -> 'None':
        store = SharedObjectStore()
        _ = store.compare_and_set(ModuleCtx.Shared_Object_Type, self.token, {'token': self.token}, None)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(shared_object_table.c.name, self.token, True)
        return out

# ################################################################################################################################

class AlertAPI(WriteAPI):

    def __init__(self, token:'str') -> 'None':
        super().__init__(token)
        self.rule_name = f'durability-{token}'

    def write(self) -> 'None':
        rule = new_rule(self.rule_name, ModuleCtx.Finding_Kind)
        finding = new_finding(ModuleCtx.Finding_Kind, ModuleCtx.Finding_Source, ModuleCtx.Finding_Object, self.token)
        now = datetime.now(timezone.utc)

        _ = raise_alert(get_database_engine(), rule, finding, now)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(alert_table.c.rule_name, self.rule_name, True)
        return out

# ################################################################################################################################

class RuleVersionAPI(WriteAPI):

    def __init__(self, token:'str') -> 'None':
        super().__init__(token)
        self.ruleset_id = 0

    def prepare(self) -> 'None':
        engine = get_database_engine()
        self.backend = RuleSQLBackend.from_engine(engine)

        definition = self.backend.definitions.create(
            name=f'Durability rulesets {self.token}',
            object_type=Definition_Type_Ruleset,
            document={'rules': [{'id': ModuleCtx.Rule_ID}]},
            author=ModuleCtx.Author,
            comment='Ruleset of the durability versions',
        )
        self.ruleset_id = definition.id

    def write(self) -> 'None':
        _ = self.backend.versions.create(
            definition_id=self.ruleset_id,
            expected_current_version=1,
            document={'rules': [{'id': ModuleCtx.Rule_ID}]},
            author=ModuleCtx.Author,
            comment=self.token,
        )

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(rule_version_table.c.comment, self.token, True)
        return out

# ################################################################################################################################
# ################################################################################################################################

Write_APIs:'dict[str, type[WriteAPI]]' = {
    'publish': PublishAPI,
    'ack': AckAPI,
    'ack-atomic': AckAtomicAPI,
    'lease': LeaseAPI,
    'record-attempts': RecordAttemptsAPI,
    'claim': ClaimAPI,
    'ack-and-claim': AckAndClaimAPI,
    'audit-insert': AuditInsertAPI,
    'shared-object': SharedObjectAPI,
    'alert': AlertAPI,
    'rule-version': RuleVersionAPI,
}

# ################################################################################################################################
# ################################################################################################################################
