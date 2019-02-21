# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import inspect
import logging
import os
from contextlib import closing
from datetime import datetime
from functools import total_ordering
from hashlib import sha256
from importlib import import_module
from inspect import isclass
from pickle import HIGHEST_PROTOCOL as highest_pickle_protocol
from traceback import format_exc
from typing import Any, List

# dill
from dill import dumps as dill_dumps, load as dill_load

# gevent
from gevent.lock import RLock

# humanize
from humanize import naturalsize

# PyYAML
try:
    from yaml import CDumper  # For pyflakes
    Dumper = CDumper
except ImportError:
    from yaml import Dumper   # ditto
    Dumper = Dumper

# Zato
from zato.common import DONT_DEPLOY_ATTR_NAME, KVDB, SourceCodeInfo, TRACE1
from zato.common.match import Matcher
from zato.common.odb.model.base import Base as ModelBase
from zato.common.util import deployment_info, import_module_from_path, is_func_overridden, is_python_file, visit_py_source
from zato.common.util.json_ import dumps
from zato.server.service import after_handle_hooks, after_job_hooks, before_handle_hooks, before_job_hooks, PubSubHook, Service
from zato.server.service.internal import AdminService

# For pyflakes
Any = Any
List = List

# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)
has_trace1 = logger.isEnabledFor(TRACE1)

# ################################################################################################################################

_unsupported_pickle_protocol_msg = 'unsupported pickle protocol:'

# ################################################################################################################################

hook_methods = ('accept', 'get_request_hash') + before_handle_hooks + after_handle_hooks + before_job_hooks + after_job_hooks

# ################################################################################################################################

@total_ordering
class InRAMService(object):
    __slots__ = 'cluster_id', 'id', 'name', 'impl_name', 'deployment_info', 'service_class', 'is_active', 'is_internal', \
        'slow_threshold', 'source_code_info'

    def __init__(self):
        self.cluster_id = None       # type: int
        self.id = None               # type: int
        self.impl_name = None        # type: text
        self.name = None             # type: text
        self.deployment_info = None  # type: text
        self.service_class = None    # type: object
        self.is_active = None        # type: bool
        self.is_internal = None      # type: bool
        self.slow_threshold = None   # type: int
        self.source_code_info = None # type: SourceCodeInfo

    def __repr__(self):
        return '<{} at {} name:{} impl_name:{}>'.format(self.__class__.__name__, hex(id(self)), self.name, self.impl_name)

    def __eq__(self, other):
        # type: (InRAMService) -> bool
        return self.name == other.name

    def __lt__(self, other):
        # type: (InRAMService) -> bool
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def to_dict(self):
        return {
            'name': self.name,
            'impl_name': self.impl_name,
            'is_active': self.is_active,
            'is_internal': self.is_internal,
            'cluster_id': self.cluster_id
        }

# ################################################################################################################################

class DeploymentInfo(object):
    __slots__ = 'to_process', 'total_services', 'total_size', 'total_size_human'

    def __init__(self):
        self.to_process = []      # type: List
        self.total_size = 0       # type: int
        self.total_size_human = 0 # type: text

# ################################################################################################################################

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

        class_.servers = service_store.server.servers
        class_.odb = service_store.server.worker_store.server.odb
        class_.kvdb = service_store.server.worker_store.kvdb
        class_.pubsub = service_store.server.worker_store.pubsub
        class_.cloud.openstack.swift = service_store.server.worker_store.worker_config.cloud_openstack_swift
        class_.cloud.aws.s3 = service_store.server.worker_store.worker_config.cloud_aws_s3
        class_._out_ftp = service_store.server.worker_store.worker_config.out_ftp
        class_._out_plain_http = service_store.server.worker_store.worker_config.out_plain_http
        class_.amqp.invoke = service_store.server.worker_store.amqp_invoke # .send is for pre-3.0 backward compat
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
        class_.component_enabled_ibm_mq = service_store.server.fs_server_config.component_enabled.ibm_mq
        class_.component_enabled_odoo = service_store.server.fs_server_config.component_enabled.odoo
        class_.component_enabled_stomp = service_store.server.fs_server_config.component_enabled.stomp
        class_.component_enabled_zeromq = service_store.server.fs_server_config.component_enabled.zeromq
        class_.component_enabled_patterns = service_store.server.fs_server_config.component_enabled.patterns
        class_.component_enabled_target_matcher = service_store.server.fs_server_config.component_enabled.target_matcher
        class_.component_enabled_invoke_matcher = service_store.server.fs_server_config.component_enabled.invoke_matcher
        class_.component_enabled_sms = service_store.server.fs_server_config.component_enabled.sms

        # User management and SSO
        if service_store.server.is_sso_enabled:
            class_.sso = service_store.server.sso_api

        # Crypto operations
        class_.crypto = service_store.server.crypto_manager

        # Audit log
        class_.audit_pii = service_store.server.audit_pii

    class_._before_job_hooks = []
    class_._after_job_hooks = []

    # Override hook methods that have not been implemented by user
    for func_name in hook_methods:
        func = getattr(class_, func_name, None)
        if func:
            # Replace with None or use as-is depending on whether the hook was overridden by user.
            impl = func if is_func_overridden(func) else None

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

