# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


# Zato
from zato.zmq_ import BaseZMQSimple

# ################################################################################################################################

class OutZMQSimple(BaseZMQSimple):
    """ An outgoing ZeroMQ connection of a type other than Majordomo (MDP).
    """
    # Does not override or implement anything above what the parent already does