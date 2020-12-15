# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from collections import namedtuple

# Zato
from zato.cli import ManageCommand

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from logging import Logger

    # Zato
    from zato.client import APIClient

    # For pyflakes
    APIClient = APIClient
    Logger = Logger

# ################################################################################################################################

DEFAULT_COLS_WIDTH = '15,100'
ZATO_NO_SECURITY = 'zato-no-security'

Code = namedtuple('Code', ('symbol', 'desc'))

WARNING_ALREADY_EXISTS_IN_ODB = Code('W01', 'already exists in ODB')
WARNING_MISSING_DEF = Code('W02', 'missing def')
WARNING_MISSING_DEF_INCL_ODB = Code('W04', 'missing def incl. ODB')
ERROR_ITEM_INCLUDED_MULTIPLE_TIMES = Code('E01', 'item incl multiple')
ERROR_INCLUDE_COULD_NOT_BE_PARSED = Code('E03', 'incl parsing error')
ERROR_INVALID_INPUT = Code('E05', 'invalid JSON')
ERROR_UNKNOWN_ELEM = Code('E06', 'unrecognized import element')
ERROR_KEYS_MISSING = Code('E08', 'missing keys')
ERROR_INVALID_SEC_DEF_TYPE = Code('E09', 'invalid sec def type')
ERROR_INVALID_KEY = Code('E10', 'invalid key')
ERROR_SERVICE_NAME_MISSING = Code('E11', 'service name missing')
ERROR_SERVICE_MISSING = Code('E12', 'service missing')
ERROR_MISSING_DEP = Code('E13', 'dependency missing')
ERROR_COULD_NOT_IMPORT_OBJECT = Code('E13', 'could not import object')
ERROR_TYPE_MISSING = Code('E04', 'type missing')

def find_first(it, pred):
    """Given any iterable, return the first element `elem` from it matching `pred(elem)`"""
    for obj in it:
        if pred(obj):
            return obj

def dict_match(haystack, needle):
    """Return True if all the keys from `needle` appear in `haystack` with the same value.
    """

    # Python 2/3 compatibility
    from future.utils import iteritems

    return all(haystack.get(key) == value for key, value in iteritems(needle))


#: List of zato services we explicitly don't support.
IGNORE_PREFIXES = {
    "zato.kvdb.data-dict.dictionary",
    "zato.kvdb.data-dict.translation",
}

def populate_services_from_apispec(client, logger):
    """ Request a list of services from the APISpec service, and merge the results into SERVICES_BY_PREFIX,
    creating new ServiceInfo instances to represent previously unknown services as appropriate.
    """

    # Python 2/3 compatibility
    from future.utils import iteritems

    response = client.invoke('zato.apispec.get-api-spec', {
        'return_internal': True,
        'include': '*',
        'needs_sphinx': False
    })

    if not response.ok:
        logger.error('could not fetch service list')
        return

    by_prefix = {}  # { "zato.apispec": {"get-api-spec": { .. } } }

    for service in response.data['namespaces']['']['services']:
        prefix, _, name = service['name'].rpartition('.')
        methods = by_prefix.setdefault(prefix, {})
        methods[name] = service

    # Services belonging here may not have all the CRUD methods and it is expected that they do not
    allow_incomplete_methods = [
        'zato.security',
        'zato.security.rbac.client-role'
    ]

    for prefix, methods in iteritems(by_prefix):

        # Ignore prefixes lacking 'get-list', 'create' and 'edit' methods.
        if not all(n in methods for n in ('get-list', 'create', 'edit')):

            # RBAC client roles cannot be edited so it is fine that they lack the 'edit' method.
            if prefix not in allow_incomplete_methods:
                continue

        if prefix in IGNORE_PREFIXES:
            continue

        service_info = SERVICE_BY_PREFIX.get(prefix)
        if service_info is None:
            service_info = ServiceInfo(prefix=prefix, name=make_service_name(prefix))
            SERVICE_BY_PREFIX[prefix] = service_info
            SERVICE_BY_NAME[service_info.name] = service_info
            SERVICES.append(service_info)

        service_info.methods = methods

# The common prefix for a set of services is tested against the first element in this list using startswith().
# If it matches, that prefix is replaced by the second element. The prefixes must match exactly if the first element
# does not end in a period.
SHORTNAME_BY_PREFIX = [
    ('zato.pubsub.', 'pubsub'),
    ('zato.definition.', 'def'),
    ('zato.email.', 'email'),
    ('zato.message.namespace', 'def_namespace'),
    ('zato.cloud.aws.s3', 'cloud_aws_s3'),
    ('zato.cloud.openstack.swift', 'def_cloud_openstack_swift'),
    ('zato.message.xpath', 'xpath'),
    ('zato.message.json-pointer', 'json_pointer'),
    ('zato.notif.', 'notif'),
    ('zato.outgoing.', 'outconn'),
    ('zato.scheduler.job', 'scheduler'),
    ('zato.search.', 'search'),
    ('zato.security.tls.channel', 'tls_channel_sec'),
    ('zato.security.xpath', 'xpath_sec'),
    ('zato.security.', ''),
    ('zato.channel.', ''),
]


def make_service_name(prefix):

    # stdlib
    import re

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

def normalize_service_name(item):
    """ Given an item originating from the API or from an import file, if the item contains either the 'service'
    or 'service_name' keys, ensure the other key is set. Either the dict contains neither key, or both keys set
    to the same value."""
    if 'service' in item or 'service_name' in item:
        item.setdefault('service', item.get('service_name'))
        item.setdefault('service_name', item.get('service'))

