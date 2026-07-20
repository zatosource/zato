# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, Column, Integer, LargeBinary, MetaData, select, String, Table, Text, UniqueConstraint
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import AS2
from zato.common.as2.inbound import StoredMDN
from zato.common.audit_log.api import get_audit_engine
from zato.common.json_internal import dumps, loads
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import strstrdict
    datetime = datetime
    Engine = Engine
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the identifier columns.
_short_column_len = 255

# Retention runs after every that many stores.
_retention_check_interval = 1000

# ################################################################################################################################
# ################################################################################################################################

# The duplicate store lives in the same database the audit log uses - one table with a unique
# constraint on the identity triple, so detection stays atomic when more than one server handles traffic.
metadata = MetaData()

duplicate_table = Table('as2_duplicate', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('as2_from', String(_short_column_len)),
    Column('as2_to', String(_short_column_len)),
    Column('message_id', String(_short_column_len)),
    Column('status_code', Integer),
    Column('body', LargeBinary),
    Column('headers', Text),
    Column('created_iso', String(_short_column_len)),
    UniqueConstraint('as2_from', 'as2_to', 'message_id', name='uq_as2_duplicate_message'),
)

# ################################################################################################################################
# ################################################################################################################################

class DuplicateStore:
    """ Remembers each processed message under its {AS2-From, AS2-To, Message-ID} triple together
    with the signed MDN bytes of the first delivery, so a replay gets the exact same bytes back,
    never a recomputed answer. The comparison is case-sensitive on the full addr-spec
    and the angle brackets are already stripped by the inbound pipeline.
    """

    def __init__(self, window_days:'int'=AS2.Default.Duplicate_Window_Days, engine:'Engine | None'=None) -> 'None':

        self.window_days = window_days

        # The store shares the audit log's database unless the caller brought its own engine.
        if engine is None:
            engine = get_audit_engine()

        self.engine:'Engine' = engine

        # The schema creation is idempotent, the same way the audit log's is.
        metadata.create_all(self.engine)

        # Counts stores so retention can run periodically instead of on every write.
        self._store_count = 0

# ################################################################################################################################

    def get(self, as2_from:'str', as2_to:'str', message_id:'str') -> 'StoredMDN | None':
        """ Returns the stored MDN of an earlier delivery of the same message, or None
        when the message was never seen - the is_duplicate callable of the inbound pipeline.
        """
        statement = select(
            duplicate_table.c.status_code,
            duplicate_table.c.body,
            duplicate_table.c.headers,
        ).where(and_(
            duplicate_table.c.as2_from == as2_from,
            duplicate_table.c.as2_to == as2_to,
            duplicate_table.c.message_id == message_id,
        ))

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            row = result.first()

        # An unseen message is not a duplicate ..
        if row is None:
            return None

        # .. a seen one comes back with the stored bytes exactly as they were sent the first time.
        status_code, body, headers = row

        out = StoredMDN()
        out.status_code = status_code
        out.body = body
        out.headers = loads(headers)

        return out

# ################################################################################################################################

    def store(
        self,
        as2_from:'str',
        as2_to:'str',
        message_id:'str',
        status_code:'int',
        body:'bytes',
        headers:'strstrdict',
        ) -> 'bool':
        """ Remembers one processed message and its MDN response. Returns True when this call
        was the first to store the triple and False when another server stored it first -
        the unique constraint is what keeps the detection atomic.
        """
        now = utcnow()
        created_iso = now.isoformat()
        headers_json = dumps(headers)

        insert = duplicate_table.insert()
        insert_statement = insert.values(
            as2_from=as2_from,
            as2_to=as2_to,
            message_id=message_id,
            status_code=status_code,
            body=body,
            headers=headers_json,
            created_iso=created_iso,
        )

        # A constraint violation means another server already stored this very triple.
        try:
            with self.engine.begin() as connection:
                _ = connection.execute(insert_statement)
            out = True
        except IntegrityError:
            out = False

        # Periodically delete rows older than the detection window.
        self._store_count += 1

        if self._store_count % _retention_check_interval == 0:
            self._run_retention(now)

        return out

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Deletes entries older than the duplicate detection window.
        """
        cutoff = now - timedelta(days=self.window_days)
        cutoff_iso = cutoff.isoformat()

        delete = duplicate_table.delete()
        delete_statement = delete.where(duplicate_table.c.created_iso < cutoff_iso)

        with self.engine.begin() as connection:
            result = connection.execute(delete_statement)

        if result.rowcount:
            suffix = 'row' if result.rowcount == 1 else 'rows'
            logger.info('AS2 duplicate store retention deleted %d %s older than %s', result.rowcount, suffix, cutoff_iso)

# ################################################################################################################################
# ################################################################################################################################
