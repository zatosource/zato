# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# ################################################################################################################################
# ################################################################################################################################

class BaseFileClient(object):

    def __init__(self, config):
        # type: (dict) -> None
        self.config = config

    def sort_result(self, result):
        # type: (dict) -> None

        result['directory_list'].sort(key=itemgetter('name'))
        result['file_list'].sort(key=itemgetter('name'))

    # ftp
    def create_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def delete_directory(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def get(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def get_as_file_object(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def store(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def move_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    def delete_file(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def list(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def touch(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def path_exists(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def ping(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

    # ftp
    def close(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################
