# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import inspect
import logging
import os
from datetime import datetime
from hashlib import sha256
from importlib import import_module
from json import dumps
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import bunchify

# dill
from dill import dumps as dill_dumps, load as dill_load

# gevent
from gevent.lock import RLock

# PyYAML
try:
    from yaml import CDumper  # Looks awkward but it's to make import checkers happy
    Dumper = CDumper
except ImportError:
    from yaml import Dumper   # ditto
    Dumper = Dumper

# Spring Python
from springpython.context import InitializingObject

# Zato
from zato.common import DONT_DEPLOY_ATTR_NAME, KVDB, SourceInfo, TRACE1
from zato.common.match import Matcher
from zato.common.util import decompress, deployment_info, fs_safe_now, import_module_from_path, is_python_file, visit_py_source
from zato.server.service import after_handle_hooks, after_job_hooks, before_handle_hooks, before_job_hooks, Service, \
    zato_no_op_marker
from zato.server.service.internal import AdminService

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

hook_methods = ('accept',) + before_handle_hooks + after_handle_hooks + before_job_hooks + after_job_hooks

def set_up_class_attributes(class_, service_store=None, name=None):
    class_.add_http_method_handlers()

    # Set up enforcement of what other services a given service can invoke
    try:
        class_.invokes
    except AttributeError:
        class_.invokes = []

    try:
        class_.SimpleIO
        class_.has_sio = True
    except AttributeError:
        class_.has_sio = False

    # May be None during unit-tests. Not every one will provide it because it's not always needed in a given test.
    if service_store:

        # Set up all attributes that do not have to be assigned to each instance separately
        # and can be shared as class attributes.
        class_._enforce_service_invokes = service_store.server.enforce_service_invokes

        class_.odb = service_store.server.worker_store.server.odb
        class_.kvdb = service_store.server.worker_store.kvdb
        class_.pubsub = service_store.server.worker_store.pubsub
        class_.cloud.openstack.swift = service_store.server.worker_store.worker_config.cloud_openstack_swift
        class_.cloud.aws.s3 = service_store.server.worker_store.worker_config.cloud_aws_s3
        class_._out_ftp = service_store.server.worker_store.worker_config.out_ftp
        class_.amqp.invoke = class_.amqp.send = service_store.server.worker_store.amqp_invoke # .send is for pre-3.0 backward compat
        class_.amqp.invoke_async = class_.amqp.send = service_store.server.worker_store.amqp_invoke_async

        class_._worker_store = service_store.server.worker_store
        class_._worker_config = service_store.server.worker_store.worker_config
        class_._msg_ns_store = service_store.server.worker_store.worker_config.msg_ns_store
        class_._json_pointer_store = service_store.server.worker_store.worker_config.json_pointer_store
        class_._xpath_store = service_store.server.worker_store.worker_config.xpath_store

        _req_resp_freq_key = '%s%s' % (KVDB.REQ_RESP_SAMPLE, name)
        class_._req_resp_freq = int(service_store.server.kvdb.conn.hget(_req_resp_freq_key, 'freq') or 0)

        class_.component_enabled_cassandra = service_store.server.fs_server_config.component_enabled.cassandra
        class_.component_enabled_email = service_store.server.fs_server_config.component_enabled.email
        class_.component_enabled_search = service_store.server.fs_server_config.component_enabled.search
        class_.component_enabled_msg_path = service_store.server.fs_server_config.component_enabled.msg_path
        class_.component_enabled_websphere_mq = service_store.server.fs_server_config.component_enabled.websphere_mq
        class_.component_enabled_odoo = service_store.server.fs_server_config.component_enabled.odoo
        class_.component_enabled_stomp = service_store.server.fs_server_config.component_enabled.stomp
        class_.component_enabled_zeromq = service_store.server.fs_server_config.component_enabled.zeromq
        class_.component_enabled_patterns = service_store.server.fs_server_config.component_enabled.patterns
        class_.component_enabled_target_matcher = service_store.server.fs_server_config.component_enabled.target_matcher
        class_.component_enabled_invoke_matcher = service_store.server.fs_server_config.component_enabled.invoke_matcher

    # Replace hook methods with None if they have not been overridden by users.
    # Each method's .im_func.func_defaults attribute will be a one-element tuple in the form such as ('_zato_no_op_marker',)
    # if it's not been redefined from parent class. We replace it with None and Service.update_handle does not call
    # the hook if it's not been defined by user thus not incurring overhead of function calls that cost even if no-op.

    class_._before_job_hooks = []
    class_._after_job_hooks = []

    for func_name in hook_methods:
        func = getattr(class_, func_name, None)
        if func and inspect.ismethod(func):
            func_defaults = func.im_func.func_defaults

            # Replace with None ..
            if func_defaults and isinstance(func_defaults, tuple) and zato_no_op_marker in func_defaults:
                impl = None

            # .. or use the method as is.
            else:
                impl = func

            # Assign to class either the replaced value or the original one.
            setattr(class_, func_name, impl)

            if impl and func_name in before_job_hooks:
                class_._before_job_hooks.append(impl)

            if impl and func_name in after_job_hooks:
                class_._after_job_hooks.append(impl)

    class_._has_before_job_hooks = bool(class_._before_job_hooks)
    class_._has_after_job_hooks = bool(class_._after_job_hooks)

