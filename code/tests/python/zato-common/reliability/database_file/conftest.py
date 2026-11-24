# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The builder of the fault library is shared with the fault suites ..
pubsub_faults_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'pubsub_faults')
pubsub_faults_dir = os.path.abspath(pubsub_faults_dir)
sys.path.insert(0, pubsub_faults_dir)

# .. and the environment of the server of this directory precedes it on the path.
sys.path.insert(0, os.path.dirname(__file__))

# ################################################################################################################################
# ################################################################################################################################
