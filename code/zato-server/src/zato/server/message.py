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
        return self.xpath_store.get(name).invoke(msg)

# ##############################################################################

class NamespaceStore(object):
    """ A store of all the namespaces used with XML processing.
    """
    def __init__(self, data={}):
        self.data = Bunch.fromDict(data)
        self.update_lock = RLock()

    def __getitem__(self, name):
        return self.data[name].config.value

    def _update(self, name, config):
        with self.update_lock:
            self.data[name] = Bunch.fromDict(config)

    create = _update

    def on_broker_msg_MSG_NS_CREATE(self, msg, *args):
        """ Creates a new namespace
        """
        self.create(msg.name, msg)

    def on_broker_msg_MSG_NS_EDIT(self, msg, *args):
        """ Updates an existing namespace.
        """
        with self.update_lock:
            del self.data[msg.old_name]
        self._update(msg.name, msg)

    def on_broker_msg_MSG_NS_DELETE(self, msg, *args):
        """ Deletes a namespace.
        """
        with self.update_lock:
            del self.data[msg.name]

# ##############################################################################

class ElemPathStore(object):
    pass

# ##############################################################################

class XPathStore(object):
    pass

# ##############################################################################