def test_item(item, cond):
    """ Given a dictionary `cond` containing some conditions to test an item for, return True if those conditions match.
    Currently only supports testing whether a field has a particular value. Returns ``True`` if `cond` is ``None``."""
    if cond is not None:
        only_if_field = cond.get('only_if_field')
        only_if_value = cond.get('only_if_value')
        if not isinstance(only_if_value, (list, tuple)):
            only_if_value = [only_if_value]
        if only_if_field and item.get(only_if_field) not in only_if_value:
            return False
    return True

class ServiceInfo(object):
    def __init__(self, prefix=None, name=None, object_dependencies=None, service_dependencies=None, export_filter=None):
        assert name or prefix

        # Short service name as appears in export data.
        self.name = name or prefix

        # Optional name of the object enumeration/retrieval service.
        self.prefix = prefix

        # Overwritten by populate_services_from_apispec().
        self.methods = {}

        # Specifies a list of object dependencies:
        # field_name: {"dependent_type": "shortname", "dependent_field":
        # "fieldname", "empty_value": None, or e.g. ZATO_NO_SECURITY}
        self.object_dependencies = object_dependencies or {}

        # Specifies a list of service dependencies. The field's value contains
        # the name of a service that must exist.
        # field_name: {"only_if_field": "field_name" or None, "only_if_value": "value" or None}
        self.service_dependencies = service_dependencies or {}

        # List of field/value specifications that should be ignored during export:
        # field_name: value
        self.export_filter = export_filter or {}

# ################################################################################################################################

    @property
    def is_security(self):
        """ If True, indicates the service is source of authentication credentials for use in another service.
        """
        return self.prefix and self.prefix.startswith('zato.security.')

# ################################################################################################################################

    def get_service_name(self, method):
        return self.methods.get(method, {}).get('name')

# ################################################################################################################################

    def get_required_keys(self):
        """ Return the set of keys required to create a new instance.
        """
        method_sig = self.methods.get('create')
        if method_sig is None:
            return set()

        input_required = method_sig['simple_io']['zato']['input_required']
        required = set(f['name'] for f in input_required)
        required.discard('cluster_id')
        return required

# ################################################################################################################################

    def __repr__(self):
        return '<ServiceInfo for {}>'.format(self.prefix)

# ServiceInfo templates for services that have additional semantics not yet described by apispec.
# To be replaced by introspection later.
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
        name='web_socket',
        prefix='zato.channel.web-socket',
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': ZATO_NO_SECURITY,
                'id_field': 'security_id',
            },
        },
        service_dependencies={
            'service': {}
        },
    ),
    ServiceInfo(
        name='pubsub_endpoint',
        prefix='zato.pubsub.endpoint',
        object_dependencies={
            'ws_channel_name': {
                'dependent_type': 'web_socket',
                'dependent_field': 'name',
                'condition': {
                    'only_if_field': 'endpoint_type',
                    'only_if_value': 'wsx',
                },
                'id_field': 'ws_channel_id',
            },
            'sec_def': {
                'dependent_type': 'basic_auth',
                'dependent_field': 'name',
                'empty_value': ZATO_NO_SECURITY,
                'condition': {
                    'only_if_field': 'endpoint_type',
                    'only_if_value': ['soap', 'rest'],
                },
                'id_field': 'security_id',
            }
        },
    ),
    ServiceInfo(
        name='channel_jms_wmq',
        prefix='zato.channel.jms-wmq',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
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
        # Covers outconn_plain_http, outconn_soap, channel_plain_http, channel_soap
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': ZATO_NO_SECURITY,
                'id_field': 'security_id',
            },
        },
        service_dependencies={
            'service_name': {
                'id_field': 'service_id',
                'condition': {
                    'only_if_field': 'connection',
                    'only_if_value': 'channel',
                },
            }
        },
        export_filter={
            'is_internal': True,
        }
    ),
    ServiceInfo(
        name='scheduler',
        service_dependencies={
            'service_name': {
                'id_field': 'service_id',
            }
        },
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
    ),
    ServiceInfo(
        name='query_cassandra',
        prefix='zato.query.cassandra',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_cassandra',
                'dependent_field': 'name',
                'empty_value': ZATO_NO_SECURITY,
            },
        },
    ),
]

SERVICE_BY_NAME = {info.name: info for info in SERVICES}
SERVICE_BY_PREFIX = {info.prefix: info for info in SERVICES}

HTTP_SOAP_KINDS = (
    # item_type             connection      transport
    ('channel_soap',        'channel',      'soap'),
    ('channel_plain_http',  'channel',      'plain_http'),
    ('outconn_soap',        'outgoing',     'soap'),
    ('outconn_plain_http',  'outgoing',     'plain_http')
)
HTTP_SOAP_ITEM_TYPES = set(tup[0] for tup in HTTP_SOAP_KINDS)

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

# ################################################################################################################################

    def __repr__(self):
        return "<{} at {} value_raw:'{}' value:'{}' code:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.value_raw,
            self.value, self.code)

class Results(object):
    def __init__(self, warnings=None, errors=None, service=None):

        # List of Warning instances
        self.warnings = warnings or []

        # List of Error instances
        self.errors = errors or []

        self.service_name = service.get_name() if service else None

# ################################################################################################################################

    def add_error(self, raw, code, msg, *args):
        if args:
            msg = msg.format(*args)
        self.errors.append(Notice(raw, msg, code))

# ################################################################################################################################

    def add_warning(self, raw, code, msg, *args):
        if args:
            msg = msg.format(*args)
        self.warnings.append(Notice(raw, msg, code))

# ################################################################################################################################

    @property
    def ok(self):
        return not (self.warnings or self.errors)

class InputValidator(object):
    def __init__(self, json):
        #: Validation result.
        self.results = Results()
        #: Input JSON to validate.
        self.json = json

# ################################################################################################################################

    def validate(self):
        # type: () -> Results

        # Python 2/3 compatibility
        from future.utils import iteritems

        for item_type, items in iteritems(self.json):
            for item in items:
                self.validate_one(item_type, item)

        return self.results

