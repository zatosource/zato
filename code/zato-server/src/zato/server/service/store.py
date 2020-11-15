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
from datetime import datetime
from functools import total_ordering
from hashlib import sha256
from importlib import import_module
from inspect import getargspec, getmodule, getmro, getsourcefile, isclass
from pickle import HIGHEST_PROTOCOL as highest_pickle_protocol
from random import randint
from shutil import copy as shutil_copy
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
from zato.common.api import CHANNEL, DONT_DEPLOY_ATTR_NAME, KVDB, RATE_LIMIT, SourceCodeInfo, TRACE1
from zato.common.json_internal import dumps
from zato.common.json_schema import get_service_config, ValidationConfig as JSONSchemaValidationConfig, \
     Validator as JSONSchemaValidator
from zato.common.match import Matcher
from zato.common.odb.model.base import Base as ModelBase
from zato.common.util.api import deployment_info, import_module_from_path, is_func_overridden, is_python_file, visit_py_source
from zato.server.config import ConfigDict
from zato.server.service import after_handle_hooks, after_job_hooks, before_handle_hooks, before_job_hooks, PubSubHook, Service, \
     WSXFacade
from zato.server.service.internal import AdminService

# Zato - Cython
from zato.simpleio import CySimpleIO

# Python 2/3 compatibility
from past.builtins import basestring

# ################################################################################################################################

if 0:

    # stdlib
    from inspect import ArgSpec

    # Zato
    from zato.common.odb.api import ODBManager
    from zato.server.base.parallel import ParallelServer

    # For pyflakes
    ArgSpec = ArgSpec
    ConfigDict = ConfigDict
    ODBManager = ODBManager
    ParallelServer = ParallelServer

# ################################################################################################################################

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

class _TestingWorkerStore(object):
    sql_pool_store = None
    outconn_wsx = None
    vault_conn_api = None
    outconn_ldap = None
    outconn_mongodb = None
    def_kafka = None
    zmq_out_api = None
    sms_twilio_api = None
    cassandra_api = None
    cassandra_query_api = None
    email_smtp_api = None
    email_imap_api = None
    search_es_api = None
    search_solr_api = None
    cache_api = None

    def __init__(self):
        self.worker_config = None # type: _TestingWorkerConfig

# ################################################################################################################################

class _TestingWorkerConfig(object):
    out_odoo = None
    out_soap = None
    out_sap = None
    out_sftp = None

# ################################################################################################################################

@total_ordering
class InRAMService(object):
    __slots__ = 'cluster_id', 'id', 'name', 'impl_name', 'deployment_info', 'service_class', 'is_active', 'is_internal', \
        'slow_threshold', 'source_code_info'

    def __init__(self):
        self.cluster_id = None       # type: int
        self.id = None               # type: int
        self.impl_name = None        # type: unicode
        self.name = None             # type: unicode
        self.deployment_info = None  # type: unicode
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
    def __init__(self, services=None, odb=None, server=None, is_testing=False):
        # type: (dict, ODBManager, ParallelServer, bool)
        self.services = services
        self.odb = odb
        self.server = server
        self.is_testing = is_testing
        self.max_batch_size = 0
        self.id_to_impl_name = {}
        self.impl_name_to_id = {}
        self.name_to_impl_name = {}
        self.deployment_info = {}  # impl_name to deployment information
        self.update_lock = RLock()
        self.patterns_matcher = Matcher()
        self.needs_post_deploy_attr = 'needs_post_deploy'

        if self.is_testing:
            self._testing_worker_store =  _TestingWorkerStore()
            self._testing_worker_store.worker_config = _TestingWorkerConfig()

# ################################################################################################################################

    def edit_service_data(self, config):
        # type: (dict)

        # Udpate the ConfigDict object
        config_dict = self.server.config.service[config.name] # type: ConfigDict
        config_dict['config'].update(config)

        # Recreate the rate limiting configuration
        self.set_up_rate_limiting(config.name)

