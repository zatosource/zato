# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

class Echo(Service):
    """ Copies request over to response.
    """
    def handle(self):
        self.response.payload = self.request.raw_request

class InputLogger(Service):
    """ Writes out all input data to server logs.
    """
    def handle(self):
        pass
    
    def finalize_handle(self):
        self.log_input()

class SIOInputLogger(Service):
    """ Writes out all SIO input parameters to server logs.
    """
    def handle(self):
        self.logger.info('%r', self.request.input)