def get_batch_indexes(services, max_batch_size):
    # type: (List[InRAMService], int) -> List[int, int]

    # If there is only one service to deploy, we can already return the result
    if len(services) == 1:
        return [[0, 1]]

    out = []

    start_idx = 0
    current_batch_size = 0
    batch_size_reached = False

    # We expect for indexes to end at this one
    max_index_possible = len(services)

    # This is needed because current_idx below is not available outside the loop
    max_index_reached = 0

    # We have more than one service, so we need to iterate through them all
    for current_idx, item in enumerate(services, 1): # type: (int, InRAMService)

        current_batch_size += item.source_code_info.len_source

        if current_batch_size >= max_batch_size:
            batch_size_reached = True

        if batch_size_reached:
            out.append([start_idx, current_idx])
            start_idx = current_idx

            max_index_reached = current_idx

            current_batch_size = 0
            batch_size_reached = False

    # It is possible that the for loop above completed before we reached the list's theoretical max index,
    # this is possible if batch_size_reached is not reached in the last iteration, i.e. there was not enough
    # of len_source to fill out the whole batch. At this point, the batch must be smaller that the maximum
    # size allowed so we can just group together anything that is left after the loop.
    if max_index_reached < max_index_possible:
        out.append([max_index_reached, max_index_possible])

    return out

# ################################################################################################################################

class ServiceStore(object):
    """ A store of Zato services.
    """
    def __init__(self, services=None, odb=None, server=None):
        self.services = services          # type: dict
        self.odb = odb                    # type: Any
        self.server = server              # type: Any
        self.max_batch_size = 0           # type: int
        self.id_to_impl_name = {}
        self.impl_name_to_id = {}
        self.name_to_impl_name = {}
        self.update_lock = RLock()
        self.patterns_matcher = Matcher()

# ################################################################################################################################

    def get_service_class_by_id(self, service_id):
        try:
            impl_name = self.id_to_impl_name[service_id]
        except KeyError:
            keys_found = sorted(repr(elem) for elem in self.id_to_impl_name.keys())
            keys_found = [(elem, type(elem)) for elem in keys_found]
            raise KeyError('No such service_id key `{}` `({})` among `{}`'.format(repr(service_id), type(service_id), keys_found))
        else:
            try:
                return self.services[impl_name]
            except KeyError:
                keys_found = sorted(repr(elem) for elem in self.services.keys())
                keys_found = [(elem, type(elem)) for elem in keys_found]
                raise KeyError('No such impl_name key `{}` `({})` among `{}`'.format(
                    repr(impl_name), type(impl_name), keys_found))

# ################################################################################################################################

    def get_service_id_by_name(self, service_name):
        impl_name = self.name_to_impl_name[service_name]
        return self.impl_name_to_id[impl_name]

# ################################################################################################################################

    def get_service_name_by_id(self, service_id):
        return self.get_service_class_by_id(service_id)['name']

# ################################################################################################################################

    def has_service(self, service_name):
        return service_name in self.name_to_impl_name

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

    def new_instance(self, impl_name):
        """ Returns a new instance of a service of the given impl name.
        """
        _info = self.services[impl_name]
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

    def is_deployed(self, name):
        """ Returns True if input service by name is deployed, False otherwise.
        """
        return name in self.name_to_impl_name

