# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib
import inspect
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering
from hashlib import sha256
from importlib import import_module
from inspect import getmodule, getmro, getsourcefile, isclass
from pickle import HIGHEST_PROTOCOL as highest_pickle_protocol
from random import randint
from shutil import copy as shutil_copy
from traceback import format_exc
from typing import Any, List

# dill
from dill import load as dill_load

# gevent
from gevent import sleep as gevent_sleep
from gevent.lock import RLock

# humanize
from humanize import naturalsize

# PyYAML
try:
    from yaml import CDumper # For pyflakes
    Dumper = CDumper
except ImportError:
    from yaml import Dumper  # (Ditto)
    Dumper = Dumper

# Zato
from zato.common.api import CHANNEL, DONT_DEPLOY_ATTR_NAME, RATE_LIMIT, SourceCodeInfo, TRACE1
from zato.common.facade import SecurityFacade
from zato.common.json_internal import dumps
from zato.common.json_schema import get_service_config, ValidationConfig as JSONSchemaValidationConfig, \
     Validator as JSONSchemaValidator
from zato.common.match import Matcher
from zato.common.marshal_.api import Model as DataClassModel
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.odb.model.base import Base as ModelBase
from zato.common.typing_ import cast_, list_
from zato.common.util.api import deployment_info, import_module_from_path, is_func_overridden, is_python_file, visit_py_source
from zato.common.util.platform_ import is_non_windows
from zato.common.util.python_ import get_module_name_by_path
from zato.server.config import ConfigDict
from zato.server.service import after_handle_hooks, after_job_hooks, before_handle_hooks, before_job_hooks, \
    PubSubHook, SchedulerFacade, Service, WSXAdapter, WSXFacade
from zato.server.service.internal import AdminService

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.hot_deploy_ import HotDeployProject
    from zato.common.odb.api import ODBManager
    from zato.common.typing_ import any_, anydict, anylist, callable_, dictnone, intstrdict, module_, stranydict, \
        strdictdict, strint, strintdict, strlist, stroriter, tuple_
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from zato.server.config import ConfigStore
    callable_ = callable_
    intstrdict = intstrdict
    strdictdict = strdictdict
    strintdict = strintdict
    stroriter = stroriter
    ConfigStore      = ConfigStore
    HotDeployProject = HotDeployProject
    ODBManager       = ODBManager
    ParallelServer   = ParallelServer
    WorkerStore      = WorkerStore

# ################################################################################################################################
# ################################################################################################################################

# For pyflakes
Any = Any
List = List

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)
has_trace1 = logger.isEnabledFor(TRACE1)
_utcnow=datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

# For backward compatibility we ignore certain modules
internal_to_ignore = []

# STOMP was removed in 3.2
internal_to_ignore.append('stomp')

# ################################################################################################################################
# ################################################################################################################################

_unsupported_pickle_protocol_msg = 'unsupported pickle protocol:'
data_class_model_class_name = 'zato.server.service.Model'

# ################################################################################################################################
# ################################################################################################################################

hook_methods = ('accept', 'get_request_hash') + before_handle_hooks + after_handle_hooks + before_job_hooks + after_job_hooks

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Rate_Limit_Exact   = RATE_LIMIT.TYPE.EXACT.id,
    Rate_Limit_Service = RATE_LIMIT.OBJECT_TYPE.SERVICE

# ################################################################################################################################
# ################################################################################################################################

class _TestingWorkerStore:
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
        self.worker_config = cast_('ConfigStore', None)

# ################################################################################################################################

class _TestingWorkerConfig:
    out_odoo = None
    out_soap = None
    out_sap = None
    out_sftp = None

# ################################################################################################################################

@total_ordering
class InRAMService:

    cluster_id: 'int' = 0
    id: 'int' = 0
    impl_name: 'str' = ''
    name: 'str' = ''
    deployment_info: 'str' = ''
    service_class: 'type[Service]'
    is_active: 'bool' = True
    is_internal: 'bool' = False
    slow_threshold: 'int' = 99999
    source_code_info: 'SourceCodeInfo'

    def __repr__(self) -> 'str':
        return '<{} at {} name:{} impl_name:{}>'.format(self.__class__.__name__, hex(id(self)), self.name, self.impl_name)

    def __eq__(self, other:'InRAMService') -> 'bool':
        return self.name == other.name

    def __lt__(self, other:'InRAMService') -> 'bool':
        return self.name < other.name

    def __hash__(self) -> 'int':
        return hash(self.name)

    def to_dict(self) -> 'stranydict':
        return {
            'name': self.name,
            'impl_name': self.impl_name,
            'is_active': self.is_active,
            'is_internal': self.is_internal,
            'cluster_id': self.cluster_id
        }

inramlist = list_[InRAMService]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ModelInfo:
    name: 'str'
    path: 'str'
    mod_name: 'str'
    source: 'str'

modelinfolist = list_[ModelInfo]

# ################################################################################################################################
# ################################################################################################################################

class DeploymentInfo:
    __slots__ = 'to_process', 'total_services', 'total_size', 'total_size_human'

    def __init__(self):
        self.to_process = []       # type: anylist
        self.total_size = 0        # type: int
        self.total_size_human = '' # type: str

# ################################################################################################################################

def get_service_name(class_obj:'type[Service]') -> 'str':
    """ Return the name of a service which will be either given us explicitly
    via the 'name' attribute or it will be a concatenation of the name of the
    class and its module's name.
    """
    return getattr(class_obj, 'name', '%s.%s' % (class_obj.__module__, class_obj.__name__))

# ################################################################################################################################

def get_batch_indexes(services:'inramlist', max_batch_size:'int') -> 'anylist':

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
    for current_idx, item in enumerate(services, 1):

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

