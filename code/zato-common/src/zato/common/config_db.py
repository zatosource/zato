# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config DB - what the SQL screen saves are the Zato_Audit_Log_DB_* and Zato_Analytics_DB_*
# environment variables, applied to the running process and persisted into an env.ini file
# so they survive restarts. Both the server-side services and the dashboard process use
# these helpers so the two processes stay in step.

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Where the saved variables are persisted when there is no explicit env file - a dedicated
# subdirectory of the config repo, because the server watches the env file's parent directory
# for changes and scans it for user config, so the file cannot sit next to server.conf itself.
Env_Dir_Name  = 'env'
Env_File_Name = 'env.ini'

# The environment prefixes of the SQL databases the SQL screen knows about
sql_env_prefix_by_database = {
    'audit-log': 'Zato_Audit_Log_DB_',
    'analytics': 'Zato_Analytics_DB_',
    'pubsub':    'Zato_PubSub_DB_',
}

# Maps the SQL form fields to the suffixes of the corresponding environment variables
sql_field_suffixes = {
    'display_name':  'Display_Name',
    'description':   'Description',
    'type':          'Type',
    'host':          'Host',
    'port':          'Port',
    'username':      'Username',
    'password':      'Password',
    'name':          'Name',
    'ssl':           'SSL',
    'ssl_ca_file':   'SSL_CA_File',
    'ssl_cert_file': 'SSL_Cert_File',
    'ssl_key_file':  'SSL_Key_File',
    'ssl_verify':    'SSL_Verify',
}

# ################################################################################################################################
# ################################################################################################################################

def build_env_variables(env_prefix:'str', suffixes:'strstrdict', values:'stranydict') -> 'stranydict':
    """ Turns a dict of form values into a dict of environment variables under a given prefix.
    Booleans become explicit True/False strings so an unchecked box overrides a non-empty
    default, empty strings stay empty and mean the variable is to be removed.
    """

    # Our response to produce
    out:'stranydict' = {}

    for key, suffix in suffixes.items():

        env_name = env_prefix + suffix
        value = values[key]

        if isinstance(value, bool):
            value = str(value)

        out[env_name] = value

    return out

# ################################################################################################################################

def apply_env_variables(env_variables:'stranydict') -> 'int':
    """ Writes a dict of environment variables into this process's environment.
    Empty values delete their variables so the built-in defaults apply again.
    Returns how many variables were set.
    """

    # How many variables were set
    set_count = 0

    for env_name, value in env_variables.items():

        # Non-empty values are set as they are ..
        if value:
            os.environ[env_name] = value
            set_count += 1

        # .. and empty ones remove their variables so the defaults apply again.
        else:
            _ = os.environ.pop(env_name, None)

    return set_count

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
    under gunicorn, a save lands in one worker only - the other workers pick the change up
    through this call. Variables that were removed from the file since the last application
    are deleted from the environment too. Returns True if the file was (re-)applied.
    """

    # Zato
    from zato.common.util.env import populate_environment_from_file

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

def persist_env_variables(env_path:'str', env_variables:'stranydict') -> 'None':
    """ Writes a dict of environment variables into the [env] section of an ini file,
    creating the file and its directory if needed, so the values are re-applied
    on the next start through populate_environment_from_file.
    Empty values remove their keys.
    """

    # Zato
    from zato.common.ext.configobj_ import ConfigObj

    # The file's directory may not exist yet
    env_dir = os.path.dirname(env_path)
    os.makedirs(env_dir, exist_ok=True)

    # Read the file if it exists, start empty otherwise ..
    env_config = ConfigObj(env_path)

    # .. the variables live in the [env] section ..
    if 'env' not in env_config:
        env_config['env'] = {}

    env_section = env_config['env']

    # .. mirror the in-process application - set what is given, drop what is empty ..
    for env_name, value in env_variables.items():

        if value:
            env_section[env_name] = value
        else:
            _ = env_section.pop(env_name, None)

    # .. and write it all back to disk - the filename was set when the object was built.
    env_config.write()

# ################################################################################################################################
# ################################################################################################################################
