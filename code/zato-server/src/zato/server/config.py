# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from logging import getLogger
from threading import RLock

# Paste
from paste.util.multidict import MultiDict

# Bunch
from zato.bunch import Bunch

# Python 2/3 compatibility
from zato.common.ext.future.utils import itervalues
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common.api import ZATO_NONE
from zato.common.const import SECRETS
from zato.common.util.config import resolve_name, resolve_value
from zato.common.util.sql import ElemsWithOpaqueMaker

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    from zato.server.connection.ftp import FTPStore
    FTPStore = FTPStore

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class ConfigDict:
    """ Stores configuration of a particular item of interest, such as an
    outgoing HTTP connection. Could've been a dict and we wouldn't have been using
    .get and .set but things like connection names aren't necessarily proper
    Python attribute names. Also, despite certain dict operations being atomic
    in CPython, the class employs a threading.Lock in critical places so the code
    doesn't assume anything about CPython's byte code-specific implementation
    details.
    """
    def __init__(self, name, _bunch=None):
        self.name = name    # type: unicode
        self._impl = _bunch # type: Bunch
        self.lock = RLock()

# ################################################################################################################################

    def get(self, key, default=None):
        with self.lock:
            key = key.strip()
            return self._impl.get(key, default)

# ################################################################################################################################

    def set(self, key, value):
        with self.lock:
            self._impl[key] = value

    __setitem__ = set

# ################################################################################################################################

    def __getitem__(self, key):
        with self.lock:
            key = key.strip()
            return self._impl.__getitem__(key)

# ################################################################################################################################

    def __delitem__(self, key):
        with self.lock:
            del self._impl[key]

# ################################################################################################################################

    def pop(self, key, default):
        with self.lock:
            return self._impl.pop(key, default)

# ################################################################################################################################

    def update(self, dict_):
        # type: (dict_)
        with self.lock:
            self._impl.update(dict_)

# ################################################################################################################################

    def __iter__(self):
        with self.lock:
            return iter(self._impl)

# ################################################################################################################################

    def __repr__(self):
        with self.lock:
            return '<{} at {} keys:[{}]>'.format(self.__class__.__name__,
                hex(id(self)), sorted(self._impl.keys()))

    __str__ = __repr__

# ################################################################################################################################

    def __nonzero__(self):
        with self.lock:
            return bool(self._impl)

# ################################################################################################################################

    def keys(self):
        with self.lock:
            return self._impl.keys()

# ################################################################################################################################

    def values(self):
        with self.lock:
            return self._impl.values()

# ################################################################################################################################

    def itervalues(self):
        with self.lock:
            return itervalues(self._impl)

# ################################################################################################################################

    def items(self):
        with self.lock:
            return self._impl.items()

# ################################################################################################################################

    def get_by_id(self, key_id, default=None):
        with self.lock:
            key = self._impl.get('_zato_id_%s' % key_id)
            return self._impl.get(key, default)

# ################################################################################################################################

    def set_key_id_data(self, config):
        with self.lock:
            key_id = config['id']
            key = config['name']
            self._impl['_zato_id_%s' % key_id] = key

# ################################################################################################################################

    def copy(self):
        """ Returns a new instance of ConfigDict with items copied over from self.
        """
        with self.lock:
            config_dict = ConfigDict(self.name)
            config_dict._impl = Bunch()
            config_dict._impl.update(deepcopy(self._impl))

            return config_dict

# ################################################################################################################################

    def get_config_list(self, predicate=lambda value: value):
        """ Returns a list of deepcopied config Bunch objects.
        """
        out = []
        with self.lock:
            for value in self.values():
                if isinstance(value, dict):
                    config = value['config']
                    if predicate(config):
                        out.append(deepcopy(config))
        return out

# ################################################################################################################################

    def copy_keys(self, skip_ids=True):
        """ Returns a deepcopy of the underlying Bunch's keys
        """
        with self.lock:
            keys = self._impl.keys()
            if skip_ids:
                keys = [elem for elem in keys if not elem.startswith('_zato_id')]
            return deepcopy(keys)

# ################################################################################################################################

    @staticmethod
    def from_query(name, query_data, impl_class=Bunch, item_class=Bunch, list_config=False, decrypt_func=None, drop_opaque=False):
        """ Return a new ConfigDict with items taken from an SQL query.
        """
        config_dict = ConfigDict(name)
        config_dict._impl = impl_class()

        if query_data:
            query, attrs = query_data

            for item in query:

                if hasattr(item, 'name'):
                    item_name = item.name
                else:
                    item_name = item.get_name()

                item_name = resolve_name(item_name)

                if list_config:
                    list_dict = Bunch()
                    if item_name not in config_dict._impl:
                        config_dict._impl[item_name] = []
                    config_dict._impl[item_name].append(list_dict)
                else:
                    config_dict._impl[item_name] = item_class()

                if list_config:
                    for attr_name in attrs.keys():
                        list_dict[attr_name] = getattr(item, attr_name)

                else:
                    config_dict._impl[item_name].config = item_class()
                    for attr_name in attrs.keys():
                        config = config_dict._impl[item_name]['config']
                        original = value = getattr(item, attr_name)
                        value = resolve_value(attr_name, value, decrypt_func)
                        config[attr_name] = value

                        # Temporarily, add a flag to indicate whether the password in ODB was encrypted or not.
                        if attr_name in SECRETS.PARAMS:

                            if original is None:
                                original = ''

                            config['_encryption_needed'] = True

                            if not isinstance(original, unicode):
                                orig_uni = original.decode('utf8')
                            else:
                                orig_uni = original

                            if orig_uni.startswith(SECRETS.PREFIX):
                                config['_encrypted_in_odb'] = True
                            else:
                                config['_encrypted_in_odb'] = False

        # Post-process data before it is returned to resolve any opaque attributes
        for value in config_dict.values():
            value_config = value['config']
            if ElemsWithOpaqueMaker.has_opaque_data(value_config):
                ElemsWithOpaqueMaker.process_config_dict(value_config, drop_opaque)

        return config_dict

