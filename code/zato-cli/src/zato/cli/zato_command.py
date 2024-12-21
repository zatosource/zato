#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import ArgumentParser
    from zato.common.typing_ import any_, callnone, dictlist, strlist, tuple_
    callnone = callnone

# ################################################################################################################################
# ################################################################################################################################

class CommandStore:

    def add_opts(self, parser:'ArgumentParser', opts:'dictlist') -> 'None':
        """ Adds parser-specific options.
        """
        for opt in opts:
            arguments = {}
            for name in ('help', 'action', 'default', 'choices', 'type'):
                # Almost no command uses 'action' or 'default' parameters
                if name in opt:
                    arguments[name] = opt[name]

            parser.add_argument(opt['name'], **arguments)

# ################################################################################################################################

    def build_core_parser(self) -> 'tuple_':

        # stdlib
        import argparse

        base_parser = argparse.ArgumentParser(add_help=False)
        base_parser.add_argument('--store-log', help='Whether to store an execution log', action='store_true')
        base_parser.add_argument('--verbose', help='Show verbose output', action='store_true')
        base_parser.add_argument(
            '--store-config',
            help='Whether to store config options in a file for a later use', action='store_true')

        parser = argparse.ArgumentParser(prog='zato')
        subs = parser.add_subparsers()

        return parser, base_parser, subs, argparse.RawDescriptionHelpFormatter

# ################################################################################################################################

    def load_start_parser(
        self,
        parser=None,         # type: ArgumentParser | None
        base_parser=None,    # type: ArgumentParser | None
        subs=None,           # type: any_
        formatter_class=None # type: callnone
    ) -> 'ArgumentParser':

        # Zato
        from zato.cli import start as start_mod

        if not parser:
            parser, base_parser, subs, formatter_class = self.build_core_parser()

        #
        # start
        #
        start_ = subs.add_parser(
            'start', description=start_mod.Start.__doc__, parents=[base_parser], formatter_class=formatter_class)
        start_.add_argument('path', help='Path to the Zato component to be started')
        start_.set_defaults(command='start')
        self.add_opts(start_, start_mod.Start.opts)

        return cast_('ArgumentParser', parser)

    add_start_server_parser = load_start_parser

# ################################################################################################################################

    def load_version_parser(self) -> 'ArgumentParser':
        parser, _, _, _ = self.build_core_parser()
        self._add_version(parser)
        return parser

# ################################################################################################################################

    def _add_version(self, parser:'ArgumentParser') -> 'None':

        # Zato
        from zato.common.version import get_version

        parser.add_argument('--version', action='version', version=get_version())

