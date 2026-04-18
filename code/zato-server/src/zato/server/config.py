# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging as _logging
from copy import deepcopy
from logging import getLogger
from threading import RLock

# Bunch
from zato.bunch import Bunch

# Python 2/3 compatibility
from zato.common.ext.future.utils import itervalues
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common.api import ZATO_NONE
from zato.common.const import SECRETS
from zato.common.util.config import resolve_name, resolve_value

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    from zato.server.connection.ftp import FTPStore
    FTPStore = FTPStore

# ################################################################################################################################

logger = getLogger(__name__)

def _rest_log_write(msg):
    with open('/tmp/rest.txt', 'a') as _f:
        from datetime import datetime
        _f.write(datetime.now().isoformat() + ' ' + msg + '\n')
        _f.flush()

# ################################################################################################################################

class ConfigDict:
    """ Thin facade that delegates storage to the Rust ConfigStore. If no
    config_manager/entity_type are provided, falls back to an in-memory Bunch
    (legacy mode for simple_io, url_sec, etc. that have no Rust backing).

    Callers access items as config_dict[name].config.password and the Bunch
    wrapper is constructed on the fly from the Rust-side dict.
    """
    def __init__(self, name, _bunch=None, *, config_manager=None, entity_type=None, sec_type_filter=None):
        self.name = name
        self.lock = RLock()
        self._config_manager = config_manager
        self._entity_type = entity_type
        self._sec_type_filter = sec_type_filter

        # Runtime-only Python objects (e.g. .conn, .ping wrappers) that cannot
        # be serialized to Rust, keyed by item name.
        self._runtime = {}

        if config_manager is not None and entity_type is not None:
            self._impl = None
        else:
            self._impl = _bunch if _bunch is not None else Bunch()

    @property
    def _delegates_to_rust(self):
        return self._config_manager is not None and self._entity_type is not None

    def _wrap_item(self, raw_dict, key=None):
        """ Wrap a raw dict from Rust into Bunch({'config': Bunch(...)}).
        If there are runtime attributes stored for this key, merge them in.
        """
        item = Bunch({'config': Bunch(raw_dict)})
        if key and key in self._runtime:
            runtime_keys = list(self._runtime[key].keys())
            _rest_log_write('_wrap_item: entity=%s key=%s, merging runtime attrs=%s' % (self._entity_type, key, runtime_keys))
            for attr_name, attr_value in self._runtime[key].items():
                item[attr_name] = attr_value
        else:
            _rest_log_write('_wrap_item: entity=%s key=%s, no runtime attrs (all runtime keys=%s)' % (self._entity_type, key, list(self._runtime.keys())))
        return item

    def _unwrap_item(self, key, value):
        """ Extract the raw dict from a Bunch({'config': Bunch(...)}) wrapper.
        Any non-config, non-serializable attributes are saved to _runtime.
        """
        runtime_attrs = {}

        _rest_log_write('_unwrap_item: entity=%s key=%s, value type=%s, isinstance(dict)=%s' % (self._entity_type, key, type(value).__name__, isinstance(value, dict)))
        if isinstance(value, dict):
            config = value.get('config')
            all_keys = list(value.keys())
            _rest_log_write('_unwrap_item: entity=%s key=%s, value dict keys=%s, has config=%s' % (self._entity_type, key, all_keys, config is not None))
            for attr_name, attr_value in value.items():
                if attr_name != 'config':
                    runtime_attrs[attr_name] = attr_value
            raw = dict(config) if config is not None else dict(value)
        else:
            raw = dict(value) if isinstance(value, dict) else value

        if runtime_attrs:
            _rest_log_write('_unwrap_item: entity=%s key=%s, storing runtime attrs=%s' % (self._entity_type, key, list(runtime_attrs.keys())))
            self._runtime[key] = runtime_attrs
        else:
            _rest_log_write('_unwrap_item: entity=%s key=%s, NO runtime attrs found' % (self._entity_type, key))
        _rest_log_write('_unwrap_item: entity=%s key=%s, self id=%s, _runtime keys after=%s' % (self._entity_type, key, id(self), list(self._runtime.keys())))
        return raw

    def _get_all_items_from_rust(self):
        """ Return {name: Bunch({'config': Bunch(...)})} for all items. """
        items = self._config_manager.get_list(self._entity_type)
        result = Bunch()
        for item in items:
            item_name = item.get('name', '')
            if self._sec_type_filter:
                sec_type = item.get('sec_type') or item.get('type', '')
                if sec_type != self._sec_type_filter:
                    continue
            result[item_name] = self._wrap_item(item, key=item_name)
        return result

