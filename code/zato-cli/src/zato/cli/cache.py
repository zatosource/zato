# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys

# Requests
import requests

# Zato
from zato.cli import ManageCommand
from zato.common.util import get_client_from_server_conf
from zato.common.util.cache import Client as CacheClient, CommandConfig

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
    {'name':'--path', 'help':'Path to a local Zato server'},
    {'name':'--is-https', 'help':'When connecting via --path, should HTTPS be used', 'action':'store_true'},
    {'name':'--address', 'help':'HTTP(S) address of a Zato server'},
    {'name':'--username', 'help':'Username to authenticate with to a remote Zato server', 'default':_not_given},
    {'name':'--password', 'help':'Password to authenticate with to a remote Zato server', 'default':_not_given},
    {'name':'--format', 'help':'Response format, one of text, json or table', 'default':'text'},
]

data_type_opts = [
    {'name':'--string-key', 'help':'In get and set operations, whether keys should be treated as strings', 'action':'store_true'},
    {'name':'--int-key', 'help':'In get and set operations, whether keys should be treated as integers', 'action':'store_true'},
    {'name':'--string-value', 'help':'In get and set operations, whether values should be treated as strings', 'action':'store_true'},
    {'name':'--int-value', 'help':'In get and set operations, whether values should be treated as integers', 'action':'store_true'},
]

# ################################################################################################################################
# ################################################################################################################################

class CacheCommand(ManageCommand):
    """ Base class for cache-related commands.
    """
    opts = common_cache_opts

    def _on_server(self, args, _modifiers=_modifiers):
        # type: (Namespace, tuple)

        client = CacheClient.from_server_conf(self.component_dir, args.is_https)

        command = args.command
        command = command.replace('cache_', '') # type: str

        modifier = None # type: str
        for elem in _modifiers:
            if getattr(args, elem, None):
                modifier = elem
                break

        command_config = CommandConfig()
        command_config.command = command
        command_config.key = args.key
        command_config.modifier = modifier
        command_config.is_int_key = args.int_key
        command_config.is_string_key = args.string_key
        command_config.is_int_value = args.int_value
        command_config.is_string_value = args.string_value

        response = client.run_command(command_config)

        # We either report the actual value or an error message.
        value = response.data.value if response.has_value else response.raw

        # Report what was found ..
        sys.stdout.write(value)
        sys.stdout.flush()

        # .. and exit with a non-zero code if there was an error
        if not response.has_value:
            sys.exit(self.SYS_ERROR.CACHE_KEY_NOT_FOUND)

# ################################################################################################################################
# ################################################################################################################################

class CacheGet(CacheCommand):

    opts = common_cache_opts + data_type_opts + [
        {'name':'key', 'help':'Key to use'},
        {'name':'--details', 'help':'Whether to return additional details about data found', 'action':'store_true'},
        {'name':'--by-prefix', 'help':'Get values of keys matching the prefix', 'action':'store_true'},
        {'name':'--by-suffix', 'help':'Get values of keys matching the suffix', 'action':'store_true'},
        {'name':'--by-regex', 'help':'Get values of keys matching the regular expression', 'action':'store_true'},
        {'name':'--contains', 'help':'Get values of keys containing the string', 'action':'store_true'},
        {'name':'--not-contains', 'help':'Get values of keys that do not contain the string', 'action':'store_true'},
        {'name':'--contains-all', 'help':'Get values of keys containing all the strings', 'action':'store_true'},
        {'name':'--contains-any', 'help':'Get values of keys containing at least one of the strings', 'action':'store_true'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheSet(CacheCommand):

    opts = common_cache_opts + data_type_opts + [
        {'name':'--by-prefix', 'help':'Set keys matching the prefix to hold the input value', 'action':'store_true'},
        {'name':'--by-suffix', 'help':'Set keys matching the suffix to hold the input value', 'action':'store_true'},
        {'name':'--by-regex', 'help':'Set keys matching the regular expression to hold the input value', 'action':'store_true'},
        {'name':'--contains', 'help':'Set keys containing the string to hold the input value', 'action':'store_true'},
        {'name':'--not-contains', 'help':'Set keys that do not contain the string to hold the input value', 'action':'store_true'},
        {'name':'--contains-all', 'help':'Set keys containing all the strings to hold the input value', 'action':'store_true'},
        {'name':'--contains-any', 'help':'Set keys containing at least one of the strings to hold the input value',
         'action':'store_true'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheDelete(CacheCommand):

    opts = common_cache_opts + [
        {'name':'--by-prefix', 'help':'Delete keys matching the prefix', 'action':'store_true'},
        {'name':'--by-suffix', 'help':'Delete keys matching the suffix', 'action':'store_true'},
        {'name':'--by-regex', 'help':'Delete keys matching the regular expression', 'action':'store_true'},
        {'name':'--contains', 'help':'Delete keys containing the string', 'action':'store_true'},
        {'name':'--not-contains', 'help':'Delete keys that do not contain the string', 'action':'store_true'},
        {'name':'--contains-all', 'help':'Delete keys containing all the strings', 'action':'store_true'},
        {'name':'--contains-any', 'help':'Delete keys containing at least one of the strings', 'action':'store_true'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheExpire(CacheCommand):

    opts = common_cache_opts + [
        {'name':'--by-prefix', 'help':'Expire keys matching the prefix', 'action':'store_true'},
        {'name':'--by-suffix', 'help':'Expire keys matching the suffix', 'action':'store_true'},
        {'name':'--by-regex', 'help':'Expire keys matching the regular expression', 'action':'store_true'},
        {'name':'--contains', 'help':'Expire keys containing the string', 'action':'store_true'},
        {'name':'--not-contains', 'help':'Expire keys that do not contain the string', 'action':'store_true'},
        {'name':'--contains-all', 'help':'Expire keys containing all the strings', 'action':'store_true'},
        {'name':'--contains-any', 'help':'Expire keys containing at least one of the strings', 'action':'store_true'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheList(CacheCommand):

    opts = common_cache_opts + [
        {'name':'--list', 'help':'List keys in the input cache'},
    ]

# ################################################################################################################################
# ################################################################################################################################

class CacheInfo(CacheCommand):

    opts = common_cache_opts + [
        {'name':'--info', 'help':'Return information about the input cache'},
    ]

# ################################################################################################################################
# ################################################################################################################################
