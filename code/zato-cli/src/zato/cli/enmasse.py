# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os, sys
from copy import deepcopy
from datetime import datetime
from itertools import chain
from json import dumps
from os.path import abspath, exists, join
from traceback import format_exc

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch, bunchify

# Pip
from pip import download

# Texttable
from texttable import Texttable

# Zato
from zato.cli import ManageCommand
from zato.cli.check_config import CheckConfig
from zato.common.odb.model import APIKeySecurity, AWSSecurity, Base, CassandraConn, ConnDefAMQP, ConnDefWMQ, HTTPBasicAuth, \
     HTTPSOAP, IMAP, NTLM, OAuth, OutgoingOdoo, SecurityBase, Service, SMTP, TechnicalAccount, TLSChannelSecurity, \
     TLSKeyCertSecurity, to_json, WSSDefinition, XPathSecurity
from zato.common.odb.query import cloud_openstack_swift_list, notif_cloud_openstack_swift_list, notif_sql_list, out_sql_list
from zato.common.util import get_client_from_server_conf
from zato.server.service import ForceType

# --------------- IMPORTS HERE WILL BE REMOVED SOON --------------------
from zato.server.service.internal.cloud.aws import s3 as cloud_aws_s3
from zato.server.service.internal.search import es as search_es
from zato.server.service.internal.search import solr as search_solr
# ---------- END OF OBSOLETE IMPORTS ------------

DEFAULT_COLS_WIDTH = '15,100'
NO_SEC_DEF_NEEDED = 'zato-no-security'

class Code(object):
    def __init__(self, symbol, desc):
        self.symbol = symbol
        self.desc = desc

    def __repr__(self):
        return "<{} at {} symbol:'{}' desc:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.symbol, self.desc)

WARNING_ALREADY_EXISTS_IN_ODB = Code('W01', 'already exists in ODB')
WARNING_MISSING_DEF = Code('W02', 'missing def')
WARNING_NO_DEF_FOUND = Code('W03', 'no def found')
WARNING_MISSING_DEF_INCL_ODB = Code('W04', 'missing def incl. ODB')
ERROR_ITEM_INCLUDED_MULTIPLE_TIMES = Code('E01', 'item incl multiple')
ERROR_ITEM_INCLUDED_BUT_MISSING = Code('E02', 'incl missing')
ERROR_INCLUDE_COULD_NOT_BE_PARSED = Code('E03', 'incl parsing error')
ERROR_NAME_MISSING = Code('E04', 'name missing')
ERROR_DEF_KEY_NOT_DEFINED = Code('E05', 'def key not defined')
ERROR_NO_DEF_KEY_IN_LOOKUP_TABLE = Code('E06', 'no def key in lookup')
ERROR_KEYS_MISSING = Code('E08', 'missing keys')
ERROR_INVALID_SEC_DEF_TYPE = Code('E09', 'invalid sec def type')
ERROR_INVALID_KEY = Code('E10', 'invalid key')
ERROR_SERVICE_NAME_MISSING = Code('E11', 'service name missing')
ERROR_SERVICE_MISSING = Code('E12', 'service missing')
ERROR_COULD_NOT_IMPORT_OBJECT = Code('E13', 'could not import object')
ERROR_TYPE_MISSING = Code('E04', 'type missing')

def import_module(modname):
    """Import and return the Python module `modname`."""
    module = None
    exec('import %s as module' % (modname,))
    return module

class ServiceInfo(object):
    def __init__(self, name, module_name, needs_password=False,
                 create_class_name='Create',
                 edit_class_name='Edit',
                 supports_import=True,
                 get_list_service=None,
                 get_odb_objects_ignore=False,
                 dependencies=None):
        #: Short service name as appears in export data.
        self.name = name
        #: Canonical name of service's implementation module.
        self.module_name = module_name
        #: True if service requires a password key.
        self.needs_password = needs_password
        #: Name of the object creation class in the service module.
        self.create_class_name = create_class_name
        #: Name of the object modification class in the service module.
        self.edit_class_name = edit_class_name
        #: True if importer accepts this object. Some services were not
        #: supported previously; this is to maintain temporary compatibility
        #: with the old code.
        self.supports_import = supports_import
        #: Optional name of the object enumeration/retrieval service. CAUTION:
        #: see get_odb_objects() before adding this to every ServiceInfo.
        self.get_list_service = get_list_service
        #: If True, tell get_odb_objects() to ignore this type temporarily.
        #: This allows setting get_list_service for new bits of code.
        self.get_odb_objects_ignore = get_odb_objects_ignore
        #: Specifies a list of dependencies:
        #:      field_name: {"dependent_type": "shortname",
        #:                   "dependent_field": "fieldname"}
        self.dependencies = dependencies or {}

    def get_module(self):
        """Import and return the module containing the service
        implementation."""
        return import_module(self.module_name)

    def get_create_class(self):
        """Import and return the class implementation for creating objects in
        the service."""
        return getattr(self.get_module(), self.create_class_name)

    def get_edit_class(self):
        """Import and return the class implementation for editing objects in
        the service."""
        return getattr(self.get_module(), self.edit_class_name)

    def __repr__(self):
        return "<{} at {} mod:'{}' needs_password:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.mod, self.needs_password)

#: FTP definition may use a password but are not required to.
MAYBE_NEEDS_PASSWORD = 'MAYBE_NEEDS_PASSWORD'