# ################################################################################################################################

    def load_full_parser(self) -> 'ArgumentParser':

        # Zato
        from zato.cli import \
             apispec             as apispec_mod,             \
             ca_create_ca        as ca_create_ca_mod,        \
             ca_create_lb_agent  as ca_create_lb_agent_mod,  \
             ca_create_scheduler as ca_create_scheduler_mod, \
             ca_create_server    as ca_create_server_mod,    \
             ca_create_web_admin as ca_create_web_admin_mod, \
             cache               as cache_mod,               \
             check_config        as check_config_mod,        \
             component_version   as component_version_mod,   \
             create_cluster      as create_cluster_mod,      \
             create_lb           as create_lb_mod,           \
             create_odb          as create_odb_mod,          \
             create_scheduler    as create_scheduler_mod,    \
             create_server       as create_server_mod,       \
             create_web_admin    as create_web_admin_mod,    \
             crypto              as crypto_mod,              \
             delete_odb          as delete_odb_mod,          \
             enmasse             as enmasse_mod,             \
             FromConfig,                                     \
             hl7_                as hl7_mod,                 \
             ide                 as ide_mod,                 \
             info                as info_mod,                \
             openapi_            as openapi_mod,             \
             quickstart          as quickstart_mod,          \
             service             as service_mod,             \
             sso                 as sso_mod,                 \
             stop                as stop_mod,                \
             wait                as wait_mod,                \
             web_admin_auth      as web_admin_auth_mod,      \
             wsx                 as wsx_mod # noqa: E272

        # Zato - Pub/sub
        from zato.cli.pubsub import \
            cleanup              as pubsub_cleanup_mod,      \
            endpoint             as pubsub_endpoint_mod,     \
            topic                as pubsub_topic_mod # noqa: E272

        # Zato - REST
        from zato.cli.rest import \
            channel              as rest_channel_mod  # noqa: E272

        # Zato - Security
        from zato.cli.security import \
            api_key              as sec_api_key_mod,         \
            basic_auth           as sec_basic_auth_mod # noqa: E272

        parser, base_parser, subs, formatter_class = self.build_core_parser()
        self._add_version(parser)

        #
        # apispec
        #
        apispec = subs.add_parser(
            'apispec',
            description='API specifications generator',
            parents=[base_parser])
        apispec.set_defaults(command='apispec')
        apispec.add_argument('path', help='Path to a Zato server')
        self.add_opts(apispec, apispec_mod.APISpec.opts)

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
        self.add_opts(ca_create_ca, ca_create_ca_mod.Create.opts)

        ca_create_lb_agent = ca_create_subs.add_parser(
            'lb_agent', description=ca_create_lb_agent_mod.Create.__doc__, parents=[base_parser])
        ca_create_lb_agent.set_defaults(command='ca_create_lb_agent')
        ca_create_lb_agent.add_argument('path', help='Path to a CA directory')
        self.add_opts(ca_create_lb_agent, ca_create_lb_agent_mod.Create.opts)

        ca_create_scheduler = ca_create_subs.add_parser(
            'scheduler', description=ca_create_scheduler_mod.Create.__doc__, parents=[base_parser])
        ca_create_scheduler.set_defaults(command='ca_create_scheduler')
        ca_create_scheduler.add_argument('path', help='Path to a CA directory')
        self.add_opts(ca_create_scheduler, ca_create_scheduler_mod.Create.opts)

        ca_create_server = ca_create_subs.add_parser(
            'server', description=ca_create_server_mod.Create.__doc__, parents=[base_parser])
        ca_create_server.set_defaults(command='ca_create_server')
        ca_create_server.add_argument('path', help='Path to a CA directory')
        self.add_opts(ca_create_server, ca_create_server_mod.Create.opts)

        ca_create_web_admin = ca_create_subs.add_parser(
            'web_admin', description=ca_create_web_admin_mod.Create.__doc__, parents=[base_parser])
        ca_create_web_admin.set_defaults(command='ca_create_web_admin')
        ca_create_web_admin.add_argument('path', help='Path to a CA directory')
        self.add_opts(ca_create_web_admin, ca_create_web_admin_mod.Create.opts)

        #
        # cache
        #
        cache = subs.add_parser(
            'cache', description='Cache keys - get, set, delete or expire keys and more', parents=[base_parser])
        cache_subs = cache.add_subparsers()

        cache_get = cache_subs.add_parser('get', description=cache_mod.CacheGet.__doc__, parents=[base_parser])
        cache_get.set_defaults(command='cache_get')
        self.add_opts(cache_get, cache_mod.CacheGet.opts)

        cache_set = cache_subs.add_parser('set', description=cache_mod.CacheSet.__doc__, parents=[base_parser])
        cache_set.set_defaults(command='cache_set')
        self.add_opts(cache_set, cache_mod.CacheSet.opts)

        cache_delete = cache_subs.add_parser('delete', description=cache_mod.CacheDelete.__doc__, parents=[base_parser])
        cache_delete.set_defaults(command='cache_delete')
        self.add_opts(cache_delete, cache_mod.CacheDelete.opts)

        #
        # change-password
        #
        change_password = subs.add_parser(
            'change-password',
            description="Changes a security definition's password",
            parents=[base_parser])
        change_password.set_defaults(command='change_password')
        self.add_opts(change_password, sec_basic_auth_mod.ChangePassword.opts)

        #
        # check-config
        #
        check_config = subs.add_parser(
            'check-config',
            description='Checks config of a Zato component (currently limited to servers only)',
            parents=[base_parser])
        check_config.set_defaults(command='check_config')
        check_config.add_argument('path', help='Path to a Zato component')
        self.add_opts(check_config, check_config_mod.CheckConfig.opts)

        #
        # component-version
        #
        component_version = subs.add_parser(
            'component-version',
            description='Shows the version of a Zato component installed in a given directory',
            parents=[base_parser])
        component_version.set_defaults(command='component_version')
        component_version.add_argument('path', help='Path to a Zato component')
        self.add_opts(component_version, component_version_mod.ComponentVersion.opts)

        #
        # create
        #
        create = subs.add_parser('create', description='Creates new Zato components')
        create_subs = create.add_subparsers()

        create_api_key = create_subs.add_parser(
            'api-key', description=sec_api_key_mod.CreateDefinition.__doc__, parents=[base_parser])
        create_api_key.set_defaults(command='create_api_key')
        self.add_opts(create_api_key, sec_api_key_mod.CreateDefinition.opts)

        create_basic_auth = create_subs.add_parser(
            'basic-auth', description=sec_basic_auth_mod.CreateDefinition.__doc__, parents=[base_parser])
        create_basic_auth.set_defaults(command='create_basic_auth')
        self.add_opts(create_basic_auth, sec_basic_auth_mod.CreateDefinition.opts)

        create_cluster = create_subs.add_parser(
            'cluster', description=create_cluster_mod.Create.__doc__, parents=[base_parser])
        create_cluster.set_defaults(command='create_cluster')
        self.add_opts(create_cluster, create_cluster_mod.Create.opts)

        create_lb = create_subs.add_parser('load-balancer', description=create_lb_mod.Create.__doc__, parents=[base_parser])
        create_lb.add_argument('path', help='Path to an empty directory to install the load-balancer in')
        create_lb.set_defaults(command='create_lb')
        self.add_opts(create_lb, create_lb_mod.Create.opts)

        create_odb = create_subs.add_parser('odb', description=create_odb_mod.Create.__doc__, parents=[base_parser])
        create_odb.set_defaults(command='create_odb')
        self.add_opts(create_odb, create_odb_mod.Create.opts)

        create_scheduler = create_subs.add_parser(
            'scheduler', description=create_scheduler_mod.Create.__doc__, parents=[base_parser])
        create_scheduler.add_argument('path', help='Path to an empty directory to install the scheduler in')
        create_scheduler.set_defaults(command='create_scheduler')
        self.add_opts(create_scheduler, create_scheduler_mod.Create.opts)

        create_key = create_subs.add_parser('secret-key', description=crypto_mod.CreateSecretKey.__doc__, parents=[base_parser])
        create_key.set_defaults(command='create_secret_key')
        self.add_opts(create_key, crypto_mod.CreateSecretKey.opts)

        create_server = create_subs.add_parser('server', description=create_server_mod.Create.__doc__, parents=[base_parser])
        create_server.add_argument('path', help='Path to an empty directory to install the server in')
        create_server.set_defaults(command='create_server')
        self.add_opts(create_server, create_server_mod.Create.opts)

        create_user = create_subs.add_parser('user', description=web_admin_auth_mod.CreateUser.__doc__, parents=[base_parser])
        create_user.add_argument('path', help='Path to a web-admin instance')
        create_user.set_defaults(command='create_user')
        self.add_opts(create_user, web_admin_auth_mod.CreateUser.opts)

        create_web_admin = create_subs.add_parser(
            'web-admin', description=create_web_admin_mod.Create.__doc__, parents=[base_parser])
        create_web_admin.add_argument('path', help='Path to an empty directory to install a new web admin in')
        create_web_admin.set_defaults(command='create_web_admin')
        self.add_opts(create_web_admin, create_web_admin_mod.Create.opts)

        #
        # create-rest-channel
        #

        create_rest_channel = subs.add_parser('create-rest-channel',
            description=rest_channel_mod.CreateChannel.__doc__, parents=[base_parser])
        create_rest_channel.set_defaults(command='create_rest_channel')
        self.add_opts(create_rest_channel, rest_channel_mod.CreateChannel.opts)

        #
        # create-wsx-channel
        #

        create_wsx_channel = subs.add_parser('create-wsx-channel',
            description=wsx_mod.CreateChannel.__doc__, parents=[base_parser])
        create_wsx_channel.set_defaults(command='create_wsx_channel')
        self.add_opts(create_wsx_channel, wsx_mod.CreateChannel.opts)

        #
        # create-wsx-outconn
        #

        create_wsx_outconn = subs.add_parser('create-wsx-outconn',
            description=wsx_mod.CreateOutconn.__doc__, parents=[base_parser])
        create_wsx_outconn.set_defaults(command='create_wsx_outconn')
        self.add_opts(create_wsx_outconn, wsx_mod.CreateOutconn.opts)

        #
        # crypto
        #
        crypto = subs.add_parser('crypto', description='Cryptographic operations')
        crypto_subs = crypto.add_subparsers()

        crypto_create_secret_key = crypto_subs.add_parser('create-secret-key',
            description=crypto_mod.CreateSecretKey.__doc__, parents=[base_parser])
        crypto_create_secret_key.set_defaults(command='crypto_create_secret_key')
        self.add_opts(crypto_create_secret_key, crypto_mod.CreateSecretKey.opts)

        #
        # decrypt
        #
        decrypt = subs.add_parser('decrypt', description=crypto_mod.Decrypt.__doc__, parents=[base_parser])
        decrypt.set_defaults(command='decrypt')
        self.add_opts(decrypt, crypto_mod.Decrypt.opts)

        #
        # delete
        #
        delete = subs.add_parser('delete', description=delete_odb_mod.Delete.__doc__)
        delete_subs = delete.add_subparsers()

        delete_api_key = delete_subs.add_parser('api-key', description='Deletes an API key definition',
            parents=[base_parser])
        delete_api_key.set_defaults(command='delete_api_key')
        self.add_opts(delete_api_key, sec_basic_auth_mod.DeleteDefinition.opts)

        delete_basic_auth = delete_subs.add_parser('basic-auth', description='Deletes a Basic Auth definition',
            parents=[base_parser])
        delete_basic_auth.set_defaults(command='delete_basic_auth')
        self.add_opts(delete_basic_auth, sec_basic_auth_mod.DeleteDefinition.opts)

        delete_odb = delete_subs.add_parser('odb', description='Deletes a Zato ODB', parents=[base_parser])
        delete_odb.set_defaults(command='delete_odb')

        self.add_opts(delete_odb, delete_odb_mod.Delete.opts)

        #
        # delete-rest-channel
        #

        delete_rest_channel = subs.add_parser('delete-rest-channel',
            description=rest_channel_mod.DeleteChannel.__doc__, parents=[base_parser])
        delete_rest_channel.set_defaults(command='delete_rest_channel')
        self.add_opts(delete_rest_channel, rest_channel_mod.DeleteChannel.opts)

        #
        # delete-wsx-channel
        #

        delete_wsx_channel = subs.add_parser('delete-wsx-channel',
            description=wsx_mod.DeleteChannel.__doc__, parents=[base_parser])
        delete_wsx_channel.set_defaults(command='delete_wsx_channel')
        self.add_opts(delete_wsx_channel, wsx_mod.DeleteChannel.opts)

        #
        # delete-wsx-channel
        #

        delete_wsx_outconn = subs.add_parser('delete-wsx-outconn',
            description=wsx_mod.DeleteOutconn.__doc__, parents=[base_parser])
        delete_wsx_outconn.set_defaults(command='delete_wsx_outconn')
        self.add_opts(delete_wsx_outconn, wsx_mod.CreateOutconn.opts)

        #
        # encrypt
        #

        encrypt = subs.add_parser('encrypt', description=crypto_mod.Encrypt.__doc__, parents=[base_parser])
        encrypt.set_defaults(command='encrypt')
        self.add_opts(encrypt, crypto_mod.Encrypt.opts)

        #
        # enmasse
        #
        enmasse = subs.add_parser('enmasse', description=enmasse_mod.Enmasse.__doc__, parents=[base_parser])
        enmasse.add_argument('path', help='Path to a running Zato server')
        enmasse.set_defaults(command='enmasse')
        self.add_opts(enmasse, enmasse_mod.Enmasse.opts)

        #
        # update
        #
        hash = subs.add_parser('hash', description='Updates Zato components and users')
        hash_subs = hash.add_subparsers()

        #
        # from-config-file
        #
        from_config = subs.add_parser('from-config', description=FromConfig.__doc__, parents=[base_parser])
        from_config.add_argument('path', help='Path to a Zato command config file')
        from_config.set_defaults(command='from_config')

        # .. hash info

        hash_get_rounds = hash_subs.add_parser('get-rounds', description=crypto_mod.GetHashRounds.__doc__, parents=[base_parser])
        hash_get_rounds.set_defaults(command='hash_get_rounds')
        self.add_opts(hash_get_rounds, crypto_mod.GetHashRounds.opts)

        #
        # hl7
        #
        hl7 = subs.add_parser('hl7', description='HL7-related commands')
        hl7_subs = hl7.add_subparsers()

        hl7_mllp_send = hl7_subs.add_parser('mllp-send', description=hl7_mod.MLLPSend.__doc__, parents=[base_parser])
        hl7_mllp_send.set_defaults(command='hl7_mllp_send')
        self.add_opts(hl7_mllp_send, hl7_mod.MLLPSend.opts)

        #
        # IDE
        #
        ide = subs.add_parser('set-ide-password', description=ide_mod.SetIDEPassword.__doc__, parents=[base_parser])
        ide.add_argument('path', help='Path to a Zato server')
        ide.set_defaults(command='set_ide_password')
        self.add_opts(ide, ide_mod.SetIDEPassword.opts)

        #
        # info
        #
        info = subs.add_parser('info', description=info_mod.Info.__doc__, parents=[base_parser])
        info.add_argument('path', help='Path to a Zato component')
        info.set_defaults(command='info')
        self.add_opts(info, info_mod.Info.opts)

        #
        # openapi
        #
        openapi = subs.add_parser(
            'openapi',
            description='OpenAPI specification generator',
            parents=[base_parser])
        openapi.set_defaults(command='openapi')
        openapi.add_argument('path', help='Path to a Zato server')
        self.add_opts(openapi, openapi_mod.OpenAPI.opts)

        #
        # pubsub
        #
        pubsub = subs.add_parser('pubsub', description='Publish/subscribe topics and message queues')
        pubsub_subs = pubsub.add_subparsers()

        #
        # pubsub cleanup
        #

        pubsub_cleanup = pubsub_subs.add_parser('cleanup',
            description=pubsub_cleanup_mod.Cleanup.__doc__, parents=[base_parser])
        pubsub_cleanup.set_defaults(command='pubsub_cleanup')
        self.add_opts(pubsub_cleanup, pubsub_cleanup_mod.Cleanup.opts)

        #
        # pubsub create-endpoint
        #

        pubsub_create_endpoint = pubsub_subs.add_parser('create-endpoint',
            description=pubsub_endpoint_mod.CreateEndpoint.__doc__, parents=[base_parser])
        pubsub_create_endpoint.set_defaults(command='pubsub_create_endpoint')
        self.add_opts(pubsub_create_endpoint, pubsub_endpoint_mod.CreateEndpoint.opts)

        #
        # pubsub create-topic
        #

        pubsub_create_topic = pubsub_subs.add_parser('create-topic',
            description=pubsub_topic_mod.CreateTopic.__doc__, parents=[base_parser])
        pubsub_create_topic.set_defaults(command='pubsub_create_topic')
        self.add_opts(pubsub_create_topic, pubsub_topic_mod.CreateTopic.opts)

        #
        # pubsub create-topics
        #

        pubsub_create_test_topics = pubsub_subs.add_parser('create-test-topics',
            description=pubsub_topic_mod.CreateTestTopics.__doc__, parents=[base_parser])
        pubsub_create_test_topics.set_defaults(command='pubsub_create_test_topics')
        self.add_opts(pubsub_create_test_topics, pubsub_topic_mod.CreateTestTopics.opts)

        #
        # pubsub delete-endpoint
        #

        pubsub_delete_endpoint = pubsub_subs.add_parser('delete-endpoint',
            description=pubsub_endpoint_mod.DeleteEndpoint.__doc__, parents=[base_parser])
        pubsub_delete_endpoint.set_defaults(command='pubsub_delete_endpoint')
        self.add_opts(pubsub_delete_endpoint, pubsub_endpoint_mod.DeleteEndpoint.opts)

        #
        # pubsub delete-topic (an alias for delete-topics)
        #

        pubsub_delete_topic = pubsub_subs.add_parser('delete-topic',
            description=pubsub_topic_mod.DeleteTopics.__doc__, parents=[base_parser])
        pubsub_delete_topic.set_defaults(command='pubsub_delete_topic')
        self.add_opts(pubsub_delete_topic, pubsub_topic_mod.DeleteTopics.opts)

        #
        # pubsub delete-topics
        #

        pubsub_delete_topics = pubsub_subs.add_parser('delete-topics',
            description=pubsub_topic_mod.DeleteTopics.__doc__, parents=[base_parser])
        pubsub_delete_topics.set_defaults(command='pubsub_delete_topics')
        self.add_opts(pubsub_delete_topics, pubsub_topic_mod.DeleteTopics.opts)

        #
        # pubsub get-topic (alias to get-topics)
        #

        pubsub_get_topic = pubsub_subs.add_parser('get-topic',
            description=pubsub_topic_mod.GetTopics.__doc__, parents=[base_parser])
        pubsub_get_topic.set_defaults(command='pubsub_get_topic')
        self.add_opts(pubsub_get_topic, pubsub_topic_mod.GetTopics.opts)

        #
        # pubsub get-topics
        #

        pubsub_get_topics = pubsub_subs.add_parser('get-topics',
            description=pubsub_topic_mod.GetTopics.__doc__, parents=[base_parser])
        pubsub_get_topics.set_defaults(command='pubsub_get_topics')
        self.add_opts(pubsub_get_topics, pubsub_topic_mod.GetTopics.opts)

        #
        # reset-totp-key
        #
        reset_totp_key = subs.add_parser('reset-totp-key',
            description=web_admin_auth_mod.ResetTOTPKey.__doc__, parents=[base_parser])
        reset_totp_key.add_argument('path', help='Path to web-admin')
        reset_totp_key.set_defaults(command='reset_totp_key')
        self.add_opts(reset_totp_key, web_admin_auth_mod.ResetTOTPKey.opts)

        #
        # set-admin-invoke-password
        #
        set_admin_invoke_password = subs.add_parser('set-admin-invoke-password',
            description=web_admin_auth_mod.SetAdminInvokePassword.__doc__, parents=[base_parser])
        set_admin_invoke_password.add_argument('path', help='Path to web-admin')
        set_admin_invoke_password.set_defaults(command='set_admin_invoke_password')
        self.add_opts(set_admin_invoke_password, web_admin_auth_mod.SetAdminInvokePassword.opts)

        #
        # quickstart
        #
        quickstart = subs.add_parser('quickstart', description='Quickly set up and manage Zato clusters', parents=[base_parser])
        quickstart_subs = quickstart.add_subparsers()

        quickstart_create = quickstart_subs.add_parser('create', description=quickstart_mod.Create.__doc__, parents=[base_parser])
        quickstart_create.add_argument('path', help='Path to an empty directory for the quickstart cluster')
        quickstart_create.set_defaults(command='quickstart_create')
        self.add_opts(quickstart_create, quickstart_mod.Create.opts)

        #
        # service
        #
        service = subs.add_parser('service', description='Commands related to the management of Zato services')
        service_subs = service.add_subparsers()

        service_invoke = service_subs.add_parser('invoke', description=service_mod.Invoke.__doc__, parents=[base_parser])
        service_invoke.set_defaults(command='service_invoke')
        self.add_opts(service_invoke, service_mod.Invoke.opts)

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
        self.add_opts(sso_create_user, sso_mod.CreateUser.opts)

        #
        # create-super-user
        #
        sso_create_super_user = sso_subs.add_parser(
            'create-super-user', description=sso_mod.CreateSuperUser.__doc__, parents=[base_parser])
        sso_create_super_user.add_argument('path', help='Path to a Zato server')
        sso_create_super_user.set_defaults(command='sso_create_super_user')
        self.add_opts(sso_create_super_user, sso_mod.CreateSuperUser.opts)

        #
        # lock-user
        #
        sso_lock_user = sso_subs.add_parser('lock-user', description=sso_mod.LockUser.__doc__, parents=[base_parser])
        sso_lock_user.add_argument('path', help='Path to a Zato server')
        sso_lock_user.set_defaults(command='sso_lock_user')
        self.add_opts(sso_lock_user, sso_mod.LockUser.opts)

        #
        # login
        #
        sso_login = sso_subs.add_parser('login', description=sso_mod.Login.__doc__, parents=[base_parser])
        sso_login.add_argument('path', help='Path to a Zato server')
        sso_login.set_defaults(command='sso_login')
        self.add_opts(sso_login, sso_mod.Login.opts)

        #
        # logout
        #
        sso_logout = sso_subs.add_parser('logout', description=sso_mod.Logout.__doc__, parents=[base_parser])
        sso_logout.add_argument('path', help='Path to a Zato server')
        sso_logout.set_defaults(command='sso_logout')
        self.add_opts(sso_logout, sso_mod.Logout.opts)

        #
        # unlock-user
        #
        sso_unlock_user = sso_subs.add_parser('unlock-user', description=sso_mod.UnlockUser.__doc__, parents=[base_parser])
        sso_unlock_user.add_argument('path', help='Path to a Zato server')
        sso_unlock_user.set_defaults(command='sso_unlock_user')
        self.add_opts(sso_unlock_user, sso_mod.UnlockUser.opts)

        #
        # delete-user
        #
        sso_delete_user = sso_subs.add_parser('delete-user', description=sso_mod.DeleteUser.__doc__, parents=[base_parser])
        sso_delete_user.add_argument('path', help='Path to a Zato server')
        sso_delete_user.set_defaults(command='sso_delete_user')
        self.add_opts(sso_delete_user, sso_mod.DeleteUser.opts)

        #
        # change-user-password
        #
        sso_change_user_password = sso_subs.add_parser(
            'change-user-password', description=sso_mod.ChangeUserPassword.__doc__, parents=[base_parser])
        sso_change_user_password.add_argument('path', help='Path to a Zato server')
        sso_change_user_password.set_defaults(command='sso_change_user_password')
        self.add_opts(sso_change_user_password, sso_mod.ChangeUserPassword.opts)

        #
        # reset-totp-key (sso)
        #
        sso_reset_totp_key_password = sso_subs.add_parser(
            'reset-totp-key', description=sso_mod.ResetTOTPKey.__doc__, parents=[base_parser])
        sso_reset_totp_key_password.add_argument('path', help='Path to a Zato server')
        sso_reset_totp_key_password.set_defaults(command='sso_reset_totp_key')
        self.add_opts(sso_reset_totp_key_password, sso_mod.ResetTOTPKey.opts)

        #
        # reset-user-password
        #
        sso_reset_user_password = sso_subs.add_parser(
            'reset-user-password', description=sso_mod.ResetUserPassword.__doc__, parents=[base_parser])
        sso_reset_user_password.add_argument('path', help='Path to a Zato server')
        sso_reset_user_password.set_defaults(command='sso_reset_user_password')
        self.add_opts(sso_reset_user_password, sso_mod.ResetUserPassword.opts)

        #
        # create-odb
        #
        sso_create_odb = sso_subs.add_parser(
            'create-odb', description=sso_mod.CreateODB.__doc__, parents=[base_parser])
        sso_create_odb.set_defaults(command='sso_create_odb')
        self.add_opts(sso_create_odb, sso_mod.CreateODB.opts)

        #
        # start
        #
        _ = self.add_start_server_parser(parser, base_parser, subs, formatter_class)

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

        # .. update password

        update_password = update_subs.add_parser(
            'password', description=web_admin_auth_mod.UpdatePassword.__doc__, parents=[base_parser])
        update_password.add_argument('path', help='Path to a web admin directory')
        update_password.set_defaults(command='update_password')
        self.add_opts(update_password, web_admin_auth_mod.UpdatePassword.opts)

        #
        # wait
        #
        wait = subs.add_parser('wait', description=wait_mod.Wait.__doc__, parents=[base_parser])
        wait.set_defaults(command='wait')
        self.add_opts(wait, wait_mod.Wait.opts)

        return parser

