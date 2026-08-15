# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# How long the archive build runs for, in seconds - longer than its gateway's invoke timeout
_archive_build_seconds = 10

# The bytes of the badge image - a PNG header, which is not valid UTF-8
_badge_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'

# ################################################################################################################################
# ################################################################################################################################

class ArchiveBuild(Service):
    """ Builds a full archive of a customer's records - pass the customer id to archive.
    """

    name = 'crm.archive.build'
    input = 'customer_id'

    def handle(self):

        # Building the archive takes longer than the gateway allows a call to run
        time.sleep(_archive_build_seconds)

        self.response.payload = {'customer_id': self.request.input.customer_id, 'archived': True}

# ################################################################################################################################
# ################################################################################################################################

class BadgeRender(Service):
    """ Renders a customer's loyalty badge as an image - pass the customer id.
    """

    name = 'crm.badge.render'
    input = 'customer_id'

    def handle(self):

        # The badge is binary image data, which no MCP text response can carry
        self.response.payload = _badge_bytes

# ################################################################################################################################
# ################################################################################################################################

class TagCollect(Service):
    """ Collects the distinct tags used across a customer's records - pass the customer id.
    """

    name = 'crm.tag.collect'
    input = 'customer_id'

    def handle(self):

        # A set is not representable in JSON
        self.response.payload = {'vip', 'beta', 'trial'}

# ################################################################################################################################
# ################################################################################################################################

class AckSilent(Service):
    """ Acknowledges that a customer's record was touched - pass the customer id.
    """

    name = 'crm.ack.silent'
    input = 'customer_id'

    def handle(self):

        # The acknowledgment is the call itself - there is nothing to say back
        pass

# ################################################################################################################################
# ################################################################################################################################