# ################################################################################################################################

    def delete_service_data(self, name):
        # type: (unicode)

        with self.update_lock:
            impl_name = self.name_to_impl_name[name]     # type: unicode
            service_id = self.impl_name_to_id[impl_name] # type: int

            del self.id_to_impl_name[service_id]
            del self.impl_name_to_id[impl_name]
            del self.name_to_impl_name[name]
            del self.services[impl_name]

# ################################################################################################################################

    def post_deploy(self, class_):
        self.set_up_class_json_schema(class_)

# ################################################################################################################################

    def set_up_class_json_schema(self, class_, service_config=None):
        # type: (Service, dict)

        class_name = class_.get_name()

        # We are required to configure JSON Schema for this service
        # but first we need to check if the service is already deployed.
        # If it is not, we need to set a flag indicating that our caller
        # should do it later, once the service has been actually deployed.
        service_info = self.server.config.service.get(class_name)
        if not service_info:
            setattr(class_, self.needs_post_deploy_attr, True)
            return

        service_config = service_config or service_info['config']
        json_schema_config = get_service_config(service_config, self.server)

        # Make sure the schema points to an absolute path and that it exists
        if not os.path.isabs(class_.schema):
            schema_path = os.path.join(self.server.json_schema_dir, class_.schema)
        else:
            schema_path = class_.schema

        if not os.path.exists(schema_path):
            logger.warn('Could not find JSON Schema for `%s` in `%s` (class_.schema=%s)',
                class_name, schema_path, class_.schema)
            return

        config = JSONSchemaValidationConfig()
        config.is_enabled = json_schema_config['is_json_schema_enabled']
        config.object_name = class_name
        config.object_type = CHANNEL.SERVICE
        config.schema_path = schema_path
        config.needs_err_details = json_schema_config['needs_json_schema_err_details']

        validator = JSONSchemaValidator()
        validator.config = config
        validator.init()

        class_._json_schema_validator = validator

# ################################################################################################################################

    def set_up_rate_limiting(self, name, class_=None, _exact=RATE_LIMIT.TYPE.EXACT.id, _service=RATE_LIMIT.OBJECT_TYPE.SERVICE):
        # type: (unicode, Service, unicode, unicode)

        if not class_:
            service_id = self.get_service_id_by_name(name) # type: int
            info = self.get_service_info_by_id(service_id) # type: dict
            class_ = info['service_class'] # type: Service

        # Will set up rate limiting for service if it needs to be done, returning in such a case or False otherwise.
        is_rate_limit_active = self.server.set_up_object_rate_limiting(_service, name, 'service')

        # Set a flag to signal that this service has rate limiting enabled or not
        class_._has_rate_limiting = is_rate_limit_active