command_store = CommandStore()

# ################################################################################################################################

def pre_process_quickstart(sys_argv:'strlist', opts_idx:'int') -> 'None':

    # We know that it exists so we can skip the try/except ValueError: block
    create_idx = sys_argv.index('create')

    # We are looking for the idx of the path element but it is still possible
    # that we have an incomplete command 'zato quickstart create' alone on input.
    # In such a case, 'create' will be our last element among args and we can return immediately.
    if len(sys_argv) == create_idx:
        return

    # If we are here, we have 'zato quickstart create' followed by a path, ODB and Redis options.
    path_idx = create_idx + 1

    # ODB + Redis options start here .
    original_odb_type_idx   = path_idx + 1
    opts = sys_argv[path_idx+1:opts_idx]

    # No options = we can return
    if not opts:
        return

    # Extract the options ..
    odb_type   = opts[0]
    redis_host = opts[1]
    redis_port = opts[2]

    # .. remove them from their pre-3.2 non-optional positions,
    # .. note that we need to do it once for each of odb_type, redis_host and redis_port
    # .. using the same index because .pop will modify the list in place ..
    _ = sys_argv.pop(original_odb_type_idx)
    _ = sys_argv.pop(original_odb_type_idx)
    _ = sys_argv.pop(original_odb_type_idx)

    # .. now, add the options back as '--' ones.
    sys_argv.append('--odb_type')
    sys_argv.append(odb_type)

    sys_argv.append('--kvdb_host')
    sys_argv.append(redis_host)

    sys_argv.append('--kvdb_port')
    sys_argv.append(redis_port)

