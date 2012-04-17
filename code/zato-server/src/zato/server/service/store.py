# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import imp, inspect, logging, os, shutil, sys, tempfile, zipimport
from datetime import datetime
from hashlib import sha256
from importlib import import_module
from os.path import getmtime
from traceback import format_exc
from uuid import uuid4

# Distribute
import pkg_resources

# pip
from pip.download import is_archive_file

# anyjson
from anyjson import dumps

# PyYAML
try:
    from yaml import CDumper  # Looks awkward but
    Dumper = CDumper          # it's to make import checkers happy
except ImportError:
    from yaml import Dumper

# Spring Python
from springpython.util import synchronized
from springpython.context import InitializingObject

# Zato
from zato.common import SourceInfo
from zato.common.util import deployment_info, is_python_file, service_name_from_impl, TRACE1
from zato.server.service import Service
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

def get_service_name(class_obj):
    """ Return the name of a service which will be either given us explicitly
    via the 'name' attribute or it will be a concatenation of the name of the
    class and its module's name.
    """
    return getattr(class_obj, 'name', '%s.%s' % (class_obj.__module__, class_obj.__name__))

class ServiceStore(InitializingObject):
    """ A store of Zato services.
    """
    def __init__(self, services=None, service_store_config=None, odb=None):
        self.services = services
        self.service_store_config = service_store_config
        self.odb = odb

    def _invoke_hook(self, object_, hook_name):
        """ A utility method for invoking various service's hooks.
        """
        try:
            hook = getattr(object_, hook_name)
            hook()
        except Exception:
            msg = 'Error while invoking [%s] on service [%s] ' \
                ' e=[%s]' % (hook_name, service_name, format_exc())
            logger.error(msg)

    def new_instance(self, class_name):
        """ Returns a new instance of a service of the given name.
        """
        return self.services[class_name]['service_class']()

    def service_data(self, class_name):
        """ Returns all the service-related data.
        """
        return self.services[class_name]

    def import_services_from_fs(self, items, base_dir):
        """ Imports services from all the specified resources, be it module names,
        individual files or distutils2 packages.
        """
        for item_name in items:
            logger.debug('About to import services from:[%s]', item_name)
            
            is_internal = item_name.startswith('zato')
            
            # distutils2 ..
            if is_archive_file(item_name):
                pass
            
            # .. a .py/.pyc/.pyw
            elif is_python_file(item_name):
                self.import_services_from_file(item_name, is_internal, base_dir)
            
            # .. must be a module object
            else:
                self.import_services_from_module(item_name, is_internal)

    def import_services_from_file(self, file_name, is_internal, base_dir):
        """ Imports all the services from the path to a file.
        """
        if not os.path.isabs(file_name):
            file_name = os.path.normpath(os.path.join(base_dir, file_name))

        if not os.path.exists(file_name):
            raise ValueError("Could not import services, path:[{}] doesn't exist".format(file_name))
        
        mod_dir, mod_file = os.path.split(file_name)
        mod_name, mod_ext = os.path.splitext(mod_file)
        
        mod = imp.load_source(mod_name, file_name)
        self._visit_module(mod, is_internal, file_name)
        
    def import_services_from_module(self, mod_name, is_internal):
        """ Imports all the services from a module specified by the given name.
        """
        mod = import_module(mod_name)
        self._visit_module(mod, is_internal, inspect.getfile(mod))
        
    def _should_deploy(self, name, item):
        """ Is an object something we can deploy on a server?
        """
        try:
            if issubclass(item, Service):
                if item is not AdminService and item is not Service:
                    return True
        except TypeError, e:
            # Ignore non-class objects passed in to issubclass
            logger.log(TRACE1, 'Ignoring exception, name:[{}], item:[{}], e:[{}]'.format(name, item, format_exc(e)))
            
    def _get_source_code_info(self, mod):
        """ Returns the source code of and the FS path to the given module.
        """
        si = SourceInfo()
        try:
            si.source = inspect.getsource(mod)
            si.path = inspect.getsourcefile(mod)
            si.hash = sha256(si.source).hexdigest()
            si.hash_method = 'SHA-256'
        except IOError, e:
            logger.log(TRACE1, 'Ignoring IOError, mod:[{}], e:[{}]'.format(mod, format_exc(e)))
            
        return si
                
    def _visit_module(self, mod, is_internal, fs_location):
        """ Actually imports services from a module object.
        """
        for name in dir(mod):
            item = getattr(mod, name)
            if self._should_deploy(name, item):
                timestamp = datetime.utcnow().isoformat()
                depl_info = deployment_info('ServiceStore', item, timestamp, fs_location)
    
                class_name = '{}.{}'.format(item.__module__, item.__name__)
                self.services[class_name] = depl_info
                
                si = self._get_source_code_info(mod)
    
                last_mod = datetime.fromtimestamp(getmtime(mod.__file__))
                self.odb.add_service(service_name_from_impl(class_name), class_name, is_internal, timestamp, dumps(str(depl_info)), si)
