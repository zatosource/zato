# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from json import loads
from threading import RLock
from traceback import format_exc

# Bunch
from bunch import Bunch

# jsonpointer
from jsonpointer import JsonPointer, JsonPointerException

# lxml
from lxml import etree

# xmldict
from xmltodict import parse, unparse

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

class MessageFacade(object):
    """ An object through which services access all the message-related features,
    such as namespaces, JSON Pointer or XPath.
    """
    def __init__(self, msg_ns_store=None, json_pointer_store=None, xpath_store=None, payload=None):
        self._ns = msg_ns_store
        self._json_pointer_store = json_pointer_store
        self._xpath_store = xpath_store
        self._payload = payload

    def json_pointer(self, doc=None):
        return JSONPointerAPI(doc or self._payload, self._json_pointer_store)

    def xpath(self, msg):
        return self._xpath_store

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

    def create(self, name, item):
        with self.update_lock:
            self.data[name] = Bunch()
            self.data[name].config = item
            self.ns_map[name] = self.data[name].config.value

    def on_broker_msg_MSG_NS_CREATE(self, msg, *args):
        """ Creates a new namespace.
        """
        self.create(msg.name, msg)

    def on_broker_msg_MSG_NS_EDIT(self, msg, *args):
        """ Updates an existing namespace.
        """
        with self.update_lock:
            del self.data[msg.old_name]
            del self.ns_map[msg.old_name]
        self.create(msg.name, msg)

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
        except Exception, e:
            logger.warn('Failed to compile expr:[%s] with ns_map:[%s]', expr, ns_map)
            raise
        else:
            return compiled

    def on_broker_msg_create(self, msg, ns_map):
        """ Creates a new XPath.
        """
        self.add(msg.name, msg.value, ns_map)

    def on_broker_msg_edit(self, msg, ns_map):
        """ Updates an existing XPath.
        """
        with self.update_lock:
            del self.data[msg.old_name]
            self.add(msg.name, msg.value, ns_map)

    def on_broker_msg_delete(self, msg, *args):
        """ Deletes an XPath.
        """
        with self.update_lock:
            del self.data[msg.name]

    def convert_dict_to_xml(self, d):
        return unparse(d).encode('utf-8')

    def convert_xml_to_dict(self, xml):
        return parse(xml)

    def invoke(self, msg, expr_name, needs_text=True, needs_tree=False):
        """ Invokes an expression of expr_name against the msg and returns
        results.
        """
        logger.debug('expr_name:[%s], msg:[%s], needs_text:[%s]', 
            expr_name, msg, needs_text)

        logger.debug('XPath msg:[%s]', msg)

        expr = self.data[expr_name]

        if needs_text:
            compile_func = expr.compiled_text
        else:
            compile_func = expr.compiled_elem

        logger.debug('XPath compile_func:[%s]', compile_func)

        tree = etree.fromstring(msg)
        result = compile_func(tree)

        if expr.config.value.endswith('.text') and len(result) == 1:
            result = result[0]

        if needs_tree:
            return result, tree
        else:
            return result

class XPathStore(BaseStore):
    """ Keeps config of and evaluates XPath expressions.
    """
    def add(self, name, item, ns_map):
        with self.update_lock:
            compiled_elem = self.compile(item.value, ns_map)
            self.data[name] = Bunch()
            self.data[name].config = item
            self.data[name].compiled_elem = compiled_elem

    def set(self, msg, expr_name, new_value):
        """ Evaluates expr_name against a msg which can be either a dictionary
        or an XML string. Text value of all  the elements returned is replaced
        with new_value.
        """
        orig_msg = msg

        result, tree = self.invoke(msg, expr_name, False, True)

        if isinstance(result, list):
            for elem in result:
                elem.text = new_value
        else:
            result.text = new_value

        return etree.tostring(tree)

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

        return self.data[name].set(doc, value, in_place)

    def add(self, name, expr, *ignored_args, **ignored_kwargs):
        """ Adds a new JSON Pointer expression to the store.
        """
        # Make sure it's valid, no exception in 'resolve' means the expression was valid.
        pointer = JsonPointer(expr)
        pointer.resolve({}, None)

        with self.update_lock:
            self.data[name] = pointer

# ################################################################################################################################
