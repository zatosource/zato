# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import secrets

# Zato
from faults import Total_Loss
from managed_faults import CredentialRotationFault
from profiles import get_profile_limits
from run import FaultRun
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# The variable with the path to the file that holds the password of pub/sub.
_env_password_file = 'Zato_PubSub_DB_Password_File'

# How many rotations a run must include at the least.
_min_rotations = 2

# ################################################################################################################################
# ################################################################################################################################

def test_credential_rotation(start_managed:'callable_') -> 'None':
    """ The password of pub/sub changes during the traffic, the existing connections continue,
    and the new connections of the server and of the cleanup process authenticate with the current password
    without a restart.
    """
    limits = get_profile_limits()

    token = secrets.token_hex(4)
    password_path = os.path.join(get_runtime_dir(), f'pubsub-password-{token}')

    try:
        managed = start_managed('credentials', env={_env_password_file: password_path})
        database = managed.database

        with open(password_path, 'w') as password_file:
            _ = password_file.write(database.password)

        fault = CredentialRotationFault(database, password_path, limits.rotation_seconds)

        run = FaultRun(fault.name)
        run.run(fault, Total_Loss)
        run.check()

        assert fault.rotations >= _min_rotations, fault.rotations

    finally:
        if os.path.exists(password_path):
            os.remove(password_path)

# ################################################################################################################################
# ################################################################################################################################
