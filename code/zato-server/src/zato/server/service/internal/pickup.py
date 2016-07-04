# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# ################################################################################################################################

class Static(Service):
    """ Picks up static files.
    """

# ################################################################################################################################

class Conf(Service):
    """ Picks up configuration files.
    """

# ################################################################################################################################

class JSON(Service):
    """ Picks up JSON files.
    """

# ################################################################################################################################

class XML(Service):
    """ Picks up XML files.
    """

# ################################################################################################################################

class CSV(Service):
    """ Picks up CSV files.
    """

# ################################################################################################################################