# ################################################################################################################################

    def import_internal_services(self, items, base_dir, sync_internal, is_first):
        """ Imports and optionally caches locally internal services.
        """
        cache_file_path = os.path.join(base_dir, 'config', 'repo', 'internal-cache.dat')

        sql_services = {}
        for item in self.odb.get_sql_internal_service_list(self.server.cluster_id):
            sql_services[item.impl_name] = {
                'id': item.id,
                'impl_name': item.impl_name,
                'is_active': item.is_active,
                'slow_threshold': item.slow_threshold,
            }

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

            logger.info('Deploying and caching internal services (%s)', self.server.name)
            info = self.import_services_from_anywhere(items, base_dir)

            for service in info.to_process: # type: InRAMService

                class_ = service.service_class
                impl_name = service.impl_name

                service_info.append({
                    'service_class': class_,
                    'mod': inspect.getmodule(class_),
                    'impl_name': impl_name,
                    'service_id': self.impl_name_to_id[impl_name],
                    'is_active': self.services[impl_name]['is_active'],
                    'slow_threshold': self.services[impl_name]['slow_threshold'],
                    'fs_location': inspect.getfile(class_),
                    'deployment_info': 'zzz'
                })

            # All set, write out the cache file
            f = open(cache_file_path, 'wb')
            f.write(dill_dumps(internal_cache))
            f.close()

            logger.info('Deployed and cached %d internal services (%s) (%s)',
                len(info.to_process), info.total_size_human, self.server.name)

            return info.to_process

        else:
            logger.info('Deploying cached internal services (%s)', self.server.name)

            to_process = []

            try:
                f = open(cache_file_path, 'rb')
                dill_items = dill_load(f)
            except ValueError as e:
                msg = e.args[0]
                if _unsupported_pickle_protocol_msg in msg:
                    msg = msg.replace(_unsupported_pickle_protocol_msg, '').strip()
                    protocol_found = int(msg)

                    # If the protocol found is higher than our own, it means that the cache
                    # was built a Python version higher than our own, we are on Python 2.7
                    # and cache was created under Python 3.4. In such a case, we need to
                    # recreate the cache anew.
                    if protocol_found > highest_pickle_protocol:
                        logger.info('Cache pickle protocol found `%d` > current highest `%d`, forcing sync_internal',
                            protocol_found, highest_pickle_protocol)
                        return self.import_internal_services(items, base_dir, True, is_first)

                    # A different reason, re-raise the erorr then
                    else:
                        raise

                # Must be a different kind of a ValueError, propagate it then
                else:
                    raise
            finally:
                f.close()

            len_si = len(dill_items['service_info'])

            for idx, item in enumerate(dill_items['service_info'], 1):
                class_ = self._visit_class(item['mod'], item['service_class'], item['fs_location'], True)
                to_process.append(class_)

            self._store_in_ram(to_process)

            logger.info('Deployed %d cached internal services (%s)', len_si, self.server.name)

            return to_process

# ################################################################################################################################

    def _store_in_ram(self, to_process):
        # type: (List[DeploymentInfo]) -> None

        # We need to look up all the services in ODB to be able to find their IDs
        services = self.get_basic_data_services()

        with self.update_lock:
            for item in to_process: # type: InRAMService

                service_dict = services[item.name]
                service_id = service_dict['id']

                self.services[item.impl_name] = {}
                self.services[item.impl_name]['name'] = item.name
                self.services[item.impl_name]['deployment_info'] = item.deployment_info
                self.services[item.impl_name]['service_class'] = item.service_class

                self.services[item.impl_name]['is_active'] = item.is_active
                self.services[item.impl_name]['slow_threshold'] = item.slow_threshold

                if 'hook' in item.name:
                    print(111, item.impl_name, item.name, service_id)

                self.id_to_impl_name[service_id] = item.impl_name
                self.impl_name_to_id[item.impl_name] = service_id
                self.name_to_impl_name[item.name] = item.impl_name

                item.service_class.after_add_to_store(logger)

# ################################################################################################################################

    def _store_services_in_odb(self, session, batch_indexes, to_process):
        """ Looks up all Service objects in ODB and if any of our local ones is not in the databaset yet, it is added.
        """
        # Will be set to True if any of the batches added at list one new service to ODB
        any_added = False

        # Get all services already deployed in ODB for comparisons (Service)
        services = self.get_basic_data_services()

        # Add any missing Service objects from each batch delineated by indexes found
        for start_idx, end_idx in batch_indexes:

            to_add = []
            batch_services = to_process[start_idx:end_idx]

            for service in batch_services: # type: InRAMService

                # No such Service object in ODB so we need to store it
                if service.name not in services:
                    to_add.append(service)

            # Add to ODB all the Service objects from this batch found not to be in ODB already
            if to_add:
                self.odb.add_services(session, [elem.to_dict() for elem in to_add])
                any_added = True

        return any_added

