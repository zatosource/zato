# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import Alerting
from zato.common.json_internal import dumps
from zato.common.odb.query.generic import GenericObjectWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dictlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The keys an explanation's opaque document carries.
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
    'explanation',
    'confidence',
    'remediation',
    'is_parsed',
    'created_iso',
)

# ################################################################################################################################
# ################################################################################################################################

class ExplanationStore:
    """ Reads and writes explained alerts - generic objects of the zato-alert-explanation type
    with everything in the opaque document. There is no lifecycle here - an explanation
    is written once, next to the alert it explains, and only ever read back.
    """

    def __init__(self, session:'callable_', cluster_id:'int') -> 'None':
        self.session = session
        self.cluster_id = cluster_id

# ################################################################################################################################

    def _new_wrapper(self, session:'any_') -> 'GenericObjectWrapper':
        wrapper = GenericObjectWrapper(session, self.cluster_id)
        wrapper.type_ = Alerting.Explanation_Type

        return wrapper

# ################################################################################################################################

    def _row_to_explanation(self, row:'stranydict') -> 'stranydict':
        """ Normalizes a generic_object row, with its opaque keys merged in, to an explanation dict.
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
        """ Stores a new explanation under the given name.
        """
        opaque = dumps(details)

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            insert = wrapper.create(name, opaque)

            session.execute(insert)
            session.commit()

# ################################################################################################################################

    def get(self, name:'str') -> 'stranydict | None':
        """ Returns one explanation by its name, or None if there is no such explanation.
        """

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            row = wrapper.get(name)

        if not row:
            return None

        out = self._row_to_explanation(row)
        return out

# ################################################################################################################################

    def get_list(self) -> 'dictlist':
        """ Returns all explanations, newest first.
        """

        # Our response to produce
        out:'dictlist' = []

        with closing(self.session()) as session:

            wrapper = self._new_wrapper(session)
            rows = wrapper.get_list()

        for row in rows:
            explanation = self._row_to_explanation(row)
            out.append(explanation)

        # The rows arrive ordered by name and names embed no time - the creation time orders them instead.
        out.sort(key=_by_created, reverse=True)

        return out

# ################################################################################################################################

    def exists(self, name:'str') -> 'bool':
        """ Whether an explanation is already stored under the given name -
        one alert produces one explanation, not one per sweep.
        """
        out = self.get(name) is not None
        return out

# ################################################################################################################################
# ################################################################################################################################

def _by_created(explanation:'stranydict') -> 'str':
    """ The sort key ordering explanations by their creation time.
    """
    out = explanation['created_iso']
    return out

# ################################################################################################################################
# ################################################################################################################################
