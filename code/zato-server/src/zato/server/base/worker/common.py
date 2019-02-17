# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


class WorkerImpl(object):
    """ Base class for objects that implement worker functionality. Does not implement anything itself,
    instead serving as a common marker for all derived subclasses.
    """
    def __init__(self):
        self.server = None
        self.worker_idx = None
        self.url_data = None

