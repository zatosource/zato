# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from logging import DEBUG
from pprint import pprint

# Django
from django.conf import settings
from django.template import Context, Template

# Zato
from zato.server.service import Service

# Configure Django settings when the module is picked up
if not settings.configured:
    settings.configure()

# ################################################################################################################################

class Echo(Service):
    """ Copies request over to response.
    """
    def handle(self):
        self.response.payload = self.request.raw_request

# ################################################################################################################################

class InputLogger(Service):
    """ Writes out all input data to server logs.
    """
    def handle(self):
        pass
    
    def finalize_handle(self):
        self.log_input()

# ################################################################################################################################

class SIOInputLogger(Service):
    """ Writes out all SIO input parameters to server logs.
    """
    def handle(self):
        self.logger.info('%r', self.request.input)

# ################################################################################################################################

class HTMLService(Service):
    def set_html_payload(self, ctx, template):

        # Generate HTML and return response
        c = Context(ctx)
        t = Template(template)
        payload = t.render(c).encode('utf-8')
        
        self.logger.debug('Ctx:[%s]', ctx)
        self.logger.debug('Payload:[%s]', payload)
        
        if self.logger.isEnabledFor(DEBUG):
            buff = StringIO()
            pprint(ctx, buff)
            self.logger.debug(buff.getvalue())
            buff.close()
        
        self.response.payload = payload
        self.response.content_type = 'text/html; charset=utf-8'

# ################################################################################################################################