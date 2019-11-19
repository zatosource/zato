# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# Test support services below

# ################################################################################################################################

namespace = 'myns'

# ################################################################################################################################

class Namespace11(Service):
    name = '_test.namespace11'

# ################################################################################################################################

class Namespace22(Service):
    name = '_test.namespace22'

# ################################################################################################################################

class Namespace33(Service):
    namespace = 'my-other-ns-abc'
    name = '_test.namespace33'

# ################################################################################################################################
