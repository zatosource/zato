# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import simple_io_conf_contents
from zato.common.util import get_config_from_string

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class SimpleIOConfig(BaseTestCase):

# ################################################################################################################################

    def test_default_config(self):
        config = get_config_from_string(simple_io_conf_contents)

        print(111, config)

# ################################################################################################################################
# ################################################################################################################################
