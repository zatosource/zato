# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ManageCommand

# ################################################################################################################################

if 0:
    # stdlib
    from argparse import Namespace

    # Zato
    from zato.client import JSONResponse

    JSONResponse = JSONResponse
    Namespace = Namespace

# ################################################################################################################################

_not_given = '_zato_not_given'
_modifiers = 'by_prefix', 'by_regex', 'by_suffix', 'contains', 'contains_all', 'contains_any', 'not_contains'

# ################################################################################################################################

common_cache_opts = [
    {'name':'--cache', 'help':'Cache to use, the default one will be used if not given on input', 'default':'default'},
    {'name':'--path', 'help':'Path to a local Zato server', 'default':''},
    {'name':'--is-https', 'help':'When connecting via --path, should HTTPS be used', 'action':'store_true'},
    {'name':'--address', 'help':'HTTP(S) address of a Zato server'},
    {'name':'--username', 'help':'Username to authenticate with to a remote Zato server', 'default':_not_given},
    {'name':'--password', 'help':'Password to authenticate with to a remote Zato server', 'default':_not_given},
]

data_type_opts = [
    {'name':'--string-value', 'help':'In get and set operations, whether values should be treated as strings', 'action':'store_true'},
    {'name':'--int-value', 'help':'In get and set operations, whether values should be treated as integers', 'action':'store_true'},
    {'name':'--bool-value', 'help':'In get and set operations, whether values should be treated as booleans', 'action':'store_true'},
]

# ################################################################################################################################
# ################################################################################################################################

class CacheCommand(ManageCommand):
    """ Base class for cache-related commands.
    """
    opts = common_cache_opts

    def _on_server(self, args, _modifiers=_modifiers):
        # type: (Namespace, tuple)

        # stdlib
        import sys

        # Zato
        from zato.common.api import NotGiven
        from zato.common.util.cache import Client as CacheClient, CommandConfig

        if args.address:
            client = CacheClient.from_dict({
                'address': args.address,
                'username': args.username,
                'password': args.password,
                'cache_name': args.cache,
                'is_https': args.is_https,
            })
        else:
            client = CacheClient.from_server_conf(self.component_dir, args.cache, args.is_https)

        command = args.command
        command = command.replace('cache_', '') # type: str

        modifier = None # type: str
        for elem in _modifiers:
            if getattr(args, elem, None):
                modifier = elem
                break

        command_config = CommandConfig()
        command_config.command = command
        command_config.modifier = modifier
        command_config.key = args.key

        command_config.value = getattr(args, 'value', NotGiven)

        if command_config.command in ('get', 'set'):
            command_config.is_int_value = args.int_value
            command_config.is_string_value = args.string_value
            command_config.is_bool_value = args.bool_value

        response = client.run_command(command_config)

        # Report what was found ..
        sys.stdout.write(response.text)
        sys.stdout.flush()

        # .. and exit with a non-zero code if there was an error
        if not response.has_value:
            sys.exit(self.SYS_ERROR.CACHE_KEY_NOT_FOUND)

# ################################################################################################################################
# ################################################################################################################################

class CacheGet(CacheCommand):

    opts = common_cache_opts + data_type_opts + [
        {'name':'key', 'help':'Key to get value of'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheSet(CacheCommand):

    opts = common_cache_opts + data_type_opts + [
        {'name':'key', 'help':'Key to set value of'},
        {'name':'value', 'help':'Value to set'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheDelete(CacheCommand):

    opts = common_cache_opts + [
        {'name':'key', 'help':'Key to delete'},
    ]

# ################################################################################################################################
# ################################################################################################################################
