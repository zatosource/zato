# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit log as services read it - self.audit is an instance of AuditFacade,
# answering what messages arrived, what failed and per-object newest event times.

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.body import resolve_body
from zato.common.audit_log.search import last_seen, search_events, Default_Page, Default_Page_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist, strnone, strorlist, strstrdict

    # Dummy assignments to satisfy type checkers
    dictlist = dictlist
    strnone = strnone
    strorlist = strorlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class AuditFacade:
    """ The API through which services read the audit log, e.g. self.audit.search(query='ADT-A01').
    """
    __slots__ = ()

    def search(
        self,
        *,
        source:'strorlist' = '',
        object_name:'strorlist' = '',
        outcome:'strorlist' = '',
        event_type:'strorlist' = '',
        query:'str' = '',
        status:'str' = '',
        time_from:'str' = '',
        time_to:'str' = '',
        page:'int' = Default_Page,
        page_size:'int' = Default_Page_Size,
        ) -> 'dictlist':
        """ Returns one page of audit events matching the filters, newest first. Every filter
        is optional - unset filters leave their column unfiltered, and each of source,
        object_name, outcome and event_type accepts one value or a list of values.
        The free-text query covers payloads, message ids and each source's searchable
        attributes, e.g. the MRN of an HL7 message.
        The filter values come from zato.common.audit_log.api - AuditSource, AuditEvent,
        AuditOutcome and Status_Outstanding.
        """
        engine = get_audit_engine()

        out = search_events(
            engine,
            source=source,
            object_name=object_name,
            outcome=outcome,
            event_type=event_type,
            query=query,
            status=status,
            time_from=time_from,
            time_to=time_to,
            page=page,
            page_size=page_size,
        )

        return out

# ################################################################################################################################

    def last_seen(self, source:'str') -> 'strstrdict':
        """ Returns the newest event time of each of one source's objects - a dict mapping
        each object name, e.g. each MLLP channel, to an ISO timestamp.
        """
        engine = get_audit_engine()

        out = last_seen(engine, source)
        return out

# ################################################################################################################################

    def get_payload(self, event_id:'int', kind:'str' = '') -> 'strnone':
        """ Returns the payload of one event - the full message body the event row itself
        only previews. An empty kind returns the newest body of any kind, otherwise
        kind names which one, e.g. 'request', 'response' or 'error'.
        """
        engine = get_audit_engine()

        # The body may live in the source's own store, so read the event's source first ..
        statement = select(event_table.c.source)
        statement = statement.where(event_table.c.id == event_id)

        with engine.connect() as connection:
            result = connection.execute(statement)
            row = result.first()

        # .. an event that does not exist has no payload ..
        if not row:
            return None

        source = row[0]

        # .. and the body itself is read the same way the Dashboard reads it.
        out = resolve_body(engine, source, event_id, kind)
        return out

# ################################################################################################################################
# ################################################################################################################################