class ServiceStore:
    """ A store of Zato services.
    """
    services: 'stranydict'
    odb: 'ODBManager'
    server: 'ParallelServer'
    is_testing:'bool'

    def __init__(
        self,
        *,
        services,   # type: strdictdict
        odb,        # type: ODBManager
        server,     # type: ParallelServer
        is_testing, # type: bool
    ) -> 'None':
        self.services = services
        self.odb = odb
        self.server = server
        self.is_testing = is_testing
        self.max_batch_size = 0
        self.models = {}            # type: stranydict
        self.id_to_impl_name = {}   # type: intstrdict
        self.impl_name_to_id = {}   # type: strintdict
        self.name_to_impl_name = {} # type: stranydict
        self.deployment_info = {}   # type: stranydict
        self.update_lock = RLock()
        self.patterns_matcher = Matcher()
        self.needs_post_deploy_attr = 'needs_post_deploy'
        self.has_internal_cache = is_non_windows

        if self.has_internal_cache:
            self.action_internal_doing = 'Deploying and caching'
            self.action_internal_done  = 'Deployed and cached'
        else:
            self.action_internal_doing = 'Deploying'
            self.action_internal_done  = 'Deployed'

        if self.is_testing:
            self._testing_worker_store = cast_('WorkerStore', _TestingWorkerStore())
            self._testing_worker_store.worker_config = cast_('ConfigStore', _TestingWorkerConfig())

# ################################################################################################################################

    def is_service_wsx_adapter(self, service_name:'str') -> 'bool':
        try:
            impl_name = self.name_to_impl_name[service_name]
            service_info = self.services[impl_name]
            service_class = service_info['service_class']
            return issubclass(service_class, WSXAdapter)
        except Exception as e:
            logger.warn('Exception in ServiceStore.is_service_wsx_adapter -> %s', e.args)
            return False

# ################################################################################################################################

    def edit_service_data(self, config:'stranydict') -> 'None':

        # Udpate the ConfigDict object
        config_dict = self.server.config.service[config['name']] # type: ConfigDict
        config_dict['config'].update(config)

        # Recreate the rate limiting configuration
        self.set_up_rate_limiting(config['name'])

# ################################################################################################################################

    def _delete_service_from_odb(self, service_id:'int') -> 'None':
        _ = self.server.invoke('zato.service.delete', {
            'id':service_id
        })

# ################################################################################################################################

    def _delete_service_data(self, name:'str', delete_from_odb:'bool'=False) -> 'None':
        try:
            impl_name = self.name_to_impl_name[name]     # type: str
            service_id = self.impl_name_to_id[impl_name] # type: int
            del self.id_to_impl_name[service_id]
            del self.impl_name_to_id[impl_name]
            del self.name_to_impl_name[name]
            del self.services[impl_name]
            if delete_from_odb:
                self._delete_service_from_odb(service_id)
        except KeyError:
            # This is as expected and may happen if a service
            # was already deleted, e.g. it was in the same module
            # that another deleted service was in.
            pass

# ################################################################################################################################

    def delete_service_data(self, name:'str') -> 'None':
        with self.update_lock:
            self._delete_service_data(name)

# ################################################################################################################################

    def _delete_model_data(self, name:'str') -> 'None':
        try:
            del self.models[name]
        except KeyError:
            # Same comment as in self._delete_service_data
            pass

# ################################################################################################################################

    def delete_model_data(self, name:'str') -> 'None':
        with self.update_lock:
            self._delete_service_data(name)

# ################################################################################################################################

    def _collect_objects_by_file_path(self, file_path:'str', container:'stranydict', *, is_dict:'bool') -> 'strlist':

        # Our response to produce
        out = []

        # Go through all the objects in the container ..
        for value in container.values():

            # .. look up the path using keys or attributes, depending on whether it's a dict value or not ..
            if is_dict:
                object_path = value['path']
                object_name = value['name']
            else:
                object_path = value.path
                object_name = value.name

            # .. do we have a match here? ..
            if file_path == object_path:

                # .. if yes, we're going to return that path to our caller ..
                out.append(object_name)

        # .. finally, we are ready to return our output.
        return out

# ################################################################################################################################

    def delete_objects_by_file_path(self, file_path:'str', *, delete_from_odb:'bool') -> 'None':

        with self.update_lock:

            # Collect all services to delete
            services_to_delete = self._collect_objects_by_file_path(file_path, self.services, is_dict=True)

            # Collect all models to delete
            models_to_delete = self._collect_objects_by_file_path(file_path, self.models, is_dict=False)

            # Delete all the services
            for item in services_to_delete:
                self._delete_service_data(item, delete_from_odb)

            # Delete all the models
            for item in models_to_delete:
                self._delete_model_data(item)

# ################################################################################################################################

    def post_deploy(self, class_:'type[Service]') -> 'None':
        self.set_up_class_json_schema(class_)