# ################################################################################################################################

    def _store_deployed_services_in_odb(self, session, batch_indexes, to_process, _utcnow=datetime.utcnow):
        """ Looks up all Service objects in ODB, checks if any is not deployed locally and deploys it if it is not.
        """
        # Local objects
        now = _utcnow()
        now_iso = now.isoformat()

        # Get all services already deployed in ODB for comparisons (Service) - it is needed to do it again,
        # in addition to _store_deployed_services_in_odb, because that other method may have added
        # DB-level IDs that we need with our own objects.
        services = self.get_basic_data_services()

        # Same goes for deployed services objects (DeployedService)
        deployed_services = self.get_basic_data_deployed_services()

        # Modules visited may return a service that has been already visited via another module,
        # in which case we need to skip such a duplicate service.
        already_visited = set()

        # Add any missing DeployedService objects from each batch delineated by indexes found
        for start_idx, end_idx in batch_indexes:

            to_add = []
            batch_services = to_process[start_idx:end_idx]

            for service in batch_services: # type: InRAMService

                if service.name in already_visited:
                    continue
                else:
                    already_visited.add(service.name)

                # At this point we wil always have IDs for all Service objects
                service_id = services[service.name]['id']

                # Metadata about this deployment as a JSON object
                class_ = service.service_class
                path = service.source_code_info.path
                deployment_details = dumps(deployment_info('service-store', str(class_), now_iso, path))

                # No such Service object in ODB so we need to store it
                if service.name not in deployed_services:
                    to_add.append({
                        'server_id': self.server.id,
                        'service_id': service_id,
                        'deployment_time': now,
                        'details': deployment_details,
                        'source': service.source_code_info.source,
                        'source_path': service.source_code_info.path,
                        'source_hash': service.source_code_info.hash,
                        'source_hash_method': service.source_code_info.hash_method,
                    })

            # If any services are to be deployed, do it now.
            if to_add:
                self.odb.add_deployed_services(session, to_add)

# ################################################################################################################################

    def _store_in_odb(self, to_process):
        # type: (List[DeploymentInfo]) -> None

        # Indicates boundaries of deployment batches
        batch_indexes = get_batch_indexes(to_process, self.max_batch_size)

        with closing(self.odb.session()) as session:

            # Store Service objects first
            needs_commit = self._store_services_in_odb(session, batch_indexes, to_process)

            # This flag will be True if there were any services to be added,
            # in which case we need to commit the sesssion here to make it possible
            # for the next method to have access to these newly added Service objects.
            if needs_commit:
                session.commit()

            # Now DeployedService can be added - they assume that all Service objects all are in ODB already
            self._store_deployed_services_in_odb(session, batch_indexes, to_process)

            # Done with everything, we can commit it now
            session.commit()

# ################################################################################################################################

    def get_basic_data_services(self):
        # type: (None) -> dict

        # We will return service keyed by their names
        out = {}

        # This is a list of services to turn into a dict
        service_list = self.odb.get_basic_data_service_list()

        for service_id, name, impl_name in service_list: # type: name, name
            out[name] = {'id': service_id, 'impl_name': impl_name}

        return out

# ################################################################################################################################

    def get_basic_data_deployed_services(self):
        # type: (None) -> set

        # This is a list of services to turn into a set
        deployed_service_list = self.odb.get_basic_data_deployed_service_list()

        return set(elem[0] for elem in deployed_service_list)

# ################################################################################################################################

    def import_services_from_anywhere(self, items, base_dir, work_dir=None):
        """ Imports services from any of the supported sources, be it module names,
        individual files, directories or distutils2 packages (compressed or not).
        """
        # type: (Any, text, text) -> DeploymentInfo

        items = items if isinstance(items, (list, tuple)) else [items]
        to_process = []

        for item in items:
            if has_debug:
                logger.debug('About to import services from:`%s`', item)

            is_internal = item.startswith('zato')

            # A regular directory
            if os.path.isdir(item):
                to_process.extend(self.import_services_from_directory(item, base_dir))

            # .. a .py/.pyw
            elif is_python_file(item):
                to_process.extend(self.import_services_from_file(item, is_internal, base_dir))

            # .. must be a module object
            else:
                to_process.extend(self.import_services_from_module(item, is_internal))

        total_size = 0

        to_process = set(to_process)
        to_process = list(to_process)

        for item in to_process: # type: InRAMService
            total_size += item.source_code_info.len_source

        info = DeploymentInfo()
        info.to_process[:] = to_process
        info.total_size = total_size
        info.total_size_human = naturalsize(info.total_size)

        # Save data to both ODB and RAM now
        self._store_in_odb(info.to_process)
        self._store_in_ram(info.to_process)

        # Done deploying, we can return
        return info