# ################################################################################################################################

    def set_up_class_attributes(self, class_, service_store=None, name=None):
        # type: (Service, ServiceStore, unicode)

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
        else:
            CySimpleIO.attach_sio(service_store.server.sio_config, class_)

        # May be None during unit-tests - not every test provides it.
        if service_store:

            # Set up all attributes that do not have to be assigned to each instance separately
            # and can be shared as class attributes.

            class_.servers = service_store.server.servers
            class_.wsx = WSXFacade(service_store.server)

            if self.is_testing:

                class_._worker_store = self._testing_worker_store
                class_._worker_config = self._testing_worker_store.worker_config
                class_.component_enabled_cassandra = True
                class_.component_enabled_email = True
                class_.component_enabled_search = True
                class_.component_enabled_msg_path = True
                class_.component_enabled_ibm_mq = True
                class_.component_enabled_odoo = True
                class_.component_enabled_zeromq = True
                class_.component_enabled_patterns = True
                class_.component_enabled_target_matcher = True
                class_.component_enabled_invoke_matcher = True
                class_.component_enabled_sms = True

            else:

                class_.add_http_method_handlers()
                class_._worker_store = service_store.server.worker_store
                class_._enforce_service_invokes = service_store.server.enforce_service_invokes
                class_.odb = service_store.server.odb
                class_.kvdb = service_store.server.worker_store.kvdb
                class_.pubsub = service_store.server.worker_store.pubsub
                class_.cloud.aws.s3 = service_store.server.worker_store.worker_config.cloud_aws_s3
                class_.cloud.dropbox = service_store.server.worker_store.cloud_dropbox
                class_.cloud.openstack.swift = service_store.server.worker_store.worker_config.cloud_openstack_swift
                class_._out_ftp = service_store.server.worker_store.worker_config.out_ftp
                class_._out_plain_http = service_store.server.worker_store.worker_config.out_plain_http
                class_.amqp.invoke = service_store.server.worker_store.amqp_invoke # .send is for pre-3.0 backward compat
                class_.amqp.invoke_async = class_.amqp.send = service_store.server.worker_store.amqp_invoke_async

                class_.definition.kafka = service_store.server.worker_store.def_kafka
                class_.im.slack = service_store.server.worker_store.outconn_im_slack
                class_.im.telegram = service_store.server.worker_store.outconn_im_telegram

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
                class_.component_enabled_zeromq = service_store.server.fs_server_config.component_enabled.zeromq
                class_.component_enabled_patterns = service_store.server.fs_server_config.component_enabled.patterns
                class_.component_enabled_target_matcher = service_store.server.fs_server_config.component_enabled.target_matcher
                class_.component_enabled_invoke_matcher = service_store.server.fs_server_config.component_enabled.invoke_matcher
                class_.component_enabled_sms = service_store.server.fs_server_config.component_enabled.sms

            # JSON Schema
            if class_.schema:
                self.set_up_class_json_schema(class_)

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

    def has_sio(self, service_name):
        """ Returns True if service indicated by service_name has a SimpleIO definition.
        """
        # type: (str) -> bool

        with self.update_lock:
            service_id = self.get_service_id_by_name(service_name)
            service_info = self.get_service_info_by_id(service_id) # type: Service
            class_ = service_info['service_class'] # type: Service
            return getattr(class_, 'has_sio', False)

# ################################################################################################################################

    def get_service_info_by_id(self, service_id):
        if not isinstance(service_id, int):
            service_id = int(service_id)

        try:
            impl_name = self.id_to_impl_name[service_id]
        except KeyError:
            keys_found = sorted(self.id_to_impl_name)
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
        return self.get_service_info_by_id(service_id)['name']

# ################################################################################################################################

    def get_deployment_info(self, impl_name):
        # type: (unicode) -> dict
        return self.deployment_info[impl_name]

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

    def new_instance(self, impl_name, *args, **kwargs):
        """ Returns a new instance of a service of the given impl name.
        """
        # type: (str, object, object) -> (Service, bool)
        _info = self.services[impl_name]
        return _info['service_class'](*args, **kwargs), _info['is_active']

# ################################################################################################################################

    def new_instance_by_id(self, service_id, *args, **kwargs):
        impl_name = self.id_to_impl_name[service_id]
        return self.new_instance(impl_name)

# ################################################################################################################################

    def new_instance_by_name(self, name, *args, **kwargs):
        impl_name = self.name_to_impl_name[name]
        return self.new_instance(impl_name, *args, **kwargs)

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

        # It is possible that the cache file exists but it is of size zero.
        # This will happen if the process of writing data out to the file
        # was interrupted for any reason the last time the server was starting up.
        # In that case, we need to delete the file altogether and let it recreate.

        if os.path.exists(cache_file_path):
            stat = os.stat(cache_file_path)

            if stat.st_size == 0:
                logger.info('Deleting empty `%s` file', cache_file_path)
                os.remove(cache_file_path)

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
                    'deployment_info': '<todo>'
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

            self._store_in_ram(None, to_process)

            logger.info('Deployed %d cached internal services (%s)', len_si, self.server.name)

            return to_process

