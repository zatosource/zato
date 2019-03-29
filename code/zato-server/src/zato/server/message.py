# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from decimal import Decimal
from threading import RLock
from traceback import format_exc

# Arrow
from arrow import get as arrow_get

# Bunch
from bunch import Bunch

# dpath
from dpath import util as dpath_util

# jsonpointer
from jsonpointer import JsonPointer

# lxml
from lxml import etree

# Paste
from paste.util.converters import asbool

# Python 2/3 compatibility
from past.builtins import long

# Zato
from zato.common import MSG_MAPPER, ZATO_NOT_GIVEN
from zato.common.nav import DictNav

logger = logging.getLogger(__name__)

# ################################################################################################################################

class JSONPointerAPI(object):
    """ User-visible API to a store of JSON Pointers.
    """
    def __init__(self, doc, store):
        self._doc = doc
        self._store = store

    def get(self, name, default=None):
        return self._store.get(name, self._doc, default)

    def set(self, name, value, return_on_missing=False, in_place=True):
        return self._store.set(name, self._doc, value, return_on_missing, in_place)

class XPathAPI(object):
    """ User-visible API to a store of XPath expressions.
    """
    def __init__(self, doc, store, ns_store):
        self._doc = doc
        self._store = store
        self._ns_store = ns_store

    def get(self, name, default=None):
        return self._store.get(name, self._doc, default)

    def set(self, name, value):
        return self._store.set(name, self._doc, value, self._ns_store.ns_map)

class MessageFacade(object):
    """ An object through which services access all the message-related features,
    such as namespaces, JSON Pointer or XPath.
    """
    def __init__(self, json_pointer_store=None, xpath_store=None, ns_store=None, payload=None, time_util=None):
        self._json_pointer_store = json_pointer_store
        self._xpath_store = xpath_store
        self._ns_store = ns_store
        self._payload = payload
        self._time_util = time_util

    def json_pointer(self, doc=None):
        return JSONPointerAPI(doc if doc is not None else self._payload, self._json_pointer_store)

    def xpath(self, msg=None):
        return XPathAPI(msg if msg is not None else self._payload, self._xpath_store, self._ns_store)

    def mapper(self, source, target=None, *args, **kwargs):
        return Mapper(source, target, time_util=self._time_util, *args, **kwargs)

# ################################################################################################################################

class NamespaceStore(object):
    """ A store of all the namespaces used with XML processing.
    """
    def __init__(self, data={}):
        self.data = Bunch.fromDict(data)
        self.ns_map = {}
        self.update_lock = RLock()

    def __getitem__(self, name):
        return self.data[name].config.value

    def add(self, name, item):
        with self.update_lock:
            self.data[name] = Bunch()
            self.data[name].config = item
            self.ns_map[name] = self.data[name].config.value

    def on_broker_msg_MSG_NS_CREATE(self, msg, *args):
        """ Creates a new namespace.
        """
        self.add(msg.name, msg)

    def on_broker_msg_MSG_NS_EDIT(self, msg, *args):
        """ Updates an existing namespace.
        """
        with self.update_lock:
            del self.data[msg.old_name]
            del self.ns_map[msg.old_name]
        self.add(msg.name, msg)

    def on_broker_msg_MSG_NS_DELETE(self, msg, *args):
        """ Deletes a namespace.
        """
        with self.update_lock:
            del self.data[msg.name]
            del self.ns_map[msg.name]

# ################################################################################################################################

class BaseStore(object):
    def __init__(self, data={}):
        self.data = Bunch.fromDict(data)
        self.update_lock = RLock()

        # Dummy document to test expressions against - will yield
        # an XPathEvalError in an XPath's .evaluate method if a namespace
        # prefix used wasn't defined in a namespace map.
        self.dummy_doc = etree.XML('<dummy/>')

    def __getitem__(self, name):
        return self.data[name].config.value

    def compile(self, expr, ns_map={}):
        """ Compiles an XPath expression using a namespace map provided, if any,
        and evaluates it against a dummy document to check that all the namespace
        prefixes are valid.
        """
        try:
            compiled = etree.XPath(expr, namespaces=ns_map)
            compiled.evaluate(self.dummy_doc)
        except Exception:
            logger.warn('Failed to compile expr:[%s] with ns_map:[%s]', expr, ns_map)
            raise
        else:
            return compiled

    def on_broker_msg_create(self, msg, ns_map=None):
        """ Creates a new XPath expression or JSON Pointer.
        """
        self.add(msg.name, msg, ns_map)

    def on_broker_msg_edit(self, msg, ns_map=None):
        """ Updates an existing XPath expression or JSON Pointer.
        """
        with self.update_lock:
            del self.data[msg.old_name]
            self.add(msg.name, msg, ns_map)

    def on_broker_msg_delete(self, msg, *args):
        """ Deletes an XPath expression or JSON Pointer.
        """
        with self.update_lock:
            del self.data[msg.name]

# ################################################################################################################################

