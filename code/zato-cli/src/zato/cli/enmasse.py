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

def find_first(it, pred):
    """Given any iterable, return the first element `elem` from it matching
    `pred(elem)`

    ::

        strings = [("a", 1), ("b", 2), ("c", 3)]
        _, n = find_first(strings, lambda (x, y): x == 'b')
        assert n == 2
    """
    for obj in it:
        if pred(obj):
            return obj

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
                 object_dependencies=None,
                 service_dependencies=None,
                 is_security=False):
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
        #: Specifies a list of object dependencies:
        #:      field_name: {"dependent_type": "shortname",
        #:                   "dependent_field": "fieldname",
        #:                   "empty_value": None, or e.g. NO_SEC_DEF_NEEDED}
        self.object_dependencies = object_dependencies or {}
        #: Specifies a list of service dependencies:
        #:      field_name: {"only_if_field": "field_name" or None,
        #:                   "only_if_value": "vlaue" or None}
        self.service_dependencies = service_dependencies or {}
        #: If True, indicates the service is source of authentication
        #: credentials for use in another service.
        self.is_security = is_security

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
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='channel_jms_wmq',
        module_name='zato.server.service.internal.channel.jms_wmq',
        get_list_service='zato.channel.jms-wmq.get-list',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='channel_plain_http',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='channel_soap',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='channel_zmq',
        module_name='zato.server.service.internal.channel.zmq',
        get_list_service='zato.channel.zmq.get-list',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
        service_dependencies={
            'service_name': {}
        },
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
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
        service_dependencies={
            'service_name': {
                'only_if_field': 'connection',
                'only_if_value': 'channel',
            }
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
        object_dependencies={
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
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
            },
        },
        service_dependencies={
            'service': {}
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
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
    ),
    ServiceInfo(
        name='outconn_soap',
        module_name='zato.server.service.internal.http_soap',
        supports_import=False,
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
    ),
    ServiceInfo(
        name='query_cassandra',
        module_name='zato.server.service.internal.query.cassandra',
        supports_import=False,
        get_list_service='zato.query.cassandra.get-list',
    ),
    ServiceInfo(
        name='apikey',
        module_name='zato.server.service.internal.security.apikey',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='aws',
        module_name='zato.server.service.internal.security.aws',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='basic_auth',
        module_name='zato.server.service.internal.security.basic_auth',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='ntlm',
        module_name='zato.server.service.internal.security.ntlm',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='oauth',
        module_name='zato.server.service.internal.security.oauth',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='tech_acc',
        module_name='zato.server.service.internal.security.tech_account',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='tls_key_cert',
        module_name='zato.server.service.internal.security.tls.key_cert',
        is_security=True,
    ),
    ServiceInfo(
        name='tls_channel_sec',
        module_name='zato.server.service.internal.security.tls.channel',
        is_security=True,
    ),
    ServiceInfo(
        name='wss',
        module_name='zato.server.service.internal.security.wss',
        needs_password=True,
        is_security=True,
    ),
    ServiceInfo(
        name='xpath_sec',
        module_name='zato.server.service.internal.security.xpath',
        needs_password=True,
        is_security=True,
    ),
]


# channels - chan_
# outgoing connections - outconn_
# definitions - def_
# secdef_ 

SERVICE_NAMES = set(s.name for s in SERVICES)
SECURITY_SERVICE_NAMES = set(s.name for s in SERVICES if s.is_security)

SERVICE_BY_NAME = {
    info.name: info
    for info in SERVICES
}

class _DummyLink(object):
    """ Pip requires URLs to have a .url attribute.
    """
    def __init__(self, url):
        self.url = url

class Notice(object):
    def __init__(self, value_raw, value, code):
        self.value_raw = value_raw
        self.value = value
        self.code = code

    def __repr__(self):
        return "<{} at {} value_raw:'{}' value:'{}' code:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.value_raw,
            self.value, self.code)

class Results(object):
    def __init__(self, warnings=None, errors=None, service=None):
        #: List of Warning instances.
        self.warnings = warnings or []
        #: List of Error instances.
        self.errors = errors or []
        self.service_name = service.get_name() if service else None

    def add_error(self, raw, code, msg, *args):
        if args:
            msg = msg.format(*args)
        self.errors.append(Notice(raw, msg, code))

    def add_warning(self, raw, code, msg, *args):
        if args:
            msg = msg.format(*args)
        self.warnings.append(Notice(raw, msg, code))

    def _get_ok(self):
        return not(self.warnings or self.errors)

    ok = property(_get_ok)