# ################################################################################################################################

    def get(self, key, default=None):
        with self.lock:
            key = key.strip()
            if self._delegates_to_rust:
                raw = self._config_manager.get(self._entity_type, key)
                if raw is None:
                    return default
                if self._sec_type_filter:
                    sec_type = raw.get('sec_type') or raw.get('type', '')
                    if sec_type != self._sec_type_filter:
                        return default
                return self._wrap_item(raw, key=key)
            return self._impl.get(key, default)

# ################################################################################################################################

    def set(self, key, value):
        with self.lock:
            if self._delegates_to_rust:
                raw = self._unwrap_item(key, value)
                self._config_manager.set(self._entity_type, key, raw)
            else:
                self._impl[key] = value

    __setitem__ = set

# ################################################################################################################################

    def __getitem__(self, key):
        with self.lock:
            key = key.strip()
            if self._delegates_to_rust:
                raw = self._config_manager.get(self._entity_type, key)
                if raw is None:
                    raise KeyError(key)
                if self._sec_type_filter:
                    sec_type = raw.get('sec_type') or raw.get('type', '')
                    if sec_type != self._sec_type_filter:
                        raise KeyError(key)
                return self._wrap_item(raw, key=key)
            return self._impl.__getitem__(key)

# ################################################################################################################################

    def __delitem__(self, key):
        with self.lock:
            if self._delegates_to_rust:
                self._config_manager.delete(self._entity_type, key)
                self._runtime.pop(key, None)
            else:
                del self._impl[key]

# ################################################################################################################################

    def pop(self, key, default):
        with self.lock:
            if self._delegates_to_rust:
                raw = self._config_manager.get(self._entity_type, key)
                if raw is None:
                    return default
                self._config_manager.delete(self._entity_type, key)
                self._runtime.pop(key, None)
                return self._wrap_item(raw, key=key)
            return self._impl.pop(key, default)

# ################################################################################################################################

    def update(self, dict_):
        with self.lock:
            if self._delegates_to_rust:
                for key, value in dict_.items():
                    raw = self._unwrap_item(key, value)
                    self._config_manager.set(self._entity_type, key, raw)
            else:
                self._impl.update(dict_)

# ################################################################################################################################

    def __iter__(self):
        with self.lock:
            if self._delegates_to_rust:
                return iter(self._get_all_items_from_rust())
            return iter(self._impl)

# ################################################################################################################################

    def __repr__(self):
        with self.lock:
            if self._delegates_to_rust:
                items = self._get_all_items_from_rust()
                return '<{} at {} keys:[{}]>'.format(self.__class__.__name__,
                    hex(id(self)), sorted(items.keys()))
            return '<{} at {} keys:[{}]>'.format(self.__class__.__name__,
                hex(id(self)), sorted(self._impl.keys()))

    __str__ = __repr__

# ################################################################################################################################

    def __nonzero__(self):
        with self.lock:
            if self._delegates_to_rust:
                return len(self._config_manager.get_list(self._entity_type)) > 0
            return bool(self._impl)

# ################################################################################################################################

    def keys(self):
        with self.lock:
            if self._delegates_to_rust:
                return self._get_all_items_from_rust().keys()
            return self._impl.keys()

# ################################################################################################################################

    def values(self):
        with self.lock:
            if self._delegates_to_rust:
                return self._get_all_items_from_rust().values()
            return self._impl.values()

# ################################################################################################################################

    def itervalues(self):
        with self.lock:
            if self._delegates_to_rust:
                return iter(self._get_all_items_from_rust().values())
            return itervalues(self._impl)

# ################################################################################################################################

    def items(self):
        with self.lock:
            if self._delegates_to_rust:
                return self._get_all_items_from_rust().items()
            return self._impl.items()

# ################################################################################################################################

    def get_by_id(self, key_id, default=None):
        with self.lock:
            if self._delegates_to_rust:
                key_id_str = str(key_id)
                items = self._config_manager.get_list(self._entity_type)
                for item in items:
                    if str(item.get('id', '')) == key_id_str:
                        if self._sec_type_filter:
                            sec_type = item.get('sec_type') or item.get('type', '')
                            if sec_type != self._sec_type_filter:
                                continue
                        return self._wrap_item(item)
                return default
            key = self._impl.get('_zato_id_%s' % key_id)
            return self._impl.get(key, default)

