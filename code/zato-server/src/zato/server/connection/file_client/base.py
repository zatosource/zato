# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# ################################################################################################################################
# ################################################################################################################################

class PathAccessException(Exception):
    """ Raised when a given remote path can not be accessed by a file client.
    """

# ################################################################################################################################
# ################################################################################################################################

class BaseFileClient:

    def __init__(self, config):
        # type: (dict) -> None
        self.config = config

    def sort_result(self, result):
        # type: (dict) -> None

        result['directory_list'].sort(key=itemgetter('name'))
        result['file_list'].sort(key=itemgetter('name'))

    def create_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def get(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def get_as_file_object(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def store(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def move_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def list(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def touch(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def path_exists(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def ping(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def close(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################
