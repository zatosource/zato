# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


# Zato
from zato.cli import ZatoCommand
from zato.common.util import get_client_from_server_conf

# ################################################################################################################################

if 0:
    # stdlib
    from argparse import Namespace

    Namespace = Namespace

# ################################################################################################################################

class Cache(ZatoCommand):
    """ Base class for cache-related commands.
    """
    opts = [
        {'name':'--cache', 'help':'Cache to use, the default one will be used if not given on input', 'default':'default'},

        {'name':'--get', 'help':'Get value of key'},
        {'name':'--get-by-prefix', 'help':'Get values of keys matching the prefix'},
        {'name':'--get-by-suffix', 'help':'Get values of keys matching the suffix'},
        {'name':'--get-by-regex', 'help':'Get values of keys matching the regular expression'},
        {'name':'--get-contains', 'help':'Get values of keys containing the string'},
        {'name':'--get-not-contains', 'help':'Get values of keys that do not contain the string'},
        {'name':'--get-contains-all', 'help':'Get values of keys containing all the strings'},
        {'name':'--get-contains-any', 'help':'Get values of keys containing at least one of the strings'},

        {'name':'--set', 'help':'Set key to hold the input value'},
        {'name':'--set-by-prefix', 'help':'Set keys matching the prefix to hold the input value'},
        {'name':'--set-by-suffix', 'help':'Set keys matching the suffix to hold the input value'},
        {'name':'--set-by-regex', 'help':'Set keys matching the regular expression to hold the input value'},
        {'name':'--set-contains', 'help':'Set keys containing the string to hold the input value'},
        {'name':'--set-not-contains', 'help':'Set keys that do not contain the string to hold the input value'},
        {'name':'--set-contains-all', 'help':'Set keys containing all the strings to hold the input value'},
        {'name':'--set-contains-any', 'help':'Set keys containing at least one of the strings to hold the input value'},

        {'name':'--delete', 'help':'Delete a matching key'},
        {'name':'--delete-by-prefix', 'help':'Delete keys matching the prefix'},
        {'name':'--delete-by-suffix', 'help':'Delete keys matching the suffix'},
        {'name':'--delete-by-regex', 'help':'Delete keys matching the regular expression'},
        {'name':'--delete-contains', 'help':'Delete keys containing the string'},
        {'name':'--delete-not-contains', 'help':'Delete keys that do not contain the string'},
        {'name':'--delete-contains-all', 'help':'Delete keys containing all the strings'},
        {'name':'--delete-contains-any', 'help':'Delete keys containing at least one of the strings'},

        {'name':'--expire', 'help':'Expire a matching key'},
        {'name':'--expire-by-prefix', 'help':'Expire keys matching the prefix'},
        {'name':'--expire-by-suffix', 'help':'Expire keys matching the suffix'},
        {'name':'--expire-by-regex', 'help':'Expire keys matching the regular expression'},
        {'name':'--expire-contains', 'help':'Expire keys containing the string'},
        {'name':'--expire-not-contains', 'help':'Expire keys that do not contain the string'},
        {'name':'--expire-contains-all', 'help':'Expire keys containing all the strings'},
        {'name':'--expire-contains-any', 'help':'Expire keys containing at least one of the strings'},

        {'name':'--string', 'help':'In get and set operations, values should be treated as strings'},
        {'name':'--int', 'help':'In get and set operations, values should be treated as integers'},

        {'name':'--list', 'help':'List keys in the input cache'},
        {'name':'--info', 'help':'Return information about the input cache'},
        {'name':'--details', 'help':'In get operations, return additional details about keys'},
    ]

    def execute(self, args):
        # type: (Namespace) -> object

        self.logger.warn('QQQ %s', args)

# ################################################################################################################################
