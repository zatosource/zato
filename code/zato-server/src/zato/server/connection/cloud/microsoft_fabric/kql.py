# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from http.client import OK, UNAUTHORIZED
from time import monotonic

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric.spark import MicrosoftFabricSpark

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabric.Default

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Eventhouse:
    """ Where an eventhouse answers KQL queries and which of its databases is queried by default.
    """
    query_uri: 'str'
    database:  'str'

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricKQL(MicrosoftFabricSpark):
    """ KQL queries against the eventhouses of a workspace.
    """

    def _get_eventhouse(self, workspace_id:'str', eventhouse_id:'str') -> 'Eventhouse':
        """ Returns an eventhouse's query URI and default database, reading them from Fabric the first time.
        """
        eventhouses = self._eventhouses
        eventhouse_key = f'{workspace_id}/{eventhouse_id}'

        if eventhouse := eventhouses.get(eventhouse_key):
            return eventhouse

        with self._eventhouse_lock:

            # Another greenlet may have built it while we waited for the lock
            if eventhouse := eventhouses.get(eventhouse_key):
                return eventhouse

            # The eventhouse itself has the address queries go to ..
            item = self.get(f'/workspaces/{workspace_id}/eventhouses/{eventhouse_id}')
            item = cast_('anydict', item)
            properties = item['properties']

            query_uri = properties.get('queryServiceUri')
            database_ids = properties.get('databasesItemIds') or []

            # .. an eventhouse just created has neither yet ..
            if not (query_uri and database_ids):
                raise Exception(f'Eventhouse {eventhouse_id} is not ready for queries yet ({self.name})')

            # .. and its first database is the one queried when the caller names none.
            database = self.get(f'/workspaces/{workspace_id}/kqlDatabases/{database_ids[0]}')
            database = cast_('anydict', database)

            eventhouse = Eventhouse()
            eventhouse.query_uri = query_uri
            eventhouse.database = database['displayName']

            eventhouses[eventhouse_key] = eventhouse

        out = eventhouse
        return out

# ################################################################################################################################

    def _get_eventhouse_headers(self) -> 'anydict':
        """ Returns the headers each KQL request needs.
        """
        token = self._get_eventhouse_token()

        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

# ################################################################################################################################

    def _to_rows(self, reply:'anydict') -> 'dictlist':
        """ Turns the first table of a KQL reply into a list of dicts keyed by column name.
        """
        tables = reply['Tables']
        result = tables[0]

        column_names:'strlist' = []
        for column in result['Columns']:
            column_names.append(column['ColumnName'])

        out:'dictlist' = []
        for values in result['Rows']:
            row = {}
            for name, value in zip(column_names, values):
                row[name] = value
            out.append(row)

        return out

# ################################################################################################################################

    def query_events(self, workspace_id:'str', eventhouse_id:'str', query:'str', database:'str'='') -> 'dictlist':
        """ Runs a KQL query against an eventhouse and returns its rows as a list of dicts.
        The query runs against the eventhouse's first database unless another one is named.
        """
        eventhouse = self._get_eventhouse(workspace_id, eventhouse_id)

        url = f'{eventhouse.query_uri}{_default.Eventhouse_Query_Path}'
        data = {
            'db': database or eventhouse.database,
            'csl': query,
        }

        start = monotonic()

        # A failed call is recorded too, before the caller learns about it
        try:

            # Run the query ..
            headers = self._get_eventhouse_headers()
            response = self.session.post(url, headers=headers, json=data)

            # .. a 401 means our token was rejected, e.g. it was revoked server-side,
            # .. so obtain a new one and retry the request once ..
            if response.status_code == UNAUTHORIZED:
                self._acquire_eventhouse_token()
                headers = self._get_eventhouse_headers()
                response = self.session.post(url, headers=headers, json=data)

            # .. anything other than 200 OK is an error.
            if response.status_code != OK:
                raise Exception(f'Fabric KQL error ({self.name}): {response.status_code} -> {repr(response.text)}')

        except Exception as e:
            self._record_call(url, start, str(e))
            raise

        self._record_call(url, start)

        out = self._to_rows(response.json())
        return out

# ################################################################################################################################
# ################################################################################################################################