class InputValidator(object):
    def __init__(self, json):
        #: Validation result.
        self.results = Results()
        #: Input JSON to validate.
        self.json = json

    #: Fields that may be marked as required by SimpleIO that are always
    #: optional during import.
    always_optional_fields = ('cluster_id',)

    replace_names = {
        'def_id': 'def_name',
    }

    def get_required_keys(self, service_name):
        """
        Return a set of keys required by a service definition.

        :param service_name:
            Service short name, e.g. "channel_amqp".
        :rtype set:
        """
        sinfo = SERVICE_BY_NAME[service_name]
        required = set()
        create_class = sinfo.get_create_class()
        for name in create_class.SimpleIO.input_required:
            if name in self.always_optional_fields:
                continue
            if isinstance(name, ForceType):
                name = name.name
            name = self.replace_names.get(name, name)
            required.add(name)
        return required

    def _needs_password(self, key):
        return 'sql' in key

    def validate_def_sec(self, item_type, item):
        sec_type = item.get('type')
        if not sec_type:
            item_dict = item.toDict()
            raw = (item_type, item_dict)
            self.results.add_error(raw, ERROR_TYPE_MISSING,
                                   "'{}' has no required 'type' key (def_sec)",
                                   item_dict)
        elif sec_type not in SECURITY_SERVICE_NAMES:
            raw = (sec_type, SECURITY_SERVICE_NAMES, item)
            self.results.add_error(raw, ERROR_INVALID_SEC_DEF_TYPE,
                                   "Invalid type '{}', must be one of '{}' (def_sec)",
                                   sec_type, SECURITY_SERVICE_NAMES)
        else:
            self._validate(item_type, item, True)

    def validate_other(self, item_type, item):
        if item_type not in SERVICE_BY_NAME:
            raw = (item_type, SERVICE_NAMES)
            self.results.add_error(raw, ERROR_INVALID_KEY,
                                   "Invalid key '{}', must be one of '{}'",
                                   item_type, SERVICE_NAMES)
        else:
            self._validate(item_type, item, False)

    def validate(self):
        """
        :rtype Results:
        """
        for item_type, items in self.json.items():
            for item in items:
                if item_type == 'def_sec':
                    self.validate_def_sec(item_type, item)
                else:
                    self.validate_other(item_type, item)

        return self.results

    def _validate(self, key, item, is_sec):
        name = item.get('name')
        item_dict = item.toDict()
        missing = None

        if not name:
            raw = (key, item_dict)
            self.results.add_error(raw, ERROR_NAME_MISSING,
                                   "No 'name' key found in item '{}' ({})",
                                   item_dict, key)
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
                self.results.add_error(raw, ERROR_KEYS_MISSING,
                                       "Missing {} in '{}', the rest is '{}' ({})",
                                       missing_value, name, item_dict, key)
            else:
                # OK, the keys are there, but do they all have non-None values?
                for req_key in required_keys:
                    if item.get(req_key) is None: # 0 or '' can be correct values
                        raw = (req_key, required_keys, item_dict, key)
                        self.results.add_error(raw, ERROR_KEYS_MISSING,
                                               "Key '{}' must not be None in '{}' ({})",
                                               req_key, item_dict, key)

class DependencyScanner(object):
    def __init__(self, json, ignore_missing=False):
        self.json = json
        self.ignore_missing = ignore_missing
        #: (item_type, name): [(item_type, name), ..]
        self.missing = {}

    def find_by_type_and_value(self, item_type, field, value):
        """
        Find an object in :py:attr:`json` of a particular type with a field
        matching a particular value.

        :param item_type:
            ServiceInfo.name of the item's type.
        :param field:
            The name of the field in the item to compare.
        :param value:
            The value to match.
        :return:
            First matching object, or ``None`` if no such object exists.
        """
        lst = self.json.get(item_type, ())
        return find_first(lst, lambda item: item[field] == value)

    def scan_item(self, item_type, item):
        """
        Scan the data of a single item for required dependencies, recording any
        that are missing in :py:attr:`missing`.

        :param item_type: ServiceInfo.name of the item's type.
        :param item: dict describing the item.
        """
        sinfo = SERVICE_BY_NAME[item_type]
        for dep_key, dep_info in sinfo.object_dependencies.items():
            if ((item.get(dep_key) != dep_info.get('empty_value')) and
                self.find_by_type_and_value(dep_info['dependent_type'],
                                            dep_info['dependent_field'],
                                            item[dep_key]) is None):
                key = (dep_info['dependent_type'], item[dep_key])
                names = self.missing.setdefault(key, [])
                names.append(item.name)

    def scan(self):
        """
        :rtype Results:
        """
        results = Results()
        for item_type, items in self.json.items():
            for item in items:
                self.scan_item(item_type, item)

        if not self.ignore_missing:
            for (missing_type, missing_name), dep_names in sorted(self.missing.items()):
                existing = sorted(item.name for item in self.json.get(missing_type, []))
                raw = (missing_type, missing_name, dep_names, existing)
                results.add_warning(raw, WARNING_MISSING_DEF,
                    "'{}' is needed by '{}' but was not among '{}'",
                    missing_name, sorted(dep_names), existing)

        return results

