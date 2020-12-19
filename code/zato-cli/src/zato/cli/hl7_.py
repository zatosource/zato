# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################

class MLLPSend(ZatoCommand):
    """ Sends an HL7 v2 file to an MLLP endpoint.
    """
    opts = [
        {'name':'--file', 'help':'File with HL7 v2 data to send', 'required':True},
        {'name':'--address', 'help':'Address of an MLLP server', 'required':True},
    ]

# ################################################################################################################################

    def execute(self, args):

        if not args.file:
            self.logger.warn('Missing required parameter --file')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        if not args.address:
            self.logger.warn('Missing required parameter --address')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        print()
        print(111, args)
        print()

# ################################################################################################################################
