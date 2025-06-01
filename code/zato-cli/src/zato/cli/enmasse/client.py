# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError

# Zato
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.odb.model import to_json
from zato.common.odb.query import service_list
from zato.common.util.api import get_config, get_odb_session_from_server_config, get_repo_dir_from_component_dir, utcnow
from zato.common.util.cli import read_stdin_data

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Default timeout = 30 days in seconds
Default_Service_Wait_Timeout = 30 * 24 * 60 * 60  # 30 days

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, bool_, strnone

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

def cleanup(prefixes:list['str'], server_dir:'str', stdin_data:'strnone'=None) -> 'None':
    """ Deletes all objects from database tables whose name starts with any of the given prefixes.
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
            # First fetch IDs from sec_base that match any of the prefixes
            like_clauses = [f'name LIKE "{p}%"' for p in prefixes]
            where_clause = ' OR '.join(like_clauses)
            query = f'SELECT id FROM sec_base WHERE {where_clause}'
            result = session.execute(query)
            security_ids = [row[0] for row in result.fetchall()]

            if security_ids:
                logger.info(f'Found {len(security_ids)} security ID{'s' if len(security_ids) != 1 else ''} in sec_base matching prefixes: {', '.join(prefixes)}') # type: ignore

                # Delete from sec_base
                delete_query = f'DELETE FROM sec_base WHERE {where_clause}'
                result = session.execute(delete_query)
                session.commit()
                logger.info(f'Deleted {result.rowcount} row{'s' if result.rowcount != 1 else ''} from sec_base matching prefixes: {', '.join(prefixes)}')
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
                        logger.info(f'Deleted {result.rowcount} row{'s' if result.rowcount != 1 else ''} from {table_name} with ID{'s' if len(security_ids) != 1 else ''} from sec_base')
                except SQLAlchemyError as e:
                    session.rollback()
                    logger.debug(f'Could not delete from {table_name}: {e}')

        # Special handling for job_interval_based table - need to handle it before job records are deleted
        # as it doesn't have a name column but depends on job_id from the job table
        try:
            # First fetch job IDs from the job table that match any of the prefixes
            like_clauses = [f'name LIKE "{p}%"' for p in prefixes]
            where_clause = ' OR '.join(like_clauses)
            query = f'SELECT id FROM job WHERE {where_clause}'
            result = session.execute(query)
            job_ids = [row[0] for row in result.fetchall()]

            if job_ids:
                logger.info(f'Found {len(job_ids)} job ID{'s' if len(job_ids) != 1 else ''} in job table matching prefixes: {', '.join(prefixes)}')

                # Delete from job_interval_based using the job_ids
                ids_string = ', '.join(str(id) for id in job_ids)
                delete_query = f'DELETE FROM job_interval_based WHERE job_id IN ({ids_string})'

                result = session.execute(delete_query)
                session.commit()
                logger.info(f'Deleted {result.rowcount} row{'s' if result.rowcount != 1 else ''} from job_interval_based linked to jobs matching prefixes: {', '.join(prefixes)}')
        except SQLAlchemyError as e:
            session.rollback()
            logger.debug(f'Error handling job_interval_based cleanup: {e}')

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
                    # Check if the table has a 'name' column
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    if 'name' in columns:
                        # Execute a delete query for objects with names starting with any of the prefixes
                        like_clauses = [f'name LIKE "{p}%"' for p in prefixes]
                        where_clause = ' OR '.join(like_clauses)
                        result = session.execute(
                            f'DELETE FROM {table_name} WHERE {where_clause}'
                        )

                        # Commit the changes
                        session.commit()

                        # If rows were deleted
                        if result.rowcount > 0:
                            changes_made = True
                            logger.info(f'Deleted {result.rowcount} row{'s' if result.rowcount != 1 else ''} from {table_name} matching prefixes: {', '.join(prefixes)}')
                    else:
                        logger.debug(f'Table {table_name} does not have a "name" column, skipping name-based delete.')

                except SQLAlchemyError as e:

                    # Roll back in case of error
                    session.rollback()
                    logger.debug(f'Could not delete from {table_name}: {e}')

        logger.info(f'Cleanup completed for prefixes: {', '.join(prefixes)}')

    finally:
        # Always close the session
        session.close()

# ################################################################################################################################

def cleanup_enmasse() -> 'None':
    """ Cleans up all database objects with the 'enmasse' prefix using the default server path.
    """
    server_path = os.path.expanduser('~/env/qs-1/server1')
    cleanup(['enmasse', 'test_sync_group'], server_path)
    logger.info('Enmasse cleanup completed for prefixes: enmasse, test_sync_group')

# ################################################################################################################################

def wait_for_services(
    config_dict:'anydict',
    server_dir:'str',
    stdin_data:'strnone'=None,
    timeout_seconds:'int'=Default_Service_Wait_Timeout,
    log_after_seconds:'int'=3
) -> 'bool_':
    """ Waits for all services defined in the configuration to be available in the database.
    """
    # Get a session from the server directory
    session = get_session_from_server_dir(server_dir, stdin_data)

    # Build list of unique service names from the configuration
    service_names = set()

    # Extract service names from channel_rest definitions if present
    if channel_rest := config_dict.get('channel_rest'):
        for item in channel_rest:
            if service := item.get('service'):
                service_names.add(service)

    # Extract service names from scheduler definitions if present
    if scheduler := config_dict.get('scheduler'):
        for item in scheduler:
            if service := item.get('service'):
                service_names.add(service)

    # If no services to check, return True immediately
    if not service_names:
        return True

    service_count = len(service_names)
    service_label = 'service' if service_count == 1 else 'services'
    logger.info(f'Waiting for {service_count} {service_label} to be available: {sorted(service_names)}')

    # Track start time for timeout calculation and logging delay
    start_time = utcnow()
    should_log = False
    last_log_time = utcnow()

    try:
        # Keep checking until all services are found or timeout is reached
        while True:
            current_time = utcnow()

            # Check if timeout has been reached
            elapsed_seconds = (current_time - start_time).total_seconds()
            # Ensure both are float for comparison
            if elapsed_seconds > float(timeout_seconds):
                logger.warning(f'Timeout of {timeout_seconds} seconds reached while waiting for {service_label}')
                return False

            # Determine if we should start logging based on elapsed time
            # Ensure both are float for comparison
            if not should_log and elapsed_seconds >= float(log_after_seconds):
                should_log = True
                logger.info(f'Still waiting for {service_label} after {log_after_seconds} seconds')

            # Get list of all available non-internal services
            db_services = service_list(session, 1, return_internal=False)
            db_services = to_json(db_services)
            db_service_names = set()

            for service in db_services:
                db_service_names.add(service['name'])

            # Find missing services
            missing_services = service_names - db_service_names

            # If no services are missing, return success
            if not missing_services:
                logger.info(f'All required {service_label} found in the database')
                return True

            # Log missing services and wait before retrying (but not too frequently)
            missing_count = len(missing_services)
            missing_label = 'service' if missing_count == 1 else 'services'

            if should_log and (current_time - last_log_time).total_seconds() >= 1.0:
                logger.info(f'Waiting for {missing_count} missing {missing_label}: {sorted(missing_services)}')
                last_log_time = current_time

            time.sleep(0.1)

    except Exception:
        logger.error(f'Exception while waiting for services: {format_exc()}')
        return False

    finally:
        # Always close the session
        session.close()

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