#: List of ServiceInfo objects for all supported services. To be replaced by
#: introspection later.
SERVICES = [
    ServiceInfo(
        name='channel_amqp',
        module_name='zato.server.service.internal.channel.amqp_',
        get_list_service='zato.channel.amqp.get-list',
        dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='channel_jms_wmq',
        module_name='zato.server.service.internal.channel.jms_wmq',
        get_list_service='zato.server.service.internal.jms_wmq',
        dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='channel_plain_http',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
        dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='channel_soap',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
        dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='channel_zmq',
        module_name='zato.server.service.internal.channel.zmq',
        get_list_service='zato.channel.zmq.get-list',
    ),
    ServiceInfo(
        name='def_amqp',
        module_name='zato.server.service.internal.definition.amqp_',
        get_list_service='zato.definition.amqp.get-list',
        get_odb_objects_ignore=True,
    ),
    ServiceInfo(
        name='def_sec',
        module_name='zato.server.service.internal.security',
        get_list_service='zato.security.get-list',
        get_odb_objects_ignore=True,
    ),
    ServiceInfo(
        name='def_jms_wmq',
        module_name='zato.server.service.internal.definition.jms_wmq',
        get_list_service='zato.definition.jms-wmq.get-list',
    ),
    ServiceInfo(
        name='def_cassandra',
        module_name='zato.server.service.internal.definition.cassandra',
        get_list_service='zato.definition.cassandra.get-list',
        get_odb_objects_ignore=True,
    ),
    ServiceInfo(
        name='email_imap',
        module_name='zato.server.service.internal.email.imap',
        needs_password=MAYBE_NEEDS_PASSWORD
    ),
    ServiceInfo(
        name='email_smtp',
        module_name='zato.server.service.internal.email.smtp',
        needs_password=MAYBE_NEEDS_PASSWORD
    ),
    ServiceInfo(
        name='json_pointer',
        module_name='zato.server.service.internal.message.json_pointer',
        get_list_service='zato.message.json-pointer.get-list',
    ),
    ServiceInfo(
        name='http_soap',
        module_name='zato.server.service.internal.http_soap',
        # TODO: note: covers all of outconn_plain_http, outconn_soap, http_soap
        dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='def_namespace',
        module_name='zato.server.service.internal.message.namespace',
        get_list_service='zato.message.namespace.get-list',
    ),
    ServiceInfo(
        name='notif_cloud_openstack_swift',
        module_name='zato.server.service.internal.notif.cloud.openstack.swift',
    ),
    ServiceInfo(
        name='notif_sql',
        module_name='zato.server.service.internal.notif.sql',
    ),
    ServiceInfo(
        name='outconn_amqp',
        module_name='zato.server.service.internal.outgoing.amqp_',
        get_list_service='zato.outgoing.amqp.get-list',
        dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_ftp',
        module_name='zato.server.service.internal.outgoing.ftp',
        needs_password=MAYBE_NEEDS_PASSWORD,
        get_list_service='zato.outgoing.ftp.get-list',
    ),
    ServiceInfo(
        name='outconn_odoo',
        module_name='zato.server.service.internal.outgoing.odoo',
    ),
    ServiceInfo(
        name='outconn_jms_wmq',
        module_name='zato.server.service.internal.outgoing.jms_wmq',
        get_list_service='zato.outgoing.jms-wmq.get-list',
        dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_sql',
        module_name='zato.server.service.internal.outgoing.sql',
        needs_password=True,
    ),
    ServiceInfo(
        name='outconn_zmq',
        module_name='zato.server.service.internal.outgoing.zmq',
        get_list_service='zato.outgoing.zmq.get-list',
    ),
    ServiceInfo(
        name='scheduler',
        module_name='zato.server.service.internal.scheduler',
        get_list_service='zato.scheduler.job.get-list',
    ),
    ServiceInfo(
        name='xpath',
        module_name='zato.server.service.internal.message.xpath',
        get_list_service='zato.message.xpath.get-list',
    ),
    ServiceInfo(
        name='cloud_aws_s3',
        module_name='zato.server.service.internal.cloud.aws.s3',
        get_list_service='zato.cloud.aws.s3.get-list',
    ),
    ServiceInfo(
        name='def_cloud_openstack_swift',
        module_name='zato.server.service.internal.cloud.openstack.swift',
    ),
    ServiceInfo(
        name='search_es',
        module_name='zato.server.service.internal.search.es',
        get_list_service='zato.search.es.get-list',
    ),
    ServiceInfo(
        name='search_solr',
        module_name='zato.server.service.internal.search.solr',
        get_list_service='zato.search.solr.get-list',
    ),
    ServiceInfo(
        name='rbac_permission',
        module_name='zato.server.service.internal.security.rbac.permission',
        get_list_service='zato.security.rbac.permission.get-list',
    ),
    ServiceInfo(
        name='rbac_role',
        module_name='zato.server.service.internal.security.rbac.role',
        get_list_service='zato.security.rbac.role.get-list',
    ),
    ServiceInfo(
        name='rbac_client_role',
        module_name='zato.server.service.internal.security.rbac.client_role',
        get_list_service='zato.security.rbac.client-role.get-list',
    ),
    ServiceInfo(
        name='rbac_role_permission',
        module_name='zato.server.service.internal.security.rbac.role_permission',
        get_list_service='zato.security.rbac.role-permission.get-list',
    ),
    ServiceInfo(
        name='tls_ca_cert',
        module_name='zato.server.service.internal.security.tls.ca_cert',
        get_list_service='zato.security.tls.ca-cert.get-list',
    ),
    # Added for the exporter.
    ServiceInfo(
        name='outconn_plain_http',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
    ),
    ServiceInfo(
        name='outconn_soap',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
    ),
    ServiceInfo(
        name='query_cassandra',
        module_name='zato.server.service.internal.query.cassandra',
        supports_import=False,
        get_list_service='zato.query.cassandra.get-list',
    ),

]

#: List of security services. To be merged with SERVICES later.
SECURITY_SERVICES = [
    ServiceInfo(
        name='apikey',
        module_name='zato.server.service.internal.security.apikey',
        needs_password=True,
    ),
    ServiceInfo(
        name='aws',
        module_name='zato.server.service.internal.security.aws',
        needs_password=True,
    ),
    ServiceInfo(
        name='basic_auth',
        module_name='zato.server.service.internal.security.basic_auth',
        needs_password=True,
    ),
    ServiceInfo(
        name='ntlm',
        module_name='zato.server.service.internal.security.ntlm',
        needs_password=True,
    ),
    ServiceInfo(
        name='oauth',
        module_name='zato.server.service.internal.security.oauth',
        needs_password=True,
    ),
    ServiceInfo(
        name='tech_acc',
        module_name='zato.server.service.internal.security.tech_account',
        needs_password=True,
    ),
    ServiceInfo(
        name='tls_key_cert',
        module_name='zato.server.service.internal.security.tls.key_cert',
    ),
    ServiceInfo(
        name='tls_channel_sec',
        module_name='zato.server.service.internal.security.tls.channel',
    ),
    ServiceInfo(
        name='wss',
        module_name='zato.server.service.internal.security.wss',
        needs_password=True,
    ),
    ServiceInfo(
        name='xpath_sec',
        module_name='zato.server.service.internal.security.xpath',
        needs_password=True,
    ),
]

