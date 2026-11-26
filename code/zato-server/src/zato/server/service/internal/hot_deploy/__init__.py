# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fcntl
import os
import shutil
from base64 import b64decode
from dataclasses import dataclass
from errno import ENOENT
from tempfile import mkdtemp
from time import sleep
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.typing_ import cast_
from zato.common.broker_message import HOT_DEPLOY
from zato.common.exception import BadRequest
from zato.common.util.api import import_module_from_path, is_python_file, is_archive_file
from zato.common.util.file_system import fs_safe_now, get_file_digest
from zato.common.util.import_graph import ImportGraph
from zato.common.util.open_ import open_r, open_w
from zato.common.util.python_ import import_module_by_path
from zato.server.generic.api.outconn_sdk import extract_connector_classes, register_connector_type
from zato.server.service import AsIs
from zato.server.service.internal import AdminService

# ################################################################################################################################

if 0:
    from types import ModuleType
    from zato.common.typing_ import any_, anylist, anylistnone, commoniter, intlist, stranydict, strbytes, strlist, strset
    from zato.server.service.store import InRAMService
    strbytes = strbytes
    InRAMService = InRAMService

# ################################################################################################################################

MAX_BACKUPS = 1000
_first_prefix = '0' * (len(str(MAX_BACKUPS)) - 1) # So it runs from, e.g.,  000 to 999

# The file next to the backup directory whose lock the processes of a server hold in turn while each makes its backup,
# because each process deletes the archives that it found in the directory before it made its own.
_backup_lock_suffix = '.lock'

# How long a process waits, in seconds, before it tries again to take the lock of the backup directory.
_backup_lock_interval = 0.05

# The directory of the work directory to which the modules of an archive are extracted, followed by the name of the archive,
# and the temporary directory that each process extracts the archive to first.
_archive_dir_prefix = 'archive-'
_archive_staging_prefix = 'archive-staging-'

# What an IDE plugin's connection test receives in reply.
_msg_server_reached = 'OK, server reached'

# What an IDE plugin receives once its file is in the pickup directory.
_msg_deployed = 'OK, deployed to server'

# Files with certificates, keys and CA certificates that outgoing connections read.
_tls_material_suffix = '.pem'

# The configuration keys of an outgoing connection that name such files.
_tls_material_keys = ('tls_client_cert', 'tls_client_key', 'ca_certs_path')

# The transports of the outgoing connections that read such files.
_tls_material_transports = ('plain_http', 'soap')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeploymentCtx:
    connector_type_list: 'strlist'
    model_name_list:     'strlist'
    service_id_list:     'intlist'
    service_name_list:   'strlist'

# ################################################################################################################################
# ################################################################################################################################