# ################################################################################################################################

    def import_services_from_file(self, file_name, is_internal, base_dir):
        """ Imports all the services from the path to a file.
        """
        to_process = []

        try:
            mod_info = import_module_from_path(file_name, base_dir)
        except Exception:
            msg = 'Could not load source, file_name:`%s`, e:`%s`'
            logger.error(msg, file_name, format_exc())
        else:
            to_process.extend(self._visit_module(mod_info.module, is_internal, mod_info.file_name))
        finally:
            return to_process

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
        to_process = []

        for py_path in visit_py_source(dir_name):
            to_process.extend(self.import_services_from_file(py_path, False, base_dir))

        return to_process

# ################################################################################################################################

    def import_services_from_module(self, mod_name, is_internal):
        """ Imports all the services from a module specified by the given name.
        """
        try:
            return self.import_services_from_module_object(import_module(mod_name), is_internal)
        except ImportError:
            logger.warn('Could not import module `%s` (internal:%d)', mod_name, is_internal)
            raise

# ################################################################################################################################

    def import_services_from_module_object(self, mod, is_internal):
        """ Imports all the services from a Python module object.
        """
        return self._visit_module(mod, is_internal, inspect.getfile(mod))

# ################################################################################################################################

    def _should_deploy(self, name, item):
        """ Is an object something we can deploy on a server?
        """
        if isclass(item) and hasattr(item, '__mro__') and hasattr(item, 'get_name'):
            if item is not Service and item is not AdminService and item is not PubSubHook:
                if not hasattr(item, DONT_DEPLOY_ATTR_NAME) and not issubclass(item, ModelBase):

                    service_name = item.get_name()

                    # Don't deploy SSO services if SSO as such is not enabled
                    if not self.server.is_sso_enabled:
                        if 'zato.sso' in service_name:
                            return False

                    if self.patterns_matcher.is_allowed(service_name):
                        return True
                    else:
                        logger.info('Skipped disallowed `%s`', service_name)

# ################################################################################################################################

    def _get_source_code_info(self, mod):
        """ Returns the source code of and the FS path to the given module.
        """
        # type: (Any) -> SourceInfo

        source_info = SourceCodeInfo()
        try:
            file_name = mod.__file__
            if file_name[-1] in('c', 'o'):
                file_name = file_name[:-1]

            # We would have used inspect.getsource(mod) had it not been apparently using
            # cached copies of the source code
            source_info.source = open(file_name, 'rb').read()
            source_info.len_source = len(source_info.source)

            source_info.path = inspect.getsourcefile(mod)
            source_info.hash = sha256(source_info.source).hexdigest()
            source_info.hash_method = 'SHA-256'

        except IOError:
            if has_trace1:
                logger.log(TRACE1, 'Ignoring IOError, mod:`%s`, e:`%s`', mod, format_exc())

        return source_info

# ################################################################################################################################

    def _visit_class(self, mod, class_, fs_location, is_internal, _utcnow=datetime.utcnow):
        # type: (Any, Any, text, bool, Any, Any) -> InRAMService

        name = class_.get_name()
        impl_name = class_.get_impl_name()

        set_up_class_attributes(class_, self, name)

        # Note that at this point we do not have the service's ID, is_active and slow_threshold values;
        # this is because this object is created prior to its deployment in ODB.
        service = InRAMService()
        service.cluster_id = self.server.cluster_id
        service.is_active = True
        service.is_internal = is_internal
        service.name = name
        service.impl_name = impl_name
        service.service_class = class_
        service.source_code_info = self._get_source_code_info(mod)

        return service

# ################################################################################################################################

    def on_worker_initialized(self):
        """ Executed after a worker has been fully initialized, e.g. all connectors are started and references to these objects
        can be assigned as class-wide attributes to services.
        """

# ################################################################################################################################

    def _visit_module(self, mod, is_internal, fs_location, needs_odb_deployment=True):
        """ Actually imports services from a module object.
        """
        to_process = []
        try:
            for name in sorted(dir(mod)):
                with self.update_lock:
                    item = getattr(mod, name)

                    if self._should_deploy(name, item):
                        if item.before_add_to_store(logger):
                            to_process.append(self._visit_class(mod, item, fs_location, is_internal))
                        else:
                            logger.info('Skipping `%s` from `%s`', item, fs_location)

        except Exception:
            logger.error(
                'Exception while visiting mod:`%s`, is_internal:`%s`, fs_location:`%s`, e:`%s`',
                mod, is_internal, fs_location, format_exc())
        finally:
            return to_process

# ################################################################################################################################
