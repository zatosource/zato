# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

class UserSessionAttrs(object):
    """ A set of arbitrary key-value attributes attached to a user session.
    """

# ################################################################################################################################

    def get(self):
        """ A dict-like method to return names of all attributes assigned to a user session.
        """

# ################################################################################################################################

    def keys(self):
        """ A dict-like method to return names of all attributes assigned to a user session.
        """

# ################################################################################################################################

    def values(self):
        """ A dict-like method to return values of all attributes assigned to a user session.
        """

# ################################################################################################################################

    def items(self):
        """ A dict-like method to return key/value pairs for all attributes assigned to a user session.
        """

# ################################################################################################################################

    def update(self, source=None, **kwargs):
        """ A dict-like method to update user session-attributes from a dict-like source or kwargs parameters.
        """

# ################################################################################################################################
