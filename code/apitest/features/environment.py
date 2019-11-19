# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.apitest.util import new_context

def before_feature(context, feature):
    environment_dir = os.path.dirname(os.path.realpath(__file__))
    context.zato = new_context(None, environment_dir)