# ################################################################################################################################

    def set_up_class_json_schema(self, class_:'type[Service]', service_config:'dictnone'=None) -> 'None':

        class_name = class_.get_name()

        # We are required to configure JSON Schema for this service
        # but first we need to check if the service is already deployed.
        # If it is not, we need to set a flag indicating that our caller
        # should do it later, once the service has been actually deployed.
        service_info = self.server.config.service.get(class_name)
        if not service_info:
            setattr(class_, self.needs_post_deploy_attr, True)
            return

        _service_config = service_config or service_info['config'] # type: anydict
        json_schema_config = get_service_config(_service_config, self.server)

        # Make sure the schema points to an absolute path and that it exists
        if not os.path.isabs(class_.schema):
            schema_path = os.path.join(self.server.json_schema_dir, class_.schema)
        else:
            schema_path = class_.schema

        if not os.path.exists(schema_path):
            logger.warning('Could not find JSON Schema for `%s` in `%s` (class_.schema=%s)',
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

    def set_up_rate_limiting(
        self,
        name,       # type: str
        class_=None # type: type[Service] | None
    ) -> 'None':

        if not class_:
            service_id = self.get_service_id_by_name(name) # type: int
            info = self.get_service_info_by_id(service_id) # type: anydict
            _class = info['service_class'] # type: type[Service]
        else:
            _class = class_

        # Will set up rate limiting for service if it needs to be done, returning in such a case or False otherwise.
        is_rate_limit_active = self.server.set_up_object_rate_limiting(ModuleCtx.Rate_Limit_Service, name, 'service')

        # Set a flag to signal that this service has rate limiting enabled or not
        _class._has_rate_limiting = is_rate_limit_active

# ################################################################################################################################

    def _has_io_data_class(
        self,
        class_:'type[Service]',
        msg_class:'any_',
        msg_type:'str'
    ) -> 'bool':

        # Is this a generic alias, e.g. in the form of list_[MyModel]?
        _is_generic = hasattr(msg_class, '__origin__')

        # Do check it now ..
        if _is_generic and msg_class.__origin__ is list:

            # .. it is a list but does it have any inner models? ..
            if msg_class.__args__:

                # .. if we are here, it means that it is a generic class of a list type
                # .. that has a model inside thus we need to check this model in later steps ..
                msg_class = msg_class.__args__[0]

        # Dataclasses require class objects ..
        if isclass(msg_class):

            # .. and it needs to be our own Model subclass ..
            if not issubclass(msg_class,  DataClassModel):
                logger.warning('%s definition %s in service %s will be ignored - \'%s\' should be a subclass of %s',
                msg_type,
                msg_class,
                class_,
                msg_type.lower(),
                data_class_model_class_name)
                return False

            # .. if we are here, it means that this is really a Model-based I/O definition
            else:
                return True

        # It is not a dataclass so we can return False
        else:
            return False

# ################################################################################################################################

    def set_up_class_attributes(self, class_:'type[Service]', service_store:'ServiceStore') -> 'None':

        # Local aliases
        _Class_SimpleIO = None # type: ignore
        _Class_SimpleIO = _Class_SimpleIO # For flake8

        # Set up enforcement of what other services a given service can invoke
        try:
            class_.invokes
        except AttributeError:
            class_.invokes = []

        # If the class does not have a SimpleIO attribute
        # but it does have input or output declared
        # then we add a SimpleIO wrapper ourselves.
        if not hasattr(class_, 'SimpleIO'):

            _direct_sio_input  = getattr(class_, 'input', None)
            _direct_sio_output = getattr(class_, 'output', None)

            if _direct_sio_input or _direct_sio_output:

                # If I/O is declared directly, it means that we do not need response wrappers
                class_._zato_needs_response_wrapper = False # type: ignore

                class _Class_SimpleIO:
                    pass

                if _direct_sio_input:
                    _Class_SimpleIO.input = _direct_sio_input # type: ignore

                if _direct_sio_output:
                    _Class_SimpleIO.output = _direct_sio_output # type: ignore

                class_.SimpleIO = _Class_SimpleIO # type: ignore

        try:
            class_.SimpleIO # type: ignore
            class_.has_sio = True
        except AttributeError:
            class_.has_sio = False

        if class_.has_sio:

            sio_input  = getattr(
                class_.SimpleIO, # type: ignore
                'input',
                 None
                )

            sio_output = getattr(
                class_.SimpleIO, # type: ignore
                'output',
                None
            )

            has_input_data_class  = self._has_io_data_class(class_, sio_input,  'Input')
            has_output_data_class = self._has_io_data_class(class_, sio_output, 'Output')

            # If either input or output is a dataclass but the other one is not,
            # we need to turn the latter into a dataclass as well.

            # We are here if output is a dataclass ..
            if has_output_data_class:

                # .. but input is not and it should be ..
                if (not has_input_data_class) and sio_input:

                    # .. create a name for the dynamically-generated input model class ..
                    name = class_.__module__ + '_' + class_.__name__
                    name = name.replace('.', '_')
                    name += '_AutoInput'

                    # .. generate the input model class now ..
                    model_input = DataClassModel.build_model_from_flat_input(
                        service_store.server,
                        service_store.server.sio_config,
                        CySimpleIO,
                        name,
                        sio_input
                    )

                    # .. and assign it as input.
                    if _Class_SimpleIO:
                        _Class_SimpleIO.input = model_input # type: ignore

            # We are here if input is a dataclass ..
            if has_input_data_class:

                # .. but output is not and it should be.
                if (not has_output_data_class) and sio_output:

                    # .. create a name for the dynamically-generated output model class ..
                    name = class_.__module__ + '_' + class_.__name__
                    name = name.replace('.', '_')
                    name += '_AutoOutput'

                    # .. generate the input model class now ..
                    model_output = DataClassModel.build_model_from_flat_input(
                        service_store.server,
                        service_store.server.sio_config,
                        CySimpleIO,
                        name,
                        sio_output
                    )

                    if _Class_SimpleIO:
                        _Class_SimpleIO.output = model_output # type: ignore

            if has_input_data_class or has_output_data_class:
                SIOClass = DataClassSimpleIO
            else:
                SIOClass = CySimpleIO # type: ignore

            _ = SIOClass.attach_sio(service_store.server, service_store.server.sio_config, class_) # type: ignore

        # May be None during unit-tests - not every test provides it.
        if service_store:

            # Set up all attributes that do not have to be assigned to each instance separately
            # and can be shared as class attributes.
            class_.wsx = WSXFacade(service_store.server)

            if self.is_testing:

                class_._worker_store = self._testing_worker_store
                class_._worker_config = self._testing_worker_store.worker_config
                class_.component_enabled_email = True
                class_.component_enabled_search = True
                class_.component_enabled_msg_path = True
                class_.component_enabled_hl7 = True
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
                class_._enforce_service_invokes = service_store.server.enforce_service_invokes # type: ignore
                class_.odb = service_store.server.odb
                class_.schedule = SchedulerFacade(service_store.server)
                class_.kvdb = service_store.server.worker_store.kvdb # type: ignore
                class_.pubsub = service_store.server.worker_store.pubsub
                class_.cloud.aws.s3 = service_store.server.worker_store.worker_config.cloud_aws_s3
                class_.cloud.confluence = service_store.server.worker_store.cloud_confluence
                class_.cloud.dropbox = service_store.server.worker_store.cloud_dropbox
                class_.cloud.jira = service_store.server.worker_store.cloud_jira
                class_.cloud.salesforce = service_store.server.worker_store.cloud_salesforce
                class_.cloud.ms365 = service_store.server.worker_store.cloud_microsoft_365
                class_._out_ftp = service_store.server.worker_store.worker_config.out_ftp # type: ignore
                class_._out_plain_http = service_store.server.worker_store.worker_config.out_plain_http
                class_.amqp.invoke = service_store.server.worker_store.amqp_invoke # .send is for pre-3.0 backward compat
                class_.amqp.invoke_async = class_.amqp.send = service_store.server.worker_store.amqp_invoke_async
                class_.commands.init(service_store.server)

                class_.definition.kafka = service_store.server.worker_store.def_kafka
                class_.im.slack = service_store.server.worker_store.outconn_im_slack
                class_.im.telegram = service_store.server.worker_store.outconn_im_telegram

                class_._worker_config = service_store.server.worker_store.worker_config
                class_.rules = service_store.server.rules

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

                # New in Zato 3.2, thus optional
                class_.component_enabled_hl7 = service_store.server.fs_server_config.component_enabled.get('hl7')

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

    def has_sio(self, service_name:'str') -> 'bool':
        """ Returns True if service indicated by service_name has a SimpleIO definition.
        """
        with self.update_lock:
            service_id = self.get_service_id_by_name(service_name)
            service_info = self.get_service_info_by_id(service_id) # type: stranydict
            class_ = service_info['service_class'] # type: Service
            return getattr(class_, 'has_sio', False)

# ################################################################################################################################

    def get_service_info_by_id(self, service_id:'strint') -> 'stranydict':
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

    def get_service_id_by_name(self, service_name:'str') -> 'int':
        impl_name = self.name_to_impl_name[service_name]
        return self.impl_name_to_id[impl_name]

# ################################################################################################################################

    def get_service_name_by_id(self, service_id:'int') -> 'str':
        return self.get_service_info_by_id(service_id)['name']

# ################################################################################################################################

    def get_deployment_info(self, impl_name:'str') -> 'anydict':
        return self.deployment_info.get(impl_name) or {}

# ################################################################################################################################

    def has_service(self, service_name:'str') -> 'bool':
        return service_name in self.name_to_impl_name

# ################################################################################################################################

    def _invoke_hook(self, service:'Service', hook_name:'str') -> 'None':
        """ A utility method for invoking various service's hooks.
        """
        try:
            hook = getattr(service, hook_name)
            hook()
        except Exception:
            logger.error('Error while invoking `%s` on service `%s` e:`%s`', hook_name, service, format_exc())

# ################################################################################################################################

    def new_instance(self, impl_name:'str', *args:'any_', **kwargs:'any_') -> 'tuple_[Service, bool]':
        """ Returns a new instance of a service of the given impl name.
        """

        # Extract information about this instance ..
        _info = self.services[impl_name]

        # .. extract details ..
        service_class = _info['service_class']
        is_active = _info['is_active']

        # .. do create a new instance ..
        service:'Service' = service_class(*args, **kwargs)

        # .. populate its basic attributes ..
        service.server = self.server
        service.config = self.server.user_config
        service.user_config = self.server.user_config
        service.time = self.server.time_util
        service.security = SecurityFacade(service.server)

        # .. and return everything to our caller.
        return service, is_active

# ################################################################################################################################

    def new_instance_by_id(self, service_id:'int', *args:'any_', **kwargs:'any_') -> 'tuple_[Service, bool]':
        impl_name = self.id_to_impl_name[service_id]
        return self.new_instance(impl_name)

# ################################################################################################################################

    def new_instance_by_name(self, name:'str', *args:'any_', **kwargs:'any_') -> 'tuple_[Service, bool]':
        try:
            impl_name = self.name_to_impl_name[name]
        except KeyError:
            logger.warning('No such key `{}` among `{}`'.format(name, sorted(self.name_to_impl_name)))
            raise
        else:
            return self.new_instance(impl_name, *args, **kwargs)

# ################################################################################################################################

    def service_data(self, impl_name:'str') -> 'stranydict':
        """ Returns all the service-related data.
        """
        return self.services[impl_name]

# ################################################################################################################################

    def is_deployed(self, name:'str') -> 'bool':
        """ Returns True if input service by name is deployed, False otherwise.
        """
        return name in self.name_to_impl_name

# ################################################################################################################################

    def import_internal_services(
        self,
        items,         # type: stroriter
        base_dir,      # type: str
        sync_internal, # type: bool
        is_first       # type: bool
    ) -> 'anylist':
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
            sql_services[item.impl_name] = { # type: ignore
                'id': item.id,               # type: ignore
                'impl_name': item.impl_name, # type: ignore
                'is_active': item.is_active, # type: ignore
                'slow_threshold': item.slow_threshold, # type: ignore
            }

        # sync_internal may be False but if the cache does not exist (which is the case if a server starts up the first time),
        # we need to create it anyway and sync_internal becomes True then. However, the should be created only by the very first
        # worker in a group of workers - the rest can simply assume that the cache is ready to read.
        # if is_first and not os.path.exists(cache_file_path):
        sync_internal = True

        if sync_internal:

            # Synchronizing internal modules means re-building the internal cache from scratch
            # and re-deploying everything.

            service_info = []
            internal_cache = {
                'service_info': service_info
            }

            # This is currently unused
            internal_cache = internal_cache

            logger.info('{} internal services (%s)'.format(self.action_internal_doing), self.server.name)
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
                    'deployment_info': 'no-deployment-info'
                })

            # All set, write out the cache file, assuming that we can do it.
            # We cannot on Windows or under a debugger (as indicated by the environment variable).
            if self.has_internal_cache:

                if not os.environ.get('ZATO_SERVER_BASE_DIR'):
                    f = open(cache_file_path, 'wb')
                    # f.write(dill_dumps(internal_cache))
                    f.close()

                logger.info('{} %d internal services (%s) (%s)'.format(self.action_internal_done),
                    len(info.to_process), info.total_size_human, self.server.name)

            return info.to_process

        else:
            logger.info('Deploying cached internal services (%s)', self.server.name)
            to_process = []

            # Declare it upfront because we need to assume  that opening the path can fail.
            f = None

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
                if f:
                    f.close()

            len_si = len(dill_items['service_info'])

            for _, item in enumerate(dill_items['service_info'], 1):
                class_ = self._visit_class_for_service(item['mod'], item['service_class'], item['fs_location'], True)
                to_process.append(class_)

            self._store_in_ram(None, to_process)

            logger.info('Deployed %d cached internal services (%s)', len_si, self.server.name)

            return to_process

