# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace

# ################################################################################################################################
# ################################################################################################################################

class CreateTopic(ServerAwareCommand):
    """ Creates a new publish/subscribe topic.
    """
    opts = [
        {'name':'--name', 'help':'Name of the topic to create', 'required':False},
        {'name':'--gd',   'help':'Should the topic use Guaranteed Delivery', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server',   'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        service = 'zato.ping'
        request = {}

        response = self.zato_client.invoke(**{
            'name': service,
            'payload': request
        })

        print(111, response)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from os import environ

    # Bunch
    from bunch import Bunch

    args = Bunch()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateTopic(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
