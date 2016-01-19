# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Carles Sala <csala at delfos.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent import Timeout, sleep

# Zato
from zato.server.service import Service, Integer, Boolean

# ################################################################################################################################

class SlowService(Service):
    def handle(self):
        """ Responds SUCCESS after 2 seconds
        """
        sleep(2)
        self.response.payload = 'SUCCESS'

# ################################################################################################################################

class InvokeSlowService(Service):

    class SimpleIO:
        input_optional = (Integer('timeout'), Boolean('raise_timeout'))
        default_value = None
        output_required = ('result',)

    def handle(self):
        """ Invokes the SlowService with timeout and
        """
        try:
            kwargs = {}
            if self.request.input.timeout:
                kwargs['timeout'] = self.request.input.timeout
            if self.request.input.raise_timeout != None: # nopep8 - This is OK, because it's a boolean and can be False
                kwargs['raise_timeout'] = self.request.input.raise_timeout
            result = self.invoke(SlowService.get_name(), **kwargs)
            self.logger.info('Got result: {}'.format(result))
            self.response.payload.result = result
        except Timeout:
            self.logger.info('Caught Timeout')
            self.response.payload.result = 'TIMEOUT'
