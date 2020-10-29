# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, sys

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# Zato
from zato.agent.load_balancer.server import LoadBalancerAgent, TLSLoadBalancerAgent
from zato.common.util.api import get_lb_agent_json_config, parse_cmd_line_options, store_pidfile

if __name__ == '__main__':
    repo_dir = sys.argv[1]
    component_dir = os.path.join(repo_dir, '..', '..')

    lba_config = get_lb_agent_json_config(repo_dir)

    # Store agent's pidfile only if we are not running in foreground
    options = parse_cmd_line_options(sys.argv[2])
    if not options.get('fg', None):
        store_pidfile(component_dir, lba_config['pid_file'])

    lba_class = TLSLoadBalancerAgent if lba_config.get('is_tls_enabled', True) else LoadBalancerAgent

    lba = lba_class(repo_dir)
    lba.start_load_balancer()
    lba.serve_forever()
