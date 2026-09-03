# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic, sleep

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric.tables import MicrosoftFabricTables

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabric.Default
_spark_state = MicrosoftFabric.Spark_State
_output_status = MicrosoftFabric.Spark_Output_Status

# The MIME key the query results of a Spark statement are stored under.
_result_mime_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricSpark(MicrosoftFabricTables):
    """ Spark sessions of a lakehouse and SQL queries running on them.
    """

    def _get_sessions_path(self, workspace_id:'str', lakehouse_id:'str') -> 'str':
        """ Returns the base path of a lakehouse's Spark sessions.
        """
        version = _default.Livy_API_Version

        out = f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/livyapi/versions/{version}/sessions'
        return out

# ################################################################################################################################

    def open_spark_session(self, workspace_id:'str', lakehouse_id:'str') -> 'str':
        """ Opens a new Spark session and waits until it is ready to accept statements.
        """
        sessions_path = self._get_sessions_path(workspace_id, lakehouse_id)

        # Ask for a new session ..
        response = self.post(sessions_path, data={})
        response = cast_('anydict', response)
        session_id = response['id']

        # .. and wait until Spark reports it as ready.
        timeout = _default.Spark_Session_Timeout
        deadline = monotonic() + timeout

        while True:

            # Check where the session stands now ..
            session = self.get(f'{sessions_path}/{session_id}')
            session = cast_('anydict', session)
            state = session['state']

            # .. it is ready to accept statements ..
            if state == _spark_state.Idle:
                break

            # .. it will never become ready ..
            if state in (_spark_state.Dead, _spark_state.Error, _spark_state.Killed):
                raise Exception(f'Spark session failed to start ({self.name}) -> {session}')

            # .. give up if it did not start in time ..
            now = monotonic()
            if now >= deadline:
                raise Exception(f'Spark session did not start in {timeout}s ({self.name}) -> {session_id}')

            # .. otherwise, wait before the next check.
            sleep(_default.Operation_Poll_Interval)

        out = session_id
        return out

# ################################################################################################################################

    def run_spark(
        self,
        workspace_id:'str',
        lakehouse_id:'str',
        session_id:'str',
        code:'str',
        kind:'str'='pyspark',
        ) -> 'anydict':
        """ Runs code on a Spark session and returns the statement's output once it completes.
        """
        sessions_path = self._get_sessions_path(workspace_id, lakehouse_id)
        statements_path = f'{sessions_path}/{session_id}/statements'

        # Submit the statement ..
        request_data = {'code': code, 'kind': kind}
        response = self.post(statements_path, data=request_data)
        response = cast_('anydict', response)
        statement_id = response['id']

        # .. and wait until it completes.
        timeout = _default.Spark_Session_Timeout
        deadline = monotonic() + timeout

        while True:

            # Check where the statement stands now ..
            statement = self.get(f'{statements_path}/{statement_id}')
            statement = cast_('anydict', statement)
            state = statement['state']

            # .. its output is ready ..
            if state == _spark_state.Available:
                break

            # .. it will never produce one ..
            if state in (_spark_state.Error, _spark_state.Cancelled):
                raise Exception(f'Spark statement failed ({self.name}) -> {statement}')

            # .. give up if it did not complete in time ..
            now = monotonic()
            if now >= deadline:
                raise Exception(f'Spark statement did not complete in {timeout}s ({self.name}) -> {statement_id}')

            # .. otherwise, wait before the next check.
            sleep(_default.Operation_Poll_Interval)

        # The statement completed but the code itself may still have failed.
        output = statement['output']
        if output['status'] == _output_status.Error:
            error_value = output['evalue']
            raise Exception(f'Spark error ({self.name}) -> {error_value}')

        out = output
        return out

# ################################################################################################################################

    def query(self, workspace_id:'str', lakehouse_id:'str', sql:'str') -> 'dictlist':
        """ Runs an SQL query against a lakehouse and returns its rows as a list of dicts.
        """

        # Run the query on the lakehouse's shared session ..
        session_id = self._get_spark_session(workspace_id, lakehouse_id)
        output = self.run_spark(workspace_id, lakehouse_id, session_id, sql, kind='sql')

        # .. the result travels as a schema and a list of rows ..
        output_data = output['data']
        payload = output_data[_result_mime_type]

        # .. the column names come from the schema ..
        schema = payload['schema']
        fields = schema['fields']

        column_names = []
        for field in fields:
            column_names.append(field['name'])

        # .. and each row becomes a dict keyed by those names.
        out:'dictlist' = []

        for row in payload['data']:
            item = {}
            for column_name, value in zip(column_names, row):
                item[column_name] = value
            out.append(item)

        return out

# ################################################################################################################################

    def _get_spark_session(self, workspace_id:'str', lakehouse_id:'str') -> 'str':
        """ Returns the ID of the lakehouse's shared Spark session, opening a new one
        if there is none yet or the current one is no longer usable.
        """
        session_key = f'{workspace_id}/{lakehouse_id}'

        # If a session exists already, confirm it is still usable ..
        if session_id := self._spark_sessions.get(session_key):

            sessions_path = self._get_sessions_path(workspace_id, lakehouse_id)

            try:
                session = self.get(f'{sessions_path}/{session_id}')
            except Exception:
                # The session is gone, e.g. it expired server-side, so a new one is needed.
                del self._spark_sessions[session_key]
            else:
                session = cast_('anydict', session)
                state = session['state']

                # A session that has not failed can still run statements.
                if state not in (_spark_state.Dead, _spark_state.Error, _spark_state.Killed):
                    out = session_id
                    return out

                # This one is no longer usable.
                del self._spark_sessions[session_key]

        # .. no usable session exists at this point, so open a new one.
        session_id = self.open_spark_session(workspace_id, lakehouse_id)
        self._spark_sessions[session_key] = session_id

        out = session_id
        return out

# ################################################################################################################################

    def close_spark_session(self, workspace_id:'str', lakehouse_id:'str') -> 'None':
        """ Closes the lakehouse's shared Spark session, if one is open.
        """
        session_key = f'{workspace_id}/{lakehouse_id}'

        if session_id := self._spark_sessions.pop(session_key, None):
            sessions_path = self._get_sessions_path(workspace_id, lakehouse_id)
            _ = self.delete(f'{sessions_path}/{session_id}')

# ################################################################################################################################
# ################################################################################################################################
