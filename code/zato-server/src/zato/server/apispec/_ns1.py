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
namespace_docs = """This is my namespace.
As with regular docstrings it can contain multi-line documentation.

* Documentation will be parsed as Markdown
* Bullet lists *and* other non-obtrusive markup can be used
"""

# ################################################################################################################################

class Namespace1(Service):
    name = '_test.namespace1'

# ################################################################################################################################

class Namespace2(Service):
    namespace = 'my-other-ns'
    name = '_test.namespace2'

# ################################################################################################################################

class Namespace3(Service):
    name = '_test.namespace3'

# ################################################################################################################################
