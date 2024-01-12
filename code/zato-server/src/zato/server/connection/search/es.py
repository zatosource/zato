# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# elasticsearch
from elasticsearch.client import Elasticsearch

# Zato
from zato.server.store import BaseAPI, BaseStore

class ElasticSearchAPI(BaseAPI):
    """ API to obtain ElasticSearch connections through.
    """

class ElasticSearchConnStore(BaseStore):
    """ Stores connections to ElasticSearch.
    """
    def create_impl(self, config, config_no_sensitive):
        return Elasticsearch(config.hosts.splitlines(), timeout=float(config.timeout), send_get_body_as=config.body_as)