# ################################################################################################################################

    def validate_one(self, item_type, item):
        if item_type not in SERVICE_BY_NAME:
            raw = (item_type, sorted(SERVICE_BY_NAME))
            self.results.add_error(raw, ERROR_INVALID_KEY, "Invalid key '{}', must be one of '{}'", item_type, sorted(SERVICE_BY_NAME))
            return

        item_dict = dict(item)
        service_info = SERVICE_BY_NAME[item_type]
        required_keys = service_info.get_required_keys()
        # OK, the keys are there, but do they all have non-None values?
        for req_key in required_keys:
            if item.get(req_key) is None: # 0 or '' can be correct values
                raw = (req_key, required_keys, item_dict, item_type)
                self.results.add_error(raw, ERROR_KEYS_MISSING, "Key '{}' must exist in {}: {}", req_key, item_type, item_dict)

class DependencyScanner(object):
    def __init__(self, json, ignore_missing=False):
        self.json = json
        self.ignore_missing = ignore_missing
        #: (item_type, name): [(item_type, name), ..]
        self.missing = {}

# ################################################################################################################################

    def find(self, item_type, fields):
        if item_type == 'def_sec':
            return self.find_sec(fields)
        lst = self.json.get(item_type, ())
        return find_first(lst, lambda item: dict_match(item, fields))

# ################################################################################################################################

    def find_sec(self, fields):
        for service in SERVICES:
            if service.is_security:
                item = self.find(service.name, fields)
                if item is not None:
                    return item

# ################################################################################################################################

    def scan_item(self, item_type, item, results):
        """ Scan the data of a single item for required dependencies, recording any that are missing in self.missing.
        """
        # type: (str, dict, Results)

        # Python 2/3 compatibility
        from future.utils import iteritems

        service_info = SERVICE_BY_NAME[item_type] # type: ServiceInfo

        for dep_key, dep_info in iteritems(service_info.object_dependencies):
            if not test_item(item, dep_info.get('condition')):
                continue

            if item.get('security_id') == 'ZATO_SEC_USE_RBAC':
                continue

            if dep_key not in item:
                results.add_error(
                    (dep_key, dep_info), ERROR_MISSING_DEP, "{} lacks required {} field: {}", item_type, dep_key, item)

            value = item.get(dep_key)
            if value != dep_info.get('empty_value'):

                dep = self.find(dep_info['dependent_type'], {dep_info['dependent_field']: value})
                if dep is None:
                    key = (dep_info['dependent_type'], item[dep_key])
                    names = self.missing.setdefault(key, [])
                    names.append(item.name)

# ################################################################################################################################

    def scan(self):
        # type: () -> Results

        # Python 2/3 compatibility
        from future.utils import iteritems

        results = Results()
        for item_type, items in iteritems(self.json):
            for item in items:
                self.scan_item(item_type, item, results)

        if not self.ignore_missing:
            for (missing_type, missing_name), dep_names in sorted(iteritems(self.missing)):
                existing = sorted(item.name for item in self.json.get(missing_type, []))
                raw = (missing_type, missing_name, dep_names, existing)
                results.add_warning(
                    raw, WARNING_MISSING_DEF, "'{}' is needed by '{}' but was not among '{}'",
                        missing_name, sorted(dep_names), existing)

        return results

class ObjectImporter(object):
    def __init__(self, client, logger, object_mgr, json, ignore_missing, args):
        # type: (APIClient, Logger, ObjectManager, dict, bool, object)

        # Bunch
        from bunch import bunchify

        # Zato client.
        self.client = client

        self.logger = logger

        # Validation result.
        self.results = Results()

        # ObjectManager instance.
        self.object_mgr = object_mgr

        # JSON to import.
        self.json = bunchify(json)

        # Command-line arguments
        self.args = args

        self.ignore_missing = ignore_missing

# ################################################################################################################################

    def validate_service_required(self, item_type, item):

        # Python 2/3 compatibility
        from future.utils import iteritems

        service_info = SERVICE_BY_NAME[item_type]
        item_dict = dict(item)

        for dep_field, dep_info in iteritems(service_info.service_dependencies):
            if not test_item(item, dep_info.get('condition')):
                continue

            service_name = item.get(dep_field)
            raw = (service_name, item_dict, item_type)
            if not service_name:
                self.results.add_error(raw, ERROR_SERVICE_NAME_MISSING, "No {} service key defined type {}: {}", dep_field, item_type, item_dict)
            elif service_name not in self.object_mgr.services:
                self.results.add_error(raw, ERROR_SERVICE_MISSING, "Service '{}' from '{}' missing in ODB ({})", service_name, item_dict, item_type)

# ################################################################################################################################

    def validate_import_data(self):

        # Python 2/3 compatibility
        from future.utils import iteritems

        results = Results()
        dep_scanner = DependencyScanner(self.json, ignore_missing=self.ignore_missing)
        scan_results = dep_scanner.scan()

        if not scan_results.ok:
            return scan_results

        for warning in scan_results.warnings:
            missing_type, missing_name, dep_names, existing = warning.value_raw
            if not self.object_mgr.find(missing_type, {'name': missing_name}):
                raw = (missing_type, missing_name)
                results.add_warning(raw, WARNING_MISSING_DEF_INCL_ODB, "Definition '{}' not found in JSON/ODB ({}), needed by '{}'",
                                    missing_name, missing_type, dep_names)

        for item_type, items in iteritems(self.json):
            for item in items:
                self.validate_service_required(item_type, item)

        return results

# ################################################################################################################################

    def remove_from_import_list(self, item_type, name):
        lst = self.json.get(item_type, [])
        item = find_first(lst, lambda item: item.name == name)
        if item:
            lst.remove(item)
        else:
            raise KeyError('Tried to remove missing %r named %r' % (item_type, name))