# ################################################################################################################################

def get_service_name(class_obj):
    """ Return the name of a service which will be either given us explicitly
    via the 'name' attribute or it will be a concatenation of the name of the
    class and its module's name.
    """
    return getattr(class_obj, 'name', '%s.%s' % (class_obj.__module__, class_obj.__name__))

# ################################################################################################################################

class ServiceStore(InitializingObject):
    """ A store of Zato services.
    """
    def __init__(self, services=None, service_store_config=None, odb=None, server=None):
        self.services = services
        self.service_store_config = service_store_config
        self.odb = odb
        self.server = server
        self.id_to_impl_name = {}
        self.impl_name_to_id = {}
        self.name_to_impl_name = {}
        self.update_lock = RLock()
        self.patterns_matcher = Matcher()

# ################################################################################################################################

    def _invoke_hook(self, object_, hook_name):
        """ A utility method for invoking various service's hooks.
        """
        try:
            hook = getattr(object_, hook_name)
            hook()
        except Exception:
            logger.error('Error while invoking `%s` on service `%s` e:`%s`', hook_name, object_, format_exc())

# ################################################################################################################################

    def new_instance(self, class_name):
        """ Returns a new instance of a service of the given impl name.
        """
        _info = self.services[class_name]
        return _info['service_class'](), _info['is_active']

# ################################################################################################################################

    def new_instance_by_id(self, service_id):
        impl_name = self.id_to_impl_name[service_id]
        return self.new_instance(impl_name)

# ################################################################################################################################

    def new_instance_by_name(self, name):
        impl_name = self.name_to_impl_name[name]
        return self.new_instance(impl_name)

# ################################################################################################################################

    def service_data(self, impl_name):
        """ Returns all the service-related data.
        """
        return self.services[impl_name]

# ################################################################################################################################

    def decompress(self, archive, work_dir):
        """ Decompresses an archive into a randomly named directory.
        """
        # 6 characters will do, we won't deploy millions of services
        # in the very same (micro-)second after all
        rand = uuid4().hex[:6]

        dir_name = os.path.join(work_dir, '{}-{}'.format(fs_safe_now(), rand), os.path.split(archive)[1])
        os.makedirs(dir_name)

        # .. unpack the archive into it ..
        decompress(archive, dir_name)

        # .. and return the name of the newly created directory so that the
        # rest of the machinery can pick the services up
        return dir_name

# ################################################################################################################################

    def import_internal_services(self, items, base_dir, sync_internal, is_first):
        """ Imports and optionally caches locally internal services.
        """
        cache_file_path = os.path.join(base_dir, 'config', 'repo', 'internal-cache.dat')

        # sync_internal may be False but if the cache does not exist (which is the case if a server starts up the first time),
        # we need to create it anyway and sync_internal becomes True then. However, the should be created only by the very first
        # worker in a group of workers - the rest can simply assume that the cache is ready to read.
        if is_first and not os.path.exists(cache_file_path):
            sync_internal = True

        if sync_internal:

            # Synchronizing internal modules means re-building the internal cache from scratch
            # and re-deploying everything.

            service_info = []
            internal_cache = {
                'service_info': service_info
            }

            deployed = self.import_services_from_anywhere(items, base_dir)

            for class_ in deployed:
                impl_name = class_.get_impl_name()
                service_info.append({
                    'class_': class_,
                    'mod': inspect.getmodule(class_),
                    'impl_name': impl_name,
                    'service_id': self.impl_name_to_id[impl_name],
                    'is_active': self.services[impl_name]['is_active'],
                    'slow_threshold': self.services[impl_name]['slow_threshold'],
                    'fs_location': inspect.getfile(class_),
                })


            # All set, write out the cache file
            f = open(cache_file_path, 'wb')
            f.write(dill_dumps(internal_cache))
            f.close()

            return deployed

        else:
            deployed = []

            f = open(cache_file_path, 'rb')
            items = bunchify(dill_load(f))
            f.close()

            for item in items.service_info:
                self._visit_class(item.mod, deployed, item.class_, item.fs_location, True,
                    item.service_id, item.is_active, item.slow_threshold)

            return deployed

# ################################################################################################################################

    def import_services_from_anywhere(self, items, base_dir, work_dir=None):
        """ Imports services from any of the supported sources, be it module names,
        individual files, directories or distutils2 packages (compressed or not).
        """
        deployed = []

        for item in items:
            logger.debug('About to import services from:`%s`', item)

            is_internal = item.startswith('zato')

            # A regular directory
            if os.path.isdir(item):
                deployed.extend(self.import_services_from_directory(item, base_dir))

            # .. a .py/.pyw
            elif is_python_file(item):
                deployed.extend(self.import_services_from_file(item, is_internal, base_dir))

            # .. must be a module object
            else:
                deployed.extend(self.import_services_from_module(item, is_internal))

        return deployed