# ################################################################################################################################

    def _store_in_ram(self, session:'SASession | None', to_process:'inramlist') -> 'None':

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

                item_name = item.name
                item_deployment_info = item.deployment_info
                item_service_class = item.service_class

                self.services[item.impl_name] = {}
                self.services[item.impl_name]['name'] = item_name
                self.services[item.impl_name]['deployment_info'] = item_deployment_info
                self.services[item.impl_name]['service_class'] = item_service_class
                self.services[item.impl_name]['path'] = item.source_code_info.path
                self.services[item.impl_name]['source_code'] = item.source_code_info.source.decode('utf8')

                item_is_active = item.is_active
                item_slow_threshold = item.slow_threshold

                self.services[item.impl_name]['is_active'] = item_is_active
                self.services[item.impl_name]['slow_threshold'] = item_slow_threshold

                self.id_to_impl_name[service_id] = item.impl_name
                self.impl_name_to_id[item.impl_name] = service_id
                self.name_to_impl_name[item.name] = item.impl_name

                hook_arg = self.server
                item.service_class.after_add_to_store(hook_arg)

# ################################################################################################################################

    def _store_services_in_odb(
        self,
        session,       # type: any_
        batch_indexes, # type: anylist
        to_process     # type: anylist
    ) -> 'bool':
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
                    [elem['name'] for elem in elems]) # type: anydict

                # .. and add them for later use.
                for item in service_id_list: # type: dict
                    self.impl_name_to_id[item.impl_name] = item.id

                any_added = True

        return any_added

