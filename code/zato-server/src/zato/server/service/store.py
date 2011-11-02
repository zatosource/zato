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
import imp, logging, os, shutil, sys, tempfile, time, zipimport
from datetime import datetime
from os.path import getmtime
from traceback import format_exc
from uuid import uuid4

# Distribute
import pkg_resources

# PyYAML
from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

# Spring Python
from springpython.util import synchronized
from springpython.context import InitializingObject

# Zato
from zato.common import ZATO_OK
from zato.common.util import TRACE1
from zato.server.service import Service

__all__ = ['Service']

logger = logging.getLogger(__name__)

def get_service_name(class_obj):
    """ Return the name of a service which will be either given us explicitly
    via the 'name' attribute or it will be a concatenation of the name of the
    class and its module's name.
    """
    return getattr(class_obj, 'name', '%s.%s' % (class_obj.__module__, class_obj.__name__))

def _get_services(module, egg_path, names_only):
    """ Iterates through a Python module object and returns a dictionary
    of services, keyed by their names. If 'names_only' is True, return only
    the names of services, dictionary values are all set to True.
    """
    services = {}
    contents = dir(module)
    logger.debug('Module contents %s' % contents)

    for item in contents:
        obj = getattr(module, item)

        try:
            is_service = issubclass(obj, Service) and not obj is Service
        except TypeError, e:
            # Ignore non-class objects passed to issubclass.
            is_service = False

        if is_service:
            service_name = get_service_name(obj)
            logger.debug('Found service [%s] to pick up, egg_path=[%s]' % (
                service_name, egg_path))

            # Just return True if told not to actually fetch services.
            if names_only:
                services[service_name] = True
            else:
                services[service_name] = obj

    return services

def _visit_egg(egg_path, names_only):
    """ Make sure the .egg is internally consistent and either return the actual
    services defined in an .egg or their names only.
    """

    # By default we assume there are no services to import.
    services = None

    # A list of modules available in sys.modules right before we attempt to
    # import services from the .egg. It will be populated and restored later
    # on below.
    original_modules = []

    imp.acquire_lock()
    try:
        metadata = pkg_resources.EggMetadata(zipimport.zipimporter(egg_path))
        dist = pkg_resources.Distribution.from_filename(egg_path, metadata)
        dist.activate()

        try:

            # top_level will be a module that holds a 'services' submodule which
            # will in turn have a list of Zato services to import (if any).
            top_level = dist.get_metadata('top_level.txt')

            if top_level:
                top_level = top_level.strip()
                services_mod_name = top_level + '.services'

                try:
                    # Make a snapshot of modules' names to be restored once
                    # we fetch the services.
                    original_modules = sys.modules.keys()

                    if logger.isEnabledFor(TRACE1):
                        msg = 'sorted(original_modules)=[%s]' % sorted(original_modules)
                        logger.log(TRACE1, msg)

                    # We know we are going to import the correct module because
                    # we're inside an import lock and we've just activated an .egg
                    # distribution.
                    __import__(services_mod_name)

                except ImportError:
                    msg = 'Could not import services, package [%s] doesn\'t ' \
                        'seem to contain a \'services\' module. egg_path=[%s], ' \
                        'e=[%s]' % (top_level, egg_path, format_exc())
                    logger.error(msg)
                else:
                    try:
                        # OK, does the .egg have any services to import?
                        services = _get_services(sys.modules[services_mod_name],
                                                      egg_path, names_only)
                    finally:
                        current_modules = sys.modules.keys()

                        if logger.isEnabledFor(TRACE1):
                            msg = 'sorted(current_modules)=[%s]' % sorted(current_modules)
                            logger.log(TRACE1, msg)

                        mod_diff = set(current_modules) - set(original_modules)

                        # Has been added to sys.modules by calling dist.activate above
                        mod_diff.add(top_level)

                        msg = 'Will now delete modules from sys.modules [%s]' % mod_diff
                        logger.debug(msg)

                        for mod_name in mod_diff:
                            del sys.modules[mod_name]
                            msg = 'module [%s] deleted from sys.modules' % mod_name
                            logger.log(TRACE1, msg)

                        if logger.isEnabledFor(TRACE1):
                            msg = 'sorted(sys.modules.keys()) after removing ' \
                                'newly imported ones [%s]' % sorted(sys.modules.keys())
                            logger.log(TRACE1, msg)

            else:
                msg = 'Could not find a top-level module to import, ' \
                    'seems like EGG-INFO/top_level.txt is empty, ' \
                    'egg_path=[%s]' % egg_path
                logger.error(msg)
        finally:
            # It's safe to delete the newly added distribution because
            # we're still holding onto an import lock and if we managed to get
            # here it means the distribution has been activated.
            msg = 'Will now delete egg_path [%s] from sys.path' % egg_path
            logger.debug(msg)

            egg_idx = sys.path.index(egg_path)

            if logger.isEnabledFor(TRACE1):
                msg = 'egg_idx=[%s], sys.path=[%s]' % (egg_idx, sys.path)
                logger.log(TRACE1, msg)

            del sys.path[egg_idx]

    finally:
        imp.release_lock()

    return services