# ################################################################################################################################

    def _store_in_ram(self, session, to_process):
        # type: (object, List[InRAMService]) -> None

        if self.is_testing:
            services = {}

            for in_ram_service in to_process: # type: InRAMService
                service_info = {}
                service_info['id'] = randint(0, 1000000)
                services[in_ram_service.name] = service_info

        else:

            # We need to look up all the services in ODB to be able to find their IDs
            if session:
                needs_new_session = False
            else:
                needs_new_session = True
                session = self.odb.session()
            try:
                services = self.get_basic_data_services(session)
            finally:
                if needs_new_session and session:
                    session.close()

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

                self.id_to_impl_name[service_id] = item.impl_name
                self.impl_name_to_id[item.impl_name] = service_id
                self.name_to_impl_name[item.name] = item.impl_name

                arg_spec = getargspec(item.service_class.after_add_to_store) # type: ArgSpec
                args = arg_spec.args # type: list

                # GH #1018 made server the argument that the hook receives ..
                if len(args) == 1 and args[0] == 'server':
                    hook_arg = self.server

                # .. but for backward-compatibility we provide the hook with the logger object by default.
                else:
                    hook_arg = logger

                item.service_class.after_add_to_store(hook_arg)

# ################################################################################################################################

    def _store_services_in_odb(self, session, batch_indexes, to_process):
        """ Looks up all Service objects in ODB and if any of our local ones is not in the databaset yet, it is added.
        """
        # Will be set to True if any of the batches added at list one new service to ODB
        any_added = False

        # Get all services already deployed in ODB for comparisons (Service)
        services = self.get_basic_data_services(session)

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
                elems = [elem.to_dict() for elem in to_add]

                # This saves services in ODB
                self.odb.add_services(session, elems)

                # Now that we have them, we can look up their IDs ..
                service_id_list = self.odb.get_service_id_list(session, self.server.cluster_id,
                    [elem['name'] for elem in elems]) # type: dict

                # .. and add them for later use.
                for item in service_id_list: # type: dict
                    self.impl_name_to_id[item.impl_name] = item.id

                any_added = True

        return any_added

# ################################################################################################################################

    def _should_delete_deployed_service(self, service, already_deployed):
        """ Returns True if a given service has been already deployed but its current source code,
        one that is about to be deployed, is changed in comparison to what is stored in ODB.
        """
        # type: (InRAMService, dict)

        # Already deployed ..
        if service.name in already_deployed:

            # .. thus, return True if current source code is different to what we have already
            if service.source_code_info.source != already_deployed[service.name]:
                return True

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
        services = self.get_basic_data_services(session)

        # Same goes for deployed services objects (DeployedService)
        already_deployed = self.get_basic_data_deployed_services()

        # Modules visited may return a service that has been already visited via another module,
        # in which case we need to skip such a duplicate service.
        already_visited = set()

        # Add any missing DeployedService objects from each batch delineated by indexes found
        for start_idx, end_idx in batch_indexes:

            # Deployed services that need to be deleted before they can be re-added,
            # which will happen if a service's name does not change but its source code does
            to_delete = []

            # DeployedService objects to be added
            to_add = []

            # InRAMService objects to process in this iteration
            batch_services = to_process[start_idx:end_idx]

            for service in batch_services: # type: InRAMService

                # Ignore service we have already processed
                if service.name in already_visited:
                    continue
                else:
                    already_visited.add(service.name)

                # Make sure to re-deploy services that have changed their source code
                if self._should_delete_deployed_service(service, already_deployed):
                    to_delete.append(self.get_service_id_by_name(service.name))
                    del already_deployed[service.name]

                # At this point we wil always have IDs for all Service objects
                service_id = services[service.name]['id']

                # Metadata about this deployment as a JSON object
                class_ = service.service_class
                path = service.source_code_info.path
                deployment_info_dict = deployment_info('service-store', str(class_), now_iso, path)
                self.deployment_info[service.impl_name] = deployment_info_dict
                deployment_details = dumps(deployment_info_dict)

                # No such Service object in ODB so we need to store it
                if service.name not in already_deployed:
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

            # If any services are to be redeployed, delete them first now
            if to_delete:
                self.odb.drop_deployed_services_by_name(session, to_delete)

            # If any services are to be deployed, do it now.
            if to_add:
                self.odb.add_deployed_services(session, to_add)