# ################################################################################################################################

def pre_process_server(sys_argv, opts_idx, opts):
    # type: (list, int, list) -> None

    #
    # This is pre-3.2
    # 'zato0', 'create1', 'server2', '/path/to/server3', 'sqlite4', 'kvdb_host5', 'kvdb_port6', 'cluster_name7', 'server_name8'
    #
    len_pre_32 = 9

    #
    # This is 3.2
    # 'zato0', 'create1', 'server2', '/path/to/server3', 'cluster_name7', 'server_name8'
    #

    # We are turning pre-3.2 options into 3.2 ones.
    if len(sys_argv[:opts_idx]) == len_pre_32:

        # New arguments to produce
        new_argv = []

        new_argv.append(sys_argv[0]) # zato0
        new_argv.append(sys_argv[1]) # create1
        new_argv.append(sys_argv[2]) # server2
        new_argv.append(sys_argv[3]) # /path/to/server3

        new_argv.append(sys_argv[7]) # cluster_name7
        new_argv.append(sys_argv[8]) # server_name8

        new_argv.append('--odb_type') # sqlite4
        new_argv.append(sys_argv[4])

        new_argv.append('--kvdb_host') # kvdb_host5
        new_argv.append(sys_argv[5])

        new_argv.append('--kvdb_port') # kvdb_port6
        new_argv.append(sys_argv[6])

        new_argv.extend(opts)

        # We are ready to replace sys.argv now
        sys_argv[:] = new_argv

