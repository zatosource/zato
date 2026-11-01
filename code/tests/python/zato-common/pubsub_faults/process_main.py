# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Zato server of one fault of a single process - the production traffic through the phases of the fault,
# which the test that started this process applies and removes on request, followed by the checks.
# The exit code is what the test reads.

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_stability_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_stability'))
_perf_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_backend_perf'))
_lib_dir = os.path.abspath(os.path.join(_here, '..', 'lib'))

sys.path.insert(0, _lib_dir)
sys.path.insert(0, _perf_dir)
sys.path.insert(0, _stability_dir)
sys.path.insert(0, _here)

# Zato
from remote import RemoteFault
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    label, fault_name, level, control_dir = sys.argv[1:]

    fault = RemoteFault(fault_name, control_dir)

    run = FaultRun(label)
    run.run(fault, int(level))
    run.check()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