# ################################################################################################################################

    def _store_in_odb(self, session, to_process):
        # type: (object, List[DeploymentInfo]) -> None

        # Indicates boundaries of deployment batches
        batch_indexes = get_batch_indexes(to_process, self.max_batch_size)

        # Store Service objects first
        needs_commit = self._store_services_in_odb(session, batch_indexes, to_process)

        # This flag will be True if there were any services to be added,
        # in which case we need to commit the sesssion here to make it possible
        # for the next method to have access to these newly added Service objects.
        if needs_commit:
            session.commit()

        # Now DeployedService can be added - they assume that all Service objects all are in ODB already
        self._store_deployed_services_in_odb(session, batch_indexes, to_process)

# ################################################################################################################################

    def get_basic_data_services(self, session):
        # type: (object) -> dict

        # We will return service keyed by their names
        out = {}

        # This is a list of services to turn into a dict
        service_list = self.odb.get_basic_data_service_list(session)

        for service_id, name, impl_name in service_list: # type: name, name
            out[name] = {'id': service_id, 'impl_name': impl_name}

        return out

# ################################################################################################################################

    def get_basic_data_deployed_services(self):
        # type: (None) -> dict

        # This is a list of services to turn into a set
        deployed_service_list = self.odb.get_basic_data_deployed_service_list()

        return dict((elem[0], elem[1]) for elem in deployed_service_list)

# ################################################################################################################################

    def import_services_from_anywhere(self, items, base_dir, work_dir=None, is_internal=None):
        """ Imports services from any of the supported sources.
        """
        # type: (Any, text, text) -> DeploymentInfo

        items = items if isinstance(items, (list, tuple)) else [items]
        to_process = []

        for item in items:
            if has_debug:
                logger.debug('About to import services from:`%s`', item)

            if is_internal is None:
                is_internal = item.startswith('zato')

            if isinstance(item, basestring):

                # A regular directory
                if os.path.isdir(item):
                    to_process.extend(self.import_services_from_directory(item, base_dir))

                # .. a .py/.pyw
                elif is_python_file(item):
                    to_process.extend(self.import_services_from_file(item, is_internal, base_dir))

                # .. a named module
                else:
                    to_process.extend(self.import_services_from_module(item, is_internal))

            # .. must be a module object
            else:
                to_process.extend(self.import_services_from_module_object(item, is_internal))

        total_size = 0

        to_process = set(to_process)
        to_process = list(to_process)

        for item in to_process: # type: InRAMService
            total_size += item.source_code_info.len_source

        info = DeploymentInfo()
        info.to_process[:] = to_process
        info.total_size = total_size
        info.total_size_human = naturalsize(info.total_size)

        if self.is_testing:
            session = None
        else:
            session = self.odb.session()

        try:
            # Save data to both ODB and RAM if we are not testing,
            # otherwise, in RAM only.
            if not self.is_testing:
                self._store_in_odb(session, info.to_process)
            self._store_in_ram(session, info.to_process)

            # Postprocessing, like rate limiting which needs access to information that becomes
            # available only after a service is saved to ODB.
            if not self.is_testing:
                self.after_import(session, info)

        # Done with everything, we can commit it now, assuming we are not in a unittest
        finally:
            if session:
                session.commit()

        # Done deploying, we can return
        return info