# channels - chan_
# outgoing connections - outconn_
# definitions - def_
# secdef_ 

SERVICE_BY_NAME = {
    info.name: info
    for info in SERVICES
}

SECURITY_SERVICE_BY_NAME = {
    info.name: info
    for info in SECURITY_SERVICES
}

SERVICE_NAMES = sorted(SERVICE_BY_NAME)
SECURITY_SERVICE_NAMES = sorted(SECURITY_SERVICE_BY_NAME)


class _DummyLink(object):
    """ Pip requires URLs to have a .url attribute.
    """
    def __init__(self, url):
        self.url = url

class _Incorrect(object):
    def __init__(self, value_raw, value, code):
        self.value_raw = value_raw
        self.value = value
        self.code = code

    def __repr__(self):
        return "<{} at {} value_raw:'{}' value:'{}' code:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.value_raw,
            self.value, self.code)

class Warning(_Incorrect):
    pass

class Error(_Incorrect):
    pass

class Results(object):
    def __init__(self, warnings=None, errors=None, service=None):
        #: List of Warning instances.
        self.warnings = warnings or []
        #: List of Error instances.
        self.errors = errors or []
        self.service_name = service.get_name() if service else None

    def _get_ok(self):
        return not(self.warnings or self.errors)

    ok = property(_get_ok)

class InputValidator(object):
    def __init__(self, json):
        #: Validation result.
        self.results = Results()
        #: Input JSON to validate.
        self.json = json

    def get_required_keys(self, service_name):
        """
        Return a set of keys required by a service definition.

        :param service_name:
            Service short name, e.g. "channel_amqp".
        :rtype set:
        """
        sinfo = SERVICE_BY_NAME.get(service_name)
        if sinfo is None:
            sinfo = SECURITY_SERVICE_BY_NAME[service_name]

        required = set()
        create_class = sinfo.get_create_class()
        for name in create_class.SimpleIO.input_required:
            if name in self.skip_names:
                continue
            if isinstance(name, ForceType):
                name = name.name
            name = self.replace_names.get(name, name)
            required.add(name)
        return required

    def _needs_password(self, key):
        return 'sql' in key

    def validate(self):
        """
        :rtype Results:
        """
        for key, items in self.json.items():
            for item in items:
                if key == 'def_sec':
                    sec_type = item.get('type')
                    if not sec_type:
                        item_dict = item.toDict()
                        raw = (key, item_dict)
                        value = "'{}' has no required 'type' key (def_sec) ".format(item_dict)
                        self.results.errors.append(Error(raw, value, ERROR_TYPE_MISSING))
                    else:
                        if sec_type not in SECURITY_SERVICE_BY_NAME:
                            raw = (sec_type, SECURITY_SERVICE_NAMES, item)
                            value = "Invalid type '{}', must be one of '{}' (def_sec)".format(sec_type, SECURITY_SERVICE_NAMES)
                            self.results.errors.append(Error(raw, value, ERROR_INVALID_SEC_DEF_TYPE))
                        else:
                            self._validate(key, item, True)
                else:
                    if key not in SERVICE_BY_NAME:
                        raw = (key, SERVICE_NAMES)
                        value = "Invalid key '{}', must be one of '{}'".format(key, SERVICE_NAMES)
                        self.results.errors.append(Error(raw, value, ERROR_INVALID_KEY))
                    else:
                        self._validate(key, item, False)

        return self.results

    def _validate(self, key, item, is_sec):
        name = item.get('name')
        item_dict = item.toDict()
        missing = None

        if not name:
            raw = (key, item_dict)
            value = "No 'name' key found in item '{}' ({})".format(item_dict, key)
            self.results.errors.append(Error(raw, value, ERROR_NAME_MISSING))
        else:
            if is_sec:
                # We know we have one of correct types already so we can
                # just look up required attributes.
                required_keys = self.get_required_keys(item.get('type'))
            else:
                required_keys = self.get_required_keys(key)

            if self._needs_password(key):
                required_keys.add('password')

            missing = sorted(required_keys - set(item))
            if missing:
                # Special case service and service_name because both can be used interchangeably
                _missing = list(missing)
                if len(_missing) == 1:
                    service_and_service_name = missing[0] == 'service' and 'service_name' in item
                    service_name_and_service = missing[0] == 'service_name' and 'service' in item
                    if service_and_service_name or service_name_and_service:
                        return

                missing_value = "key '{}'".format(missing[0]) if len(missing) == 1 else "keys '{}'".format(missing)
                raw = (key, name, item_dict, required_keys, missing)
                value = "Missing {} in '{}', the rest is '{}' ({})".format(missing_value, name, item_dict, key)
                self.results.errors.append(Error(raw, value, ERROR_KEYS_MISSING))

            # OK, the keys are there, but do they all have non-None values?
            else:
                for req_key in required_keys:
                    if item.get(req_key) is None: # 0 or '' can be correct values
                        raw = (req_key, required, item_dict, key)
                        value = "Key '{}' must not be None in '{}' ({})".format(req_key, item_dict, key)

    replace_names = {
        'def_id': 'def_name',
    }

    skip_names = ('cluster_id',)

