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
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabric.Default
_spark_state = MicrosoftFabric.Spark_State
_output_status = MicrosoftFabric.Spark_Output_Status

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricSpark(MicrosoftFabricTables):
    """ Spark sessions of a lakehouse and the code that runs on them.
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

    def close_spark_session(self, workspace_id:'str', lakehouse_id:'str', session_id:'str') -> 'None':
        """ Closes a Spark session opened with open_spark_session.
        """
        sessions_path = self._get_sessions_path(workspace_id, lakehouse_id)
        _ = self.delete(f'{sessions_path}/{session_id}')

# ################################################################################################################################
# ################################################################################################################################