# ################################################################################################################################

    def should_skip_item(self, item_type, attrs, is_edit):

        # Plain HTTP channels cannot create JSON-RPC ones
        if item_type == 'http_soap' and attrs.name.startswith('json.rpc.channel'):
            return True

        # Root RBAC role cannot be edited
        elif item_type == 'rbac_role' and attrs.name == 'Root':
            return True

        # RBAC client roles cannot be edited
        elif item_type == 'rbac_client_role' and is_edit:
            return True

# ################################################################################################################################

    def _set_generic_connection_secret(self, name, type_, secret):
        response = self.client.invoke('zato.generic.connection.change-password', {
            'name': name,
            'type_': type_,
            'password1': secret,
            'password2': secret
        })

        if not response.ok:
            raise Exception('Unexpected response; e:{}'.format(response))
        else:
            self.logger.info('Set password for generic connection `%s` (%s)', name, type_)

# ################################################################################################################################

    def _import(self, item_type, attrs, is_edit):

        attrs_dict = dict(attrs)

        # Generic connections cannot import their IDs during edits
        if item_type == 'zato_generic_connection' and is_edit:
            attrs_dict.pop('id', None)

        # RBAC objects cannot refer to other objects by their IDs
        elif item_type == 'rbac_role_permission':
            attrs_dict.pop('id', None)
            attrs_dict.pop('perm_id', None)
            attrs_dict.pop('role_id', None)
            attrs_dict.pop('service_id', None)

        elif item_type == 'rbac_client_role':
            attrs_dict.pop('id', None)
            attrs_dict.pop('role_id', None)

        elif item_type == 'rbac_role':
            attrs_dict.pop('id', None)
            attrs_dict.pop('parent_id', None)

        attrs.cluster_id = self.client.cluster_id

        response = self._import_object(item_type, attrs, is_edit)
        if response.ok:
            if not (item_type == 'rbac_role_permission' and is_edit):
                object_id = response.data['id']
                response = self._maybe_change_password(object_id, item_type, attrs)

        # We quit on first error encountered
        if response and not response.ok:
            raw = (item_type, attrs_dict, response.details)
            self.results.add_error(raw, ERROR_COULD_NOT_IMPORT_OBJECT,
                "Could not import (is_edit {}) '{}' with '{}', response from '{}' was '{}'",
                    is_edit, attrs.name, attrs_dict, item_type, response.details)
            return self.results

        # It's been just imported so we don't want to create it in next steps
        # (this in fact would result in an error as the object already exists).
        if is_edit:
            self.remove_from_import_list(item_type, attrs.name)

        # If this is a generic connection and it has a secret set (e.g. MongoDB password),
        # we need to explicitly set it for the connection we are editing.
        if is_edit and item_type == 'zato_generic_connection' and attrs_dict.get('secret'):
            self._set_generic_connection_secret(attrs_dict['name'], attrs_dict['type_'], attrs_dict['secret'])

        # We'll see how expensive this call is. Seems to be but let's see in practice if it's a burden.
        self.object_mgr.get_objects_by_type(item_type)

# ################################################################################################################################

    def add_warning(self, results, item_type, value_dict, item):
        raw = (item_type, value_dict)
        results.add_warning(
            raw, WARNING_ALREADY_EXISTS_IN_ODB, '{} already exists in ODB {} ({})', dict(value_dict), dict(item), item_type)

# ################################################################################################################################

    def find_already_existing_odb_objects(self):

        # Python 2/3 compatibility
        from future.utils import iteritems

        results = Results()
        for item_type, items in iteritems(self.json):
            for item in items:
                name = item.get('name')
                if not name:
                    raw = (item_type, item)
                    results.add_error(raw, ERROR_KEYS_MISSING, '{} has no `name` key ({})', dict(item), item_type)

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
                    existing = self.object_mgr.find(item_type, {'name': name})
                    if existing is not None:
                        self.add_warning(results, item_type, item, existing)

        return results

# ################################################################################################################################

    def may_be_dependency(self, item_type):
        """ Returns True if input item_type may be possibly a dependency, for instance,
        a security definition may be potentially a dependency of channels or a web socket
        object may be a dependency of pub/sub endpoints.
        """
        return SERVICE_BY_NAME[item_type].is_security or 'def' in item_type or item_type == 'web_socket'

# ################################################################################################################################

    def import_objects(self, already_existing):
        # type: (Results)

        # stdlib
        from time import sleep

        # Python 2/3 compatibility
        from future.utils import iteritems

        rbac_sleep = float(self.args.rbac_sleep)

        existing_defs = []
        existing_rbac_role = []
        existing_rbac_role_permission = []
        existing_rbac_client_role = []
        existing_other = []

        new_defs = []
        new_rbac_role = []
        new_rbac_role_permission = []
        new_rbac_client_role = []
        new_other = []

        #
        # Update already existing objects first, definitions before any object that may depend on them ..
        #

        for w in already_existing.warnings:
            item_type, _ = w.value_raw

            if 'def' in item_type:
                existing = existing_defs
            elif item_type == 'rbac_role':
                existing = existing_rbac_role
            elif item_type == 'rbac_role_permission':
                existing = existing_rbac_role_permission
            elif item_type == 'rbac_client_role':
                existing = existing_rbac_client_role
            else:
                existing = existing_other
            existing.append(w)

        #
        # .. actually invoke the updates now ..
        #
        existing_combined = existing_defs + existing_rbac_role + existing_rbac_role_permission + \
            existing_rbac_client_role + existing_other

        for w in existing_combined:

            item_type, attrs = w.value_raw

            if self.should_skip_item(item_type, attrs, True):
                continue

            results = self._import(item_type, attrs, True)

            if 'rbac' in item_type:
                sleep(rbac_sleep)

            if results:
                return results

        #
        # Create new objects, again, definitions come first ..
        #
        for item_type, items in iteritems(self.json):
            if self.may_be_dependency(item_type):
                if item_type == 'rbac_role':
                    append_to = new_rbac_role
                elif item_type == 'rbac_role_permission':
                    append_to = new_rbac_role_permission
                elif item_type == 'rbac_client_role':
                    append_to = new_rbac_client_role
                else:
                    append_to = new_defs
            else:
                append_to = new_other
            append_to.append({item_type: items})

        #
        # .. actually create the objects now.
        #
        new_combined = new_defs + new_rbac_role + new_rbac_role_permission + new_rbac_client_role + new_other

        for elem in new_combined:
            for item_type, attr_list in iteritems(elem):
                for attrs in attr_list:

                    if self.should_skip_item(item_type, attrs, False):
                        continue

                    results = self._import(item_type, attrs, False)

                    if 'rbac' in item_type:
                        sleep(rbac_sleep)

                    if results:
                        return results

        return self.results

