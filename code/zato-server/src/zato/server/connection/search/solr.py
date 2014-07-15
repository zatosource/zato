# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.queue import Wrapper
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

class SolrWrapper(Wrapper):
    def __init__(self, config):
        config.auth_url = config.address
        super(SolrWrapper, self).__init__(config, 'Solr')

    def add_client(self):
        logger.warn(self.config)
        self.client.put_client(None)

class SolrAPI(BaseAPI):
    """ API to obtain ElasticSearch connections through.
    """

class SolrConnStore(BaseStore):
    """ Stores connections to ElasticSearch.
    """
    def create_impl(self, _, config_no_sensitive):
        w = SolrWrapper(config_no_sensitive)
        w.build_queue()
        return w
