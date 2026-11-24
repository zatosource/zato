# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server that the faults of one test apply to. Each test starts a server of its own against the database
# that the fixtures of the test selected, with the production traffic, the topics of the expiration probe
# and whatever the test sets before the server starts.

# stdlib
import os

# Zato
from expiration import ExpirationProbe
from pubsub_rest.server import get_fixture_arguments
from pubsub_rest.suite import define_traffic
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.pubsub_profile import Env_DNS_Domain, Env_DNS_Server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from process_faults import Scope
    from pubsub_rest.definition import Definition
    from pubsub_rest.server import PubSubServer
    from zato.common.typing_ import anydict, callable_, strlist, strstrdict

    callable_list = list[callable_]

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages each topic keeps during the runs, which bounds the tables.
_delivered_max_messages = '10000'

# The variables of the test process that the server inherits - the libraries preloaded into the test process
# and the DNS server that the resolver library of the managed modes reads.
_inherited_env_names = ('LD_PRELOAD', Env_DNS_Server, Env_DNS_Domain)

# ################################################################################################################################
# ################################################################################################################################

class FaultServerConfig:
    """ What a test sets before its server starts - the variables added to the environment of the server,
    the command that the server is started through, the transient scope that this command creates,
    and the functions that add what the test needs to the definition of the server.
    """

    def __init__(self) -> 'None':
        self.server_env:'strstrdict' = {}
        self.command_prefix:'strlist' = []
        self.scope:'Scope | None' = None
        self.definers:'callable_list' = []

    def reset(self) -> 'None':
        self.server_env = {}
        self.command_prefix = []
        self.scope = None
        self.definers = []

# What the test that runs at the moment sets before its server starts.
Server_Config = FaultServerConfig()

# ################################################################################################################################
# ################################################################################################################################

def get_inherited_env() -> 'strstrdict':
    out:'strstrdict' = {}

    for name in _inherited_env_names:
        if name in os.environ:
            out[name] = os.environ[name]

    return out

# ################################################################################################################################

def get_fault_fixture_arguments(server:'PubSubServer', config:'FaultServerConfig') -> 'anydict':
    """ The arguments of create_zato_server_fixture that start the server of one test of the fault suites,
    against the database that the environment of the test selects.
    """

    def _setup(server:'PubSubServer', definition:'Definition') -> 'None':

        traffic = define_traffic(server, definition)
        traffic.tracks_deliveries = True

        probe = ExpirationProbe()
        probe.define(server, definition)

        server.server_env[ModuleCtx.Env_Delivered_Max_Messages] = _delivered_max_messages
        server.server_env.update(get_inherited_env())
        server.server_env.update(config.server_env)

        server.command_prefix = config.command_prefix

        for definer in config.definers:
            definer(server, definition)

        server.properties['probe'] = probe
        server.properties['scope'] = config.scope

    out = get_fixture_arguments(server, _setup, scope='function', autouse=False, uses_environment_database=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