# ################################################################################################################################

    def _swap_service_name(self, required, attrs, first, second):
        if first in required and second in attrs:
            attrs[first] = attrs[second]

# ################################################################################################################################

    def _import_object(self, def_type, item, is_edit):

        # Python 2/3 compatibility
        from future.utils import iteritems

        service_info = SERVICE_BY_NAME[def_type]

        if is_edit:
            service_name = service_info.get_service_name('edit')
        else:
            service_name = service_info.get_service_name('create')

        # service and service_name are interchangeable
        required = service_info.get_required_keys()
        self._swap_service_name(required, item, 'service', 'service_name')
        self._swap_service_name(required, item, 'service_name', 'service')

        # Fetch an item from a cache of ODB object and assign its ID to item so that the Edit service knows what to update.
        if is_edit:
            lookup_config = {'name': item.name}
            if def_type == 'http_soap':
                lookup_config['connection'] = item.connection
                lookup_config['transport'] = item.transport
            odb_item = self.object_mgr.find(def_type, lookup_config)
            item.id = odb_item.id

        for field_name, info in iteritems(service_info.object_dependencies):

            if item.get('security_id') == 'ZATO_SEC_USE_RBAC':
                continue

            if item.get(field_name) != info.get('empty_value') and 'id_field' in info:
                dep_obj = self.object_mgr.find(info['dependent_type'], {
                    info['dependent_field']: item[field_name]
                })

                item[info['id_field']] = dep_obj.id

        self.logger.info('Invoking %s for %s', service_name, service_info.name)

        response = self.client.invoke(service_name, item)
        if response.ok:
            verb = 'Updated' if is_edit else 'Created'
            self.logger.info('%s object `%s` with %s', verb, item.name, service_name)

        return response

# ################################################################################################################################

    def _maybe_change_password(self, object_id, item_type, attrs):

        # stdlib
        from time import sleep

        service_info = SERVICE_BY_NAME[item_type]
        service_name = service_info.get_service_name('change-password')
        if service_name is None or 'password' not in attrs:
            return None

        response = self.client.invoke(service_name, {
            'id': object_id,
            'password1': attrs.password,
            'password2': attrs.password,
        })

        if response.ok:
            self.logger.info("Updated password for '{}' ({})".format(attrs.name, service_name))

            # Wait for a moment before continuing to let AMQP connectors change their passwords.
            # This is needed because we may want to create channels right after the password
            # has been changed and this requires valid credentials, including the very
            # which is being changed here.
            if item_type == 'def_amqp':
                sleep(5)

        return response

class ObjectManager(object):
    def __init__(self, client, logger):
        self.client = client # type: APIClient
        self.logger = logger # type: Logger

# ################################################################################################################################

    def find(self, item_type, fields):

        if item_type == 'def_sec':
            return self.find_sec(fields)

        # This probably isn't necessary any more:
        item_type = item_type.replace('-', '_')
        objects_by_type = self.objects.get(item_type, ())
        return find_first(objects_by_type, lambda item: dict_match(item, fields))

# ################################################################################################################################

    def find_sec(self, fields):
        """ Find any security definition with the given name.
        """
        for service in SERVICES:
            if service.is_security:
                item = self.find(service.name, fields)
                if item is not None:
                    return item

# ################################################################################################################################

    def refresh(self):
        self._refresh_services()
        self._refresh_objects()

# ################################################################################################################################

    def _refresh_services(self):

        # Bunch
        from bunch import Bunch

        response = self.client.invoke('zato.service.get-list', {
            'cluster_id': self.client.cluster_id,
            'name_filter': '*'
        })

        if not response.ok:
            raise Exception('Unexpected response; e:{}'.format(response))

        if response.has_data:
            self.services = {
                service['name']: Bunch(service)
                for service in response.data
            }

# ################################################################################################################################

    def fix_up_odb_object(self, item_type, item):
        """ For each ODB object, ensure fields that specify a dependency have their associated name field updated
        to match the dependent object. Otherwise, ensure the field is set to the corresponding empty value
        (either None or ZATO_NO_SECURITY).
        """

        # Python 2/3 compatibility
        from future.utils import iteritems

        normalize_service_name(item)
        service_info = SERVICE_BY_NAME[item_type]

        if item_type in ('json_rpc', 'http_soap'):

            if item['sec_use_rbac'] is True:
                item['security_id'] = 'ZATO_SEC_USE_RBAC'

            elif item_type == 'json_rpc' and item['security_id'] is None:
                item['security_id'] = 'ZATO_NONE'

        for field_name, info in iteritems(service_info.object_dependencies):

            if 'id_field' not in info:
                continue

            if not test_item(item, info.get('condition')):
                # If the field's condition is false, then just set empty values and stop.
                item[field_name] = info.get('empty_value')
                item[info['id_field']] = None
                continue

            dep_id = item.get(info['id_field'])

            if dep_id is None:
                item[field_name] = info.get('empty_value')
                continue

            dep = self.find(info['dependent_type'], {'id': dep_id})

            if dep_id != 'ZATO_SEC_USE_RBAC':
                if not dep:
                    raise Exception('Dependency not found, name:`{}`, field_name:`{}`, type:`{}`, dep_id:`{}`, dep:`{}`, ' \
                        'item:`{}`'.format(service_info.name, field_name, info['dependent_type'], dep_id, dep, item))
                else:
                    item[field_name] = dep[info['dependent_field']]

            # JSON-RPC channels cannot have empty security definitions on exports
            if item_type == 'http_soap' and item['name'].startswith('json.rpc.channel'):
                if not item['security_id']:
                    item['security_id'] = 'ZATO_NONE'

        return item