# ################################################################################################################################

    def _should_delete_deployed_service(self, service:'InRAMService', already_deployed:'stranydict') -> 'bool':
        """ Returns True if a given service has been already deployed but its current source code,
        one that is about to be deployed, is changed in comparison to what is stored in ODB.
        """

        # Already deployed ..
        if service.name in already_deployed:

            # .. thus, return True if current source code is different to what we have already
            if service.source_code_info.source != already_deployed[service.name]:
                return True

        # If we are here, it means that we should not delete this service
        return False

# ################################################################################################################################

    def _store_deployed_services_in_odb(
        self,
        session,       # type: any_
        batch_indexes, # type: anylist
        to_process,    # type: anylist
    ) -> 'None':
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
                deployment_info_dict['line_number'] = service.source_code_info.line_number
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

    def _store_in_odb(self, session:'SASession | None', to_process:'inramlist') -> 'None':

        # Indicates boundaries of deployment batches
        batch_indexes = get_batch_indexes(to_process, self.max_batch_size)

        # Store Service objects first
        needs_commit = self._store_services_in_odb(session, batch_indexes, to_process)

        # This flag will be True if there were any services to be added,
        # in which case we need to commit the sesssion here to make it possible
        # for the next method to have access to these newly added Service objects.
        if needs_commit:
            if session:
                session.commit()

        # Now DeployedService can be added - they assume that all Service objects all are in ODB already
        self._store_deployed_services_in_odb(session, batch_indexes, to_process)

# ################################################################################################################################

    def get_basic_data_services(self, session:'SASession') -> 'anydict':

        # We will return service keyed by their names
        out = {}

        # This is a list of services to turn into a dict
        service_list = self.odb.get_basic_data_service_list(session)

        for service_id, name, impl_name in service_list: # type: name, name
            out[name] = {'id': service_id, 'impl_name': impl_name}

        return out

# ################################################################################################################################

    def get_basic_data_deployed_services(self) -> 'anydict':

        # This is a list of services to turn into a set
        deployed_service_list = self.odb.get_basic_data_deployed_service_list()

        return {elem[0]:elem[1] for elem in deployed_service_list}