class ObjectImporter(object):
    def __init__(self, json):
        #: Validation result.
        self.results = Results()
        #: JSON to import.
        self.json = json

    def import_objects(self, already_existing):
        existing_defs = []
        existing_other = []

        new_defs = []
        new_other = []

        self.json_to_import = Bunch(deepcopy(self.json))

        def get_odb_item(item_type, name):
            for item in self.odb_objects[item_type]:
                if item.name == name:
                    return item

        def get_security_by_name(name):
            for item in self.odb_objects.def_sec:
                if item.name == name:
                    return item.id

        def _swap_service_name(service_class, attrs, first, second):
            if first in getattr(service_class.SimpleIO, 'input_required', []) and second in attrs:
                attrs[first] = attrs[second]

        def remove_from_import_list(item_type, name):
            for json_item_type, items in self.json_to_import.items():
                if json_item_type == item_type:
                    for item in items:
                        if item.name == name:
                            items.remove(item)

                            # Name is unique, we can stop now
                            return

        def should_skip_item(item_type, attrs, is_edit):

            # Root RBAC role cannot be edited
            if item_type == 'rbac_role' and attrs.name == 'Root':
                return True

        def _import(item_type, attrs, is_edit):
            attrs_dict = attrs.toDict()
            attrs.cluster_id = self.client.cluster_id
            service_name, error_response = self._import_object(item_type, attrs, is_edit)

            # We quit on first error encountered
            if error_response:
                raw = (item_type, attrs_dict, error_response)
                value = "Could not import (is_edit {}) '{}' with '{}', response from '{}' was '{}'".format(
                    is_edit, attrs.name, attrs_dict, service_name, error_response)
                self.results.errors.append(Error(raw, value, ERROR_COULD_NOT_IMPORT_OBJECT))
                return self.results

            # It's been just imported so we don't want to create in next steps
            # (this in fact would result in an error as the object already exists).
            if is_edit:
                remove_from_import_list(item_type, attrs.name)

            # We'll see how expensive this call is. Seems to be but
            # let's see in practice if it's a burden.
            self.get_odb_objects()

        #
        # Update already existing objects first, definitions before any object
        # that may depend on them ..
        #
        for w in already_existing.warnings:
            item_type, _ = w.value_raw
            existing = existing_defs if 'def' in item_type else existing_other
            existing.append(w)

        #
        # .. actually invoke the updates now ..
        #
        for w in chain(existing_defs, existing_other):
            item_type, attrs = w.value_raw

            if should_skip_item(item_type, attrs, True):
                continue

            results = _import(item_type, attrs, True)
            if results:
                return results

        #
        # Create new objects, again, definitions come first ..
        #
        for item_type, items in self.json_to_import.items():
            new = new_defs if 'def' in item_type else new_other
            new.append({item_type:items})

        #
        # .. actually create the objects now.
        #
        for elem in chain(new_defs, new_other):
            for item_type, attr_list in elem.items():
                for attrs in attr_list:

                    if should_skip_item(item_type, attrs, False):
                        continue

                    results = _import(item_type, attrs, False)
                    if results:
                        return results

        return self.results

    def _import_object(self, def_type, attrs, is_edit):
        attrs_dict = attrs.toDict()
        if 'sec' in def_type:
            sinfo = SECURITY_SERVICE_BY_NAME[attrs.type]
        else:
            sinfo = SERVICE_BY_NAME[def_type]

        if is_edit:
            service_class = sinfo.get_edit_class()
        else:
            service_class = sinfo.get_create_class()
        service_name = service_class.get_name()

        # service and service_name are interchangeable
        _swap_service_name(service_class, attrs, 'service', 'service_name')
        _swap_service_name(service_class, attrs, 'service_name', 'service')

        # Fetch an item from a cache of ODB object and assign its ID
        # to attrs so that the Edit service knows what to update.
        if is_edit:
            odb_item = get_odb_item(def_type, attrs.name)
            attrs.id = odb_item.id

        if def_type == 'http_soap':
            if attrs.sec_def == NO_SEC_DEF_NEEDED:
                attrs.security_id = None
            else:
                attrs.security_id = get_security_by_name(attrs.sec_def)

        if def_type in('channel_amqp', 'channel_jms_wmq', 'outconn_amqp', 'outconn_jms_wmq'):
            def_type_name = def_type.replace('channel', 'def').replace('outconn', 'def')
            odb_item = get_odb_item(def_type_name, attrs.get('def_name'))
            attrs.def_id = odb_item.id

        response = self.client.invoke(service_name, attrs)
        if not response.ok:
            return service_name, response.details
        else:
            verb = 'Updated' if is_edit else 'Created'
            self.logger.info("{} object '{}' ({} {})".format(verb, attrs.name, item_type, service_name))
            if import_info.needs_password:

                password = attrs.get('password')
                if not password:
                    if import_info.needs_password == MAYBE_NEEDS_PASSWORD:
                        self.logger.info("Password missing but not required '{}' ({} {})".format(
                            attrs.name, item_type, service_name))
                    else:
                        return service_name, "Password missing but is required '{}' ({} {}) attrs '{}'".format(
                            attrs.name, item_type, service_name, attrs_dict)
                else:
                    if not is_edit:
                        attrs.id = response.data['id']

                    service_class = getattr(import_info.mod, 'ChangePassword')
                    request = {'id':attrs.id, 'password1':attrs.password, 'password2':attrs.password}
                    response = self.client.invoke(service_class.get_name(), request)
                    if not response.ok:
                        return service_name, response.details
                    else:
                        self.logger.info("Updated password '{}' ({} {})".format(attrs.name, item_type, service_name))

        return None, None


