#!/usr/bin/env python

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys

# Zato
from zato.agent.load_balancer.server import LoadBalancerAgent

if __name__ == '__main__':
    lba = LoadBalancerAgent(sys.argv[1])
    lba.start_load_balancer()
    lba.serve_forever()
