# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import CommonObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class DeleteCommon(ServerAwareCommand):
    """ A base class for CLI commands that delete objects.
    """

    # This will be populated by subclasses
    object_type = CommonObject.Invalid

    opts = [
        {'name':'--id',       'help':'An exact ID of an object to delete', 'required':False},
        {'name':'--id-list',  'help':'A list of object IDs to delete', 'required':False},
        {'name':'--name',     'help':'An exact name of an object to delete', 'required':False},
        {'name':'--name-list','help':'List of objects to delete', 'required':False},
        {'name':'--pattern',  'help':'All objects with names that contain this pattern', 'required':False},
        {'name':'--path',     'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # stdlib
        import sys

        # This will be built based on the option provided by user
        request = {
            'object_type': self.object_type,
        }

        options = ['--id', '--id-list', '--name', '--name-list', '--pattern']
        for name in options:
            arg_attr = name.replace('--', '')
            arg_attr = arg_attr.replace('-', '_')
            value = getattr(args, arg_attr, None)
            if value:
                request[arg_attr] = value
                break

        if not request:
            options = ', '.join(options)
            self.logger.warn(f'Missing input. One of the following is expected: {options}')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        # Our service to invoke
        service = 'zato.common.delete-objects'

        # Invoke the service and log the response it produced
        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################