class EnMasse(ManageCommand):
    """ Manages server objects en masse.
    """
    opts = [
        {'name':'--server-url', 'help':'URL of the server that enmasse should talk to, provided in host[:port] format. Defaults to server.conf\'s \'gunicorn_bind\''},  # nopep8
        {'name':'--export-local', 'help':'Export local JSON definitions into one file (can be used with --export-odb)', 'action':'store_true'},
        {'name':'--export-odb', 'help':'Export ODB definitions into one file (can be used with --export-local)', 'action':'store_true'},
        {'name':'--import', 'help':'Import definitions from a local JSON (excludes --export-*)', 'action':'store_true'},
        {'name':'--ignore-missing-defs', 'help':'Ignore missing definitions when exporting to JSON', 'action':'store_true'},
        {'name':'--replace-odb-objects', 'help':'Force replacing objects already existing in ODB during import', 'action':'store_true'},
        {'name':'--input', 'help':'Path to an input JSON document'},
        {'name':'--cols_width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH), 'action':'store_true'},
    ]

    def _on_server(self, args):

        self.args = args
        self.curdir = abspath(self.original_dir)
        self.replace_odb_objects = self.args.replace_odb_objects
        self.has_import = getattr(args, 'import')
        self.ignore_missing_defs = args.ignore_missing_defs
        self.json = {}
        self.json_to_import = {}

        self.odb_objects = Bunch()
        self.odb_services = Bunch()

        #
        # Tasks and scenarios
        #
        # 1) Export all local JSON files into one (--export-local)
        # 2) Export all definitions from ODB (--export-odb)
        # 3) Export all local JSON files with ODB definitions merged into one (--export-local --export-odb):
        # -> 4) Import definitions from a local JSON file (--import)
        #    4a) bail out if local JSON overrides any from ODB (no --replace-odb-objects)
        #    4b) override whatever is found in ODB with values from JSON (--replace-odb-objects)
        #

        if args.export_odb or self.has_import:

            # Checks if connections to ODB/Redis are configured properly
            cc = CheckConfig(self.args)
            cc.show_output = False
            cc.execute(Bunch(path='.'))

            # Get back to the directory we started in so following commands start afresh as well
            os.chdir(self.curdir)

            # Get client and issue a sanity check as quickly as possible
            self.client = get_client_from_server_conf(self.args.path)
            self.client.invoke('zato.ping')

        # Imports and export are mutually excluding
        if self.has_import and (args.export_local or args.export_odb):
            self.logger.error('Cannot specify import and export options at the same time, stopping now')
            sys.exit(self.SYS_ERROR.CONFLICTING_OPTIONS)

        if args.export_local or self.has_import:
            input_path = self.ensure_input_exists()
            self.json = bunchify(loads(open(input_path).read()))

            # Local JSON sanity check first
            json_sanity_results = self.json_sanity_check()
            if not json_sanity_results.ok:
                self.logger.error('JSON sanity check failed')
                self.report_warnings_errors([json_sanity_results])
                sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # 3)
        if args.export_local and args.export_odb:
            self.report_warnings_errors(self.export_local_odb())
            self.save_json()

        # 1)
        elif args.export_local:
            self.report_warnings_errors(self.export_local())
            self.save_json()

        # 2)
        elif args.export_odb:
            self.report_warnings_errors(self.export_odb())
            self.save_json()

        # 4) a/b
        elif self.has_import:
            self.report_warnings_errors(self.import_())

        else:
            self.logger.error('At least one of --export-local, --export-odb or --import is required, stopping now')
            sys.exit(self.SYS_ERROR.NO_OPTIONS)

# ################################################################################################################################

    def save_json(self):
        now = datetime.now().isoformat() # Not in UTC, we want to use user's TZ
        name = 'zato-export-{}.json'.format(now.replace(':', '_').replace('.', '_'))

        f = open(join(self.curdir, name), 'w')
        f.write(dumps(self.json, indent=1, sort_keys=True))
        f.close()

        self.logger.info('Data exported to {}'.format(f.name))

# ################################################################################################################################

    def ensure_input_exists(self):
        input_path = abspath(join(self.curdir, self.args.input))
        if not exists(input_path):
            self.logger.error('No such path: [{}]'.format(input_path))

            # TODO: ManageCommand should not ignore exit codes subclasses return
            sys.exit(self.SYS_ERROR.NO_INPUT)

        return input_path

# ################################################################################################################################

    def get_warnings_errors(self, items):

        warn_idx = 1
        error_idx = 1
        warn_err = {}

        for item in items:

            for warning in item.warnings:
                warn_err['warn{:04}/{} {}'.format(warn_idx, warning.code.symbol, warning.code.desc)] = warning.value
                warn_idx += 1

            for error in item.errors:
                warn_err['err{:04}/{} {}'.format(error_idx, error.code.symbol, error.code.desc)] = error.value
                error_idx += 1

        warn_no = warn_idx-1
        error_no = error_idx-1

        return warn_err, warn_no, error_no

    def report_warnings_errors(self, items):

        warn_err, warn_no, error_no = self.get_warnings_errors(items)
        table = self.get_table(warn_err)

        warn_plural = '' if warn_no == 1 else 's'
        error_plural = '' if error_no == 1 else 's'

        if warn_no or error_no:
            if error_no:
                level = logging.ERROR
            else:
                level = logging.WARN

            prefix = '{} warning{} and {} error{} found:\n'.format(warn_no, warn_plural, error_no, error_plural)
            self.logger.log(level, prefix + table.draw())

        else:
            # A signal that we found no warnings nor errors
            return True

# ################################################################################################################################

    def get_table(self, out):

        cols_width = self.args.cols_width if self.args.cols_width else DEFAULT_COLS_WIDTH
        cols_width = (elem.strip() for elem in cols_width.split(','))
        cols_width = [int(elem) for elem in cols_width]

        table = Texttable()
        table.set_cols_width(cols_width)

        # Use text ('t') instead of auto so that boolean values don't get converted into ints
        table.set_cols_dtype(['t', 't'])

        rows = [['Key', 'Value']]
        rows.extend(sorted(out.items()))

        table.add_rows(rows)

        return table

# ################################################################################################################################

    def get_include_abspath(self, curdir, value):
        return abspath(join(curdir, value.replace('file://', '')))

    def is_include(self, value):
        return isinstance(value, basestring)

    def get_json_includes(self):
        for key in sorted(self.json):
            for value in self.json[key]:
                if self.is_include(value):
                    yield key, value

    def json_find_include_dups(self):
        seen_includes = {}

        for key, value in self.get_json_includes():
            keys = seen_includes.setdefault(value, [])
            keys.append(key)

        dups = dict((k,v) for (k,v) in seen_includes.items() if len(v) > 1)

        return dups

    def json_find_missing_includes(self):
        missing = {}
        for key in sorted(self.json):
            for value in self.json[key]:
                if self.is_include(value):
                    if download.is_file_url(_DummyLink(value)):
                        abs_path = self.get_include_abspath(self.curdir, value)
                        if not exists(abs_path):
                            item = missing.setdefault((value, abs_path), [])
                            item.append(key)
        return missing

    def json_find_unparsable_includes(self, missing):
        unparsable = {}

        for key in sorted(self.json):
            for value in self.json[key]:
                if self.is_include(value):
                    if download.is_file_url(_DummyLink(value)):
                        abs_path = self.get_include_abspath(self.curdir, value)

                        # No point in parsing what is already known not to exist
                        if abs_path not in missing:
                            try:
                                loads(open(abs_path).read())
                            except Exception, e:
                                exc_pretty = format_exc(e)

                                item = unparsable.setdefault((value, abs_path, exc_pretty), [])
                                item.append(key)

        return unparsable

    def json_sanity_check(self):
        errors = []

        for raw, keys in sorted(self.json_find_include_dups().items()):
            len_keys = len(keys)
            keys = sorted(set(keys))
            value = '{} included multiple times ({}) \n{}'.format(
                raw, len_keys, '\n'.join(' - {}'.format(name) for name in keys))
            errors.append(Error(raw, value, ERROR_ITEM_INCLUDED_MULTIPLE_TIMES))

        missing_items = sorted(self.json_find_missing_includes().items())
        for raw, keys in missing_items:
            missing, missing_abs = raw
            len_keys = len(keys)
            keys = sorted(set(keys))
            value = '{} ({}) missing but needed in multiple definitions ({}) \n{}'.format(
                missing, missing_abs, len_keys, '\n'.join(' - {}'.format(name) for name in keys))
            errors.append(Error(raw, value, ERROR_ITEM_INCLUDED_BUT_MISSING))

        unparsable = self.json_find_unparsable_includes([elem[0][1] for elem in missing_items])
        for raw, keys in unparsable.items():
            include, abs_path, exc_pretty = raw
            len_keys = len(keys)
            suffix = '' if len_keys == 1 else 's'
            keys = sorted(set(keys))
            value = '{} ({}) could not be parsed as JSON, used in ({}) definition{}\n{} \n{}'.format(
                include, abs_path, len_keys, suffix, '\n'.join(' - {}'.format(name) for name in keys), exc_pretty)
            errors.append(Error(raw, value, ERROR_INCLUDE_COULD_NOT_BE_PARSED))

        return Results([], errors)

    def merge_includes(self):
        json_with_includes = Bunch()
        for key, values in self.json.items():
            values_with_includes = json_with_includes.setdefault(key, [])
            for value in values:
                if self.is_include(value):
                    abs_path = self.get_include_abspath(self.curdir, value)
                    include = Bunch(loads(open(abs_path).read()))
                    values_with_includes.append(include)
                else:
                    values_with_includes.append(value)

        self.json = json_with_includes
        self.logger.info('Includes merged in successfully')

    def merge_odb_json(self):
        errors = []
        merged = deepcopy(self.odb_objects)

        for json_key, json_elems in self.json.items():
            if 'http' in json_key or 'soap' in json_key:
                odb_key = 'http_soap'
            else:
                odb_key = json_key

            if odb_key not in merged:
                sorted_merged = sorted(merged)
                raw = (json_key, odb_key, sorted_merged)
                value = "JSON key '{}' not one of '{}'".format(odb_key, sorted_merged)
                errors.append(Error(raw, value, ERROR_INVALID_KEY))
            else:
                for json_elem in json_elems:
                    if 'http' in json_key or 'soap' in json_key:
                        connection, transport = json_key.split('_', 1)
                        connection = 'outgoing' if connection == 'outconn' else connection

                        for odb_elem in merged.http_soap:
                            if odb_elem.get('transport') == transport and odb_elem.get('connection') == connection:
                                if odb_elem.name == json_elem.name:
                                    merged.http_soap.remove(odb_elem)
                    else:
                        for odb_elem in merged[odb_key]:
                            if odb_elem.name == json_elem.name:
                                merged[odb_key].remove(odb_elem)
                    merged[odb_key].append(json_elem)

        if errors:
            return Results([], errors)

        self.json = merged

# ################################################################################################################################

    def get_odb_objects(self):

        def _update_service_name(item):
            item.service = self.client.odb_session.query(Service.name).\
                filter(Service.id == item.service_id).one()[0]

        def fix_up_odb_object(key, item):
            if key == 'http_soap':
                if item.connection == 'channel':
                    _update_service_name(item)
                if item.security_id:
                    item.sec_def = self.client.odb_session.query(SecurityBase.name).\
                        filter(SecurityBase.id == item.security_id).one()[0]
                else:
                    item.sec_def = NO_SEC_DEF_NEEDED
            elif key == 'scheduler':
                _update_service_name(item)
            elif 'sec_type' in item:
                item['type'] = item['sec_type']
                del item['sec_type']

            return item

        def get_fields(item):
            return Bunch(loads(to_json(item))[0]['fields'])

        def add_from_model_query(query, target, needs_password=False):
            args = (True, True) if needs_password else (True,)
            rows, columns = query(self.client.odb_session, self.client.cluster_id, *args)
            columns = columns.keys()

            for row in rows:
                item = Bunch()
                if isinstance(row, Base):
                    for idx, (key, value) in enumerate(row):
                        item[key] = value
                else:
                    for idx, value in enumerate(row):
                        key = columns[idx]
                        item[key] = value
                target.append(item)

        def add_from_simple_query(queries, target):
            for query in queries:
                for item in query.all():
                    name = item.name.lower()
                    if not 'zato' in name and name not in('admin.invoke', 'pubapi'):
                        target.append(get_fields(item))

        self.odb_objects.def_amqp = []
        self.odb_objects.def_cassandra = []
        self.odb_objects.def_cloud_openstack_swift = []
        self.odb_objects.def_jms_wmq = []
        self.odb_objects.def_sec = []
        self.odb_objects.email_imap = []
        self.odb_objects.email_smtp = []
        self.odb_objects.http_soap = []
        self.odb_objects.notif_cloud_openstack_swift = []
        self.odb_objects.notif_sql = []
        self.odb_objects.outconn_odoo = []
        self.odb_objects.outconn_sql = []

        # Security definitions

        apikey = self.client.odb_session.query(APIKeySecurity).\
            filter(APIKeySecurity.cluster_id == self.client.cluster_id)

        aws = self.client.odb_session.query(AWSSecurity).\
            filter(AWSSecurity.cluster_id == self.client.cluster_id)

        basic_auth = self.client.odb_session.query(HTTPBasicAuth).\
            filter(HTTPBasicAuth.cluster_id == self.client.cluster_id)

        ntlm = self.client.odb_session.query(NTLM).\
            filter(NTLM.cluster_id == self.client.cluster_id)

        oauth = self.client.odb_session.query(OAuth).\
            filter(OAuth.cluster_id == self.client.cluster_id)

        tech_acc = self.client.odb_session.query(TechnicalAccount).\
            filter(TechnicalAccount.cluster_id == self.client.cluster_id)

        tls_channel_sec = self.client.odb_session.query(TLSChannelSecurity).\
            filter(TLSChannelSecurity.cluster_id == self.client.cluster_id)

        tls_key_cert = self.client.odb_session.query(TLSKeyCertSecurity).\
            filter(TLSKeyCertSecurity.cluster_id == self.client.cluster_id)

        wss = self.client.odb_session.query(WSSDefinition).\
            filter(WSSDefinition.cluster_id == self.client.cluster_id)

        xpath_sec = self.client.odb_session.query(XPathSecurity).\
            filter(XPathSecurity.cluster_id == self.client.cluster_id)

        # Connections that need passwords - get-list doesn't return passwords.

        email_imap = self.client.odb_session.query(IMAP).\
            filter(IMAP.cluster_id == self.client.cluster_id)

        email_smtp = self.client.odb_session.query(SMTP).\
            filter(SMTP.cluster_id == self.client.cluster_id)

        outconn_odoo = self.client.odb_session.query(OutgoingOdoo).\
            filter(OutgoingOdoo.cluster_id == self.client.cluster_id)

        add_from_simple_query(
            [apikey, aws, basic_auth, ntlm, oauth, tech_acc, tls_channel_sec, tls_key_cert, wss, xpath_sec],
            self.odb_objects.def_sec)

        add_from_simple_query([email_imap], self.odb_objects.email_imap)
        add_from_simple_query([email_smtp], self.odb_objects.email_smtp)
        add_from_simple_query([outconn_odoo], self.odb_objects.outconn_odoo)

        add_from_model_query(notif_cloud_openstack_swift_list, self.odb_objects.notif_cloud_openstack_swift, True)
        add_from_model_query(cloud_openstack_swift_list, self.odb_objects.def_cloud_openstack_swift, False)

        add_from_model_query(notif_sql_list, self.odb_objects.notif_sql, True)
        add_from_model_query(out_sql_list, self.odb_objects.outconn_sql)

        for item in self.client.odb_session.query(ConnDefAMQP).\
            filter(ConnDefAMQP.cluster_id == self.client.cluster_id).all():
            self.odb_objects.def_amqp.append(get_fields(item))

        for item in self.client.odb_session.query(ConnDefWMQ).\
            filter(ConnDefWMQ.cluster_id == self.client.cluster_id).all():
            self.odb_objects.def_jms_wmq.append(get_fields(item))

        for item in self.client.odb_session.query(CassandraConn).\
            filter(CassandraConn.cluster_id == self.client.cluster_id).all():
            self.odb_objects.def_cassandra.append(get_fields(item))

        for item in self.client.odb_session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id == self.client.cluster_id).\
            filter(HTTPSOAP.is_internal == False).all(): # noqa E713 test for membership should be 'not in'
            if item.name not in('admin.invoke', 'pubapi', 'zato.check.service'):
                self.odb_objects.http_soap.append(get_fields(item))

        for sinfo in SERVICES + SECURITY_SERVICES:
            # Temporarily preserve function of the old enmasse.
            if sinfo.get_list_service is None:
                continue

            self.odb_objects[sinfo.name] = []
            response = self.client.invoke(sinfo.get_list_service, {
                'cluster_id':self.client.cluster_id
            })

            if response.ok:
                for item in response.data:
                    if not 'zato' in item['name'].lower():
                        self.odb_objects[sinfo.name].append(Bunch(item))

        for key, items in self.odb_objects.items():
            for item in items:
                fix_up_odb_object(key, item)

