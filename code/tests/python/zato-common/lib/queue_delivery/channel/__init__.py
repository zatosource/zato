# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the suites of REST and SOAP channels with the queue on build on - a session that starts the server before enmasse
# runs, because a channel's service has to be deployed before the channel can point to it, and the helpers that call
# a channel over HTTP and read back what its service recorded.
