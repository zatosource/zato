# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates initial cluster data.
    """
    opts = []

    opts.append({'name':'cluster_name', 'help':'Name of the cluster to create'})
    opts.append({'name':'--lb-host', 'help':'Load-balancer host', 'default':'127.0.0.1'})
    opts.append({'name':'--lb-port', 'help':'Load-balancer port', 'default':'11223'})
    opts.append({'name':'--lb-agent_port', 'help':'Load-balancer agent\'s port', 'default':'20151'})
    opts.append({'name':'--secret-key', 'help':'Secret key that servers will use for decryption and decryption'})
    opts.append({'name':'--admin-invoke-password', 'help':'Password for config API clients to connect to servers with'})
    opts.append({'name':'--skip-if-exists',
        'help':'Return without raising an error if cluster already exists', 'action':'store_true'})

# ################################################################################################################################

    def execute(self, args, show_output=True):

        if show_output:
            if self.verbose:
                msg = 'Successfully created a new cluster [{}]'.format(args.cluster_name)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

# ################################################################################################################################