# ################################################################################################################################

    IGNORED_NAMES = (
        'admin.invoke',
        'pubapi',
    )

    def is_ignored_name(self, item_type, item):
        if 'name' not in item:
            return False

        name = item.name.lower()

        # Special-case scheduler jobs that can be overridden by users
        if name.startswith('zato.wsx.cleanup'):
            return False

        if item_type != 'rbac_role_permission':
            return 'zato' in name or name in self.IGNORED_NAMES

# ################################################################################################################################

    def delete(self, item_type, item):
        service_info = SERVICE_BY_NAME[item_type]

        service_name = service_info.get_service_name('delete')
        if service_name is None:
            self.logger.error('Prefix {} has no delete service'.format(item_type))
            return

        response = self.client.invoke(service_name, {
            'cluster_id': self.client.cluster_id,
            'id': item.id,
        })
        if response.ok:
            self.logger.info("Deleted {} ID {}".format(item_type, item.id))
        else:
            self.logger.error("Could not delete {} ID {}: {}".format(item_type, item.id, response))

# ################################################################################################################################

    def delete_all(self):

        # Python 2/3 compatibility
        from future.utils import iteritems

        count = 0
        for item_type, items in iteritems(self.objects):
            for item in items:
                self.delete(item_type, item)
                count += 1
        return count

# ################################################################################################################################

    def get_objects_by_type(self, item_type):

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.common.const import SECRETS

        # Python 2/3 compatibility
        from future.utils import iteritems
        from past.builtins import basestring

        service_info = SERVICE_BY_NAME[item_type]

        # Temporarily preserve function of the old enmasse.
        service_name = service_info.get_service_name('get-list')

        if service_name is None:
            self.logger.info('Type `%s` has no `get-list` service (%s)', service_info, item_type)
            return

        self.logger.debug('Invoking %s for %s', service_name, service_info.name)
        response = self.client.invoke(service_name, {
            'cluster_id': self.client.cluster_id
        })

        if not response.ok:
            self.logger.warning('Could not fetch objects of type {}: {}'.format(service_info.name, response.details))
            return

        self.objects[service_info.name] = []

        # Generic connections' GetList includes metadata in responses so we need to dig into actual data
        if '_meta' in response.data:
            data = response.data['response']
        else:
            data = response.data

        for item in map(Bunch, data):

            if any(getattr(item, key, None) == value for key, value in iteritems(service_info.export_filter)):
                continue

            if self.is_ignored_name(item_type, item):
                continue

            # Passwords are always exported in an encrypted form so we need to decrypt them ourselves
            for key, value in iteritems(item):
                if isinstance(value, basestring):
                    if value.startswith(SECRETS.PREFIX):
                        item[key] = None # Enmasse does not export secrets such as passwords or other auth information

            self.objects[service_info.name].append(item)

# ################################################################################################################################

    def _refresh_objects(self):

        # Bunch
        from bunch import Bunch

        # Python 2/3 compatibility
        from future.utils import iteritems

        self.objects = Bunch()
        for service_info in SERVICES:
            self.get_objects_by_type(service_info.name)

        for item_type, items in iteritems(self.objects):
            for item in items:
                self.fix_up_odb_object(item_type, item)

class JsonCodec(object):
    extension = '.json'

# ################################################################################################################################

    def load(self, file_, results):

        # Zato
        from zato.common.json_internal import loads

        return loads(file_.read())

# ################################################################################################################################

    def dump(self, file_, object_):

        # Zato
        from zato.common.json_internal import dumps

        file_.write(dumps(object_, indent=1, sort_keys=True))

class YamlCodec(object):
    extension = '.yml'

# ################################################################################################################################

    def load(self, file_, results):

        # yaml
        import yaml

        return yaml.load(file_, yaml.FullLoader)

# ################################################################################################################################

    def dump(self, file_, object_):

        # pyaml
        import pyaml

        file_.write(pyaml.dump(object_, vspacing=True))

class InputParser(object):
    def __init__(self, path, logger, codec):

        # stdlib
        import os

        self.path = os.path.abspath(path)
        self.logger = logger
        self.codec = codec
        self.seen_includes = set()

# ################################################################################################################################

    def _parse_file(self, path, results):
        try:
            with open(path) as fp:
                return self.codec.load(fp, results)
        except (IOError, TypeError, ValueError) as e:
            raw = (path, e)
            results.add_error(raw, ERROR_INVALID_INPUT, 'Failed to parse {}: {}', path, e)
            return None

# ################################################################################################################################

    def _get_include_path(self, include_path):

        # stdlib
        import os

        curdir = os.path.dirname(self.path)
        joined = os.path.join(curdir, include_path.replace('file://', ''))
        return os.path.abspath(joined)

# ################################################################################################################################

    def is_include(self, value):

        # Python 2/3 compatibility
        from past.builtins import basestring

        return isinstance(value, basestring)

