# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# SQLAlchemy
from sqlalchemy import MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError

# Zato
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.util.api import get_config, get_odb_session_from_server_config, get_repo_dir_from_component_dir
from zato.common.util.cli import read_stdin_data

# ################################################################################################################################
# ################################################################################################################################

# Set up logging
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone, boolnone, strdict

# ################################################################################################################################
# ################################################################################################################################

def get_session_from_server_dir(server_dir:'str', stdin_data:'strnone'=None) -> 'any_':
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

def cleanup(prefix:'str', server_dir:'str', stdin_data:'strnone'=None) -> 'None':
    """ Deletes all objects from database tables whose name starts with the given prefix.
    Continues deletion until no errors are raised.
    """
    # Get a session from the server directory
    session = get_session_from_server_dir(server_dir, stdin_data)

    try:
        # Get the engine from the session
        engine = session.bind

        # Create an inspector to examine the database
        inspector = inspect(engine)

        # Reflect metadata to get all tables
        metadata = MetaData()
        metadata.reflect(bind=engine)

        # Get all table names
        table_names = inspector.get_table_names()
        logger.info(f'Found {len(table_names)} tables in database')

        # Store security IDs that need to be cleaned up
        security_ids = []

        # Special handling for sec_base table
        try:
            # First fetch IDs from sec_base that match the prefix
            query = f'SELECT id FROM sec_base WHERE name LIKE "{prefix}%"'
            result = session.execute(query)
            security_ids = [row[0] for row in result.fetchall()]

            if security_ids:
                logger.info(f'Found {len(security_ids)} security ID{"s" if len(security_ids) != 1 else ""} in sec_base with prefix {prefix}')

                # Delete from sec_base
                delete_query = f'DELETE FROM sec_base WHERE name LIKE "{prefix}%"'
                result = session.execute(delete_query)
                session.commit()
                logger.info(f'Deleted {result.rowcount} row{"s" if result.rowcount != 1 else ""} from sec_base with prefix {prefix}')
        except SQLAlchemyError as e:
            session.rollback()
            logger.debug(f'Error handling sec_base: {e}')

        # Find all security tables
        security_tables = [name for name in table_names if name.startswith('sec_') and name != 'sec_base']

        # If we have security IDs to clean up and security tables
        if security_ids and security_tables:
            for table_name in security_tables:
                try:
                    # Delete records with matching IDs
                    if len(security_ids) == 1:
                        query = f'DELETE FROM {table_name} WHERE id = {security_ids[0]}'
                    else:
                        ids_string = ', '.join(str(id) for id in security_ids)
                        query = f'DELETE FROM {table_name} WHERE id IN ({ids_string})'

                    result = session.execute(query)
                    session.commit()

                    if result.rowcount > 0:
                        logger.info(f'Deleted {result.rowcount} row{"s" if result.rowcount != 1 else ""} from {table_name} with ID{"s" if len(security_ids) != 1 else ""} from sec_base')
                except SQLAlchemyError as e:
                    session.rollback()
                    logger.debug(f'Could not delete from {table_name}: {e}')

        # Track if we made any changes
        changes_made = True

        # Continue until no more changes are made
        while changes_made:
            changes_made = False

            # Go through each table
            for table_name in table_names:
                # Skip security tables that we've already handled
                if table_name == 'sec_base' or (table_name.startswith('sec_') and security_ids):
                    continue

                try:
                    # Execute a delete query for objects with names starting with the prefix
                    result = session.execute(
                        f'DELETE FROM {table_name} WHERE name LIKE "{prefix}%"'
                    )

                    # Commit the changes
                    session.commit()

                    # If rows were deleted
                    if result.rowcount > 0:
                        changes_made = True
                        logger.info(f'Deleted {result.rowcount} row{"s" if result.rowcount != 1 else ""} from {table_name} with prefix {prefix}')

                except SQLAlchemyError as e:
                    # Roll back in case of error
                    session.rollback()
                    logger.debug(f'Could not delete from {table_name}: {e}')

                    # If the table doesn't have a name column, try to use an alternate strategy
                    try:
                        # Get column information
                        columns = inspector.get_columns(table_name)
                        column_names = [col['name'] for col in columns]

                        # Look for potential name-like columns
                        name_columns = [col for col in column_names if 'name' in col.lower()]

                        if name_columns:
                            name_col = name_columns[0]  # Use the first name-like column
                            result = session.execute(
                                f'DELETE FROM {table_name} WHERE {name_col} LIKE "{prefix}%"'
                            )
                            session.commit()

                            if result.rowcount > 0:
                                changes_made = True
                                logger.info(f'Deleted {result.rowcount} row{"s" if result.rowcount != 1 else ""} from {table_name} using column {name_col}')
                    except SQLAlchemyError:
                        session.rollback()
                        # Just skip this table if we can't determine how to delete by prefix
                        pass

        logger.info(f'Cleanup completed for prefix {prefix}')

    finally:
        # Always close the session
        session.close()

# ################################################################################################################################

def cleanup_enmasse() -> 'None':
    """ Cleans up all database objects with the 'enmasse' prefix using the default server path.
    """
    server_path = os.path.expanduser('~/env/qs-1/server1')
    cleanup('enmasse', server_path)
    logger.info('Enmasse cleanup completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
