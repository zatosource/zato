# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# SQLAlchemy
from sqlalchemy import and_, update

# Zato
from zato.common.api import GENERIC, Incidents
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dictlist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

ModelGenericObjectTable:'any_' = ModelGenericObject.__table__
_opaque_attr_name = GENERIC.ATTR_NAME

# The statuses under which an incident still awaits a decision.
_open_statuses = (Incidents.Status.New, Incidents.Status.Awaiting_Approval)

# The keys an incident's opaque document carries.
_detail_keys = (
    'object_name',
    'source',
    'rule',
    'alert_id',
    'count',
    'severity',
    'message',
    'link',
    'evidence',
    'diagnosis',
    'confidence',
    'remediation',
    'is_parsed',
    'created_iso',
    'history',
)

# ################################################################################################################################
# ################################################################################################################################

class IncidentStore:
    """ Reads and writes incidents - generic objects of the zato-incident type,
    with the status in the subtype column and everything else in the opaque document.
    """

    def __init__(self, session:'callable_', cluster_id:'int') -> 'None':
        self.session = session
        self.cluster_id = cluster_id

# ################################################################################################################################

    def _new_wrapper(self, session:'any_') -> 'GenericObjectWrapper':
        wrapper = GenericObjectWrapper(session, self.cluster_id)
        wrapper.type_ = Incidents.Type.Incident

        return wrapper

# ################################################################################################################################

    def _row_to_incident(self, row:'stranydict') -> 'stranydict':
        """ Normalizes a generic_object row, with its opaque keys merged in, to an incident dict.
        """

        # Our response to produce
        out:'stranydict' = {
            'id': row['id'],
            'name': row['name'],
            'status': row['subtype'],
        }

        for key in _detail_keys:
            if key in row:
                out[key] = row[key]

        return out

# ################################################################################################################################

    def create(self, name:'str', details:'stranydict', status:'str') -> 'None':
        """ Stores a new incident under the given name and status.
        """
        opaque = dumps(details)

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            insert = wrapper.create(name, opaque, subtype=status)

            session.execute(insert)
            session.commit()

# ################################################################################################################################

    def get(self, name:'str') -> 'stranydict | None':
        """ Returns one incident by its name, or None if there is no such incident.
        """

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            row = wrapper.get(name)

        if not row:
            return None

        out = self._row_to_incident(row)
        return out

# ################################################################################################################################

    def get_list(self, status:'strnone'=None) -> 'dictlist':
        """ Returns all incidents, optionally only the ones in a given status, newest first.
        """

        # Our response to produce
        out:'dictlist' = []

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            rows = wrapper.get_list(subtype=status)

        for row in rows:
            incident = self._row_to_incident(row)
            out.append(incident)

        # The rows arrive ordered by name and names embed no time - the creation time orders them instead.
        out.sort(key=_by_created, reverse=True)

        return out

# ################################################################################################################################

    def update(self, name:'str', details:'stranydict', status:'str') -> 'None':
        """ Replaces an incident's details and status.
        """
        opaque = dumps(details)
        now = utcnow()

        # The wrapper's own update never touches the subtype, which is where the status lives,
        # hence the query is built here in full.
        values = {
            _opaque_attr_name: opaque,
            'subtype': status,
            'last_modified': now,
        }

        where = and_(
            ModelGenericObjectTable.c.name == name,
            ModelGenericObjectTable.c.type_ == Incidents.Type.Incident,
            ModelGenericObjectTable.c.cluster_id == self.cluster_id,
        )

        query = update(ModelGenericObjectTable).values(values).where(where)

        with closing(self.session()) as session:
            session.execute(query)
            session.commit()

# ################################################################################################################################

    def has_open(self, object_name:'str') -> 'bool':
        """ Whether a connection already has an incident awaiting a decision -
        one failing connection produces one incident, not one per sweep.
        """
        incidents = self.get_list()

        for incident in incidents:

            if incident['object_name'] != object_name:
                continue

            if incident['status'] in _open_statuses:
                return True

        return False

# ################################################################################################################################
# ################################################################################################################################

def _by_created(incident:'stranydict') -> 'str':
    """ The sort key ordering incidents by their creation time.
    """
    out = incident['created_iso']
    return out

# ################################################################################################################################
# ################################################################################################################################
