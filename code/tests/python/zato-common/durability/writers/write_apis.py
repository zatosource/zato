# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The write APIs of the Zato database, each with the rows that its write leaves behind. Each API runs against
# the database that the environment configures, and the rows are read back through a connection of their own.

# stdlib
import sqlite3
from datetime import datetime, timezone
from typing import NamedTuple

# Zato
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.store import raise_alert
from zato.common.audit_log.api import AuditLog, AuditSource
from zato.common.audit_log.common import alert_table, event_table
from zato.common.common_db.schema import shared_object_table
from zato.common.common_db.store import SharedObjectStore
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.rule_engine.sql import DecisionWrite, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.rule_engine.sql.schema import rule_decision_table

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server that the audit events are written by
    Server_Name = 'durability-writers'

    # The topic of the publications
    Topic_Name = 'durability.writers'

    # The payload of each publication
    Data = 'Durability of the write'

    # The type of the shared objects
    Shared_Object_Type = 'durability-writers'

    # The kind, the source and the object of the findings that the alerts are raised for
    Finding_Kind = 'durability-check'
    Finding_Source = 'durability'
    Finding_Object = 'durability-writers'

    # The event type and the object of the audit events
    Audit_Event_Type = 'durability.write'
    Audit_Object = 'durability-writers'

    # The author of the rulesets and the rule that each decision fires
    Author = 'durability.writers'
    Rule_ID = 'durability-rule'

# ################################################################################################################################
# ################################################################################################################################

class WriteCheck(NamedTuple):
    """ The rows that a write leaves behind - the rows of a table whose column has a value,
    which the write creates or, if is_present is False, removes.
    """
    table_name: 'str'
    column_name: 'str'
    value: 'str'
    is_present: 'bool'

# ################################################################################################################################

def count_rows(db_path:'str', check:'WriteCheck') -> 'int':
    """ Returns how many rows of a write's check a new connection to a SQLite file finds.
    """
    connection = sqlite3.connect(db_path)

    try:
        query = f'select count(*) from {check.table_name} where {check.column_name} = ?'
        row = connection.execute(query, (check.value,)).fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def is_written(db_path:'str', check:'WriteCheck') -> 'bool':
    """ Returns whether a new connection to a SQLite file finds what a write leaves behind.
    """
    count = count_rows(db_path, check)

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
        out = WriteCheck(message_table.name, message_table.c.msg_id.name, self.msg_id, True)
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
        out = WriteCheck(delivery_table.name, delivery_table.c.sub_key.name, self.sub_key, False)
        return out

# ################################################################################################################################

class AckAtomicAPI(AckAPI):

    def write(self) -> 'None':
        self.backend.ack_with_publications(self.sub_key, [self.msg_id], [], [])

# ################################################################################################################################

class AuditInsertAPI(WriteAPI):

    def write(self) -> 'None':
        audit_log = AuditLog(ModuleCtx.Server_Name)
        _ = audit_log.insert(AuditSource.PubSub, ModuleCtx.Audit_Event_Type, ModuleCtx.Audit_Object, cid=self.token)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(event_table.name, event_table.c.cid.name, self.token, True)
        return out

# ################################################################################################################################

class SharedObjectAPI(WriteAPI):

    def write(self) -> 'None':
        store = SharedObjectStore()
        _ = store.compare_and_set(ModuleCtx.Shared_Object_Type, self.token, {'token': self.token}, None)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(shared_object_table.name, shared_object_table.c.name.name, self.token, True)
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
        out = WriteCheck(alert_table.name, alert_table.c.rule_name.name, self.rule_name, True)
        return out

# ################################################################################################################################

class DecisionAPI(WriteAPI):

    def __init__(self, token:'str') -> 'None':
        super().__init__(token)
        self.ruleset_id = 0

    def prepare(self) -> 'None':
        engine = get_database_engine()
        self.backend = RuleSQLBackend.from_engine(engine)

        definition = self.backend.definitions.create(
            name=f'Durability decisions {self.token}',
            object_type=Definition_Type_Ruleset,
            document={'rules': [{'id': ModuleCtx.Rule_ID}]},
            author=ModuleCtx.Author,
            comment='Ruleset of the durability decisions',
        )
        self.ruleset_id = definition.id

    def write(self) -> 'None':
        decision = DecisionWrite(
            decision_id=self.token,
            ruleset_id=self.ruleset_id,
            rules_version=1,
            occurred_at=datetime.now(timezone.utc),
            business_key=self.token,
            outcome='matched',
            is_error=False,
            duration_ms=1,
            story={'input': {'token': self.token}},
            fired_rule_ids=[ModuleCtx.Rule_ID],
        )

        writer = self.backend.decision_writer()
        writer.submit(decision)

    def get_check(self) -> 'WriteCheck':
        out = WriteCheck(rule_decision_table.name, rule_decision_table.c.decision_id.name, self.token, True)
        return out

# ################################################################################################################################
# ################################################################################################################################

Write_APIs:'dict[str, type[WriteAPI]]' = {
    'publish': PublishAPI,
    'ack': AckAPI,
    'ack-atomic': AckAtomicAPI,
    'audit-insert': AuditInsertAPI,
    'shared-object': SharedObjectAPI,
    'alert': AlertAPI,
    'decision': DecisionAPI,
}

# ################################################################################################################################
# ################################################################################################################################