# ################################################################################################################################

    def find_already_existing_odb_objects(self):
        warnings = []
        errors = []

        def add_warning(key, value_dict, item):
            raw = (key, value_dict)
            msg = '{} already exists in ODB {} ({})'.format(value_dict.toDict(), item.toDict(), key)
            warnings.append(Warning(raw, msg, WARNING_ALREADY_EXISTS_IN_ODB))

        for key, values in self.json.items():
            for value_dict in values:
                value_name = value_dict.get('name')
                if not value_name:
                    raw = (key, value_dict)
                    msg = "{} has no 'name' key ({})".format(value_dict.toDict(), key)
                    errors.append(Error(raw, msg, ERROR_NAME_MISSING))

                if key == 'http_soap':
                    connection = value_dict.get('connection')
                    transport = value_dict.get('transport')

                    for item in self.odb_objects.http_soap:
                        if connection == item.connection and transport == item.transport:
                            if value_name == item.name:
                                add_warning(key, value_dict, item)
                else:
                    odb_defs = self.odb_objects[key.replace('-', '_')]
                    for odb_def in odb_defs:
                        if odb_def.name == value_name:
                            add_warning(key, value_dict, odb_def)

        return Results(warnings, errors)

# ################################################################################################################################

    def find_missing_defs(self):
        warnings = []
        errors = []
        missing_def_names = {}

        def _add_error(item, key_name, def_, json_key):
            raw = (item, def_)
            value = "{} does not define '{}' (value is {}) ({})".format(item.toDict(), key_name, def_, json_key)
            errors.append(Error(raw, value, ERROR_DEF_KEY_NOT_DEFINED))

        defs_keys = {
                'def_name': ('jms-wmq', 'amqp'),
                'sec_def': ('plain-http', 'soap'),
            }

        items_defs = {
            'channel_amqp':'def_amqp',
            'channel_jms_wmq':'def_jms_wmq',
            'channel_plain_http':'def_sec',
            'channel_soap':'def_sec',
            'outconn_amqp':'def_amqp',
            'outconn_jms_wmq':'def_jms_wmq',
            'outconn_plain_http':'def_sec',
            'outconn_soap':'def_sec',
            'http_soap':'def_sec'
        }

        _no_sec_needed = ('channel-plain-http', 'channel-soap', 'outconn-plain-http', 'outconn-soap')

        def get_needed_defs():

            for json_key, json_items in self.json.items():
                for def_name, def_keys in defs_keys.items():
                    for def_key in def_keys:
                        if def_key in json_key:
                            for json_item in json_items:
                                if 'def' in json_key:
                                    continue
                                def_ = json_item.get(def_name)
                                if not def_:
                                    _add_error(json_item, def_name, def_, json_key)
                                yield ({json_key:def_})

        needed_defs = list(get_needed_defs())
        for info_dict in needed_defs:
            item_key, def_name = info_dict.items()[0]
            def_key = items_defs.get(item_key)

            if not def_key:
                raw = (info_dict, items_defs)

                items_defs_pretty = []
                for k, v in sorted(items_defs.items()):
                    items_defs_pretty.append('`{} = {}`'.format(k, v))

                value = "Could not find a def key in \n{}\nfor item_key '{}'".format('\n'.join(items_defs_pretty), item_key)
                errors.append(Error(raw, value, ERROR_NO_DEF_KEY_IN_LOOKUP_TABLE))

            else:
                defs = self.json.get(def_key)

                for item in defs:
                    if item.get('name') == def_name:
                        break
                else:
                    if def_name == NO_SEC_DEF_NEEDED and item_key in _no_sec_needed:
                        continue

                    def_names = tuple(sorted([def_.name for def_ in defs]))
                    raw = (def_key, def_name, def_names)
                    dependants = missing_def_names.setdefault(raw, set())
                    dependants.add(item_key)

        if not self.ignore_missing_defs:
            for(def_key, missing_def, existing_ones), dependants in missing_def_names.items():
                if missing_def == NO_SEC_DEF_NEEDED:
                    continue
                dependants = sorted(dependants)
                raw = (def_key, missing_def, existing_ones, dependants)
                value = "'{}' is needed by '{}' but was not among '{}'".format(missing_def, dependants, existing_ones)
                warnings.append(Warning(raw, value, WARNING_MISSING_DEF))

        if warnings or errors:
            return Results(warnings, errors)

