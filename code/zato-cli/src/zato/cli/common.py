# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import CommonObject, NotGiven

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import strdict, strdictnone, strlist, strnone
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

class CreateCommon(ServerAwareCommand):
    """ A base class for CLI commands that create objects.
    """

    # These will be populated by subclasses
    object_type = CommonObject.Invalid
    prefix = CommonObject.Prefix_Invalid

    opts = [
        {'name':'--count', 'help':'How many objects to create', 'required':False},
        {'name':'--prefix', 'help':'Prefix that each of the topics to be created will have', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':False},
        {'name':'--endpoints-per-topic',
            'help':'How many endpoints to create per each topic', 'required':False, 'default':3, 'type':int},
        {'name':'--messages-per-pub',
            'help':'How many messages to publish from each publisher', 'required':False, 'default':10, 'type':int},
        {'name':'--msg-size',
            'help':'How big, in kilobytes, each published message should be', 'required':False, 'default':3, 'type':int},
        {'name':'--needs-stdout',
            'help':'Whether to log default messages to stdout', 'required':False, 'default':NotGiven},
    ]

# ################################################################################################################################

    def invoke_common(
        self,
        service:'str',
        object_type: 'strnone',
        name_list:'strlist',
        *,
        args:'Namespace | None'=None,
        needs_stdout:'bool'=True,
        initial_data:'strdictnone'=None,
    ) -> 'strdict':

        # stdlib
        from zato.common.util import as_bool

        request:'strdict' = {
            'object_type': object_type,
            'name_list': name_list,
            'initial_data': initial_data,
        }

        if args and (args_needs_stdout := args.needs_stdout):
            args_needs_stdout = as_bool(args_needs_stdout)
            needs_stdout = args_needs_stdout

        # Invoke the service and log the response it produced
        response = self._invoke_service_and_log_response(service, request, needs_stdout=needs_stdout)

        return response

# ################################################################################################################################

    def invoke_common_create(self,
        object_type: 'strnone',
        name_list:'strlist',
        *,
        args:'Namespace | None'=None,
        needs_stdout:'bool'=True,
        initial_data:'strdictnone'=None,
    ) -> 'strdict':

        service = 'zato.common.create-objects'
        response = self.invoke_common(
            service, object_type, name_list, args=args, needs_stdout=needs_stdout, initial_data=initial_data)
        return response

# ################################################################################################################################

    def execute(self, args:'Namespace') -> 'strdict':

        # Local variables
        default_count = 1000

        # Read the parameters from the command line or fall back on the defaults
        count = int(args.count or default_count)
        prefix = args.prefix or self.prefix

        # Find out to how many digits we should fill tha names
        digits = len(str(count))

        # The list to create
        name_list = []

        for idx, _ in enumerate(range(count), 1):
            idx = str(idx).zfill(digits)
            topic_name = f'{prefix}{idx}'
            name_list.append(topic_name)

        # Invoke the service
        response = self.invoke_common_create(self.object_type, name_list, args=args)

        return response

# ################################################################################################################################
# ################################################################################################################################
