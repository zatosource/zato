#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from future.standard_library import install_aliases
install_aliases()

# stdlib
import argparse

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# Zato
from zato.cli import apispec as apispec_mod, ca_create_ca as ca_create_ca_mod, ca_create_lb_agent as ca_create_lb_agent_mod, \
     ca_create_scheduler as ca_create_scheduler_mod, ca_create_server as ca_create_server_mod, \
     ca_create_web_admin as ca_create_web_admin_mod, check_config as check_config_mod, \
     component_version as component_version_mod, create_cluster as create_cluster_mod, \
     create_lb as create_lb_mod, create_odb as create_odb_mod, create_scheduler as create_scheduler_mod, \
     create_server as create_server_mod, create_web_admin as create_web_admin_mod, crypto as crypto_mod, \
     delete_odb as delete_odb_mod, enmasse as enmasse_mod, FromConfig, info as info_mod, migrate as migrate_mod, \
     quickstart as quickstart_mod, run_command, service as service_mod, sso as sso_mod, start as start_mod, \
     stop as stop_mod, web_admin_auth as web_admin_auth_mod
from zato.common import version

def add_opts(parser, opts):
    """ Adds parser-specific options.
    """
    for opt in opts:
        arguments = {}
        for name in ('help', 'action', 'default', 'choices', 'type'):
            # Almost no command uses 'action' or 'default' parameters
            if name in opt:
                arguments[name] = opt[name]

        parser.add_argument(opt['name'], **arguments)

