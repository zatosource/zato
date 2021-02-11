# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# The constants below don't use the Bunch class because we don't need to iterate
# over them at all.

# LMC stands for the 'log message code'
# CID stands for the 'correlation ID'

CID_LENGTH = 24

NULL_LMC = '0000.0000'
NULL_CID = '0' * CID_LENGTH
