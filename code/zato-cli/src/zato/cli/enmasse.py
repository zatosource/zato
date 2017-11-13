# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import collections, logging, os, sys
from copy import deepcopy
from datetime import datetime
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
from zato.common.util import get_client_from_server_conf
from zato.server.service import ForceType

DEFAULT_COLS_WIDTH = '15,100'
NO_SEC_DEF_NEEDED = 'zato-no-security'

Code = collections.namedtuple('Code', ('symbol', 'desc'))

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
    `pred(elem)`"""
    for obj in it:
        if pred(obj):
            return obj

def populate_services_from_apispec(client):
    """Request a list of services from the APISpec service, and merge the
    results into SERVICES_BY_PREFIX, creating new ServiceInfo instances to
    represent previously unknown services as appropriate."""
    response = client.invoke('zato.apispec.get-api-spec', {
        'return_internal': True
    })

    if not response.ok:
        logger.error('could not fetch service list')
        return

    by_prefix = {}  # { "zato.apispec": {"get-api-spec": { .. } } }
    for service in response.data['namespaces']['']['services']:
        prefix, _, name = service['name'].rpartition('.')
        methods = by_prefix.setdefault(prefix, {})
        methods[name] = service

    for prefix, methods in by_prefix.items():
        # Ignore prefixes lacking "get-list", "create" and "edit" methods.
        if not all(n in methods for n in ('get-list', 'create', 'edit')):
            continue

        sinfo = SERVICE_BY_PREFIX.get(prefix)
        if sinfo is None:
            sinfo = ServiceInfo(prefix=prefix, name=make_service_name(prefix))
            SERVICE_BY_PREFIX[prefix] = sinfo
            SERVICE_BY_NAME[sinfo.name] = sinfo

        sinfo.methods = methods


#: The common prefix for a set of services is tested against the first element
#: in this list using startswith(). If it matches, that prefix is replaced by
#: the second element. The prefixes must match exactly if the first element
#: does not end in a period.
SHORTNAME_BY_PREFIX = [
    ('zato.definition.', 'def'),
    ('zato.email.', 'email'),
    ('zato.message.namespace', 'def_namespace'),
    ('zato.message.xpath', 'xpath'),
    ('zato.message.json-pointer', 'json_pointer'),
    ('zato.notif.', 'notif'),
    ('zato.outgoing.', 'outconn'),
    ('zato.scheduler.job', 'scheduler'),
    ('zato.search.', 'search'),
    ('zato.security.', ''),
]

def make_service_name(prefix):
    escaped = re.sub('[.-]', '_', prefix)
    for module_prefix, name_prefix in SHORTNAME_BY_PREFIX:
        if prefix.startswith(module_prefix) and module_prefix.endswith('.'):
            name = escaped[len(module_prefix):]
            if name_prefix:
                name = '{}_{}'.format(name_prefix, name)
            return name
        elif prefix == module_prefix:
            return name_prefix
    return escaped

class ServiceInfo(object):
    def __init__(self, prefix=None,
                 name=None,
                 object_dependencies=None,
                 service_dependencies=None,
                 export_filter=None):
        assert name or prefix
        #: Short service name as appears in export data.
        self.name = name or prefix
        #: Optional name of the object enumeration/retrieval service.
        self.prefix = prefix
        #: Overwritten by populate_services_from_apispec().
        self.methods = {}
        #: Specifies a list of object dependencies:
        #:      field_name: {"dependent_type": "shortname",
        #:                   "dependent_field": "fieldname",
        #:                   "empty_value": None, or e.g. NO_SEC_DEF_NEEDED}
        self.object_dependencies = object_dependencies or {}
        #: Specifies a list of service dependencies. The field's value contains
        #: the name of a service that must exist.
        #:      field_name: {"only_if_field": "field_name" or None,
        #:                   "only_if_value": "vlaue" or None}
        self.service_dependencies = service_dependencies or {}
        #: List of field/value specifications that should be ignored during
        #: export:
        #:      field_name: value
        self.export_filter = export_filter or {}

    @property
    def is_security(self):
        """If True, indicates the service is source of authentication
        credentials for use in another service."""
        return self.prefix and self.prefix.startswith('zato.security.')

    def get_service_name(self, method):
        return self.methods.get(method, {}).get('name')

    def has_service(self, name):
        return self.get_service_name(name) is not None

    replace_names = {
        'def_id': 'def_name',
    }

    def get_required_keys(self):
        """Return the set of keys required to create a new instance."""
        method_sig = self.methods.get('create')
        if method_sig is None:
            return set()

        required = set(
            self.replace_names.get(f['name'], f['name'])
            for f in method_sig['simple_io']['zato']['input_required']
        )
        if 'sql' in self.name:  # TODO
            required.add('password')
        required.discard('cluster_id')
        return required

    def __repr__(self):
        return '<ServiceInfo for {}>'.format(self.prefix)

#: List of ServiceInfo objects for all supported services. To be replaced by
#: introspection later.
SERVICES = [
    ServiceInfo(
        name='channel_amqp',
        prefix='zato.channel.amqp',
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
        prefix='zato.channel.jms-wmq',
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
        prefix='zato.channel.zmq',
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='def_sec',
        prefix='zato.security',
    ),
    ServiceInfo(
        name='http_soap',
        prefix='zato.http-soap',
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
        export_filter={
            'is_internal': True,
        }
    ),
    ServiceInfo(
        name='notif_sql',
        prefix='zato.notif.sql',
        object_dependencies={
            'def_name': {
                'dependent_type': 'outconn_sql',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_amqp',
        prefix='zato.outgoing.amqp',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_jms_wmq',
        prefix='zato.outgoing.jms-wmq',
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
        name='cloud_aws_s3',
        prefix='zato.cloud.aws.s3',
    ),
    ServiceInfo(
        name='def_cloud_openstack_swift',
        prefix='zato.cloud.openstack.swift',
    ),
    # Added for the exporter.
    ServiceInfo(
        name='outconn_plain_http',
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
        prefix='zato.query.cassandra',
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_cassandra',
                'dependent_field': 'name',
                'empty_value': NO_SEC_DEF_NEEDED,
            },
        },
    ),
    ServiceInfo(
        name='tech_acc',
        prefix='zato.security.tech-account',
    ),
    ServiceInfo(
        name='tls_channel_sec',
        prefix='zato.security.tls.channel',
    ),
    ServiceInfo(
        name='xpath_sec',
        prefix='zato.security.xpath',
    ),
]

SECURITY_SERVICE_NAMES = set(s.name for s in SERVICES if s.is_security)
SERVICE_BY_NAME = {info.name: info for info in SERVICES}
SERVICE_BY_PREFIX = {info.prefix: info for info in SERVICES}

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
            raw = (item_type, sorted(SERVICE_BY_NAME))
            self.results.add_error(raw, ERROR_INVALID_KEY,
                                   "Invalid key '{}', must be one of '{}'",
                                   item_type, sorted(SERVICE_BY_NAME))
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

    def _validate(self, item_type, item, is_sec):
        name = item.get('name')
        item_dict = item.toDict()
        missing = None

        if not name:
            raw = (item_type, item_dict)
            self.results.add_error(raw, ERROR_NAME_MISSING,
                                   "No 'name' key found in item '{}' ({})",
                                   item_dict, item_type)
        else:
            if is_sec:
                # We know we have one of correct types already so we can
                # just look up required attributes.
                sinfo = SERVICE_BY_NAME[item.type]
            else:
                sinfo = SERVICE_BY_NAME[item_type]

            required_keys = sinfo.get_required_keys()
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
                raw = (item_type, name, item_dict, required_keys, missing)
                self.results.add_error(raw, ERROR_KEYS_MISSING,
                                       "Missing {} in '{}', the rest is '{}' ({})",
                                       missing_value, name, item_dict,
                                       item_type)
            else:
                # OK, the keys are there, but do they all have non-None values?
                for req_key in required_keys:
                    if item.get(req_key) is None: # 0 or '' can be correct values
                        raw = (req_key, required_keys, item_dict, item_type)
                        self.results.add_error(raw, ERROR_KEYS_MISSING,
                                               "Key '{}' must not be None in '{}' ({})",
                                               req_key, item_dict, item_type)

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
            if only_if_field and item.get(only_if_field) != only_if_value:
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
                if not self.object_mgr.find(missing_type, missing_name):
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
            raise KeyError('Tried to remove missing %r named %r' % (item_type, name))

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

    def add_warning(self, results, item_type, value_dict, item):
        raw = (item_type, value_dict)
        results.add_warning(raw, WARNING_ALREADY_EXISTS_IN_ODB,
            '{} already exists in ODB {} ({})',
            value_dict.toDict(), item.toDict(), item_type)

    def find_already_existing_odb_objects(self):
        results = Results()
        for item_type, items in self.json.items():
            for item in items:
                name = item.get('name')
                if not name:
                    raw = (item_type, item)
                    results.add_error(raw, ERROR_NAME_MISSING,
                        "{} has no 'name' key ({})",
                        item.toDict(), item_type)

                if item_type == 'http_soap':
                    connection = item.get('connection')
                    transport = item.get('transport')

                    item = find_first(self.object_mgr.objects.http_soap,
                        lambda item: connection == item.connection and
                                     transport == item.transport and
                                     name == item.name)
                    if item is not None:
                        self.add_warning(results, item_type, item, item)
                else:
                    existing = self.object_mgr.find(item_type, name)
                    if existing is not None:
                        self.add_warning(results, item_type, item, existing)

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
        for w in existing_defs + existing_other:
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
        for elem in new_defs + new_other:
            for item_type, attr_list in elem.items():
                for attrs in attr_list:

                    if self.should_skip_item(item_type, attrs, False):
                        continue

                    results = self._import(item_type, attrs, False)
                    if results:
                        return results

        return self.results

    def _swap_service_name(self, required, attrs, first, second):
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
            service_name = sinfo.get_service_name('edit')
        else:
            service_name = sinfo.get_service_name('create')

        # service and service_name are interchangeable
        required = sinfo.get_required_keys()
        self._swap_service_name(required, attrs, 'service', 'service_name')
        self._swap_service_name(required, attrs, 'service_name', 'service')

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

        if def_type in ('channel_amqp', 'channel_jms_wmq', 'outconn_amqp', 'outconn_jms_wmq'):
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

                    request = {'id':attrs.id, 'password1':attrs.password, 'password2':attrs.password}
                    service_name = sinfo.change_password_service()
                    response = self.client.invoke(service_name, request)
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

    def find(self, item_type, name):
        # This probably isn't necessary any more:
        item_type = item_type.replace('-', '_')
        lst = self.objects.get(item_type, ())
        return find_first(lst, lambda item: item.name == name)

    def refresh(self):
        self._refresh_services()
        self._refresh_objects()

    def _refresh_services(self):
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
        service = find_first(self.services.values(),
            lambda s: s.id == item.service_id)
        if service:
            item.service = service.name

    def fix_up_odb_object(self, key, item):
        if key == 'http_soap':
            if item.connection == 'channel':
                self._update_service_name(item)
            if item.security_id:
                sec_def = find_first(self.objects.sec_def,
                    lambda sec_def: sec_def.id == item.security_id)
                if sec_def is not None:
                    item.sec_def = sec_def.name
            else:
                item.sec_def = NO_SEC_DEF_NEEDED
        elif key == 'scheduler':
            self._update_service_name(item)
        elif 'sec_type' in item:
            item['type'] = item['sec_type']
            del item['sec_type']

        return item

    IGNORED_NAMES = (
        'admin.invoke',
        'pubapi',
    )

    def is_ignored_name(self, item):
        name = item.name.lower()
        return 'zato' in name or name in self.IGNORED_NAMES

    def _refresh_objects(self):
        for sinfo in SERVICES:
            # Temporarily preserve function of the old enmasse.
            service_name = sinfo.get_service_name('get-list')
            if service_name is None:
                print("skipping missing get-list:", sinfo.name)
                continue
            if sinfo.name == 'def_sec':
                print("skipping def_sec")
                continue

            print("invoking", service_name, "for", sinfo.name)
            response = self.client.invoke(service_name, {
                'cluster_id': self.client.cluster_id
            })

            if not response.ok:
                self.logger.warning('Could not fetch objects of type {}'.format(sinfo.name))
                continue

            if sinfo.is_security:
                lst = self.objects.setdefault('def_sec', [])
            else:
                lst = self.objects.setdefault(sinfo.name, [])

            for item in map(Bunch, response.data):
                if any(getattr(item, key, None) == value
                       for key, value in sinfo.export_filter.items()):
                    continue
                if self.is_ignored_name(item):
                    continue

                if sinfo.is_security:
                    item.type = sinfo.name

                self.fix_up_odb_object(sinfo.name, item)
                lst.append(item)

class JsonParser(object):
    logger = logging.getLogger('JsonParser')

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.seen_includes = set()

    def _parse_file(self, path, results):
        try:
            with open(path) as fp:
                return anyjson.loads(fp.read())
        except (IOError, TypeError, ValueError) as e:
            raw = (path, e)
            results.add_error(raw, ERROR_INVALID_INPUT, 'Failed to parse {}: {}', path, exc)
            return None

    def _get_include_path(self, include_path):
        curdir = os.path.dirname(self.path)
        joined = os.path.join(curdir, include_path.replace('file://', ''))
        return os.path.abspath(joined)

    def is_include(self, value):
        return isinstance(value, basestring)

    def merge_include(self, item, results):
        abs_path = self.get_include_abspath(self.curdir, item)
        if abs_path in self.seen_includes:
            raw = (abs_path,)
            results.add_error(raw, ERROR_ITEM_INCLUDED_MULTIPLE_TIMES, '{} included multiple times', abs_path)
        self.seen_includes.add(abs_path)
        return self._parse_file(abs_path, results)

    def merge_includes(self, results):
        merged = Bunch()

        for item_type, items in self.json.items():
            merged_items = merged.setdefault(item_type, [])
            for item in items:
                if self.is_include(item):
                    item = self.merge_include(item, reults)
                merged_items.append(item)

        if results.ok:
            self.json = merged
            self.logger.info('Includes merged in successfully')

    def parse(self, merge=True):
        results = Results()
        self.json = bunchify(self._parse_file(self.path, results))
        if results.ok and merge:
            self.merge_includes(results)

        return results

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
        self.curdir = os.path.abspath(self.original_dir)
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

        # Get client and issue a sanity check as quickly as possible
        self.client = get_client_from_server_conf(self.args.path)
        self.object_mgr = ClusterObjectManager(self.client)
        self.client.invoke('zato.ping')
        populate_services_from_apispec(self.client)

        has_import = getattr(args, 'import')
        if args.export_odb or has_import:
            # Checks if connections to ODB/Redis are configured properly
            cc = CheckConfig(self.args)
            cc.show_output = False
            cc.execute(Bunch(path='.'))

            # Get back to the directory we started in so following commands start afresh as well
            os.chdir(self.curdir)

        # Imports and export are mutually excluding
        if has_import and (args.export_local or args.export_odb):
            self.logger.error('Cannot specify import and export options at the same time, stopping now')
            sys.exit(self.SYS_ERROR.CONFLICTING_OPTIONS)

        if args.export_local or has_import:
            parser = JsonParser(os.path.join(self.curdir, self.args.input))
            results = parser.parse()
            if not results.ok:
                self.logger.error('JSON parsing failed')
                self.report_warnings_errors([results])
                sys.exit(self.SYS_ERROR.INVALID_INPUT)
            self.json = parser.json

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
        elif has_import:
            self.report_warnings_errors(self.import_())

        else:
            self.logger.error('At least one of --export-local, --export-odb or --import is required, stopping now')
            sys.exit(self.SYS_ERROR.NO_OPTIONS)

# ################################################################################################################################

    def save_json(self):
        now = datetime.now().isoformat() # Not in UTC, we want to use user's TZ
        name = 'zato-export-{}.json'.format(now.replace(':', '_').replace('.', '_'))

        with open(os.path.join(self.curdir, name), 'w') as f:
            f.write(json.dumps(self.json, indent=1, sort_keys=True))

        self.logger.info('Data exported to {}'.format(f.name))

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