# ################################################################################################################################

def pre_process_sys_argv(sys_argv):
    # type: (list) -> None

    # stdlib
    import sys

    # Local aliases
    opts_idx = sys.maxsize

    #
    # We need to find out where flags begin because they are constant
    # and did not change between versions. Only what is before flags was changed.
    #
    # zato command --flag1 --flag2
    #

    for idx, elem in enumerate(sys_argv): # type: str
        if elem.startswith('--'):
            opts_idx = idx
            break

    try:
        qs_idx = sys_argv.index('quickstart', 0, opts_idx)
    except ValueError:
        qs_idx = 0

    # We enter here if it is a quickstart command
    if qs_idx:

        #
        # Quickstart commands
        #

        #
        # Turn a) into b)
        # a) zato quickstart /path [--flags]
        # b) zato quickstart create /path [--flags]
        #

        # This is 3.2
        if 'create' not in sys_argv:
            sys_argv.insert(qs_idx+1, 'create')
            return

        # An earlier version so we need to turn Redis options into what 3.2 expects
        else:
            pre_process_quickstart(sys_argv, opts_idx)
            return

    # Otherwise, it could be a 'zato create <component>' command
    else:
        if 'create' in sys_argv:

            # We want to find the last non-optional element and if opts_idx is the max size,
            # it means that we do not have any such.
            if opts_idx == sys.maxsize:
                opts_idx = len(sys_argv)

            # This is for later use, when we construct a new sys_argv
            opts = sys_argv[opts_idx:]

            if 'server' in sys_argv:
                pre_process_server(sys_argv, opts_idx, opts)
                return

