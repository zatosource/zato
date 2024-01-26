# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Import all patterns into one place

from zato.server.pattern.base import FanOut, ParallelExec
from zato.server.pattern.invoke_retry import InvokeRetry

# For flake8
FanOut = FanOut
InvokeRetry = InvokeRetry
ParallelExec = ParallelExec