# ################################################################################################################################

    def import_services_from_anywhere(
        self,
        items,             # type: stroriter
        base_dir,          # type: str
        is_internal=False, # type: bool
    ) -> 'DeploymentInfo':
        """ Imports services from any of the supported sources.
        """

        items = items if isinstance(items, (list, tuple)) else [items]
        to_process = []
        should_skip = False

        for item in items:

            for ignored_name in internal_to_ignore:
                if ignored_name in item:
                    should_skip = True
                    break
            else:
                should_skip = False

            if should_skip:
                continue

            if has_debug:
                logger.debug('About to import services from:`%s`', item)

            if is_internal is None:
                is_internal = item.startswith('zato')

            if isinstance(item, str):

                # A regular directory
                if os.path.isdir(item):
                    imported = self.import_services_from_directory(item, base_dir)
                    to_process.extend(imported)

                # .. a .py/.pyw
                elif is_python_file(item):
                    imported = self.import_services_from_file(item, is_internal, base_dir)
                    to_process.extend(imported)

                # .. a named module
                else:
                    imported = self.import_services_from_module(item, is_internal)
                    to_process.extend(imported)

            # .. a list of project roots ..
            elif isinstance(item, list):

                # .. go through each project ..
                for elem in item:

                    # .. add type hints ..
                    elem = cast_('HotDeployProject', elem)

                    # .. make the root directory's elements importable by adding the root to $PYTHONPATH ..
                    sys.path.insert(0, str(elem.sys_path_entry))

                    for dir_name in elem.pickup_from_path:

                        # .. turn Path objects into string, which is what is expected by the functions that we call ..
                        dir_name = str(dir_name)

                        # .. services need to be both imported and stored for later use ..
                        imported = self.import_services_from_directory(dir_name, base_dir)
                        to_process.extend(imported)

                        # .. while models we merely import ..
                        _ = self.import_models_from_directory(dir_name, base_dir)

            # .. if we are here, it must be a module object.
            else:
                imported = self.import_services_from_module_object(item, is_internal)
                to_process.extend(imported)

        total_size = 0

        to_process = set(to_process)
        to_process = list(to_process)

        for item in to_process:
            item = cast_('InRAMService', item)
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
                session.commit() # type: ignore

        # Done deploying, we can return
        return info

# ################################################################################################################################

    def after_import(self, session:'SASession | None', info:'DeploymentInfo') -> 'None':

        # Names of all services that have been just deployed ..
        deployed_service_name_list = [item.name for item in info.to_process]

        # .. out of which we need to substract the ones that the server is already aware of
        # because they were added to SQL ODB prior to current deployment ..
        for name in deployed_service_name_list[:]:
            if name in self.server.config.service:
                deployed_service_name_list.remove(name)

        # .. and now we know for which services to create ConfigDict objects.

        query = self.odb.get_service_list_with_include(
            session, self.server.cluster_id, deployed_service_name_list, True) # type: anylist

        service_list = ConfigDict.from_query('service_list_after_import', query, decrypt_func=self.server.decrypt)
        self.server.config.service.update(service_list._impl)

        # Rate limiting
        for item in info.to_process: # type: InRAMService
            self.set_up_rate_limiting(item.name, item.service_class)

# ################################################################################################################################

    def _should_ignore_file(self, file_name:'str', base_dir:'str') -> 'bool':

        if file_name.endswith('store.py') and 'current' in base_dir:
            with open(file_name) as f:
                data = f.read()
                if 'Zato Source' in data:
                    return True
                else:
                    return False
        else:
            return False

# ################################################################################################################################

    def import_objects_from_file(
        self,
        file_name,   # type: str
        is_internal, # type: bool
        base_dir,    # type: str
        visit_func   # type: callable_
    ) -> 'anylist':
        """ Imports all the services or models from the path to a file.
        """

        # Our response to return
        to_process = []

        # Exit early if we are not to process this file
        if self._should_ignore_file(file_name, base_dir):
            return to_process

        try:
            mod_info = import_module_from_path(file_name, base_dir)
        except Exception:
            msg = 'Could not load source, file_name:`%s`, e:`%s`'
            logger.error(msg, file_name, format_exc())
        else:
            to_process.extend(visit_func(mod_info.module, is_internal, mod_info.file_name))
        finally:
            return to_process

# ################################################################################################################################

    def import_models_from_directory(self, dir_name:'str', base_dir:'str') -> 'modelinfolist':
        """ Imports models from a specified directory.
        """
        out:'modelinfolist' = []

        for py_path in visit_py_source(dir_name):
            out.extend(self.import_models_from_file(py_path, False, base_dir))
            gevent_sleep(0.03) # type: ignore

        return out

# ################################################################################################################################

    def import_models_from_file(
        self,
        file_name,   # type: str
        is_internal, # type: bool
        base_dir,    # type: str
    ) -> 'modelinfolist':
        """ Imports all the models from the path to a file.
        """
        # This is a list of all the models imported ..
        model_info_list = self.import_objects_from_file(file_name, is_internal, base_dir, self._visit_module_for_models)

        # .. first, cache the information for later use ..
        for item in model_info_list:
            item = cast_('ModelInfo', item)
            self.models[item.name] = item

        # .. now, return the list to the caller.
        return model_info_list

# ################################################################################################################################

    def import_services_from_file(self, file_name:'str', is_internal:'bool', base_dir:'str') -> 'anylist':
        """ Imports all the services from the path to a file.
        """
        imported = self.import_objects_from_file(file_name, is_internal, base_dir, self._visit_module_for_services)
        return imported