# ################################################################################################################################

    def load_include(self, item_type, relpath, results):
        abs_path = self._get_include_path(relpath)
        if abs_path in self.seen_includes:
            raw = (abs_path,)
            results.add_error(raw, ERROR_ITEM_INCLUDED_MULTIPLE_TIMES, '{} included repeatedly', abs_path)
        self.seen_includes.add(abs_path)

        obj = self._parse_file(abs_path, results)
        if obj is None:
            return  # Failure, error was recorded.

        if not isinstance(obj, dict):
            raw = (abs_path, obj)
            results.add_error(raw, ERROR_INVALID_INPUT,
                "Include {} is incorrect: expected a dictionary containing one item, or a fully formed dump file.")
            return

        if 'name' in obj or 'id' in obj:
            # Classic raw include.
            self.parse_item(item_type, obj, results)
        else:
            # Fully formed dump input file. This allows an include file to be imported directly, or simply included.
            self.parse_items(obj, results)

# ################################################################################################################################

    def parse_def_sec(self, item, results):

        # Bunch
        from bunch import Bunch

        # While reading old enmasse files, expand def_sec entries out to their original service type.
        sec_type = item.pop('type', None)
        if sec_type is None:
            raw = ('def_sec', item)
            results.add_error(raw, ERROR_TYPE_MISSING,
                              "security definition '{}' has no required 'type' key (def_sec)",
                              item)
            return

        service_names = [si.name for si in SERVICES if si.is_security]
        if sec_type not in service_names:
            raw = (sec_type, service_names, item)
            results.add_error(raw, ERROR_INVALID_SEC_DEF_TYPE,
                "Invalid type '{}', must be one of '{}' (def_sec)", sec_type, service_names)
            return

        self.json.setdefault(sec_type, []).append(Bunch(item))

# ################################################################################################################################

    def parse_item(self, item_type, item, results):

        # Bunch
        from bunch import Bunch

        if self.is_include(item):
            self.load_include(item_type, item, results)
        elif item_type == 'def_sec':
            self.parse_def_sec(item, results)
        else:
            self.json.setdefault(item_type, []).append(Bunch(item))

# ################################################################################################################################

    def _maybe_fixup_http_soap(self, original_item_type, item):
        # Preserve old format by merging http-soap subtypes into one.
        for item_type, connection, transport in HTTP_SOAP_KINDS:
            if item_type == original_item_type:
                item['connection'] = connection
                item['transport'] = transport
                return 'http_soap'
        return original_item_type

# ################################################################################################################################

    def parse_items(self, dict_, results):

        # Python 2/3 compatibility
        from future.utils import iteritems

        for item_type, items in iteritems(dict_):
            if item_type not in SERVICE_BY_NAME and item_type not in HTTP_SOAP_ITEM_TYPES:
                raw = (item_type,)
                results.add_error(raw, ERROR_UNKNOWN_ELEM, "Ignoring unknown element type {} in the input.", item_type)
                continue

            for item in items:
                this_item_type = item_type
                if isinstance(item, dict):
                    this_item_type = self._maybe_fixup_http_soap(item_type, item)
                    normalize_service_name(item)
                self.parse_item(this_item_type, item, results)

# ################################################################################################################################

    def parse(self):
        results = Results()
        self.json = {}

        parsed = self._parse_file(self.path, results)
        if not results.ok:
            return results

        self.parse_items(parsed, results)
        return results

