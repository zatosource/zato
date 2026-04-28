# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import sys
from getpass import getpass

# Zato
from zato.common.util.backup.command_backup import command_backup
from zato.common.util.backup.command_cleanup import command_cleanup
from zato.common.util.backup.command_delete import command_delete
from zato.common.util.backup.command_list import command_list
from zato.common.util.backup.command_test import command_test
from zato.common.util.backup.common import _json_response, _write_response
from zato.common.util.backup.config import BackupConfig
from zato.common.util.backup.redis_ import _build_config_from_redis, _load_password_from_redis

# ################################################################################################################################
# ################################################################################################################################

def _build_config_from_args(args:'argparse.Namespace') -> 'BackupConfig':
    """ Builds a BackupConfig from CLI args, optionally loading defaults from Redis first.
    """
    if args.fernet_key:
        config = _build_config_from_redis(args.fernet_key)
    else:
        config = BackupConfig()

    if args.env_dir:
        config.env_dir = args.env_dir

    if args.provider:
        config.provider = args.provider

    if args.bucket:
        config.bucket_name = args.bucket

    if args.access_key:
        config.access_key = args.access_key

    if args.secret_key:
        config.secret_key = args.secret_key

    return config

# ################################################################################################################################

def _validate_config(config:'BackupConfig') -> 'None':
    """ Validates that all required fields are present. Writes JSON error and exits if not.
    """
    if not config.provider:
        response = _json_response(False, error='--provider is required (aws, gcs, azure)')
        _write_response(response)
        sys.exit(1)

    if not config.bucket_name:
        response = _json_response(False, error='--bucket is required')
        _write_response(response)
        sys.exit(1)

# ################################################################################################################################

def _resolve_password(args:'argparse.Namespace', config:'BackupConfig') -> 'str':
    """ Resolves the backup encryption password from args, Redis, or interactive prompt.
    """
    if args.password:
        return args.password

    if args.fernet_key:
        return _load_password_from_redis(config, args.fernet_key)

    return getpass('Backup encryption password: ')

# ################################################################################################################################

def _add_common_args(parser:'argparse.ArgumentParser') -> 'None':
    parser.add_argument('--fernet-key', default='')
    parser.add_argument('--dir', dest='env_dir', default='')
    parser.add_argument('--provider', default='')
    parser.add_argument('--bucket', default='')
    parser.add_argument('--access-key', default='')
    parser.add_argument('--secret-key', default='')

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    parser = argparse.ArgumentParser(description='Zato environment backup tool')
    subparsers = parser.add_subparsers(dest='command')

    # backup
    backup_parser = subparsers.add_parser('backup')
    backup_parser.add_argument('--password', default='')
    _add_common_args(backup_parser)

    # list
    list_parser = subparsers.add_parser('list')
    _add_common_args(list_parser)

    # test
    test_parser = subparsers.add_parser('test')
    _add_common_args(test_parser)

    # delete
    delete_parser = subparsers.add_parser('delete')
    delete_parser.add_argument('--backup-key', required=True)
    _add_common_args(delete_parser)

    # cleanup
    cleanup_parser = subparsers.add_parser('cleanup')
    cleanup_parser.add_argument('--retention-days', type=int, required=True)
    _add_common_args(cleanup_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = _build_config_from_args(args)
    _validate_config(config)

    # ..  dispatch to the appropriate command handler.

    if args.command == 'backup':

        if not config.env_dir:
            response = _json_response(False, error='--dir is required')
            _write_response(response)
            sys.exit(1)

        password = _resolve_password(args, config)
        command_backup(config, password)

    elif args.command == 'list':
        command_list(config)

    elif args.command == 'test':
        command_test(config)

    elif args.command == 'delete':
        command_delete(config, args.backup_key)

    elif args.command == 'cleanup':
        command_cleanup(config, args.retention_days)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