# ################################################################################################################################

    def import_services_from_directory(self, dir_name:'str', base_dir:'str') -> 'anylist':
        """ Imports services from a specified directory.
        """

        # Local variables
        to_process = []
        py_path_list = visit_py_source(dir_name)
        py_path_list = list(py_path_list)

        for py_path in py_path_list:
            imported = self.import_services_from_file(py_path, False, base_dir)
            to_process.extend(imported)
            gevent_sleep(0.03) # type: ignore

        return to_process

# ################################################################################################################################

    def import_services_from_module(self, mod_name:'str', is_internal:'bool') -> 'anylist':
        """ Imports all the services from a module specified by the given name.
        """
        try:
            module_object = import_module(mod_name)
            imported = self.import_services_from_module_object(module_object, is_internal)
            return imported
        except Exception as e:
            logger.info('Could not import module `%s` (internal:%d) -> `%s` -> `%s`',
                mod_name, is_internal, e.args, e)
            return []

# ################################################################################################################################

    def import_services_from_module_object(self, mod:'module_', is_internal:'bool') -> 'anylist':
        """ Imports all the services from a Python module object.
        """
        imported = self._visit_module_for_services(mod, is_internal, inspect.getfile(mod))
        return imported

# ################################################################################################################################

    def _has_module_import(self, source_code:'str', mod_name:'str') -> 'bool':

        # .. ignore modules that do not import what we had on input ..
        for line in source_code.splitlines():

            # .. these two will be True if we are importing this module ..
            has_import   = 'import' in line
            has_mod_name = mod_name in line

            # .. in which case, there is no need to continue ..
            if has_import and has_mod_name:
                break

        # .. otherwise, no, we are not importing this module ..
        else:
            has_import   = False
            has_mod_name = False

        return has_import and has_mod_name

# ################################################################################################################################

    def _get_service_module_imports(self, mod_name:'str') -> 'strlist':
        """ Returns a list of paths pointing to modules with services that import the module given on input.
        """
        # Local aliases
        out = []
        modules_visited = set()

        # Go through all the services that we are aware of ..
        for service_data in self.services.values():

            # .. this is the Python class representing a service ..
            service_class = service_data['service_class']

            # .. get the module of this class based on the module's name ..
            mod = importlib.import_module(service_class.__module__)

            # .. get the source of the module that this class is in, ..
            # .. but not if we have already visited this module before ..
            if mod in modules_visited:
                continue
            else:
                # .. get the actual source code ..
                source_code = service_data['source_code']

                # .. this module can be ignored if it does not import the input one ..
                if not self._has_module_import(source_code, mod_name):
                    continue

                # .. otherwise, extract the path of this module ..
                path = service_data['path']

                # .. store that module's path for later use ..
                out.append(path)

                # .. cache that item so that we do not have to visit it more than once ..
                modules_visited.add(mod)

        # .. now, we can return our result to the caller.
        return out

# ################################################################################################################################

    def _get_model_module_imports(self, mod_name:'str') -> 'strlist':
        """ Returns a list of paths pointing to modules with services that import the module given on input.
        """
        # Local aliases
        out = []
        modules_visited = set()

        # Go through all the models that we are aware of ..
        for model in self.models.values():

            # .. add type hints ..
            model = cast_('ModelInfo', model)

            # .. ignore this module if we have already visited this module before ..
            if model.mod_name in modules_visited:
                continue
            else:
                # .. this module can be ignored if it does not import the input one ..
                if not self._has_module_import(model.source, mod_name):
                    continue

                # .. otherwise, store that module's path for later use ..
                out.append(model.path)

                # .. cache that item so that we do not have to visit it more than once ..
                modules_visited.add(model.mod_name)

        # .. now, we can return our result to the caller.
        return out

# ################################################################################################################################

    def get_module_importers(self, mod_name:'str') -> 'strlist':
        """ Returns a list of paths pointing to modules that import the one given on input.
        """

        # Local aliases
        out = []

        # .. get files with services that import this module ..
        service_path_list = self._get_service_module_imports(mod_name)

        # .. get files with models that import this module ..
        model_path_list = self._get_model_module_imports(mod_name)

        # .. add everything found to the result ..
        out.extend(service_path_list)
        out.extend(model_path_list)

        # .. now, we can return our result to the caller.
        return out

# ################################################################################################################################

    def _should_deploy_model(self, name:'str', item:'any_', current_module:'module_', fs_location:'str') -> 'bool':
        """ Is item a model that we can deploy?
        """
        if isclass(item) and hasattr(item, '__mro__'):
            if issubclass(item, DataClassModel) and (item is not DataClassModel):
                if item.__module__ == current_module.__name__:
                    return True

        # If we are here, it means that we should deploy that item
        return False

# ################################################################################################################################

    def _should_deploy_service(self, name:'str', item:'any_', current_module:'module_', fs_location:'str') -> 'bool':
        """ Is item a service that we can deploy?
        """

        if isclass(item) and hasattr(item, '__mro__') and hasattr(item, 'get_name'):
            if item is not Service and item is not AdminService and item is not PubSubHook:
                if not hasattr(item, DONT_DEPLOY_ATTR_NAME) and not issubclass(item, ModelBase):

                    # Do not deploy services that only happened to have been imported
                    # in this module but are actually defined elsewhere.
                    if getmodule(item) is not current_module:
                        return False

                    # After all the checks, at this point, we know that item must be a service class
                    item = cast_('Service', item)

                    # Make sure the service has its full module's name populated ..
                    item.zato_set_module_name(fs_location)

                    # .. now, we can access its name.
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

        # If we are here, it means that we should deploy that item
        return False

