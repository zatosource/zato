# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.py23_.spring_ import ServerProxy, SSLClient

class LoadBalancerAgentClient(ServerProxy):
    pass

class TLSLoadBalancerAgentClient(SSLClient):
    pass
