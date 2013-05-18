# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Names of AMQP messages exchanged by parallel- and singleton servers. All need
# to be Unicode objects to prevent Carrot from sending them as blobs instead
# of text/plain.

GET_JOB_LIST = u"GET_JOB_LIST"