# ################################################################################################################################

    def after_import(self, session, info):
        # type: (DeploymentInfo) -> None

        # Names of all services that have been just deployed ..
        deployed_service_name_list = [item.name for item in info.to_process]

        # .. out of which we need to substract the ones that the server is already aware of
        # because they were added to SQL ODB prior to current deployment ..
        for name in deployed_service_name_list[:]:
            if name in self.server.config.service:
                deployed_service_name_list.remove(name)

        # .. and now we know for which services to create ConfigDict objects.

        query = self.odb.get_service_list_with_include(
            session, self.server.cluster_id, deployed_service_name_list, True) # type: list

        service_list = ConfigDict.from_query('service_list_after_import', query, decrypt_func=self.server.decrypt)
        self.server.config.service.update(service_list._impl)

        # Rate limiting
        for item in info.to_process: # type: InRAMService
            self.set_up_rate_limiting(item.name, item.service_class)

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
        """ Imports services from a specified directory.
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

    def _should_deploy(self, name, item, current_module):
        """ Is an object something we can deploy on a server?
        """
        if isclass(item) and hasattr(item, '__mro__') and hasattr(item, 'get_name'):
            if item is not Service and item is not AdminService and item is not PubSubHook:
                if not hasattr(item, DONT_DEPLOY_ATTR_NAME) and not issubclass(item, ModelBase):

                    # Do not deploy services that only happened to have been imported
                    # in this module but are actually defined elsewhere.
                    if getmodule(item) is not current_module:
                        return False

                    service_name = item.get_name()

                    # Don't deploy SSO services if SSO as such is not enabled
                    if not self.server.is_sso_enabled:
                        if 'zato.sso' in service_name:
                            return False

                    # We may be embedded in a test server from zato-testing
                    # in which case we deploy every service found.
                    if self.is_testing:
                        return True
                    else:
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

        self.set_up_class_attributes(class_, self, name)

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

    def redeploy_on_parent_changed(self, changed_service_name, changed_service_impl_name):

        # Local aliases
        to_auto_deploy = []

        # Iterate over all current services to check if any of them subclasses the service just deployed ..
        for impl_name, service_info in self.services.items():

            # .. skip the one just deployed ..
            if impl_name == changed_service_impl_name:
                continue

            # .. a Python class represening each service ..
            service_class = service_info['service_class']
            service_module = getmodule(service_class)

            # .. get all parent classes of that ..
            service_mro = getmro(service_class)

            # .. try to find the deployed service's parents ..
            for base_class in service_mro:
                if issubclass(base_class, Service) and (not base_class is Service):
                    if base_class.get_name() == changed_service_name:

                        # Do not deploy services that are defined in the same module their parent is
                        # because that would be an infinite loop of auto-deployment.
                        if getmodule(base_class) is service_module:
                            continue

                        # .. if it was found, add it to the list of what needs to be auto-redeployed ..
                        to_auto_deploy.append(service_info)

        # We will not always have any services to redeploy
        if to_auto_deploy:

            # Inform users that we are to auto-redeploy services and why we are doing it
            logger.info('Base service `%s` changed; auto-redeploying `%s`', changed_service_name,
                    sorted(item['name'] for item in to_auto_deploy))

            # Go through each child service found and hot-deploy it
            for item in to_auto_deploy:
                module_path = getsourcefile(item['service_class'])
                logger.info('Copying `%s` to `%s`', module_path)

                shutil_copy(module_path, self.server.hot_deploy_config.pickup_dir)

# ################################################################################################################################

    def _visit_module(self, mod, is_internal, fs_location, needs_odb_deployment=True):
        """ Actually imports services from a module object.
        """
        to_process = []
        try:
            for name in sorted(dir(mod)):
                with self.update_lock:
                    item = getattr(mod, name)

                    if self._should_deploy(name, item, mod):
                        if self.is_testing:
                            before_add_to_store_result = True
                        else:
                            before_add_to_store_result = item.before_add_to_store(logger)

                        if before_add_to_store_result:
                            to_process.append(self._visit_class(mod, item, fs_location, is_internal))
                        else:
                            logger.info('Skipping `%s` from `%s`', item, fs_location)

        except Exception:
            logger.error(
                'Exception while visiting module:`%s`, is_internal:`%s`, fs_location:`%s`, e:`%s`',
                mod, is_internal, fs_location, format_exc())
        finally:
            return to_process

# ################################################################################################################################
