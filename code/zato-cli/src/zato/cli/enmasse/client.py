# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.util.api import get_config, get_odb_session_from_server_config, get_repo_dir_from_component_dir
from zato.common.util.cli import read_stdin_data

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

def get_session_from_server_dir(
    server_dir:'str',
    stdin_data:'strnone'=None,
    ) -> 'any_':
    """ Creates a new SQLAlchemy session based on server configuration.
    """

    # Find repository location from server directory
    repo_location = get_repo_dir_from_component_dir(server_dir)

    # Handle potential stdin data for crypto operations
    stdin_data = stdin_data or read_stdin_data()

    # Initialize crypto manager for decrypting configuration
    crypto_manager = ServerCryptoManager.from_repo_dir(None, repo_location, stdin_data=stdin_data)

    # Read and parse secrets configuration
    secrets_config = ConfigObj(os.path.join(repo_location, 'secrets.conf'), use_zato=False)
    secrets_conf = get_config(
        repo_location,
        'secrets.conf',
        needs_user_config=False,
        crypto_manager=crypto_manager,
        secrets_conf=secrets_config
    )

    # Parse the server configuration file with crypto manager and secrets
    config = get_config(
        repo_location,
        'server.conf',
        crypto_manager=crypto_manager,
        secrets_conf=secrets_conf,
    )

    # Create and return an ODB session from server configuration
    return get_odb_session_from_server_config(config, crypto_manager, False)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # Create a session using the example server path
    server_path = os.path.expanduser('~/env/qs-1/server1')
    session = get_session_from_server_dir(server_path)

    # Execute a simple query
    result = session.execute('select 1+1 as result').scalar()

    # Print the result
    print(f'Query result: {result}')

    # Close the session
    session.close()

# ################################################################################################################################
# ################################################################################################################################