# ################################################################################################################################

    def set_key_id_data(self, config):
        with self.lock:
            if self._delegates_to_rust:
                return
            key_id = config['id']
            key = config['name']
            self._impl['_zato_id_%s' % key_id] = key

# ################################################################################################################################

    def copy(self):
        with self.lock:
            if self._delegates_to_rust:
                config_dict = ConfigDict(
                    self.name,
                    config_manager=self._config_manager,
                    entity_type=self._entity_type,
                    sec_type_filter=self._sec_type_filter,
                )
                return config_dict
            config_dict = ConfigDict(self.name)
            config_dict._impl = Bunch()
            config_dict._impl.update(deepcopy(self._impl))
            return config_dict

# ################################################################################################################################

    def get_config_list(self, predicate=lambda value: value):
        out = []
        with self.lock:
            if self._delegates_to_rust:
                items = self._config_manager.get_list(self._entity_type)
                for item in items:
                    if self._sec_type_filter:
                        sec_type = item.get('sec_type') or item.get('type', '')
                        if sec_type != self._sec_type_filter:
                            continue
                    config = Bunch(item)
                    if predicate(config):
                        out.append(deepcopy(config))
                return out
            for value in self.values():
                if isinstance(value, dict):
                    config = value['config']
                    if predicate(config):
                        out.append(deepcopy(config))
        return out

# ################################################################################################################################

    def copy_keys(self, skip_ids=True):
        with self.lock:
            if self._delegates_to_rust:
                items = self._get_all_items_from_rust()
                return list(items.keys())
            keys = self._impl.keys()
            if skip_ids:
                keys = [elem for elem in keys if not elem.startswith('_zato_id')]
            return deepcopy(keys)

# ################################################################################################################################

    @staticmethod
    def from_query(name, query_data, impl_class=Bunch, item_class=Bunch, list_config=False, decrypt_func=None, drop_opaque=False):
        """ Return a new ConfigDict with items taken from an SQL query.
        This legacy factory is used when ConfigStore delegation is not yet
        wired up for a particular entity type.
        """
        config_dict = ConfigDict(name)
        config_dict._impl = impl_class()

        if query_data:
            query, attrs = query_data

            for item in query:

                if hasattr(item, 'name'):
                    item_name = item.name
                elif hasattr(item, 'topic_name'):
                    item_name = item.topic_name
                elif hasattr(item, 'sub_key'):
                    item_name = item.sub_key
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

        from zato.common.util.sql import ElemsWithOpaqueMaker
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
    """ Thin namespace holding ConfigDict instances that all delegate to the
    Rust ConfigStore. Attributes are set by ConfigLoader.set_up_config().

    Non-ConfigDict attributes (http_soap, url_sec, broker_config, simple_io,
    repo_location) hold Python-only runtime data that has no Rust backing.
    """
    def __init__(self):
        self.out_ftp = None
        self.out_odoo = None
        self.out_soap = None
        self.out_sql = None
        self.out_sap = None
        self.out_plain_http = None
        self.out_amqp = None
        self.email_smtp = None
        self.email_imap = None
        self.generic_connection = None
        self.service = None
        self.search_es = None
        self.cache_builtin = None
        self.repo_location = None
        self.apikey = None
        self.basic_auth = None
        self.ntlm = None
        self.oauth = None
        self.url_sec = None
        self.http_soap = None
        self.broker_config = None
        self.simple_io = None
        self.channel_amqp = None
        self.pubsub_subs = None

# ################################################################################################################################

    def get_config_by_item_id(self, attr_name, item_id):

        from zato.server.connection.ftp import FTPStore

        item_id = int(item_id)
        config = getattr(self, attr_name)

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
        return self.out_ftp, self.out_odoo, self.out_plain_http, self.out_soap, self.out_sap

# ################################################################################################################################

    def copy(self):
        config_manager = ConfigStore()

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigDict):
                setattr(config_manager, attr_name, attr.copy())
            elif attr is ZATO_NONE:
                setattr(config_manager, attr_name, ZATO_NONE)

        config_manager.http_soap = self.http_soap
        config_manager.url_sec = self.url_sec
        config_manager.broker_config = self.broker_config
        config_manager.simple_io = self.simple_io

        return config_manager

# ################################################################################################################################
