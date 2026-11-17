# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The env.ini file under the config repository of a component, whose variables the server and the Dashboard
# apply to their processes at startup, and which the Dashboard applies again whenever the file changes.

# stdlib
import os

# Zato
from zato.common.util.env import populate_environment_from_file

# ################################################################################################################################
# ################################################################################################################################

# Where the env file is kept when there is no explicit one - a dedicated subdirectory of the config repo,
# because the server watches the env file's parent directory for changes and scans it for user config,
# so the file cannot sit next to server.conf itself.
Env_Dir_Name  = 'env'
Env_File_Name = 'env.ini'

# Turns the whole audit log off
Env_Audit_Log_Enabled = 'Zato_Audit_Log_Enabled'

# Whether the audit log is on when its variable is not set
Default_Enabled = True

# ################################################################################################################################
# ################################################################################################################################

def get_default_env_file_path(repo_location:'str') -> 'str':
    """ Returns the path to the default env file under a component's config repo directory.
    """
    out = os.path.join(repo_location, Env_Dir_Name, Env_File_Name)
    return out

# ################################################################################################################################

# The modification time of the env file as of when it was last applied to this process,
# and the keys it carried then - used by refresh_env_from_file to re-apply the file only
# when it actually changed and to delete variables that disappeared from it.
_last_env_file_mtime:'float' = 0.0
_last_env_file_keys:'list' = []

def refresh_env_from_file(env_path:'str') -> 'bool':
    """ Re-applies the variables from an env file when its modification time changed
    since the last call in this process. In multi-worker deployments, e.g. the dashboard
    under gunicorn, each worker picks a change of the file up through this call. Variables that were removed
    from the file since the last application are deleted from the environment too. Returns True if the file was (re-)applied.
    """
    global _last_env_file_mtime, _last_env_file_keys

    # A missing file means there is nothing saved yet
    try:
        mtime = os.path.getmtime(env_path)
    except OSError:
        return False

    # The file has not changed since it was last applied here
    if mtime == _last_env_file_mtime:
        return False

    # Keys applied previously but no longer in the file are to be removed
    to_delete = list(_last_env_file_keys)

    applied_keys = populate_environment_from_file(env_path, to_delete=to_delete, use_print=False)

    _last_env_file_mtime = mtime
    _last_env_file_keys = applied_keys

    return True

# ################################################################################################################################
# ################################################################################################################################
