# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

class UserAttrs(object):
    """ A set of arbitrary key-value attributes attached to a user.
    """

# ################################################################################################################################

    def keys(self):
        """ A dict-like method to return names of all attributes assigned to user.
        """

# ################################################################################################################################

    def values(self):
        """ A dict-like method to return values of all attributes assigned to user.
        """

# ################################################################################################################################

    def items(self):
        """ A dict-like method to return key/value pairs for all attributes assigned to user.
        """

# ################################################################################################################################

    def update(self, source=None, **kwargs):
        """ A dict-like method to update user-attributes from a dict-like source or kwargs parameters.
        """

# ################################################################################################################################