class ModuleImportError(BadRequest):
    """ Raised when a module that is being deployed cannot be imported, in which case nothing from it is deployed.
    """
    def __init__(self, cid:'str', file_name:'str', reason:'str', details:'str') -> 'None':
        super().__init__(cid, f'Could not import module `{file_name}` -> {reason}', True)
        self.details = details

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates all the filesystem directories and files out of a deployment package stored in the ODB.
    """
    changes_config = True
    input = '-payload', '-payload_name', '-is_startup', '-is_relayed', '-is_importer'
    output = AsIs('-services_deployed'), '-zato_ide_deploy_create_response'

# ################################################################################################################################

    def is_config_change(self) -> 'bool':

        # The raw request of a REST channel is the body as it was received, while the payload is parsed on every channel
        payload = self.request.payload

        # A request with nothing to deploy is a connection test from an IDE plugin, which changes no configuration ..
        if 'payload_name' in payload:
            payload_name = payload['payload_name']
        else:
            payload_name = ''

        if not payload_name:
            return False

        # .. and a relayed deployment puts in effect in this process a file that the config process deployed already.
        if 'is_relayed' in payload:
            is_relayed = payload['is_relayed']
        else:
            is_relayed = False

        out = not is_relayed
        return out

# ################################################################################################################################

    def _delete(self, items:'commoniter') -> 'None':
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
            else:
                msg = 'Could not delete `%s`, it is neither file nor a directory, stat:`%s`'
                self.logger.warning(msg, item, os.stat(item))

# ################################################################################################################################

    def _backup_last(self, fs_now:'str', current_work_dir:'str', backup_format:'str', last_backup_work_dir:'str') -> 'None':

        # We want to grab the directory's contents right now, before we place the
        # new backup in there
        last_backup_contents = []
        for item in os.listdir(last_backup_work_dir):
            last_backup_contents.append(os.path.join(last_backup_work_dir, item))

        # First make the backup to the special 'last' directory
        last_backup_path = os.path.join(last_backup_work_dir, fs_now)

        _ = shutil.make_archive(last_backup_path, backup_format, current_work_dir, verbose=True, logger=None)

        # Delete everything previously found in the last backup directory
        self._delete(last_backup_contents)

# ################################################################################################################################

    def _backup_linear_log(
        self,
        fs_now,           # type: str
        current_work_dir, # type: str
        backup_format,    # type: str
        backup_work_dir,  # type: str
        backup_history,   # type: int
    ) -> 'None':

        delete_previous_backups = False

        # Aren't we going to exceed the limit?
        max_backups = min(backup_history, MAX_BACKUPS)
        backup_contents = []

        for item in os.listdir(backup_work_dir):
            item = os.path.join(backup_work_dir, item)

            # We tally files only and assume each file must be one of ours so we can safely drop it if need be
            if os.path.isfile(item):
                backup_contents.append(item)

        len_backups = len(backup_contents)

        # It's the first backup or we're past the limit so we need a fresh prefix
        if not len_backups or len_backups >= max_backups:
            next_prefix = _first_prefix
        else:
            next_prefix = str(len_backups).zfill(len(_first_prefix))

        # Also, we need to delete previous backups if we're starting anew
        if len_backups >= max_backups:
            delete_previous_backups = True

        backup_name = '{}-{}'.format(next_prefix, fs_now)
        backup_path = os.path.join(backup_work_dir, backup_name)
        _ = shutil.make_archive(backup_path, backup_format, current_work_dir, verbose=True, logger=None)

        if delete_previous_backups:
            self._delete(backup_contents)

# ################################################################################################################################

    def backup_current_work_dir(self):

        # Save a few keystrokes
        last_backup_work_dir = self.server.hot_deploy_config.last_backup_work_dir
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        backup_work_dir = self.server.hot_deploy_config.backup_work_dir
        backup_history = self.server.hot_deploy_config.backup_history
        backup_format = self.server.hot_deploy_config.backup_format

        lock_path = f'{backup_work_dir}{_backup_lock_suffix}'

        with open(lock_path, 'a') as lock_file:

            # Only one process of the server makes its backup at a time ..
            self._lock_backup(lock_file)

            # .. the name is taken under the lock, so the archives of the processes keep their order ..
            fs_now = fs_safe_now()

            # .. store the last backup ..
            self._backup_last(fs_now, current_work_dir, backup_format, last_backup_work_dir)

            # .. and store the same thing in the linear log of backups.
            self._backup_linear_log(fs_now, current_work_dir, backup_format, backup_work_dir, backup_history)

# ################################################################################################################################

    def _lock_backup(self, lock_file:'any_') -> 'None':
        """ Waits until this process holds the lock of the backup directory, which the closing of the file releases.
        """
        while True:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                sleep(_backup_lock_interval)
            else:
                return

# ################################################################################################################################

    def _get_import_roots(self) -> 'strlist':
        """ Returns the directories whose Python files may import one another, the ones in sys.path first.
        """
        out:'strlist' = []
        plain_directories:'strlist' = []

        # A project contributes the directory that it adds to sys.path, while a plain directory contributes itself ..
        for source in self.server.service_sources:
            if isinstance(source, list):
                for project in source:
                    sys_path_entry = str(project.sys_path_entry)
                    out.append(sys_path_entry)
            else:
                plain_directories.append(source)

        # .. and so does the directory that files uploaded from an IDE are written to.
        out.extend(plain_directories)
        out.append(self.server.hot_deploy_config.pickup_dir)

        return out

# ################################################################################################################################

    def _redeploy_module_dependencies(self, file_name:'str') -> 'None':

        # The import graph of every hot-deployment root of this server ..
        roots = self._get_import_roots()
        graph = ImportGraph.build(roots)

        # .. the module deployed is put in effect under each of its names ..
        names = graph.get_module_names(file_name)
        _ = import_module_by_path(file_name, names)

        # .. every module that imports it, directly or through other modules, follows the modules that it imports ..
        importer_list = graph.get_ordered_importers(file_name)
        service_store = self.server.service_store

        for importer in importer_list:

            # .. a file with services or models is deployed again in this process, because every other process
            # deploys the module from the event of its own deployment and then takes care of the importers in turn.
            # The server invokes the deployment, because a service may not invoke itself ..
            if service_store.has_objects_from_path(importer):
                _ = self.server.invoke('zato.hot-deploy.create', {
                    'payload_name': importer,
                    'payload': '',
                    'is_relayed': True,
                    'is_importer': True,
                })

            # .. and each one is put in effect under each of its names, so that the next ones import it as it is now.
            importer_names = graph.get_module_names(importer)
            _ = import_module_by_path(importer, importer_names)

        if importer_list:
            importer_count = len(importer_list)
            suffix = 'module' if importer_count == 1 else 'modules'
            self.logger.info('Reloaded %d %s importing `%s` -> %s', importer_count, suffix, file_name, importer_list)

# ################################################################################################################################

    def _deploy_models(self, current_work_dir:'str', model_file_name:'str') -> 'strset':

        # This returns details of all the model classes deployed from the file
        model_info_list = self.server.service_store.import_models_from_file(
            model_file_name,
            False,
            current_work_dir,
        )

        # .. extract unique names only ..
        model_name_list = {item.name for item in model_info_list}

        # .. and return to the caller the list of models deployed.
        return model_name_list

# ################################################################################################################################

    def _import_module(self, current_work_dir:'str', file_name:'str') -> 'ModuleType':
        """ Imports a module that is being deployed, or raises an exception that names the file and the reason.
        """
        try:
            mod_info = import_module_from_path(file_name, current_work_dir)
        except Exception as e:
            reason = f'{e.__class__.__name__}: {e}'
            raise ModuleImportError(self.cid, file_name, reason, format_exc()) from None

        out = mod_info.module
        return out

# ################################################################################################################################

    def _deploy_sdk_connectors(self, module:'ModuleType') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Collect all the connector classes defined in the module ..
        connector_classes = extract_connector_classes(module)

        # .. and register each one with the config manager.
        for connector_class in connector_classes:
            type_ = register_connector_type(self.server.config_manager, connector_class)
            out.append(type_)

        return out

# ################################################################################################################################

    def _deploy_services(self, current_work_dir:'str', service_file_name:'str') -> 'intlist':

        # Local aliases
        service_id_list:'intlist' = []

        # This returns details of all the model classes deployed from the file
        service_info_list = self.server.service_store.import_services_from_anywhere(service_file_name, current_work_dir)

        # .. if we have deployed any models ..
        for service in service_info_list.to_process: # type: ignore

            # .. add type hints ..
            service = cast_('InRAMService', service)

            # .. extract the ID of the deployed service ..
            service_id = self.server.service_store.impl_name_to_id[service.impl_name]

            # .. append it for later use.
            service_id_list.append(service_id)

        # .. and return to the caller the list of IDs of all the services deployed.
        return service_id_list

# ################################################################################################################################

    def _deploy_file(
        self,
        current_work_dir, # type: str
        payload,          # type: any_
        file_name,        # type: str
        should_deploy_in_place, # type: bool
        is_importer,      # type: bool
    ) -> 'DeploymentCtx':

        if not should_deploy_in_place:
            with open(file_name, 'wb') as f:
                _ = f.write(payload)

        # A file that the service store ignores is not imported, so it has no connectors either ..
        if self.server.service_store._should_ignore_file(file_name, current_work_dir):
            connector_type_list:'strlist' = []

        # .. whereas any other one is imported before anything is deployed from it, so that a module
        # that cannot be imported is refused as a whole.
        else:
            module = self._import_module(current_work_dir, file_name)
            connector_type_list = self._deploy_sdk_connectors(module)

        model_name_list = self._deploy_models(current_work_dir, file_name)
        service_id_list = self._deploy_services(current_work_dir, file_name)

        # A Python file is imported by other modules whether or not it defines services or models,
        # and each of them is redeployed after it, so that they use its current version,
        # unless the file is itself an importer, which the deployment of the module it imports takes care of.
        if is_python_file(file_name):
            if not is_importer:
                self._redeploy_module_dependencies(file_name)

        ctx = DeploymentCtx()
        ctx.connector_type_list = connector_type_list
        ctx.model_name_list = model_name_list # type: ignore
        ctx.service_id_list = service_id_list
        ctx.service_name_list = [self.server.service_store.get_service_name_by_id(elem) for elem in service_id_list]

        return ctx

# ################################################################################################################################

    def _deploy_package(
        self,
        payload,      # type: str
        payload_name, # type: str
        is_importer,  # type: bool
    ) -> 'anylistnone':
        """ Deploy a package, either a plain Python file or an archive, and update
        the deployment status.
        """

        should_deploy_in_place = True

        # Local objects
        if should_deploy_in_place:
            work_dir = os.path.dirname(payload_name)
        else:
            work_dir:'str' = self.server.hot_deploy_config.current_work_dir

        file_name = os.path.join(work_dir, payload_name)

        # Deploy some objects of interest from the file ..
        ctx = self._deploy_file(work_dir, payload, file_name, should_deploy_in_place, is_importer)

        # We enter here if there were some connectors, models or services that we deployed ..
        if ctx.connector_type_list or ctx.model_name_list or ctx.service_name_list:

            # .. report any connector types found ..
            if ctx.connector_type_list:
                self._report_deployment(file_name, ctx.connector_type_list, 'connector type')

            # .. report any models found ..
            if ctx.model_name_list:
                self._report_deployment(file_name, ctx.model_name_list, 'model')

            # .. report any services found ..
            if ctx.service_name_list:
                self._report_deployment(file_name, ctx.service_name_list, 'service')

            # .. our callers only need services ..
            return ctx.service_id_list

        # .. we could not find anything to deploy in the file.
        else:
            # Log only if payload does not point to our own store.py module.
            if payload_name != 'store.py':
                msg = 'No services, models nor connector types were deployed from module `%s`'
                self.logger.info(msg, payload_name)

# ################################################################################################################################

    def _report_deployment(self, file_name:'str', items:'anylist', noun:'str') -> 'None':
        msg = 'Deployed %s {}%sfrom `%s` -> %s'.format(noun)
        len_items = len(items)
        suffix = 's ' if len_items > 1 else ' '
        self.logger.info(msg, len_items, suffix, file_name, sorted(items))

# ################################################################################################################################

    def _deploy_user_conf(self, payload:'str', payload_name:'str') -> 'None':

        # A relayed deployment carries the path of the file only
        if payload:
            data = b64decode(payload).decode('utf8')
        else:
            with open_r(payload_name) as f:
                data = f.read()

        file_name = os.path.basename(payload_name)

        self.invoke('zato.pickup.on-update-user-conf', {
            'data': data,
            'file_name': file_name,
            'full_path': payload_name,
            'relative_dir': '',
        })

# ################################################################################################################################

    def _deploy_enmasse(self, payload_name:'str') -> 'None':
        self.invoke('zato.pickup.update-enmasse', {'full_path': payload_name})

# ################################################################################################################################

    def _rebuild_mcp_tool_registries(self, service_id_list:'intlist') -> 'None':
        """ Rebuilds the tool registry of every MCP gateway whose allow list contains
        any of the services just deployed, so the next tools/list already advertises
        the schemas the redeployed code declares.
        """

        service_store = self.server.service_store
        deployed_names = set()

        for service_id in service_id_list:
            service_name = service_store.get_service_name_by_id(service_id)
            deployed_names.add(service_name)

        for gateway_config in self.server.config_manager.gateway_mcp.values():

            wrapper = gateway_config.conn
            allowed_names = set(wrapper.config.get('services', []))

            if not (allowed_names & deployed_names):
                continue

            # One gateway whose allow list references a since-removed service must not
            # break the deployment of the others, so each rebuild fails on its own.
            try:

                # A gateway whose earlier build left no handler is built in full now that the service exists ..
                if wrapper.handler is None:
                    wrapper.build_wrapper()

                # .. while one that was built has only its tools listed anew.
                else:
                    wrapper.handler.tool_registry.rebuild()

            except Exception:
                self.logger.warning('Could not rebuild the MCP tool registry of `%s`:\n%s',
                    gateway_config.name, format_exc())

# ################################################################################################################################

    def _uses_tls_material(self, config:'stranydict', path:'str') -> 'bool':
        """ Returns True if an outgoing connection's configuration names the given file
        as its client certificate, its key or its CA certificates.
        """
        for key in _tls_material_keys:

            # Not every connection names every file, and only those with an mTLS definition have CA certificates.
            if value := config.get(key):
                value = os.path.normpath(value)
                if value == path:
                    out = True
                    break
        else:
            out = False

        return out

# ################################################################################################################################

    def _reload_tls_material(self, path:'str') -> 'None':
        """ Makes every outgoing REST and SOAP connection that reads the given file discard its pooled
        TLS connections, so that its next request reads the file anew.
        """
        config_manager = self.server.config_manager
        config_store = config_manager.config_store

        # The names of the connections that read the file
        reloaded:'strlist' = []

        with config_manager.update_lock:

            # Go through each outgoing connection ..
            for transport in _tls_material_transports:
                config_dict = getattr(config_store, 'out_' + transport)

                for conn_name in config_dict.copy_keys():
                    wrapper = config_dict[conn_name]['conn']

                    # .. and refresh each that reads the file.
                    if self._uses_tls_material(wrapper.config, path):
                        wrapper.reload_tls_material()
                        reloaded.append(conn_name)
                        self.logger.info('Reloaded TLS material of outgoing connection `%s` (%s) -> `%s`',
                            conn_name, transport, path)

        if not reloaded:
            self.logger.info('No outgoing connection reads TLS material from `%s`', path)

# ################################################################################################################################

    def _relay_deployment(self, payload_name:'str') -> 'None':
        """ Sends the path of a deployed file to the other processes of the server, each of which deploys it from that path.
        """
        msg = {'action': HOT_DEPLOY.CREATE_SERVICE.value, 'payload_name': payload_name, 'payload': ''}
        self.config_dispatcher.relay_only(msg)

# ################################################################################################################################

    def _is_enmasse_file(self, payload_name:'str') -> 'bool':
        return 'enmasse' in payload_name and (payload_name.endswith('.yml') or payload_name.endswith('.yaml'))

# ################################################################################################################################

    def _deploy_archive(self, payload_name:'str') -> 'intlist':
        """ Extracts an archive to a directory of its own in the work directory and deploys each Python module in it.
        """
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        archive_name = os.path.basename(payload_name)

        # The staging directory is outside the work directory, which the backups of other processes archive,
        # and on the same file system, so that a module is moved into place in one step.
        target_dir = os.path.join(current_work_dir, f'{_archive_dir_prefix}{archive_name}')
        staging_dir = mkdtemp(prefix=_archive_staging_prefix, dir=os.path.dirname(current_work_dir))

        # Each process of the server extracts the archive on its own ..
        try:
            shutil.unpack_archive(payload_name, staging_dir)

            module_paths:'strlist' = []

            for staging_root, _, file_names in os.walk(staging_dir):
                for file_name in file_names:
                    if is_python_file(file_name):

                        staging_path = os.path.join(staging_root, file_name)
                        relative_path = os.path.relpath(staging_path, staging_dir)
                        module_path = os.path.join(target_dir, relative_path)

                        os.makedirs(os.path.dirname(module_path), exist_ok=True)
                        os.replace(staging_path, module_path)

                        module_paths.append(module_path)
        finally:
            shutil.rmtree(staging_dir)

        # .. and each module is deployed from where it now is.
        out:'intlist' = []

        for module_path in sorted(module_paths):
            service_id_list = self._deploy_package('', module_path, False)

            if service_id_list:
                out.extend(service_id_list)

        return out

# ################################################################################################################################

    def deploy_package(self, payload:'str', payload_name:'str', is_importer:'bool') -> 'any_':

        if is_archive_file(payload_name):
            return self._deploy_archive(payload_name)

        elif is_python_file(payload_name):
            return self._deploy_package(payload, payload_name, is_importer)

        elif self._is_enmasse_file(payload_name):
            self._deploy_enmasse(payload_name)

        elif payload_name.endswith('.ini') or payload_name.endswith('.zrules'):
            self._deploy_user_conf(payload, payload_name)

        else:
            self.logger.warning('Ignoring package id:`%s`, payload_name:`%s`, not a Python file nor an archive', payload_name)

# ################################################################################################################################

    def handle(self):

        payload = self.request.input.payload
        payload_name = self.request.input.payload_name

        # A deployment that another process relayed is deployed in this process only
        is_relayed = self.request.input.is_relayed

        # A file deployed again because it imports a module that was just deployed
        is_importer = self.request.input.is_importer

        # A request with nothing to deploy is a connection test from an IDE plugin,
        # so we confirm that we are reachable and return early.
        if not payload_name:
            self.response.payload.zato_ide_deploy_create_response = Bunch()
            self.response.payload.zato_ide_deploy_create_response.success = True
            self.response.payload.zato_ide_deploy_create_response.msg = _msg_server_reached
            return

        # If it's just a file name, it means it must've been uploaded via the plugin,
        # so we save it in our local deployment directory and then deploy it from there below,
        # the same way a file found in that directory on startup is deployed.
        # But we need to do it only for files that are not internal ones.

        internal_path = os.path.join('server', 'service', 'internal')
        payload_name = os.path.normpath(payload_name)

        # TLS material is never deployed - the outgoing connections that read it are refreshed instead.
        if payload_name.endswith(_tls_material_suffix):
            self._reload_tls_material(payload_name)

            if not is_relayed:
                self._relay_deployment(payload_name)

            return

        is_external = internal_path not in payload_name
        is_relative = not os.path.isabs(payload_name)
        is_ide_upload = is_external and is_relative

        if is_ide_upload:

            full_path = os.path.join(self.server.hot_deploy_config.pickup_dir, payload_name)
            full_path = os.path.abspath(full_path)

            payload = b64decode(payload)
            payload = payload.decode('utf8')

            with open_w(full_path) as f:
                _ = f.write(payload)

            # From now on the file is deployed from where it was just written to
            payload_name = full_path

        server_token = self.server.fs_server_config.main.token
        lock_name = '{}{}:{}'.format('uploading', server_token, payload_name)

        ttl = self.server.deployment_lock_expires
        block = self.server.deployment_lock_timeout

        # The config_dispatcher does not exist yet if services are deployed during the server's startup,
        # in which case the deployment waits until the server is fully initialized.
        while not self.server.config_dispatcher:
            sleep(0.2)

        with self.lock(lock_name, ttl, block):

            try:
                self.backup_current_work_dir()

                # The digest is read before the deployment, so a file that changes during it differs from the digest
                # and the next deployment of the pickup directory deploys it again ..
                file_digest = get_file_digest(payload_name)

                try:
                    services_deployed = self.deploy_package(payload, payload_name, is_importer) or []

                except ModuleImportError as e:

                    # A module that cannot be imported is passed over by the deployments of the pickup directory
                    # until its contents change ..
                    self.server.deployed_file_digests[payload_name] = file_digest

                    # .. and the refusal is logged by the process that the file was deployed to,
                    # while a relayed deployment leaves it to its caller.
                    if not is_relayed:
                        self.logger.error('%s\n%s', e.msg, e.details)

                    raise

                # .. which otherwise passes over the file, as this process has it in effect already.
                self.server.deployed_file_digests[payload_name] = file_digest

                # Go through all services deployed, check if any needs post-processing
                # and if does, call the relevant function and clear the flag.
                service_store = self.server.service_store
                needs_post_deploy_attr = service_store.needs_post_deploy_attr

                for service_id in services_deployed:

                    service_info = service_store.get_service_info_by_id(service_id)
                    class_ = service_info['service_class']

                    if getattr(class_, needs_post_deploy_attr, None):
                        service_store.post_deploy(class_)
                        delattr(class_, needs_post_deploy_attr)

                # A redeployed service may have a new I/O declaration, so the MCP gateways
                # that expose it rebuild their tool registries with the fresh schemas.
                self._rebuild_mcp_tool_registries(services_deployed)

                self.response.payload.services_deployed = services_deployed

                # One enmasse import writes the ODB for every process and the reload that follows it brings the result
                # to each of them, while every other file is deployed by each process from its path.
                if not is_relayed and not self._is_enmasse_file(payload_name):
                    self._relay_deployment(payload_name)

                # An IDE plugin reads a confirmation rather than the list of what was deployed
                if is_ide_upload:
                    self.response.payload.zato_ide_deploy_create_response = Bunch()
                    self.response.payload.zato_ide_deploy_create_response.success = True
                    self.response.payload.zato_ide_deploy_create_response.msg = _msg_deployed

            except OSError as e:
                if e.errno == ENOENT:
                    self.logger.debug('Caught ENOENT e:`%s`', format_exc())
                else:
                    raise

# ################################################################################################################################
# ################################################################################################################################
