# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The tests of pulls build their messages with the helpers of the writer tests
_writer_tests_dir = os.path.join(os.path.dirname(__file__), '..', 'pubsub_writer_process')
sys.path.insert(0, os.path.abspath(_writer_tests_dir))
