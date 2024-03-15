# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# pysolr
try:
    from pysolr import Solr
except ImportError:
    pass

# Zato
from zato.common.util.api import ping_solr
from zato.server.connection.queue import Wrapper
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

class SolrWrapper(Wrapper):
    def __init__(self, config):
        config.auth_url = config.address
        super(SolrWrapper, self).__init__(config, 'Solr')

    def add_client(self):

        # Make sure everything is OK
        ping_solr(self.config)

        # Create a client now
        self.client.put_client(Solr(self.config.address, timeout=self.config.timeout))

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
