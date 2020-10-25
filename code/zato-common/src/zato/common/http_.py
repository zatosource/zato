# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from http.client import responses

# https://tools.ietf.org/html/rfc6585
TOO_MANY_REQUESTS = 429

HTTP_RESPONSES = deepcopy(responses)
HTTP_RESPONSES[TOO_MANY_REQUESTS] = 'Too Many Requests'