class ObjectImporter(object):
    logger = logging.getLogger('ObjectImporter')

    def __init__(self, client, object_mgr, json, ignore_missing):
        #: Validation result.
        self.results = Results()
        #: Zato client.
        self.client = client
        #: ClusterObjectManager instance.
        self.object_mgr = object_mgr
        #: JSON to import.
        self.json = Bunch(deepcopy(json))
        self.ignore_missing = ignore_missing

    def validate_service_required(self, item_type, item):
        sinfo = SERVICE_BY_NAME[item_type]
        item_dict = item.toDict()

        for dep_field, dep_info in sinfo.service_dependencies.items():
            only_if_field = dep_info.get('only_if_field')
            only_if_value = dep_info.get('only_if_value')
            if only_if_field and item.get(only_if_value) != only_if_value:
                continue

            service_name = item.get(dep_field)
            raw = (service_name, item_dict, item_type)
            if not service_name:
                self.results.add_error(raw, ERROR_SERVICE_NAME_MISSING,
                    "No service defined in '{}' ({})",
                    item_dict, item_type)
            else:
                if service_name not in self.object_mgr.services:
                    self.results.add_error(raw, ERROR_SERVICE_MISSING,
                        "Service '{}' from '{}' missing in ODB ({})",
                        service_name, item_dict, item_type)

    def validate_import_data(self):
        results = Results()
        dep_scanner = DependencyScanner(self.json,
            ignore_missing=self.ignore_missing)

        missing_defs = dep_scanner.scan()
        if missing_defs:
            for warning in missing_defs.warnings:
                missing_type, missing_name, dep_names, existing = warning.value_raw
                if not self.object_mgr.has_def(missing_type, missing_name):
                    raw = (missing_type, missing_name)
                    results.add_warning(raw, WARNING_MISSING_DEF_INCL_ODB,
                        "Definition '{}' not found in JSON/ODB ({}), needed by '{}'",
                        missing_name, missing_type, dep_names)

        for item_type, items in self.json.items():
            for item in items:
                self.validate_service_required(item_type, item)

        return results

    def remove_from_import_list(self, item_type, name):
        lst = self.json.get(item_type, [])
        item = find_first(lst, lambda item: item.name == name)
        if item:
            lst.remove(item)
        else:
            raise ValueError('Tried to remove missing %r named %r' % (item_type, name))

    def should_skip_item(self, item_type, attrs, is_edit):
        # Root RBAC role cannot be edited
        if item_type == 'rbac_role' and attrs.name == 'Root':
            return True

    def _import(self, item_type, attrs, is_edit):
        attrs_dict = attrs.toDict()
        attrs.cluster_id = self.client.cluster_id
        service_name, error_response = self._import_object(item_type, attrs, is_edit)

        # We quit on first error encountered
        if error_response:
            raw = (item_type, attrs_dict, error_response)
            self.results.add_error(raw, ERROR_COULD_NOT_IMPORT_OBJECT,
                                   "Could not import (is_edit {}) '{}' with '{}', response from '{}' was '{}'",
                                    is_edit, attrs.name, attrs_dict, service_name, error_response)
            return self.results

        # It's been just imported so we don't want to create in next steps
        # (this in fact would result in an error as the object already exists).
        if is_edit:
            self.remove_from_import_list(item_type, attrs.name)

        # We'll see how expensive this call is. Seems to be but
        # let's see in practice if it's a burden.
        self.object_mgr.refresh()

    def add_warning(self, results, key, value_dict, item):
        raw = (key, value_dict)
        results.add_warning(raw, WARNING_ALREADY_EXISTS_IN_ODB,
            '{} already exists in ODB {} ({})',
            value_dict.toDict(), item.toDict(), key)

    def find_already_existing_odb_objects(self):
        results = Results()
        for key, values in self.json.items():
            for value_dict in values:
                value_name = value_dict.get('name')
                if not value_name:
                    raw = (key, value_dict)
                    results.add_error(raw, ERROR_NAME_MISSING,
                        "{} has no 'name' key ({})",
                        value_dict.toDict(), key)

                if key == 'http_soap':
                    connection = value_dict.get('connection')
                    transport = value_dict.get('transport')

                    for item in self.object_mgr.objects.http_soap:
                        if connection == item.connection and transport == item.transport:
                            if value_name == item.name:
                                self.add_warning(results, key, value_dict, item)
                else:
                    odb_defs = self.object_mgr.objects[key.replace('-', '_')]
                    for odb_def in odb_defs:
                        if odb_def.name == value_name:
                            self.add_warning(results, key, value_dict, odb_def)

        return results

    def import_objects(self, already_existing):
        existing_defs = []
        existing_other = []

        new_defs = []
        new_other = []

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

            if self.should_skip_item(item_type, attrs, True):
                continue

            results = self._import(item_type, attrs, True)
            if results:
                return results

        #
        # Create new objects, again, definitions come first ..
        #
        for item_type, items in self.json.items():
            new = new_defs if 'def' in item_type else new_other
            new.append({item_type:items})

        #
        # .. actually create the objects now.
        #
        for elem in chain(new_defs, new_other):
            for item_type, attr_list in elem.items():
                for attrs in attr_list:

                    if self.should_skip_item(item_type, attrs, False):
                        continue

                    results = self._import(item_type, attrs, False)
                    if results:
                        return results

        return self.results

    def _swap_service_name(self, service_class, attrs, first, second):
        required = getattr(service_class.SimpleIO, 'input_required', [])
        if first in required and second in attrs:
            attrs[first] = attrs[second]

    def _import_object(self, def_type, attrs, is_edit):
        attrs_dict = attrs.toDict()
        if 'sec' in def_type:
            sinfo = SERVICE_BY_NAME[attrs.type]
            assert sinfo.is_security
        else:
            sinfo = SERVICE_BY_NAME[def_type]
            assert not sinfo.is_security

        if is_edit:
            service_class = sinfo.get_edit_class()
        else:
            service_class = sinfo.get_create_class()
        service_name = service_class.get_name()

        # service and service_name are interchangeable
        self._swap_service_name(service_class, attrs, 'service', 'service_name')
        self._swap_service_name(service_class, attrs, 'service_name', 'service')

        # Fetch an item from a cache of ODB object and assign its ID
        # to attrs so that the Edit service knows what to update.
        if is_edit:
            odb_item = self.object_mgr.find(def_type, attrs.name)
            attrs.id = odb_item.id

        if def_type == 'http_soap':
            if attrs.sec_def == NO_SEC_DEF_NEEDED:
                attrs.security_id = None
            else:
                sec = self.object_mgr.find('def_sec', attrs.sec_def)
                attrs.security_id = sec.id

        if def_type in('channel_amqp', 'channel_jms_wmq', 'outconn_amqp', 'outconn_jms_wmq'):
            def_type_name = def_type.replace('channel', 'def').replace('outconn', 'def')
            odb_item = self.object_mgr.find(def_type_name, attrs.get('def_name'))
            attrs.def_id = odb_item.id

        response = self.client.invoke(service_name, attrs)
        if not response.ok:
            return service_name, response.details
        else:
            verb = 'Updated' if is_edit else 'Created'
            self.logger.info("{} object '{}' ({} {})".format(verb, attrs.name, def_type, service_name))
            if sinfo.needs_password:

                password = attrs.get('password')
                if not password:
                    if sinfo.needs_password == MAYBE_NEEDS_PASSWORD:
                        self.logger.info("Password missing but not required '{}' ({} {})".format(
                            attrs.name, def_type, service_name))
                    else:
                        return service_name, "Password missing but is required '{}' ({} {}) attrs '{}'".format(
                            attrs.name, def_type, service_name, attrs_dict)
                else:
                    if not is_edit:
                        attrs.id = response.data['id']

                    service_class = sinfo.get_module().ChangePassword
                    request = {'id':attrs.id, 'password1':attrs.password, 'password2':attrs.password}
                    response = self.client.invoke(service_class.get_name(), request)
                    if not response.ok:
                        return service_name, response.details
                    else:
                        self.logger.info("Updated password '{}' ({} {})".format(attrs.name, def_type, service_name))

        return None, None


