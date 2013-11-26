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

# lxml
from lxml import etree

# xmldict
from xmltodict import parse, unparse

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

class _BaseXPathStore(object):
    """ Both XPath and ElemPath stores have common functionality that is kept
    in this class.
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
            compiled_elem, compiled_text = self.compile(item.value, ns_map)

            self.data[name] = Bunch()
            self.data[name].config = item
            self.data[name].compiled_text = compiled_text
            self.data[name].compiled_elem = compiled_elem

    create = _update

    def _compile(self, expr, ns_map={}):
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
        self.create(msg.name, msg, ns_map)

    def on_broker_msg_edit(self, msg, ns_map):
        """ Updates an existing XPath.
        """
        with self.update_lock:
            del self.data[msg.old_name]
        self._update(msg.name, msg, ns_map)

    def on_broker_msg_delete(self, msg, *args):
        """ Deletes an XPath.
        """
        with self.update_lock:
            del self.data[msg.name]

# ##############################################################################

class ElemPathStore(_BaseXPathStore):
    def _elem_path_to_xpath(self, expr):
        logger.debug('Original expr:[%s]', expr)

        if expr[:2] == '*.':
            expr = '//{}'.format(expr[2:])
        else:
            expr = '/{}'.format(expr)

        if expr.endswith('.text'):
            expr = expr[:-5]

        expr = expr.replace('.*.', '//').replace('.', '/')

        logger.debug('Reformatted expr:[%s]', expr)

        return expr, '{}/text()'.format(expr)

    def compile(self, expr, ns_map={}):
        elem_path, text_path = self._elem_path_to_xpath(expr)
        return self._compile(elem_path, ns_map), self._compile(text_path, ns_map)

    def convert_dict_to_xml(self, d):
        return unparse(d).encode('utf-8')

    def convert_xml_to_dict(self, xml):
        return parse(xml)

    def invoke(self, msg, expr_name, needs_text=True, needs_tree=False):
        """ Invokes an expression of expr_name against the msg and returns
        results.
        """
        logger.debug('ElemPath expr_name:[%s], msg:[%s], needs_text:[%s]', 
            expr_name, msg, needs_text)

        if isinstance(msg, dict):
            msg = self.convert_dict_to_xml(msg)

        logger.debug('ElemPath msg:[%s]', msg)

        expr = self.data[expr_name]

        if needs_text:
            compile_func = expr.compiled_text
        else:
            compile_func = expr.compiled_elem

        logger.debug('ElemPath compile_func:[%s]', compile_func)

        tree = etree.fromstring(msg)
        result = compile_func(tree)

        if expr.config.value.endswith('.text') and len(result) == 1:
            result = result[0]

        if needs_tree:
            return result, tree
        else:
            return result

    def replace(self, msg, expr_name, new_value):
        """ Evaluates expr_name against a msg which can be either a dictionary
        or an XML string. Text value of all  the elements returned is replaced
        with new_value.
        """
        orig_msg = msg

        if isinstance(msg, dict):
            msg = self.convert_dict_to_xml(msg)

        result, tree = self.invoke(msg, expr_name, False, True)

        if isinstance(result, list):
            for elem in result:
                elem.text = new_value
        else:
            result.text = new_value

        if isinstance(orig_msg, dict):
            return self.convert_xml_to_dict(etree.tostring(tree))

        return etree.tostring(tree)

# ##############################################################################

class XPathStore(_BaseXPathStore):
    """ Keeps config of and evaluates XPath expressions.
    """
    def compile(self, expr, ns_map={}):
        return self._compile(expr, ns_map)

    def invoke(self, msg, expr_name):
        """ Runs a given XPath expression against the message.
        """
        return self.data[expr_name].compiled(msg)

# ##############################################################################