def get_parser():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--store-log', help='Whether to store an execution log', action='store_true')
    base_parser.add_argument('--verbose', help='Show verbose output', action='store_true')
    base_parser.add_argument(
        '--store-config',
        help='Whether to store config options in a file for a later use', action='store_true')

    parser = argparse.ArgumentParser(prog='zato')
    parser.add_argument('--version', action='version', version=version)

    subs = parser.add_subparsers()


    #
    # apispec
    #
    apispec = subs.add_parser(
        'apispec',
        description='API specifications generator',
        parents=[base_parser])
    apispec.set_defaults(command='apispec')
    apispec.add_argument('path', help='Path to a Zato server')
    add_opts(apispec, apispec_mod.APISpec.opts)

    #
    # ca
    #
    ca = subs.add_parser('ca', description='Basic certificate authority (CA) management')
    ca_subs = ca.add_subparsers()
    ca_create = ca_subs.add_parser('create', description='Creates crypto material for Zato components')
    ca_create_subs = ca_create.add_subparsers()

    ca_create_ca = ca_create_subs.add_parser('ca', description=ca_create_ca_mod.Create.__doc__, parents=[base_parser])
    ca_create_ca.set_defaults(command='ca_create_ca')
    ca_create_ca.add_argument('path', help='Path to an empty directory to hold the CA')
    add_opts(ca_create_ca, ca_create_ca_mod.Create.opts)

    ca_create_lb_agent = ca_create_subs.add_parser('lb_agent', description=ca_create_lb_agent_mod.Create.__doc__, parents=[base_parser])
    ca_create_lb_agent.set_defaults(command='ca_create_lb_agent')
    ca_create_lb_agent.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_lb_agent, ca_create_lb_agent_mod.Create.opts)

    ca_create_scheduler = ca_create_subs.add_parser('scheduler', description=ca_create_scheduler_mod.Create.__doc__, parents=[base_parser])
    ca_create_scheduler.set_defaults(command='ca_create_scheduler')
    ca_create_scheduler.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_scheduler, ca_create_scheduler_mod.Create.opts)

    ca_create_server = ca_create_subs.add_parser('server', description=ca_create_server_mod.Create.__doc__, parents=[base_parser])
    ca_create_server.set_defaults(command='ca_create_server')
    ca_create_server.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_server, ca_create_server_mod.Create.opts)

    ca_create_web_admin = ca_create_subs.add_parser('web_admin', description=ca_create_web_admin_mod.Create.__doc__, parents=[base_parser])
    ca_create_web_admin.set_defaults(command='ca_create_web_admin')
    ca_create_web_admin.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_web_admin, ca_create_web_admin_mod.Create.opts)

    #
    # check-config
    #
    check_config = subs.add_parser(
        'check-config',
        description='Checks config of a Zato component (currently limited to servers only)',
        parents=[base_parser])
    check_config.set_defaults(command='check_config')
    check_config.add_argument('path', help='Path to a Zato component')
    add_opts(check_config, check_config_mod.CheckConfig.opts)

    #
    # component-version
    #
    component_version = subs.add_parser(
        'component-version',
        description='Shows the version of a Zato component installed in a given directory',
        parents=[base_parser])
    component_version.set_defaults(command='component_version')
    component_version.add_argument('path', help='Path to a Zato component')
    add_opts(component_version, component_version_mod.ComponentVersion.opts)

    #
    # create
    #
    create = subs.add_parser('create', description='Creates new Zato components')
    create_subs = create.add_subparsers()

    create_cluster = create_subs.add_parser('cluster', description=create_cluster_mod.Create.__doc__, parents=[base_parser])
    create_cluster.set_defaults(command='create_cluster')
    add_opts(create_cluster, create_cluster_mod.Create.opts)

    create_lb = create_subs.add_parser('load_balancer', description=create_lb_mod.Create.__doc__, parents=[base_parser])
    create_lb.add_argument('path', help='Path to an empty directory to install the load-balancer in')
    create_lb.set_defaults(command='create_lb')
    add_opts(create_lb, create_lb_mod.Create.opts)

    create_odb = create_subs.add_parser('odb', description=create_odb_mod.Create.__doc__, parents=[base_parser])
    create_odb.set_defaults(command='create_odb')
    add_opts(create_odb, create_odb_mod.Create.opts)

    create_scheduler = create_subs.add_parser('scheduler', description=create_scheduler_mod.Create.__doc__, parents=[base_parser])
    create_scheduler.add_argument('path', help='Path to an empty directory to install the scheduler in')
    create_scheduler.set_defaults(command='create_scheduler')
    add_opts(create_scheduler, create_scheduler_mod.Create.opts)

    create_key = create_subs.add_parser('secret_key', description=crypto_mod.CreateSecretKey.__doc__, parents=[base_parser])
    create_key.set_defaults(command='create_secret_key')
    add_opts(create_key, crypto_mod.CreateSecretKey.opts)

    create_server = create_subs.add_parser('server', description=create_server_mod.Create.__doc__, parents=[base_parser])
    create_server.add_argument('path', help='Path to an empty directory to install the server in')
    create_server.set_defaults(command='create_server')
    add_opts(create_server, create_server_mod.Create.opts)

    create_user = create_subs.add_parser('user', description=web_admin_auth_mod.CreateUser.__doc__, parents=[base_parser])
    create_user.add_argument('path', help='Path to a web admin')
    create_user.set_defaults(command='create_user')
    add_opts(create_user, web_admin_auth_mod.CreateUser.opts)

    create_web_admin = create_subs.add_parser('web_admin', description=create_web_admin_mod.Create.__doc__, parents=[base_parser])
    create_web_admin.add_argument('path', help='Path to an empty directory to install a new web admin in')
    create_web_admin.set_defaults(command='create_web_admin')
    add_opts(create_web_admin, create_web_admin_mod.Create.opts)

    #
    # crypto
    #
    crypto = subs.add_parser('crypto', description='Cryptographic operations')
    crypto_subs = crypto.add_subparsers()

    crypto_create_secret_key = crypto_subs.add_parser('create-secret-key',
        description=crypto_mod.CreateSecretKey.__doc__, parents=[base_parser])
    crypto_create_secret_key.set_defaults(command='crypto_create_secret_key')
    add_opts(crypto_create_secret_key, crypto_mod.CreateSecretKey.opts)

    #
    # decrypt
    #
    decrypt = subs.add_parser('decrypt', description=crypto_mod.Decrypt.__doc__, parents=[base_parser])
    decrypt.add_argument('path', help='Path to the private key in PEM')
    decrypt.set_defaults(command='decrypt')
    add_opts(decrypt, crypto_mod.Decrypt.opts)

    #
    # delete
    #
    delete = subs.add_parser('delete', description=delete_odb_mod.Delete.__doc__)
    delete_subs = delete.add_subparsers()
    delete_odb = delete_subs.add_parser('odb', description='Deletes a Zato ODB', parents=[base_parser])
    delete_odb.set_defaults(command='delete_odb')
    add_opts(delete_odb, delete_odb_mod.Delete.opts)

    #
    # encrypt
    #
    encrypt = subs.add_parser('encrypt', description=crypto_mod.Encrypt.__doc__, parents=[base_parser])
    encrypt.add_argument('path', help='Path to the public key in PEM')
    encrypt.set_defaults(command='encrypt')
    add_opts(encrypt, crypto_mod.Encrypt.opts)

    #
    # enmasse
    #
    enmasse = subs.add_parser('enmasse', description=enmasse_mod.EnMasse.__doc__, parents=[base_parser])
    enmasse.add_argument('path', help='Path to a running Zato server')
    enmasse.set_defaults(command='enmasse')
    add_opts(enmasse, enmasse_mod.EnMasse.opts)

    #
    # update
    #
    hash = subs.add_parser('hash', description='Updates Zato components and users')
    hash_subs = hash.add_subparsers()

    # .. hash info

    hash_get_rounds = hash_subs.add_parser('get-rounds', description=crypto_mod.GetHashRounds.__doc__, parents=[base_parser])
    hash_get_rounds.set_defaults(command='hash_get_rounds')
    add_opts(hash_get_rounds, crypto_mod.GetHashRounds.opts)

    #
    # info
    #
    info = subs.add_parser('info', description=info_mod.Info.__doc__, parents=[base_parser])
    info.add_argument('path', help='Path to a Zato component')
    info.set_defaults(command='info')
    add_opts(info, info_mod.Info.opts)

    #
    # from-config-file
    #
    from_config = subs.add_parser('from-config', description=FromConfig.__doc__, parents=[base_parser])
    from_config.add_argument('path', help='Path to a Zato command config file')
    from_config.set_defaults(command='from_config')

    #
    # migrate
    #
    migrate = subs.add_parser('migrate', description=migrate_mod.Migrate.__doc__, parents=[base_parser])
    migrate.add_argument('path', help='Path to a Zato component')
    migrate.set_defaults(command='migrate')
    add_opts(migrate, migrate_mod.Migrate.opts)

    #
    # quickstart
    #
    quickstart = subs.add_parser('quickstart', description='Quickly set up and manage Zato clusters', parents=[base_parser])
    quickstart_subs = quickstart.add_subparsers()

    quickstart_create = quickstart_subs.add_parser('create', description=quickstart_mod.Create.__doc__, parents=[base_parser])
    quickstart_create.add_argument('path', help='Path to an empty directory for the quickstart cluster')
    quickstart_create.set_defaults(command='quickstart_create')
    add_opts(quickstart_create, quickstart_mod.Create.opts)

    #
    # service
    #
    service = subs.add_parser('service', description='Commands related to the management of Zato services')
    service_subs = service.add_subparsers()

    service_invoke = service_subs.add_parser('invoke', description=service_mod.Invoke.__doc__, parents=[base_parser])
    service_invoke.set_defaults(command='service_invoke')
    add_opts(service_invoke, service_mod.Invoke.opts)

    #
    # sso
    #
    sso = subs.add_parser('sso', description='SSO management')
    sso_subs = sso.add_subparsers()

    #
    # create-user
    #
    sso_create_user = sso_subs.add_parser('create-user', description=sso_mod.CreateUser.__doc__, parents=[base_parser])
    sso_create_user.add_argument('path', help='Path to a Zato server')
    sso_create_user.set_defaults(command='sso_create_user')
    add_opts(sso_create_user, sso_mod.CreateUser.opts)

    #
    # create-super-user
    #
    sso_create_super_user = sso_subs.add_parser(
        'create-super-user', description=sso_mod.CreateSuperUser.__doc__, parents=[base_parser])
    sso_create_super_user.add_argument('path', help='Path to a Zato server')
    sso_create_super_user.set_defaults(command='sso_create_super_user')
    add_opts(sso_create_super_user, sso_mod.CreateSuperUser.opts)

    #
    # lock-user
    #
    sso_lock_user = sso_subs.add_parser('lock-user', description=sso_mod.LockUser.__doc__, parents=[base_parser])
    sso_lock_user.add_argument('path', help='Path to a Zato server')
    sso_lock_user.set_defaults(command='sso_lock_user')
    add_opts(sso_lock_user, sso_mod.LockUser.opts)

    #
    # unlock-user
    #
    sso_unlock_user = sso_subs.add_parser('unlock-user', description=sso_mod.UnlockUser.__doc__, parents=[base_parser])
    sso_unlock_user.add_argument('path', help='Path to a Zato server')
    sso_unlock_user.set_defaults(command='sso_unlock_user')
    add_opts(sso_unlock_user, sso_mod.UnlockUser.opts)

    #
    # delete-user
    #
    sso_delete_user = sso_subs.add_parser('delete-user', description=sso_mod.DeleteUser.__doc__, parents=[base_parser])
    sso_delete_user.add_argument('path', help='Path to a Zato server')
    sso_delete_user.set_defaults(command='sso_delete_user')
    add_opts(sso_delete_user, sso_mod.DeleteUser.opts)

    #
    # change-user-password
    #
    sso_change_user_password = sso_subs.add_parser(
        'change-user-password', description=sso_mod.ChangeUserPassword.__doc__, parents=[base_parser])
    sso_change_user_password.add_argument('path', help='Path to a Zato server')
    sso_change_user_password.set_defaults(command='sso_change_user_password')
    add_opts(sso_change_user_password, sso_mod.ChangeUserPassword.opts)

    #
    # reset-user-password
    #
    sso_reset_user_password = sso_subs.add_parser(
        'reset-user-password', description=sso_mod.ResetUserPassword.__doc__, parents=[base_parser])
    sso_reset_user_password.add_argument('path', help='Path to a Zato server')
    sso_reset_user_password.set_defaults(command='sso_reset_user_password')
    add_opts(sso_reset_user_password, sso_mod.ResetUserPassword.opts)

    #
    # reset-user-password
    #
    sso_create_odb = sso_subs.add_parser(
        'create-odb', description=sso_mod.CreateODB.__doc__, parents=[base_parser])
    sso_create_odb.set_defaults(command='sso_create_odb')
    add_opts(sso_create_odb, sso_mod.CreateODB.opts)

    #
    # start
    #
    start = subs.add_parser(
        'start', description=start_mod.Start.__doc__, parents=[base_parser], formatter_class=argparse.RawDescriptionHelpFormatter)
    start.add_argument('path', help='Path to the Zato component to be started')
    start.set_defaults(command='start')
    add_opts(start, start_mod.Start.opts)

    #
    # stop
    #
    stop = subs.add_parser('stop', description=stop_mod.Stop.__doc__, parents=[base_parser])
    stop.add_argument('path', help='Path to the Zato component to be stopped')
    stop.set_defaults(command='stop')

    #
    # update
    #
    update = subs.add_parser('update', description='Updates Zato components and users')
    update_subs = update.add_subparsers()

    # .. update crypto

    update_crypto = update_subs.add_parser('crypto', description=crypto_mod.UpdateCrypto.__doc__, parents=[base_parser])
    update_crypto.add_argument('path', help='Path to a Zato component')
    update_crypto.set_defaults(command='update_crypto')
    add_opts(update_crypto, crypto_mod.UpdateCrypto.opts)

    # .. update password

    update_password = update_subs.add_parser(
        'password', description=web_admin_auth_mod.UpdatePassword.__doc__, parents=[base_parser])
    update_password.add_argument('path', help='Path to a web admin directory')
    update_password.set_defaults(command='update_password')
    add_opts(update_password, web_admin_auth_mod.UpdatePassword.opts)

    return parser

def main():
    return run_command(get_parser().parse_args())
