# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from threading import RLock
from traceback import format_exc

# Bunch
from bunch import Bunch

# lxml
from lxml import etree

logger = logging.getLogger(__name__)

# ##############################################################################

class MessageFacade(object):
    """ An object through which services access all the message-related features,
    such as namespaces, ElemPath or XPath.
    """
    def __init__(self, msg_ns_store=None, elem_path_store=None, xpath_store=None):
        self.ns = msg_ns_store
        self.elem_path_store = elem_path_store
        self.xpath_store = xpath_store

    def elem_path(self, msg, name):
        return self.elem_path_store.get(name).invoke(msg)

    def xpath(self, msg, name):
        return self.xpath_store.invoke(msg, name)

# ##############################################################################

class NamespaceStore(object):
    """ A store of all the namespaces used with XML processing.
    """
    def __init__(self, data={}):
        self.data = Bunch.fromDict(data)
        self.ns_map = {}
        self.update_lock = RLock()

    def __getitem__(self, name):
        return self.data[name].config.value

    def _update(self, name, item):
        with self.update_lock:
            self.data[name] = Bunch()
            self.data[name].config = item
            self.ns_map[name] = self.data[name].config.value

    create = _update

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
        self._update(msg.name, msg)

    def on_broker_msg_MSG_NS_DELETE(self, msg, *args):
        """ Deletes a namespace.
        """
        with self.update_lock:
            del self.data[msg.name]
            del self.ns_map[msg.name]

# ##############################################################################

class ElemPathStore(object):
    pass

# ##############################################################################

class XPathStore(object):
    """ Keeps config of and evaluates XPath expressions.
    """
    def __init__(self, data={}):
        self.data = Bunch.fromDict(data)
        self.update_lock = RLock()

        # Dummy document to test expressions against - will yield
        # an XPathEvalError in an XPath's .evaluate method if a namespace
        # prefix used wasn't defined in a namespace map.
        self.dummy_doc = etree.XML('<dummy/>')

    def __getitem__(self, name):
        return self.data[name].config.value

    def _update(self, name, item, ns_map):
        with self.update_lock:
            # Sanity check hence in a separate line and first
            compiled = self.compile(item.value, ns_map)

            self.data[name] = Bunch()
            self.data[name].config = item
            self.data[name].compiled = compiled

    create = _update

    def on_broker_msg_MSG_XPATH_CREATE(self, msg, ns_map):
        """ Creates a new XPath.
        """
        self.create(msg.name, msg, ns_map)

    def on_broker_msg_MSG_XPATH_EDIT(self, msg, ns_map):
        """ Updates an existing XPath.
        """
        with self.update_lock:
            del self.data[msg.old_name]
        self._update(msg.name, msg, ns_map)

    def on_broker_msg_MSG_XPATH_DELETE(self, msg, *args):
        """ Deletes an XPath.
        """
        with self.update_lock:
            del self.data[msg.name]

    def invoke(self, msg, expr_name):
        """ Runs a given XPath expression against the message.
        """
        return self.data[expr_name].compiled(msg)

    def compile(self, expr, ns_map={}):
        """ Compiles an XPath expression using a namespace map provided, if any,
        and evaluates it against a dummy document to check that all the namespace
        prefixes are valid.
        """
        compiled = etree.XPath(expr, namespaces=ns_map)
        compiled.evaluate(self.dummy_doc)

        return compiled

# ##############################################################################