class Enmasse(ManageCommand):
    """ Manages server objects en masse.
    """
    opts = [
        {'name':'--server-url', 'help':'URL of the server that enmasse should talk to, provided in host[:port] format. Defaults to server.conf\'s \'gunicorn_bind\''},  # nopep8
        {'name':'--export-local', 'help':'Export local file definitions into one file (can be used with --export-odb)', 'action':'store_true'},
        {'name':'--export-odb', 'help':'Export ODB definitions into one file (can be used with --export-local)', 'action':'store_true'},
        {'name':'--import', 'help':'Import definitions from a local file (excludes --export-*)', 'action':'store_true'},
        {'name':'--clean-odb', 'help':'Delete all ODB definitions before proceeding', 'action':'store_true'},
        {'name':'--dump-format', 'help':'Select output format ("json" or "yaml")', 'choices':('json', 'yaml'), 'default':'yaml'},
        {'name':'--ignore-missing-defs', 'help':'Ignore missing definitions when exporting to file', 'action':'store_true'},
        {'name':'--replace-odb-objects', 'help':'Force replacing objects already existing in ODB during import', 'action':'store_true'},
        {'name':'--input', 'help':'Path to input file with objects to import'},
        {'name':'--rbac-sleep', 'help':'How many seconds to sleep for after creating an RBAC object', 'default':'1'},
        {'name':'--cols-width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH), 'action':'store_true'},
    ]

    CODEC_BY_EXTENSION = {
        'json': JsonCodec,
        'yaml': YamlCodec,
        'yml': YamlCodec,
    }

# ################################################################################################################################

    def load_input(self):

        # stdlib
        import os, sys

        _, _, ext = self.args.input.rpartition('.')
        codec_class = self.CODEC_BY_EXTENSION.get(ext.lower())
        if codec_class is None:
            exts = ', '.join(sorted(self.CODEC_BY_EXTENSION))
            self.logger.error('Unrecognized file extension "{}": must be one of {}'.format(ext.lower(), exts))
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        path = os.path.join(self.curdir, self.args.input)
        parser = InputParser(path, self.logger, codec_class())
        results = parser.parse()
        if not results.ok:
            self.logger.error('JSON parsing failed')
            self.report_warnings_errors([results])
            sys.exit(self.SYS_ERROR.INVALID_INPUT)
        self.json = parser.json

# ################################################################################################################################

    def _on_server(self, args):

        # stdlib
        import os
        from time import sleep

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.cli.check_config import CheckConfig
        from zato.common.util.api import get_client_from_server_conf
        from zato.common.util.tcp import wait_for_zato_ping

        self.args = args
        self.curdir = os.path.abspath(self.original_dir)
        self.json = {}

        #: The output serialization format. Not used for input.
        self.codec = self.CODEC_BY_EXTENSION[args.dump_format]()

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

        # Get the client object ..
        self.client = get_client_from_server_conf(self.component_dir)

        # .. make sure /zato/ping replies which means the server is started
        wait_for_zato_ping(self.client.address, 300)

        # .. just to be on the safe side, optionally wait a bit more
        initial_wait_time = os.environ.get('ZATO_ENMASSE_INITIAL_WAIT_TIME')
        if initial_wait_time:
            initial_wait_time = int(initial_wait_time)
            self.logger.warn('Sleeping for %s s', initial_wait_time)
            sleep(initial_wait_time)

        self.object_mgr = ObjectManager(self.client, self.logger)
        self.client.invoke('zato.ping')
        populate_services_from_apispec(self.client, self.logger)

        has_import = getattr(args, 'import')
        if True not in (args.export_local, args.export_odb, args.clean_odb, has_import):
            self.logger.error('At least one of --clean, --export-local, --export-odb or --import is required, stopping now')
            sys.exit(self.SYS_ERROR.NO_OPTIONS)

        if args.clean_odb:
            self.object_mgr.refresh()
            count = self.object_mgr.delete_all()
            self.logger.info('Deleted {} items'.format(count))

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
            self.load_input()

        # 3)
        if args.export_local and args.export_odb:
            self.report_warnings_errors(self.export_local_odb())
            self.write_output()

        # 1)
        elif args.export_local:
            self.report_warnings_errors(self.export())
            self.write_output()

        # 2)
        elif args.export_odb:
            if self.report_warnings_errors(self.export_odb()):
                self.write_output()

        # 4) a/b
        elif has_import:
            self.report_warnings_errors(self.run_import())

# ################################################################################################################################

    def write_output(self):

        # stdlib
        import os
        import re
        from datetime import datetime

        # Bunch
        from zato.bunch import debunchify

        # Python 2/3 compatibility
        from future.utils import iteritems

        # Make a copy and remove Bunch; pyaml does not like Bunch instances.
        output = debunchify(self.json)

        # Preserve old format by splitting out particular types of http-soap.
        for item in output.pop('http_soap', []):
            for item_type, connection, transport in HTTP_SOAP_KINDS:
                if item['connection'] == connection and item['transport'] == transport:
                    output.setdefault(item_type, []).append(item)

        # Preserve old format by wrapping security services into one key.
        output['def_sec'] = []
        for service_info in SERVICES:
            if service_info.is_security:
                output['def_sec'].extend(
                    dict(item, type=service_info.name)
                    for item in output.pop(service_info.name, [])
                )

        for _, items in iteritems(output):
            for item in items:
                normalize_service_name(item)

            # Sort item lists by ID.
            items.sort(key=lambda item: item['id'])

        now = datetime.now().isoformat() # Not in UTC, we want to use user's TZ
        name = 'zato-export-{}{}'.format(re.sub('[.:]', '_', now), self.codec.extension)
        with open(os.path.join(self.curdir, name), 'w') as fp:
            self.codec.dump(fp, output)
        self.logger.info('Data exported to {}'.format(fp.name))

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

# ################################################################################################################################

    def report_warnings_errors(self, items):

        # stdlib
        import logging

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

        # texttable
        import texttable

        # Python 2/3 compatibility
        from future.utils import iteritems

        cols_width = self.args.cols_width if self.args.cols_width else DEFAULT_COLS_WIDTH
        cols_width = (elem.strip() for elem in cols_width.split(','))
        cols_width = [int(elem) for elem in cols_width]

        table = texttable.Texttable()
        table.set_cols_width(cols_width)

        # Use text ('t') instead of auto so that boolean values don't get converted into ints
        table.set_cols_dtype(['t', 't'])

        rows = [['Key', 'Value']]
        rows.extend(sorted(iteritems(out)))

        table.add_rows(rows)

        return table

# ################################################################################################################################

    def merge_odb_json(self):

        # stdlib
        import copy

        # Python 2/3 compatibility
        from future.utils import iteritems

        results = Results()
        merged = copy.deepcopy(self.object_mgr.objects)

        for json_key, json_elems in iteritems(self.json):
            if 'http' in json_key or 'soap' in json_key:
                odb_key = 'http_soap'
            else:
                odb_key = json_key

            if odb_key not in merged:
                sorted_merged = sorted(merged)
                raw = (json_key, odb_key, sorted_merged)
                results.add_error(raw, ERROR_INVALID_KEY, "JSON key '{}' not one of '{}'", odb_key, sorted_merged)
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
        results = InputValidator(self.json).validate()
        if not results.ok:
            self.logger.error('Required elements missing')
            return [results]

        return []

# ################################################################################################################################

    def export_local_odb(self, needs_local=True):
        self.object_mgr.refresh()
        self.logger.info('ODB objects read')

        results = self.merge_odb_json()
        if not results.ok:
            return [results]
        self.logger.info('ODB objects merged in')

        return self.export()

# ################################################################################################################################

    def export_odb(self):
        return self.export_local_odb(False)

# ################################################################################################################################

    def run_import(self):
        self.object_mgr.refresh()

        importer = ObjectImporter(self.client, self.logger, self.object_mgr, self.json,
            ignore_missing=self.args.ignore_missing_defs, args=self.args)

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

# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Bunch
    from bunch import Bunch

    args = Bunch()
    args.verbose = True
    args.store_log = False
    args.store_config = False
    args.dump_format = 'yaml'
    args.export_local = False
    args.export_odb = False
    args.clean_odb = True
    args.ignore_missing_defs = False
    args['import'] = True

    args.path = sys.argv[1]
    args.input = sys.argv[2]

    enmasse = Enmasse(args)
    enmasse.run(args)
