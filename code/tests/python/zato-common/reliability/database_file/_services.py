# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.common.db_env.database_env import DatabaseEnv
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is deployed into the server of the tests of the database file.

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topic that the services of the failure of the audit commit publish to
    Audit_Failure_Topic = 'reliability.database-file.audit-failure'

    # The variable with the path of the control file of the fault library
    Env_FSFault_Control = 'ZATO_FSFAULT_CONTROL'

    # The settings of the fault library under which every sync of the files of the database fails
    Fault_Settings = ('error_percent=100', 'errno=EIO', 'calls=sync')

    # How long the fault library may take to read a changed control file, in seconds
    Control_Reload_Wait = 0.3

    # The result that the service of a successful invocation returns
    Result_Published = 'published'

    # The error that the service of a failed invocation raises
    Invocation_Error = 'Order 12345 could not be shipped'

# ################################################################################################################################
# ################################################################################################################################

def _arm_commit_failure() -> 'None':
    """ Makes every sync of the files of the database fail, which fails each commit that follows,
    and waits until the fault library reads its new settings.
    """
    control_path = os.environ[ModuleCtx.Env_FSFault_Control]
    database_path = os.environ[DatabaseEnv.Env_Path]

    # The fault library compares the prefix with the resolved paths of the open files ..
    database_dir = os.path.dirname(database_path)
    database_dir = os.path.realpath(database_dir)

    lines = [f'prefix={database_dir}']
    lines.extend(ModuleCtx.Fault_Settings)

    settings = '\n'.join(lines)

    # .. the settings replace those of the control file ..
    with open(control_path, 'w') as control_file:
        _ = control_file.write(settings + '\n')

    # .. and they apply once the library reads the file again.
    time.sleep(ModuleCtx.Control_Reload_Wait)

# ################################################################################################################################
# ################################################################################################################################

class Echo(Service):
    """ Returns the correlation ID of its invocation, under which the audit log records the invocation.
    """

    name = 'test.reliability.database-file.echo'

    def handle(self) -> 'None':
        self.response.payload = {'cid': self.cid}

# ################################################################################################################################
# ################################################################################################################################

class AuditFailureOK(Service):
    """ Publishes one message, makes the commits of the database fail and returns the correlation ID of its invocation.
    """

    name = 'test.reliability.database-file.audit-failure.ok'

    def handle(self) -> 'None':

        # The message is committed before the commits start to fail ..
        _ = self.publish(ModuleCtx.Audit_Failure_Topic, {'order_id': 12345, 'status': 'shipped'})

        # .. so only the commits that follow the invocation fail ..
        _arm_commit_failure()

        # .. and the response of the invocation is complete.
        self.response.payload = {'cid': self.cid, 'result': ModuleCtx.Result_Published}

# ################################################################################################################################
# ################################################################################################################################

class AuditFailureError(Service):
    """ Publishes one message, makes the commits of the database fail and raises an exception.
    """

    name = 'test.reliability.database-file.audit-failure.error'

    def handle(self) -> 'None':

        # The message is committed before the commits start to fail ..
        _ = self.publish(ModuleCtx.Audit_Failure_Topic, {'order_id': 12345, 'status': 'rejected'})

        # .. so only the commits that follow the invocation fail ..
        _arm_commit_failure()

        # .. and the invocation ends with an error.
        raise Exception(ModuleCtx.Invocation_Error)

# ################################################################################################################################
# ################################################################################################################################
