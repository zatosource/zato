# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The harness every queue delivery suite runs on - one server per pub/sub backend, an endpoint per connection of a
# type's enmasse template, the client-side helpers that talk to the server's test services and the scenarios every
# type of outgoing connection goes through. A type's own suite is a conftest.py, a receiver, its services, its
# template and one file that runs the shared scenarios through them.
