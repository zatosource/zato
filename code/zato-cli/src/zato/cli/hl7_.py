# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import sys

# Zato
from zato.cli import ZatoCommand
from zato.hl7.mllp.client import send_data as send_mllp_data

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

        for name in ('file', 'address'):
            value = getattr(args, name, None)
            if not value:
                self.logger.warning('Missing required parameter --%s', name)
                sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        file_path = os.path.join(self.original_dir, args.file)
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            self.logger.warning('File path not found `%s`', file_path)
            sys.exit(self.SYS_ERROR.FILE_MISSING)

        if not os.path.isfile(file_path):
            self.logger.warning('Path is not a file `%s`', file_path)
            sys.exit(self.SYS_ERROR.PATH_NOT_A_FILE)

        # Now, read the file as bytes ..
        data = open(file_path, 'rb').read()

        # .. send it to the remote end ..
        response = send_mllp_data(args.address, data) # type: bytes

        # .. and print the response back.
        self.logger.info('Response: `%s`', response)

# ################################################################################################################################