# ################################################################################################################################

    def import_services_from_file(self, file_name, is_internal, base_dir):
        """ Imports all the services from the path to a file.
        """
        deployed = []

        try:
            mod_info = import_module_from_path(file_name, base_dir)
        except Exception, e:
            msg = 'Could not load source, file_name:`%s`, e:`%s`'
            logger.error(msg, file_name, format_exc(e))
        else:
            deployed.extend(self._visit_module(mod_info.module, is_internal, mod_info.file_name))
        finally:
            return deployed

# ################################################################################################################################

    def import_services_from_directory(self, dir_name, base_dir):
        """ dir_name points to a directory.

        If dist2 is True, the directory is assumed to be a Distutils2 one and its
        setup.cfg file is read and all the modules from packages pointed to by the
        'files' section are scanned for services.

        If dist2 is False, this will be treated as a directory with a flat list
        of Python source code to import, as is the case with services that have
        been hot-deployed.
        """
        deployed = []

        for py_path in visit_py_source(dir_name):
            deployed.extend(self.import_services_from_file(py_path, False, base_dir))

        return deployed

# ################################################################################################################################

    def import_services_from_module(self, mod_name, is_internal):
        """ Imports all the services from a module specified by the given name.
        """
        return self.import_services_from_module_object(import_module(mod_name), is_internal)

# ################################################################################################################################

    def import_services_from_module_object(self, mod, is_internal):
        """ Imports all the services from a Python module object.
        """
        return self._visit_module(mod, is_internal, inspect.getfile(mod))

# ################################################################################################################################

    def _should_deploy(self, name, item):
        """ Is an object something we can deploy on a server?
        """
        try:
            if issubclass(item, Service):
                if item is not AdminService and item is not Service:
                    if not hasattr(item, DONT_DEPLOY_ATTR_NAME):

                        service_name = item.get_name()

                        if self.patterns_matcher.is_allowed(service_name):
                            return True
                        else:
                            logger.info('Skipped disallowed `%s`', service_name)
        except TypeError, e:
            # Ignore non-class objects passed in to issubclass
            logger.log(TRACE1, 'Ignoring exception, name:`%s`, item:`%s`, e:`%s`', name, item, format_exc(e))

# ################################################################################################################################

    def _get_source_code_info(self, mod):
        """ Returns the source code of and the FS path to the given module.
        """
        si = SourceInfo()
        try:
            file_name = mod.__file__
            if file_name[-1] in('c', 'o'):
                file_name = file_name[:-1]

            # We would've used inspect.getsource(mod) hadn't it been apparently using
            # cached copies of the source code
            si.source = open(file_name, 'rb').read()

            si.path = inspect.getsourcefile(mod)
            si.hash = sha256(si.source).hexdigest()
            si.hash_method = 'SHA-256'

        except IOError, e:
            logger.log(TRACE1, 'Ignoring IOError, mod:`%s`, e:`%s`', mod, format_exc(e))

        return si

# ################################################################################################################################

    def _visit_class(self, mod, deployed, class_, fs_location, is_internal, service_id=None, is_active=None, slow_threshold=None):
        timestamp = datetime.utcnow()
        depl_info = dumps(deployment_info('service-store', str(class_), timestamp.isoformat(), fs_location))

        name = class_.get_name()
        impl_name = class_.get_impl_name()

        set_up_class_attributes(class_, self, name)

        self.services[impl_name] = {}
        self.services[impl_name]['name'] = name
        self.services[impl_name]['deployment_info'] = depl_info
        self.services[impl_name]['service_class'] = class_

        si = self._get_source_code_info(mod)

        if not(service_id and is_active is not None and slow_threshold):
            service_id, is_active, slow_threshold = self.odb.add_service(
                name, impl_name, is_internal, timestamp, dumps(str(depl_info)), si)

        deployed.append(class_)

        self.services[impl_name]['is_active'] = is_active
        self.services[impl_name]['slow_threshold'] = slow_threshold

        self.id_to_impl_name[service_id] = impl_name
        self.impl_name_to_id[impl_name] = service_id
        self.name_to_impl_name[name] = impl_name

        logger.debug('Imported service:`%s`', name)

        class_.after_add_to_store(logger)

# ################################################################################################################################

    def on_worker_initialized(self):
        """ Executed after a worker has been fully initialized, e.g. all connectors are started and references to these objects
        can be assigned as class-wide attributes to services.
        """

# ################################################################################################################################

    def _visit_module(self, mod, is_internal, fs_location, needs_odb_deployment=True):
        """ Actually imports services from a module object.
        """
        deployed = []
        try:
            for name in sorted(dir(mod)):
                with self.update_lock:
                    item = getattr(mod, name)

                    if self._should_deploy(name, item):
                        if item.before_add_to_store(logger):
                            self._visit_class(mod, deployed, item, fs_location, is_internal)
                        else:
                            logger.info('Skipping `%s` from `%s`', item, fs_location)

        except Exception, e:
            logger.error(
                'Exception while visit mod:`%s`, is_internal:`%s`, fs_location:`%s`, e:`%s`',
                mod, is_internal, fs_location, format_exc(e))
        finally:
            return deployed

# ################################################################################################################################