class ClusterObjectManager(object):
    logger = logging.getLogger('ClusterObjectManager')

    def __init__(self, client):
        self.client = client
        self.objects = Bunch()
        self.services = Bunch()

    def has_def(self, def_type, def_name):
        sinfo = SERVICE_BY_NAME[def_type]
        assert sinfo.get_list_service is not None

        response = self.client.invoke(sinfo.get_list_service, {
            'cluster_id':self.client.cluster_id
        })

        if not response.ok:
            self.logger.error('While attempting to verify {}, {}: {}'.format(def_type, def_name, response))

        match = None
        if response.ok:
            match = find_first(response.data, lambda item: item['name'] == def_name)
        return match is not None

    def find(self, item_type, name):
        lst = self.objects.get(item_type, ())
        return find_first(lst, lambda item: item.name == name)

    def refresh(self):
        # Previous name: get_odb_objects()
        self.get_via_odb_session()
        self.get_via_service_client()
        self.get_services()

        for item_type, items in self.objects.items():
            for item in items:
                self.fix_up_odb_object(item_type, item)

    def get_services(self):
        response = self.client.invoke('zato.service.get-list', {
            'cluster_id': self.client.cluster_id,
            'name_filter': '*'
        })

        if response.has_data:
            self.services = {
                service['name']: Bunch(service)
                for service in response.data
            }

    def _update_service_name(self, item):
        item.service = self.client.odb_session.query(Service.name).\
            filter(Service.id == item.service_id).one()[0]

    def fix_up_odb_object(self, key, item):
        if key == 'http_soap':
            if item.connection == 'channel':
                self._update_service_name(item)
            if item.security_id:
                item.sec_def = self.client.odb_session.query(SecurityBase.name).\
                    filter(SecurityBase.id == item.security_id).one()[0]
            else:
                item.sec_def = NO_SEC_DEF_NEEDED
        elif key == 'scheduler':
            self._update_service_name(item)
        elif 'sec_type' in item:
            item['type'] = item['sec_type']
            del item['sec_type']

        return item

    def get_fields(self, item):
        return Bunch(loads(to_json(item))[0]['fields'])

    def from_model_query(self, query, needs_password=False):
        args = (True, True) if needs_password else (True,)
        rows, columns = query(self.client.odb_session, self.client.cluster_id, *args)
        columns = columns.keys()

        target = []
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
        return target

    IGNORED_NAMES = (
        'admin.invoke',
        'pubapi',
    )

    def is_ignored_name(self, item):
        name = item.name.lower()
        return 'zato' in name or name in self.IGNORED_NAMES

    def from_simple_query(self, model_class, include_all=False):
        return [
            self.get_fields(item)
            for item in (
                self.client.odb_session.query(model_class).
                    filter(model_class.cluster_id == self.client.cluster_id).
                    all()
            )
            if include_all or not self.is_ignored_name(item)
        ]

    SEC_DEF_KLASSES = [
        APIKeySecurity,
        AWSSecurity,
        HTTPBasicAuth,
        NTLM,
        OAuth,
        TechnicalAccount,
        TLSChannelSecurity,
        TLSKeyCertSecurity,
        WSSDefinition,
        XPathSecurity,
    ]

    def get_via_odb_session(self):
        # Security definitions
        self.objects.def_sec = [
            item
            for klass in self.SEC_DEF_KLASSES
            for item in self.from_simple_query(klass)
        ]

        self.objects.def_amqp = self.from_simple_query(ConnDefAMQP, include_all=True)
        self.objects.def_cassandra = self.from_simple_query(CassandraConn, include_all=True)
        self.objects.def_cloud_openstack_swift = self.from_model_query(notif_cloud_openstack_swift_list, True)
        self.objects.def_jms_wmq = self.from_simple_query(ConnDefWMQ, include_all=True)
        self.objects.email_imap = self.from_simple_query(IMAP)
        self.objects.email_smtp = self.from_simple_query(SMTP)
        self.objects.notif_cloud_openstack_swift = self.from_model_query(cloud_openstack_swift_list, False)
        self.objects.notif_sql = self.from_model_query(notif_sql_list, True)
        self.objects.outconn_odoo = self.from_simple_query(OutgoingOdoo)
        self.objects.outconn_sql = self.from_model_query(out_sql_list)

        self.objects.http_soap = [
            self.get_fields(item)
            for item in self.client.odb_session.query(HTTPSOAP).
                filter(HTTPSOAP.cluster_id == self.client.cluster_id).
                filter(HTTPSOAP.is_internal == False).all()  # noqa E713 test for membership should be 'not in'
            if not self.is_ignored_name(item)
        ]

    def get_via_service_client(self):
        for sinfo in SERVICES:
            # Temporarily preserve function of the old enmasse.
            if sinfo.get_list_service is None:
                continue
            if sinfo.get_odb_objects_ignore:
                continue

            self.objects[sinfo.name] = []
            response = self.client.invoke(sinfo.get_list_service, {
                'cluster_id':self.client.cluster_id
            })

            if response.ok:
                for item in response.data:
                    if not 'zato' in item['name'].lower():
                        self.objects[sinfo.name].append(Bunch(item))


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
        self.has_import = getattr(args, 'import')
        self.json = {}

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
            self.object_mgr = ClusterObjectManager(self.client)
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
        results = Results()

        for raw, keys in sorted(self.json_find_include_dups().items()):
            len_keys = len(keys)
            keys = sorted(set(keys))
            results.add_error(raw, ERROR_ITEM_INCLUDED_MULTIPLE_TIMES,
                '{} included multiple times ({}) \n{}',
                raw, len_keys, '\n'.join(' - {}'.format(name) for name in keys))

        missing_items = sorted(self.json_find_missing_includes().items())
        for raw, keys in missing_items:
            missing, missing_abs = raw
            len_keys = len(keys)
            keys = sorted(set(keys))
            results.add_error(raw, ERROR_ITEM_INCLUDED_BUT_MISSING,
                '{} ({}) missing but needed in multiple definitions ({}) \n{}',
                missing, missing_abs, len_keys, '\n'.join(' - {}'.format(name) for name in keys))

        unparsable = self.json_find_unparsable_includes([elem[0][1] for elem in missing_items])
        for raw, keys in unparsable.items():
            include, abs_path, exc_pretty = raw
            len_keys = len(keys)
            suffix = '' if len_keys == 1 else 's'
            keys = sorted(set(keys))
            results.add_error(raw, ERROR_INCLUDE_COULD_NOT_BE_PARSED,
                '{} ({}) could not be parsed as JSON, used in ({}) definition{}\n{} \n{}',
                include, abs_path, len_keys, suffix, '\n'.join(' - {}'.format(name) for name in keys), exc_pretty)

        return results

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
        results = Results()
        merged = deepcopy(self.object_mgr.objects)

        for json_key, json_elems in self.json.items():
            if 'http' in json_key or 'soap' in json_key:
                odb_key = 'http_soap'
            else:
                odb_key = json_key

            if odb_key not in merged:
                sorted_merged = sorted(merged)
                raw = (json_key, odb_key, sorted_merged)
                results.add_error(raw, ERROR_INVALID_KEY,
                    "JSON key '{}' not one of '{}'",
                    odb_key, sorted_merged)
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

        if results.ok:
            self.json = merged
        return results


# ################################################################################################################################

    def export(self):
        # Find any definitions that are missing
        dep_scanner = DependencyScanner(self.json, ignore_missing=self.args.ignore_missing_defs)
        missing_defs = dep_scanner.scan()
        if not missing_defs.ok:
            self.logger.error('Failed to find all definitions needed')
            return [missing_defs]

        # Validate if every required input element has been specified.
        invalid_reqs = InputValidator(self.json).validate()
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
        self.object_mgr.refresh()
        self.logger.info('ODB objects read')

        results = self.merge_odb_json()
        if not results.ok:
            return [results]
        self.logger.info('ODB objects merged in')

        return self.export_local(False)

    def export_odb(self):
        return self.export_local_odb(False)

    def import_(self):
        self.object_mgr.refresh()
        importer = ObjectImporter(self.client, self.object_mgr, self.json,
            ignore_missing=self.args.ignore_missing_defs)

        # Find channels and jobs that require services that don't exist
        results = importer.validate_import_data()
        if not results.ok:
            return [results]

        already_existing = importer.find_already_existing_odb_objects()
        if not already_existing.ok and not self.args.replace_odb_objects:
            return [already_existing]

        results = importer.import_objects(already_existing)
        if not results.ok:
            return [results]

        return []