class XPathStore(BaseStore):
    """ Keeps config of and evaluates XPath expressions.
    """
    def add(self, name, config, ns_map=None):
        ns_map = ns_map or {}
        with self.update_lock:
            compiled_elem = self.compile(config.value, ns_map)
            self.data[name] = Bunch()
            self.data[name].config = config
            self.data[name].compiled_elem = compiled_elem

    def get(self, name, doc, default=None, needs_text=True):
        result = self.data[name].compiled_elem.evaluate(doc)
        if result:
            if len(result) == 1:
                if needs_text:
                    result = result[0].text
            else:
                if needs_text:
                    result = [elem.text for elem in result]
        else:
            result = None

        return result if result is not None else default

    def set(self, name, doc, value, ns_map=None):
        """ Sets a value of element(s) under a given name in a doc.
        If value is False, element(s) are deleted.
        """
        # Mostly taken from https://stackoverflow.com/a/5547668
        ns_map = ns_map or {}
        path = self.data[name].config.value
        nodes = doc.xpath(path, namespaces=ns_map)

        if nodes:
            node = nodes
        else:
            parts = path.split('/')
            parts = (part for part in parts if part)
            p = doc
            for part in parts:
                nodes = p.xpath(part, namespaces=ns_map)
                if not nodes:
                    name_elems = part.split(':')

                    # No namespaces:
                    if len(name_elems) == 1:
                        n = etree.Element(part)

                    # Need to map prefixes to actual namespaces
                    else:
                        prefix, name = name_elems
                        ns = ns_map[prefix]

                        # String interpolation is much easier to comprehend than str.format here
                        n = etree.Element('{%s}%s' % (ns, name))

                    p.append(n)
                    p = n
                else:
                    p = nodes[0]

            node = p
            nodes = [node]

        if value is False:
            node.getparent().remove(node)
        else:
            for node in nodes:
                node.text = value

    def delete(self, name, doc):
        return self.set(name, doc, False)

# ################################################################################################################################

class JSONPointerStore(BaseStore):

    def get(self, name, doc, default=None):
        value = self.data[name].get(doc, default)
        if value is not None:
            return value
        else:
            return default

    def set(self, name, doc, value, return_on_missing=False, in_place=True):
        if return_on_missing:
            if not self.get(name, doc):
                return doc

        pointer = self.data[name]

        try:
            return pointer.set(doc, value, in_place)
        except Exception:
            dpath_util.new(doc, '/' + '/'.join(pointer.parts), value)
            return doc

    def add(self, name, config, *ignored_args, **ignored_kwargs):
        """ Adds a new JSON Pointer expression to the store.
        """
        # Make sure it's valid, no exception in 'resolve' means the expression was valid.
        pointer = JsonPointer(config.value)
        pointer.resolve({}, None)

        with self.update_lock:
            self.data[name] = pointer

# ################################################################################################################################

class Mapper(object):
    def __init__(self, source, target=None, time_util=None, skip_missing=True, default=None, *args, **kwargs):
        self.target = target if target is not None else {}
        self.map_type = kwargs.get('msg_type', MSG_MAPPER.DICT_TO_DICT)
        self.skip_ns = kwargs.get('skip_ns', True)
        self.time_util = time_util
        self.skip_missing = skip_missing
        self.default = default
        self.subs = {}
        self.funcs = {'int':int, 'long':long, 'bool':asbool, 'dec':Decimal, 'arrow':arrow_get}
        self.func_keys = self.funcs.keys()
        self.times = {}
        self.cache = {}

        if isinstance(source, DictNav):
            self.source = source
        else:
            if self.map_type.startswith('dict-to-'):
                self.source = DictNav(source)

    def set_time(self, name, format):
        self.times[name] = format

    def set_substitution(self, name, value):
        self.subs[name] = value

    def set_func(self, name, func):
        self.funcs[name] = func
        self.func_keys = self.funcs.keys()

    def map(self, from_, to, separator='/', skip_missing=ZATO_NOT_GIVEN, default=ZATO_NOT_GIVEN):
        """ Maps 'from_' into 'to', splitting from using the 'separator' and applying
        transformation functions along the way.
        """
        if skip_missing == ZATO_NOT_GIVEN:
            skip_missing = self.skip_missing

        if default == ZATO_NOT_GIVEN:
            default = self.default

        # Store for later use, such as in log entries.
        orig_from = from_
        force_func = None
        force_func_name = None
        needs_time_reformat = False
        from_format, to_format = None, None

        # Perform any string substitutions first.
        if self.subs:
            from_.format(**self.subs)
            to.format(**self.subs)

        # Pick at most one processing functions.
        for key in self.func_keys:
            if from_.startswith(key):
                from_ = from_.replace('{}:'.format(key), '', 1)
                force_func = self.funcs[key]
                force_func_name = key
                break

        # Perhaps it's a date value that needs to be converted.
        if from_.startswith('time:'):
            needs_time_reformat = True
            from_format, from_ = self._get_time_format(from_)
            to_format, to_ = self._get_time_format(to)

        # Obtain the value.
        value = self.source.get(from_.split(separator)[1:])

        if needs_time_reformat:
            value = self.time_util.reformat(value, from_format, to_format)

        # Don't return anything if we are to skip missing values
        # or, we aren't, return a default value.
        if not value:
            if skip_missing:
                return
            else:
                value = default if default != ZATO_NOT_GIVEN else value

        # We have some value, let's process it using the function found above.
        if force_func:
            try:
                value = force_func(value)
            except Exception:
                logger.warn('Error in force_func:`%s` `%s` over `%s` in `%s` -> `%s` e:`%s`',
                    force_func_name, force_func, value, orig_from, to, format_exc())
                raise

        dpath_util.new(self.target, to, value)

    def map_many(self, items, *args, **kwargs):
        for to, from_ in items:
            self.map(to, from_, *args, **kwargs)

    def get(self, path, default=None, separator='/'):
        for found_path, value in dpath_util.search(self.source.obj, path, yielded=True, separator=separator):
            if path == '{}{}'.format(separator, found_path):
                return value

        return default

    def set(self, to, value):
        """ Sets 'to' to a static 'value'.
        """
        dpath_util.new(self.target, to, value)

    def _get_time_format(self, path):
        path = path.split('time:')[1]
        sep_idx = path.find(':')
        return self.times[path[:sep_idx]], path[sep_idx+1:]
