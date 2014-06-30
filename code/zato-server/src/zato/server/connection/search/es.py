# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.connection import BaseAPI, BaseConnStore

class ElasticSearchAPI(BaseAPI):
    """ API to obtain ElasticSearch connections through.
    """

class ElasticSearchConnStore(BaseConnStore):
    """ Stores connections to ElasticSearch.
    """
    def create_impl(self, config, config_no_sensitive):
        return 123