# ################################################################################################################################

    @staticmethod
    def from_generic(config_dict):
        return config_dict

# ################################################################################################################################

class ConfigStore:
    """ The central place for storing a Zato server's thread configuration.
    May /not/ be shared across threads - each thread should get its own copy
    using the .copy method.
    """
    def __init__(self):

        # Outgoing connections
        self.out_ftp = None   # type: ConfigDict
        self.out_sftp = None  # type: ConfigDict
        self.out_odoo = None  # type: ConfigDict
        self.out_soap = None  # type: ConfigDict
        self.out_sql = None   # type: ConfigDict
        self.out_sap = None   # type: ConfigDict
        self.out_plain_http = None # type: ConfigDict
        self.out_amqp = None       # type: ConfigDict
        self.cloud_aws_s3 = None   # type: ConfigDict
        self.email_smtp = None   # type: ConfigDict
        self.email_imap = None   # type: ConfigDict

        self.channel_zmq = None   # type: ConfigDict
        self.out_zmq = None   # type: ConfigDict
        self.channel_web_socket = None   # type: ConfigDict
        self.generic_connection = None   # type: ConfigDict
        self.notif_sql = None   # type: ConfigDict
        self.service = None   # type: ConfigDict
        self.sms_twilio = None   # type: ConfigDict
        self.search_es = None   # type: ConfigDict
        self.search_solr = None   # type: ConfigDict
        self.cassandra_conn = None   # type: ConfigDict
        self.cassandra_query = None   # type: ConfigDict
        self.cache_builtin = None   # type: ConfigDict
        self.cache_memcached = None   # type: ConfigDict

        self.pubsub = None   # type: ConfigDict
        self.pubsub_endpoint = None   # type: ConfigDict
        self.pubsub_topic = None   # type: ConfigDict
        self.pubsub_subscription = None   # type: ConfigDict

        # Local on-disk configuraion repository
        self.repo_location = None # type: str

        # Security definitions
        self.apikey = None   # type: ConfigDict
        self.aws = None   # type: ConfigDict
        self.basic_auth = None # type: ConfigDict
        self.jwt = None   # type: ConfigDict
        self.ntlm = None   # type: ConfigDict
        self.oauth = None   # type: ConfigDict
        self.rbac_permission = None   # type: ConfigDict
        self.rbac_role = None   # type: ConfigDict
        self.rbac_client_role = None   # type: ConfigDict
        self.rbac_role_permission = None   # type: ConfigDict
        self.tls_ca_cert = None   # type: ConfigDict
        self.tls_channel_sec = None   # type: ConfigDict
        self.tls_key_cert = None   # type: ConfigDict
        self.vault_conn_sec = None   # type: ConfigDict

        # URL security
        self.url_sec = None # type: ConfigDict

        # HTTP channels
        self.http_soap = None # type: anylist

        # Configuration for broker clients
        self.broker_config = None

        # ODB
        self.odb_data = Bunch()

        # SimpleIO
        self.simple_io = None # type: stranydict

        # Namespace
        self.msg_ns = None # type: ConfigDict

        # JSON Pointer
        self.json_pointer = None # type: ConfigDict

        # Services
        self.service = None # type: ConfigDict

        # IBM MQ
        self.definition_wmq = None # type: ConfigDict
        self.out_wmq = None        # type: ConfigDict
        self.channel_wmq = None    # type: ConfigDict
        self.channel_amqp = None   # type: ConfigDict
        self.definition_amqp = None   # type: ConfigDict

# ################################################################################################################################

    def get_config_by_item_id(self, attr_name, item_id):
        # type: (str, object) -> dict

        # Imported here to avoid circular references
        from zato.server.connection.ftp import FTPStore

        item_id = int(item_id)
        config = getattr(self, attr_name) # type: dict

        if isinstance(config, FTPStore):
            needs_inner_config = False
            values = config.conn_params.values()
        else:
            needs_inner_config = True
            values = config.values()

        for value in values:
            if needs_inner_config:
                config_dict = value['config']
            else:
                config_dict = value

            if config_dict['id'] == item_id:
                return config_dict

# ################################################################################################################################

    def __getitem__(self, key):
        return getattr(self, key)

# ################################################################################################################################

    def outgoing_connections(self):
        """ Returns all the outgoing connections.
        """
        return self.out_ftp, self.out_sftp, self.out_odoo, self.out_plain_http, self.out_soap, self.out_sap

# ################################################################################################################################

    def copy(self):
        """ Creates a copy of this ConfigStore. All configuration data is copied
        over except for SQL connections.
        """
        config_store = ConfigStore()

        # Grab all ConfigDicts - even if they're actually ZATO_NONE - and make their copies
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigDict):
                copy_func = attr.copy
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

# ################################################################################################################################
