# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

class UserAPI(object):
    """ API accessible from services through self.users.
    """

# ################################################################################################################################

    def create_user(self, username, **kwargs):
        """ Creates a new user returning their publicly visible ID.
        """

# ################################################################################################################################

    def authenticate(self, **kwargs):
        """ Authenticates a user with credentials given as keyword argument, creating a user session afterwards,
        whose ID is returned on output.
        """

# ################################################################################################################################

    def set_password(self, user_id, password):
        """ Hashes input password and sets it for user.
        """

# ################################################################################################################################

    def check_password(self, user_id, password):
        """ Confirms that input password is valid for user without creating a new user session.
        """

# ################################################################################################################################

    def change_password(self, user_id, new_password, old_password=None):
        """ Sets new_password for user. If old_password is given, first confirms that it matches current one.
        """

# ################################################################################################################################

    def set_unusable_password(self, user_id):
        """ Sets password for user to an unusable one (UUID4).
        """

# ################################################################################################################################

    def get_by_id(self, id):
        """ Returns a user by ID attribute.
        """

# ################################################################################################################################

    def get_by_username(self, username):
        """ Returns a user by username attribute.
        """

# ################################################################################################################################

    def get_by_display_name(self, display_name):
        """ Returns a list of users by display_name attribute.
        """

# ################################################################################################################################

    def get_by_last_name(self, last_name):
        """ Returns a list of users by last_name attribute.
        """

# ################################################################################################################################

    def get_by_name(self, first_name, last_name, middle_name=None):
        """ Returns a list of users by a combination of first, middle and last name. Middle name is optional.
        """

# ################################################################################################################################

    def get_by_attr(self, key, value=None):
        """ Returns a list of users by matching attributes.
        """

# ################################################################################################################################