# ################################################################################################################################

def main() -> 'any_':

    # stdlib
    import os
    import sys

    # Used by start/stop commands
    os.environ['ZATO_CURDIR'] = os.getcwd()

    # Special-case the most commonly used commands to make the parser build quickly in these cases.
    has_args = len(sys.argv) > 1

    # First, zato --version
    if has_args and sys.argv[1] == '--version':

        # Zato
        from zato.common.version import get_version

        _ = sys.stdout.write(get_version() + '\n')
        sys.exit(0)

    # Now, zato start ...
    elif has_args and sys.argv[1] == 'start':
        parser = command_store.load_start_parser()

    # All the other commands
    else:

        # Take into account changes introduced between versions
        pre_process_sys_argv(sys.argv)

        # This may change what os.getcwd returns
        parser = command_store.load_full_parser()

        # Set it back for further use after it was potentially reset by command_store.load_full_parser
        os.chdir(os.environ['ZATO_CURDIR'])

    # Parse the arguments
    args = parser.parse_args()

    # Expand user directories to full paths
    if getattr(args, 'path', None):
        args.path = os.path.expanduser(args.path)

    # Exit if no known command was found among arguments ..
    if not hasattr(args, 'command'):
        parser.print_help()

    # .. otherwise, try to run the command now ..
    else:

        # Now that we are here, we also need to check if non-SQLite databases
        # have all their required options on input. We do it here rather than in create_odb.py
        # because we want to report it as soon as possible, before actual commands execute.
        odb_type = getattr(args, 'odb_type', None)
        if odb_type and odb_type != 'sqlite':
            missing = []
            for name in 'odb_db_name', 'odb_host', 'odb_port', 'odb_user':
                if not getattr(args, name, None):
                    missing.append(name)

            if missing:
                missing_noun = 'Option ' if len(missing) == 1 else 'Options '
                missing_verb = ' is '    if len(missing) == 1 else ' are '
                missing.sort()

                _ = sys.stdout.write(
                    missing_noun                  + \
                    '`'                           + \
                    ', '.join(missing)            + \
                    '`'                           + \
                    missing_verb                  + \
                    'required if odb_type is '    + \
                    '`{}`.'.format(args.odb_type) + \
                    '\n'
                )
                sys.exit(1)

        # Zato
        from zato.cli import run_command

        return run_command(args)

# ################################################################################################################################