# ################################################################################################################################

    def _get_source_code_info(self, mod:'any_', class_:'any_') -> 'SourceCodeInfo':
        """ Returns the source code of and the FS path to the given module.
        """
        source_info = SourceCodeInfo()
        try:
            file_name = mod.__file__ or ''
            if file_name[-1] in('c', 'o'):
                file_name = file_name[:-1]

            # We would have used inspect.getsource(mod) had it not been apparently using
            # cached copies of the source code
            source_info.source = open(file_name, 'rb').read()
            source_info.len_source = len(source_info.source)

            source_info.path = inspect.getsourcefile(mod) or 'no-source-file'
            source_info.hash = sha256(source_info.source).hexdigest()
            source_info.hash_method = 'SHA-256'

            # The line number this class object is defined on
            source_info.line_number = inspect.findsource(class_)[1]

        except IOError:
            if has_trace1:
                logger.log(TRACE1, 'Ignoring IOError, mod:`%s`, e:`%s`', mod, format_exc())

        return source_info

# ################################################################################################################################

    def _visit_class_for_model(
        self,
        _ignored_mod,         # type: module_
        class_,               # type: any_
        fs_location,          # type: str
        _ignored_is_internal  # type: any_
    ) -> 'ModelInfo':

        # Reusable
        mod_name = get_module_name_by_path(fs_location)

        # Read the source and convert it from bytes to string
        source = open(fs_location, 'rb').read()
        source = source.decode('utf8')

        out = ModelInfo()
        out.name = '{}.{}'.format(mod_name, class_.__name__)
        out.path = fs_location
        out.mod_name = mod_name
        out.source = source

        return out

# ################################################################################################################################

    def _visit_class_for_service(
        self,
        mod,    # type: module_
        class_, # type: type[Service]
        fs_location, # type: str
        is_internal  # type: bool
    ) -> 'InRAMService':

        # Populate the value of the module's name that this class is in
        _ = class_.zato_set_module_name(fs_location)

        name = class_.get_name()
        impl_name = class_.get_impl_name()

        self.set_up_class_attributes(class_, self)

        # Note that at this point we do not have the service's ID, is_active and slow_threshold values;
        # this is because this object is created prior to its deployment in ODB.
        service = InRAMService()
        service.cluster_id = self.server.cluster_id
        service.is_active = True
        service.is_internal = is_internal
        service.name = name
        service.impl_name = impl_name
        service.service_class = class_
        service.source_code_info = self._get_source_code_info(mod, class_)

        return service

# ################################################################################################################################

    def on_worker_initialized(self) -> 'None':
        """ Executed after a worker has been fully initialized, e.g. all connectors are started and references to these objects
        can be assigned as class-wide attributes to services.
        """

# ################################################################################################################################

    def redeploy_on_parent_changed(self, changed_service_name:'str', changed_service_impl_name:'str') -> 'None':

        # Local aliases
        to_auto_deploy = []

        # Iterate over all current services to check if any of these subclasses the service just deployed ..
        for impl_name, service_info in self.services.items():

            # .. skip the one just deployed ..
            if impl_name == changed_service_impl_name:
                continue

            # .. a Python class representing each service ..
            service_class = service_info['service_class']
            service_module = getmodule(service_class)

            # .. get all parent classes of the current one ..
            service_mro = getmro(service_class)

            # .. try to find the deployed service's parents ..
            for base_class in service_mro:
                if issubclass(base_class, Service) and (base_class is not Service):
                    base_class_name = base_class.get_name()
                    if base_class_name == changed_service_name:

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
                module_path = getsourcefile(item['service_class']) or 'no-module-path'
                logger.debug('Copying `%s` to `%s`', module_path, self.server.hot_deploy_config.pickup_dir)

                shutil_copy(module_path, self.server.hot_deploy_config.pickup_dir)

# ################################################################################################################################

    def _visit_module_for_objects(
        self,
        mod,         # type: module_
        is_internal, # type: bool
        fs_location, # type: str
        should_deploy_func, # type: callable_
        visit_class_func,   # type: callable_
        needs_before_add_to_store_result # type: bool
    ) -> 'anylist':
        """ Imports services or models from a module object.
        """
        to_process = []
        try:
            for name in sorted(dir(mod)):
                with self.update_lock:
                    item = getattr(mod, name)

                    if should_deploy_func(name, item, mod, fs_location):

                        # Only services enter here ..
                        if needs_before_add_to_store_result:
                            if self.is_testing:
                                before_add_to_store_result = True
                            else:
                                before_add_to_store_result = item.before_add_to_store(logger)

                        # .. while models go here.
                        else:
                            before_add_to_store_result = True

                        if before_add_to_store_result:
                            to_process.append(visit_class_func(mod, item, fs_location, is_internal))
                        else:
                            logger.info('Skipping `%s` from `%s`', item, fs_location)

        except Exception:
            logger.error(
                'Exception while visiting module:`%s`, is_internal:`%s`, fs_location:`%s`, e:`%s`',
                mod, is_internal, fs_location, format_exc())
        finally:
            return to_process

# ################################################################################################################################

    def _visit_module_for_models(self, mod:'module_', is_internal:'bool', fs_location:'str') -> 'anylist':
        """ Imports models from a module object.
        """
        return self._visit_module_for_objects(mod, is_internal, fs_location,
            self._should_deploy_model, self._visit_class_for_model,
            needs_before_add_to_store_result=False)

# ################################################################################################################################

    def _visit_module_for_services(self, mod:'module_', is_internal:'bool', fs_location:'str') -> 'anylist':
        """ Imports services from a module object.
        """
        return self._visit_module_for_objects(mod, is_internal, fs_location,
            self._should_deploy_service, self._visit_class_for_service,
            needs_before_add_to_store_result=True)

# ################################################################################################################################
