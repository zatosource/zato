# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from logging import getLogger
from threading import RLock

# Paste
from paste.util.multidict import MultiDict

# Bunch
from bunch import Bunch

# Zato
from zato.common import ZATO_NONE

logger = getLogger(__name__)

class ConfigDict(object):
    """ Stores configuration of a particular item of interest, such as an
    outgoing HTTP connection. Could've been a dict and we wouldn't have been using
    .get and .set but things like connection names aren't necessarily proper
    Python attribute names. Also, despite certain dict operations being atomic
    in CPython, the class employs a threading.Lock in critical places so the code
    doesn't assume anything about CPython's byte code-specific implementation
    details.
    """
    def __init__(self, name, _bunch=None):
        self.name = name
        self._bunch = _bunch
        self.lock = RLock()

    def get(self, key, default=None):
        with self.lock:
            return self._bunch.get(key, default)

    def set(self, key, value):
        with self.lock:
            self._bunch[key] = value

    __setitem__ = set

    def __getitem__(self, key):
        with self.lock:
            return self._bunch.__getitem__(key)

    def __delitem__(self, key):
        with self.lock:
            del self._bunch[key]

    def __iter__(self):
        with self.lock:
            return iter(self._bunch)

    def __repr__(self):
        with self.lock:
            return '<{} at {} keys:[{}]>'.format(self.__class__.__name__,
                hex(id(self)), sorted(self._bunch.keys()))

    __str__ = __repr__

    def __nonzero__(self):
        with self.lock:
            return bool(self._bunch)

    def keys(self):
        with self.lock:
            return self._bunch.keys()

    def values(self):
        with self.lock:
            return self._bunch.values()

    def items(self):
        with self.lock:
            return self._bunch.items()

    def copy(self):
        """ Returns a new instance of ConfigDict with items copied over from self.
        """
        with self.lock:
            config_dict = ConfigDict(self.name)
            config_dict._bunch = Bunch()
            config_dict._bunch.update(deepcopy(self._bunch))

            return config_dict

    def get_config_list(self):
        """ Returns a list of deepcopied config Bunch objects.
        """
        with self.lock:
            out = []
            for value in self._bunch.values():
                config = value['config']
                out.append(deepcopy(config))

        return out

    def copy_keys(self):
        """ Returns a deepcopy of the underlying Bunch's keys
        """
        with self.lock:
            return deepcopy(self._bunch.keys())

    @staticmethod
    def from_query(name, query_data, item_class=Bunch):
        """ Return a new ConfigDict with items taken from an SQL query.
        """
        config_dict = ConfigDict(name)
        config_dict._bunch = Bunch()

        if query_data:
            query, attrs = query_data

            for item in query:
                config_dict._bunch[item.name] = Bunch()
                config_dict._bunch[item.name].config = Bunch()

                for attr_name in attrs.keys():
                    config_dict._bunch[item.name]['config'][attr_name] = getattr(item, attr_name)

        return config_dict

class ConfigStore(object):
    """ The central place for storing a Zato server's thread configuration.
    May /not/ be shared across threads - each thread should get its own copy
    using the .copy method.

    Note that much more should be stored in here but the work is not finished yet -
    for instance, connection definitions should be kept here.
    """
    def __init__(self, out_ftp=ZATO_NONE, out_plain_http=ZATO_NONE,
            out_soap=ZATO_NONE, out_sql=ZATO_NONE, repo_location=ZATO_NONE,
            basic_auth=ZATO_NONE, wss=ZATO_NONE, tech_acc=ZATO_NONE,
            url_sec=ZATO_NONE, http_soap=ZATO_NONE, broker_config=ZATO_NONE,
            odb_data=ZATO_NONE, simple_io=ZATO_NONE, msg_ns=ZATO_NONE,
            elem_path=ZATO_NONE, xpath=ZATO_NONE, pubsub_topics=ZATO_NONE):

        # Outgoing connections
        self.out_ftp = out_ftp
        self.out_plain_http = out_plain_http
        self.out_soap = out_soap
        self.out_sql = out_sql

        # Local on-disk configuraion repository
        self.repo_location = repo_location

        # Security definitions
        self.basic_auth = basic_auth
        self.wss = wss
        self.tech_acc = tech_acc

        # URL security
        self.url_sec = url_sec

        # HTTP channels
        self.http_soap = http_soap

        # Configuration for broker clients
        self.broker_config = broker_config

        # ODB
        self.odb_data = odb_data

        # SimpleIO
        self.simple_io = simple_io

        # Namespace
        self.msg_ns = msg_ns

        # ElemPath
        self.elem_path = elem_path

        # XPath
        self.xpath = xpath

        # Pub/sub
        self.pubsub_topics = pubsub_topics

    def outgoing_connections(self):
        """ Returns all the outgoing connections.
        """
        return self.out_ftp, self.out_plain_http, self.out_soap

    def copy(self):
        """ Creates a copy of this ConfigStore. All configuration data is copied
        over except for SQL connections.
        """
        config_store = ConfigStore()

        # Grab all ConfigDicts - even if they're actually ZATO_NONE - and make their copies
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigDict):
                copy_func = getattr(attr, 'copy')
                setattr(config_store, attr_name, copy_func())
            elif attr is ZATO_NONE:
                setattr(config_store, attr_name, ZATO_NONE)

        http_soap = MultiDict()
        dict_of_lists = self.http_soap.dict_of_lists()
        for url_path, lists in dict_of_lists.items():
            _info = Bunch()
            for elem in lists:
                for soap_action, item in elem.items():
                    _info[soap_action] = Bunch()
                    _info[soap_action].id = item.id
                    _info[soap_action].name = item.name
                    _info[soap_action].is_active = item.is_active
                    _info[soap_action].is_internal = item.is_internal
                    _info[soap_action].url_path = item.url_path
                    _info[soap_action].method = item.method
                    _info[soap_action].soap_version = item.soap_version
                    _info[soap_action].service_id = item.service_id
                    _info[soap_action].service_name = item.service_name
                    _info[soap_action].impl_name = item.impl_name
                    _info[soap_action].transport = item.transport
                    _info[soap_action].connection = item.connection
            http_soap.add(url_path, _info)

        config_store.http_soap = http_soap
        config_store.url_sec = self.url_sec
        config_store.broker_config = self.broker_config
        config_store.odb_data = deepcopy(self.odb_data)

        return config_store