# ################################################################################################################################

    def validate_input(self):
        return InputValidator(self.json).validate()


# ################################################################################################################################

    def export(self):

        # Find any definitions that are missing
        missing_defs = self.find_missing_defs()
        if missing_defs:
            self.logger.error('Failed to find all definitions needed')
            return [missing_defs]

        # Validate if every required input element has been specified.
        invalid_reqs = self.validate_input()
        if invalid_reqs:
            self.logger.error('Required elements missing')
            return [invalid_reqs]

        return []

    def export_local(self, needs_includes=True):
        if needs_includes:
            self.merge_includes()
        return self.export()

    def export_local_odb(self, needs_local=True):
        if needs_local:
            self.merge_includes()
        self.get_odb_objects()
        self.logger.info('ODB objects read')

        errors = self.merge_odb_json()
        if errors:
            return [errors]
        self.logger.info('ODB objects merged in')

        return self.export_local(False)

    def export_odb(self):
        return self.export_local_odb(False)

# ################################################################################################################################

    def validate_import_data(self):
        warnings = []
        errors = []

        items_defs = {
            'def_amqp':'zato.definition.amqp.get-list',
            'def_jms_wmq':'zato.definition.jms-wmq.get-list',
            'def_cassandra':'zato.definition.cassandra.get-list',
            'def_sec':'zato.security.get-list',
        }

        def has_def(def_type, def_name):
            service = items_defs[def_type]
            response = self.client.invoke(service, {'cluster_id':self.client.cluster_id})
            if response.ok:
                for item in response.data:
                    if item['name'] == def_name:
                        return False

            return False

        missing_defs = self.find_missing_defs()
        if missing_defs:
            for warning in missing_defs.warnings:
                def_type, def_name, _, dependants = warning.value_raw
                if not has_def(def_type, def_name):
                    raw = (def_type, def_name)
                    value = "Definition '{}' not found in JSON/ODB ({}), needed by '{}'".format(
                        def_name, def_type, dependants)
                    warnings.append(Warning(raw, value, WARNING_MISSING_DEF_INCL_ODB))

        def needs_service(json_key, item):
            return 'channel' in json_key or json_key == 'scheduler' or \
                   ('http_soap' in json_key and item.get('connection') == 'channel')

        for json_key, items in self.json.items():
            for item in items:
                if needs_service(json_key, item):
                    item_dict = item.toDict()
                    service_name = item.get('service') or item.get('service_name')
                    raw = (service_name, item_dict, json_key)
                    if not service_name:
                        value = "No service defined in '{}' ({})".format(item_dict, json_key)
                        errors.append(Error(raw, value, ERROR_SERVICE_NAME_MISSING))
                    else:
                        if service_name not in self.odb_services:
                            value = "Service '{}' from '{}' missing in ODB ({})".format(service_name, item_dict, json_key)
                            errors.append(Error(raw, value, ERROR_SERVICE_MISSING))

        return Results(warnings, errors)

    def import_objects(self, already_existing):
        return ObjectImporter().import_objects(already_existing)

    def import_(self):
        self.get_odb_objects()

        odb_services = self.client.invoke('zato.service.get-list', {'cluster_id':self.client.cluster_id, 'name_filter':'*'})
        if odb_services.has_data:
            for service in odb_services.data:
                self.odb_services[service['name']] = Bunch(service)

        # Find channels and jobs that require services that don't exist
        results = self.validate_import_data()
        if not results.ok:
            return [results]

        already_existing = self.find_already_existing_odb_objects()
        if not already_existing.ok and not self.replace_odb_objects:
            return [already_existing]

        results = self.import_objects(already_existing)
        if not results.ok:
            return [results]

        return []

# ################################################################################################################################
