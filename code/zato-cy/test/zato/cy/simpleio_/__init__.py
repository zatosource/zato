# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from sys import maxint
from tempfile import NamedTemporaryFile
from unittest import TestCase

# Bunch
from bunch import bunchify

# ConfigObj
from configobj import ConfigObj

# Zato
from zato.cli.create_server import get_bytes_to_str_encoding, simple_io_conf_contents
from zato.common.util.simpleio import get_sio_server_config

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################

test_class_name = '<my-test-class>'

# ################################################################################################################################
# ################################################################################################################################

class BaseTestCase(TestCase):

# ################################################################################################################################

    def setUp(self):
        self.maxDiff = maxint

# ################################################################################################################################

    def get_server_config(self):

        with NamedTemporaryFile() as f:
            f.write(simple_io_conf_contents.format(bytes_to_str_encoding=get_bytes_to_str_encoding()))
            f.flush()

            sio_fs_config = ConfigObj(f.name)
            sio_fs_config = bunchify(sio_fs_config)

        return get_sio_server_config(sio_fs_config)

# ################################################################################################################################

    def get_sio(self, declaration, class_):

        sio = CySimpleIO(self.get_server_config(), declaration)
        sio.build(class_)

        return sio

# ################################################################################################################################
# ################################################################################################################################
