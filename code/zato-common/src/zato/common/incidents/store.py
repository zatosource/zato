# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import Incidents
from zato.common.json_internal import dumps
from zato.common.odb.query.generic import GenericObjectWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dictlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The keys a diagnosis's opaque document carries.
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
)

# ################################################################################################################################
# ################################################################################################################################

class IncidentStore:
    """ Reads and writes diagnosed alerts - generic objects of the zato-incident type
    with everything in the opaque document. There is no lifecycle here - a diagnosis
    is written once, next to the alert it explains, and only ever read back.
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
        """ Normalizes a generic_object row, with its opaque keys merged in, to a diagnosis dict.
        """

        # Our response to produce
        out:'stranydict' = {
            'id': row['id'],
            'name': row['name'],
        }

        for key in _detail_keys:
            if key in row:
                out[key] = row[key]

        return out

# ################################################################################################################################

    def create(self, name:'str', details:'stranydict') -> 'None':
        """ Stores a new diagnosis under the given name.
        """
        opaque = dumps(details)

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            insert = wrapper.create(name, opaque)

            session.execute(insert)
            session.commit()

# ################################################################################################################################

    def get(self, name:'str') -> 'stranydict | None':
        """ Returns one diagnosis by its name, or None if there is no such diagnosis.
        """

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            row = wrapper.get(name)

        if not row:
            return None

        out = self._row_to_incident(row)
        return out

# ################################################################################################################################

    def get_list(self) -> 'dictlist':
        """ Returns all diagnoses, newest first.
        """

        # Our response to produce
        out:'dictlist' = []

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            rows = wrapper.get_list()

        for row in rows:
            incident = self._row_to_incident(row)
            out.append(incident)

        # The rows arrive ordered by name and names embed no time - the creation time orders them instead.
        out.sort(key=_by_created, reverse=True)

        return out

# ################################################################################################################################

    def exists(self, name:'str') -> 'bool':
        """ Whether a diagnosis is already stored under the given name -
        one alert produces one diagnosis, not one per sweep.
        """
        out = self.get(name) is not None
        return out

# ################################################################################################################################
# ################################################################################################################################

def _by_created(incident:'stranydict') -> 'str':
    """ The sort key ordering diagnoses by their creation time.
    """
    out = incident['created_iso']
    return out

# ################################################################################################################################
# ################################################################################################################################