class ServiceStore(InitializingObject):
    """ A store of Zato services.
    """
    def __init__(self, services=None, service_store_config=None, odb=None):
        self.services = services
        self.service_store_config = service_store_config
        self.odb = odb

    def read_service_store_config(self, location):
        data = load(open(location), Loader=Loader)
        self.service_store_config = data['services']

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

    @synchronized()
    def import_services_from_egg(self, egg_path, parallel_server):
        """ Imports new Zato services from their working dir and registers them
        with the server, making them available for immediate use - which doesn't
        mean they'll be necessarily visible to the outside world unless
        they have been already configured and now they're only being redeployed.
        """

        services = _visit_egg(egg_path, names_only=False)
        logger.debug('services to import [%s]' % services)

        for service_name in services:
            if service_name in self.services:
                old_service = self.services[service_name]['service']

                # 'before_remove_from_store' hook
                self._invoke_hook(old_service, 'before_remove_from_store')

                del self.services[service_name]

                # 'after_remove_from_store' hook
                self._invoke_hook(old_service, 'after_remove_from_store')

            data = {}
            data['egg_path'] = egg_path
            data['service_class'] = services[service_name]

            # 'before_add_to_store' hook
            self._invoke_hook(services[service_name], 'before_add_to_store')

            self.services[service_name] = data

            # 'after_add_to_store' hook
            self._invoke_hook(services[service_name], 'after_add_to_store')

            msg = 'Service [%s] imported, parallel_server=[%s], egg_path=[%s]' % (
                service_name, parallel_server, egg_path)
            logger.info(msg)

        logger.debug('Services after an import [%s]' % self.services)

    def read_internal_services(self):

        # Import internal services here to avoid circular dependencies.
        from zato.server.service import internal
        from zato.server.service.internal import AdminService
        from zato.server.service.internal import sql, scheduler, service
        from zato.server.service.internal.channel import soap
        from zato.server.service.internal.definition import amqp
        from zato.server.service.internal.security import basic_auth, \
             tech_account, wss

        # XXX: The list would be better read from the IoC container
        modules = [amqp, internal, sql, scheduler, service, soap, wss, 
                   tech_account,  basic_auth]

        # Read all definitions of Zato's own internal services.
        for mod in modules:
            for name in dir(mod):
                item = getattr(mod, name)
                try:
                    if issubclass(item, Service):
                        if item is not AdminService and item is not Service:

                            # TODO: Interal services should in fact be stored in .eggs
                            data = {'service_class': item, 'egg_path':'INTERNAL_SERVICE'}
                            data['deployment_time'] = datetime.now().isoformat()
                            data['deployment_user'] = 'INTERNAL_SERVICE'
                            
                            class_name = '%s.%s' % (item.__module__, item.__name__)
                            self.services[class_name] = data

                            last_mod = datetime.fromtimestamp(getmtime(mod.__file__))
                            self.odb.add_service(class_name, class_name, True,
                                                 last_mod, str(data))
                            
                except TypeError, e:
                    # Ignore non-class objects passed in to issubclass
                    logger.log(TRACE1, 'Ignoring exception, name=[%s], item=[%s], e=[%s]' % (
                        name, item, format_exc()))

        logger.debug('Internal services read=[%s]' % self.services)


class EggServiceImporter(object):
    """ A utility class for importing Zato services off the file system.
    """
    def __init__(self, work_dir=None, service_store_config=None, config_repo_manager=None):
        self.work_dir = work_dir
        self.service_store_config = service_store_config
        self.config_repo_manager = config_repo_manager

    @synchronized()
    def import_services(self, original_egg_path, singleton_server):
        """ Imports Zato services off an .egg distribution if it defines any.
        # 1) Move the .egg to a temporary location,
        # 2) See if it defines any services,
        # 2a) Move it to a target import dir if it does,
        # 2b) Update configuration,
        # 2c) Notify parallel servers,
        # 3) Clean up the temporary location.
        """

        # 1) Move the .egg to a temporary location
        tmp_dir = tempfile.mkdtemp()
        shutil.move(original_egg_path, tmp_dir)
        tmp_egg_path = os.path.join(tmp_dir, os.path.basename(original_egg_path))

        msg = '.egg moved from [%s] to [%s]' % (original_egg_path, tmp_egg_path)
        logger.debug(msg)

        # 2) See if it defines any services ..
        services = _visit_egg(tmp_egg_path, names_only=True)

        if services:

            # 2a) .. move it to a target import dir if it does ..
            # TODO: Make the .egg name part of the target dir name
            target_dir = os.path.join(self.work_dir, uuid4().hex)
            os.mkdir(target_dir)
            shutil.move(tmp_egg_path, target_dir)

            msg = '.egg moved from [%s] to [%s]' % (tmp_egg_path, target_dir)
            logger.debug(msg)

            target_egg_path = os.path.join(target_dir, os.path.basename(original_egg_path))

            # 2b) .. update configuration ..
            for service in services:

                if logger.isEnabledFor(logging.DEBUG):
                    msg = 'About to update configuration, services found=[%s]' % sorted(services)
                    logger.debug(msg)

                    for service in services:
                        if service in self.service_store_config:
                            text = 'will be updated'
                            # TODO: Log old .egg location
                        else:
                            text = 'will be added'
                        msg = 'Service [%s] %s, egg=[%s]' % (service, text, target_egg_path)
                        logger.debug(msg)

                data = {'egg_path': target_egg_path}
                self.service_store_config[service] = data

            # Make the changes persistent.
            self.config_repo_manager.update_service_store_config(self.service_store_config)

            # 2c) .. notify parallel servers ..
            singleton_server.load_egg_services(target_egg_path)

        # 3) .. and clean up the temporary location.
        shutil.rmtree(tmp_dir)
        logger.log(TRACE1, 'tmp_dir [%s] removed' % tmp_dir)
