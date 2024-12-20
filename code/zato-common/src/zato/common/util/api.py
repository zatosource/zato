# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import copy
import errno
import gc
import importlib.util
import inspect
import linecache
import logging
import os
import random
import re
import signal
import threading
import socket
import sys
from ast import literal_eval
from base64 import b64decode
from binascii import hexlify as binascii_hexlify
from contextlib import closing
from datetime import datetime, timedelta
from getpass import getuser as getpass_getuser
from glob import glob
from hashlib import sha256
from inspect import isfunction, ismethod
from itertools import tee, zip_longest
from io import StringIO
from logging.config import dictConfig
from operator import itemgetter
from os.path import abspath, isabs, join
from pathlib import Path
from pprint import pprint as _pprint, PrettyPrinter
from string import Template
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile, gettempdir
from threading import current_thread
from time import sleep
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import Bunch, bunchify

# ciso8601
try:
    from ciso8601 import parse_datetime # type: ignore
except ImportError:
    from dateutil.parser import parse as parse_datetime

# This is a forward declaration added for the benefit of other callers
parse_datetime = parse_datetime

# datetutil
from dateutil.parser import parse as dt_parse

# gevent
from gevent import sleep as gevent_sleep, spawn, Timeout
from gevent.greenlet import Greenlet
from gevent.hub import Hub

# lxml
from lxml import etree

# OpenSSL
from OpenSSL import crypto

# portalocker
try:
    import portalocker
    has_portalocker = True
except ImportError:
    has_portalocker = False

# pytz
import pytz

# requests
import requests

# SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import orm

# Texttable
from texttable import Texttable

# YAML
import yaml

# Python 2/3 compatibility
from builtins import bytes
from zato.common.ext.future.utils import iteritems, raise_
from zato.common.py23_.past.builtins import basestring, cmp, reduce, unicode
from six import PY3
from six.moves.urllib.parse import urlparse
from zato.common.py23_ import ifilter, izip
from zato.common.py23_.spring_ import CAValidatingHTTPSConnection, SSLClientTransport

if PY3:
    from functools import cmp_to_key

# Zato
from zato.common.api import CHANNEL, CLI_ARG_SEP, DATA_FORMAT, engine_def, engine_def_sqlite, HL7, KVDB, MISC, \
     SECRET_SHADOW, SIMPLE_IO, TLS, TRACE1, zato_no_op_marker, ZATO_NOT_GIVEN, ZMQ
from zato.common.broker_message import SERVICE
from zato.common.const import SECRETS, ServiceConst
from zato.common.crypto.api import CryptoManager
from zato.common.exception import ZatoException
from zato.common.ext.configobj_ import ConfigObj
from zato.common.ext.validate_ import is_boolean, is_integer, VdtTypeError
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP, Server
from zato.common.util.config import enrich_config_from_environment
from zato.common.util.tcp import get_free_port, is_port_taken, wait_for_zato_ping, wait_until_port_free, wait_until_port_taken
from zato.common.util.eval_ import as_bool, as_list
from zato.common.util.file_system import fs_safe_name, fs_safe_now
from zato.common.util.logging_ import ColorFormatter
from zato.common.util.open_ import open_r, open_w
from zato.hl7.parser import get_payload_from_request as hl7_get_payload_from_request

# ################################################################################################################################

if 0:
    from typing import Iterable as iterable
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict, callable_, dictlist, intlist, listnone, strlist, strlistnone, strnone, strset
    iterable = iterable
    strlistnone = strlistnone
    strnone = strnone

# ################################################################################################################################

random.seed()

# ################################################################################################################################

logger = logging.getLogger(__name__)
logging.addLevelName(TRACE1, 'TRACE1')

_repr_template = Template('<$class_name at $mem_loc$attrs>')
_uncamelify_re = re.compile(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))')

_epoch = datetime.utcfromtimestamp(0) # Start of UNIX epoch

cid_symbols = '0123456789abcdefghjkmnpqrstvwxyz'
encode_cid_symbols = {idx: elem for (idx, elem) in enumerate(cid_symbols)}
cid_base = len(cid_symbols)

# ################################################################################################################################

# For pyflakes
ColorFormatter = ColorFormatter
fs_safe_now = fs_safe_now

# ################################################################################################################################

asbool = as_bool
aslist = as_list

# ################################################################################################################################

_data_format_json      = DATA_FORMAT.JSON
_data_format_json_like = DATA_FORMAT.JSON, DATA_FORMAT.DICT
_data_format_hl7_v2    = HL7.Const.Version.v2.id

# ################################################################################################################################

# Kept here for backward compatibility
get_free_port = get_free_port
is_port_taken = is_port_taken
wait_until_port_free = wait_until_port_free
wait_until_port_taken = wait_until_port_taken

# ################################################################################################################################

class ModuleCtx:
    PID_To_Port_Pattern = 'zato-ipc-port-{cluster_name}-{server_name}-{pid}.txt'

# ################################################################################################################################

# We can initialize it once per process here
_hostname = socket.gethostname()
_fqdn = socket.getfqdn()
_current_host = '{}/{}'.format(_hostname, _fqdn)
_current_user = getpass_getuser()

# ################################################################################################################################

TLS_KEY_TYPE = {
    crypto.TYPE_DSA: 'DSA',
    crypto.TYPE_RSA: 'RSA'
}

# ################################################################################################################################

def is_encrypted(data:'str | bytes') -> 'bool':

    # Zato
    from zato.common.const import SECRETS

    if isinstance(data, bytes):
        data = data.decode('utf8')
    elif not isinstance(data, str):
        data = str(data)

    result = data.startswith(SECRETS.Encrypted_Indicator)
    return result

# ################################################################################################################################

def is_method(class_, func=isfunction if PY3 else ismethod):
    return func(class_)

# ################################################################################################################################

def absjoin(base, path):
    """ Turns a path into an absolute path if it's relative to the base location. If the path is already an absolute path,
    it is returned as-is.
    """
    if isabs(path):
        return path

    return abspath(join(base, path))

# ################################################################################################################################

def absolutize(path, base=''):
    """ Turns a relative path into an absolute one or returns it as is if it's already absolute.
    """
    if not isabs(path):
        path = os.path.expanduser(path)

    if not isabs(path):
        path = os.path.normpath(os.path.join(base, path))

    return path

# ################################################################################################################################

def current_host():
    return _current_host

# ################################################################################################################################

def current_user(_getpass_getuser=getpass_getuser):
    return _getpass_getuser()

# ################################################################################################################################

def pprint(obj):
    """ Pretty-print an object into a string buffer.
    """
    # Get dicts' items.
    if hasattr(obj, 'items'):
        obj = sorted(obj.items())

    buf = StringIO()
    _pprint(obj, buf)

    value = buf.getvalue()
    buf.close()

    return value

# ################################################################################################################################

def get_zato_command():
    """ Returns the full path to the 'zato' command' in a buildout environment.
    """
    return os.path.join(os.path.dirname(sys.executable), 'zato')

# ################################################################################################################################

def object_attrs(_object, ignore_double_underscore, to_avoid_list, sort):
    attrs = dir(_object)

    if ignore_double_underscore:
        attrs = ifilter(lambda elem: not elem.startswith('__'), attrs)

    _to_avoid_list = getattr(_object, to_avoid_list, None) # Don't swallow exceptions
    if _to_avoid_list is not None:
        attrs = ifilter(lambda elem: not elem in _to_avoid_list, attrs)

    if sort:
        attrs = sorted(attrs)

    return attrs

# ################################################################################################################################

def make_repr(_object, ignore_double_underscore=True, to_avoid_list='repr_to_avoid', sort=True):
    """ Makes a nice string representation of an object, suitable for logging purposes.
    """
    attrs = object_attrs(_object, ignore_double_underscore, to_avoid_list, sort)
    buff = StringIO()

    for attr in attrs:
        attr_obj = getattr(_object, attr)
        if not callable(attr_obj):
            buff.write('; %s:%r' % (attr, attr_obj))

    out = _repr_template.safe_substitute(
        class_name=_object.__class__.__name__, mem_loc=hex(id(_object)), attrs=buff.getvalue())
    buff.close()

    return out

# ################################################################################################################################

def to_form(_object):
    """ Reads public attributes of an object and creates a dictionary out of it;
    handy for providing initial data to a Django form which isn't backed by
    a true Django model.
    """
    out = {}
    attrs = object_attrs(_object, True, 'repr_to_avoid', False)
    for attr in attrs:
        out[attr] = getattr(_object, attr)

    return out

# ################################################################################################################################

def get_lb_client(is_tls_enabled, lb_host, lb_agent_port, ssl_ca_certs, ssl_key_file, ssl_cert_file, timeout):
    """ Returns an SSL XML-RPC client to the load-balancer.
    """
    from zato.agent.load_balancer.client import LoadBalancerAgentClient, TLSLoadBalancerAgentClient

    http_proto = 'https' if is_tls_enabled else 'http'
    agent_uri = '{}://{}:{}/RPC2'.format(http_proto, lb_host, lb_agent_port)

    if is_tls_enabled:
        if sys.version_info >= (2, 7):
            class Python27CompatTransport(SSLClientTransport):
                def make_connection(self, host):
                    return CAValidatingHTTPSConnection(
                        host, strict=self.strict, ca_certs=self.ca_certs,
                        keyfile=self.keyfile, certfile=self.certfile, cert_reqs=self.cert_reqs,
                        ssl_version=self.ssl_version, timeout=self.timeout)
            transport = Python27CompatTransport
        else:
            transport = None

        return TLSLoadBalancerAgentClient(
            agent_uri, ssl_ca_certs, ssl_key_file, ssl_cert_file, transport=transport, timeout=timeout)
    else:
        return LoadBalancerAgentClient(agent_uri)

# ################################################################################################################################

def tech_account_password(password_clear, salt):
    return sha256(password_clear+ ':' + salt).hexdigest()

# ################################################################################################################################

def new_cid(bytes:'int'=12, needs_padding:'bool'=False, _random:'callable_'=random.getrandbits) -> 'str':
    """ Returns a new 96-bit correlation identifier. It is not safe to use the ID
    for any cryptographical purposes; it is only meant to be used as a conveniently
    formatted ticket attached to each of the requests processed by Zato servers.
    """
    # Note that we need to convert bytes to bits here ..
    out = hex(_random(bytes * 8))[2:]

    # .. and that we optionally ensure it is always 24 characters on output ..
    if needs_padding:
        out = out.ljust(24, 'a')

    # .. return the output to the caller.
    return out

# ################################################################################################################################

def get_user_config_name(name:'str') -> 'str':
    items = name.split(os.sep)
    file_name = items[-1]
    return file_name.split('.')[0]

# ################################################################################################################################

def _get_config(
    *,
    conf, # type: ConfigObj
    config_name, # type: str
    bunchified, # type: bool
    needs_user_config, # type: bool
    repo_location=None # type: strnone
) -> 'Bunch | ConfigObj':

    conf = bunchify(conf) if bunchified else conf # type: ignore

    if needs_user_config:
        conf.user_config_items = {} # type: ignore

        user_config = conf.get('user_config')
        if user_config:
            for name, path in user_config.items(): # type: ignore
                path = absolutize(path, repo_location)
                if not os.path.exists(path):
                    logger.warning('User config not found `%s`, name:`%s`', path, name)
                else:
                    user_conf = ConfigObj(path)
                    user_conf = bunchify(user_conf) if bunchified else user_conf
                    conf.user_config_items[name] = user_conf # type: ignore

    # At this point, we have a Bunch instance that contains
    # the contents of the file. Now, we need to enrich it
    # with values that may be potentially found in the environment.
    if isinstance(conf, Bunch):
        conf = enrich_config_from_environment(config_name, conf) # type: ignore

    return conf # type: ignore

# ################################################################################################################################

def get_config(
    repo_location,   # type: str
    config_name,     # type: str
    bunchified=True, # type: bool
    needs_user_config=True, # type: bool
    crypto_manager=None,    # type: CryptoManager | None
    secrets_conf=None,      # type: any_
    raise_on_error=False,   # type: bool
    log_exception=True,     # type: bool
    require_exists=True,    # type: bool
    conf_location=None      # type: strnone
) -> 'Bunch | ConfigObj':
    """ Returns the configuration object. Will load additional user-defined config files, if any are available.
    """

    # Default output to produce
    result = Bunch()

    try:
        if not conf_location:
            conf_location = os.path.join(repo_location, config_name)
            conf_location = os.path.abspath(conf_location)

        if require_exists:
            if not os.path.exists(conf_location):
                raise Exception(f'Path does not exist -> `{conf_location}`', )

        logger.info('Getting configuration from `%s`', conf_location)
        conf = ConfigObj(conf_location, zato_crypto_manager=crypto_manager, zato_secrets_conf=secrets_conf)
        result = _get_config(
            conf=conf,
            config_name=config_name,
            bunchified=bunchified,
            needs_user_config=needs_user_config,
            repo_location=repo_location
        )
    except Exception:
        if log_exception:
            logger.warning('Error while reading %s from %s; e:`%s`', config_name, repo_location, format_exc())
        if raise_on_error:
            raise
        else:
            return result
    else:
        return result

# ################################################################################################################################

def get_config_from_file(conf_location, config_name):
    return get_config(repo_location=None, config_name=config_name, conf_location=conf_location)

# ################################################################################################################################

def set_up_logging(repo_location:'str') -> 'None':
    with open_r(os.path.join(repo_location, 'logging.conf')) as f:
        dictConfig(yaml.load(f, yaml.FullLoader))

# ################################################################################################################################

def get_config_from_string(data):
    """ A simplified version of get_config which creates a config object from string, skipping any user-defined config files.
    """
    buff = StringIO()
    _ = buff.write(data)
    _ = buff.seek(0)

    conf = ConfigObj(buff)
    out = _get_config(conf=conf, config_name='', bunchified=True, needs_user_config=False)

    buff.close()
    return out

# ################################################################################################################################

def get_current_user():
    return _current_user

# ################################################################################################################################

def service_name_from_impl(impl_name):
    """ Turns a Zato internal service's implementation name into a shorter
    service name
    """
    return impl_name.replace('server.service.internal.', '')

# ################################################################################################################################

def deployment_info(method, object_, timestamp, fs_location, remote_host='', remote_user='', should_deploy_in_place=False):
    """ Returns a JSON document containing information who deployed a service
    onto a server, where from and when it was.
    """
    return {
        'method': method,
        'object': object_,
        'timestamp': timestamp,
        'fs_location':fs_location,
        'remote_host': remote_host or os.environ.get('SSH_CONNECTION', ''),
        'remote_user': remote_user,
        'current_host': current_host(),
        'current_user': get_current_user(),
        'should_deploy_in_place': should_deploy_in_place
    }

# ################################################################################################################################

def get_body_payload(body):
    body_children_count = body[0].countchildren()

    if body_children_count == 0:
        body_payload = None
    elif body_children_count == 1:
        body_payload = body[0].getchildren()[0]
    else:
        body_payload = body[0].getchildren()

    return body_payload

# ################################################################################################################################

def payload_from_request(json_parser, cid, request, data_format, transport, channel_item=None):
    """ Converts a raw request to a payload suitable for usage with SimpleIO.
    """
    if request is not None:

        #
        # JSON and dicts
        #

        if data_format in _data_format_json_like:

            if not request:
                return ''

            if isinstance(request, basestring) and data_format == _data_format_json:
                try:
                    request_bytes = request if isinstance(request, bytes) else request.encode('utf8')
                    try:
                        payload = json_parser.parse(request_bytes)
                    except ValueError:
                        payload = request_bytes
                    if hasattr(payload, 'as_dict'):
                        payload = payload.as_dict()
                except ValueError:
                    logger.warning('Could not parse request as JSON:`%s`, (%s), e:`%s`', request, type(request), format_exc())
                    raise
            else:
                payload = request

        #
        # HL7 v2
        #
        elif data_format == _data_format_hl7_v2:

            payload = hl7_get_payload_from_request(
                request,
                channel_item['data_encoding'],
                channel_item['hl7_version'],
                channel_item['json_path'],
                channel_item['should_parse_on_input'],
                channel_item['should_validate']
            )

        #
        # Other data formats
        #
        else:
            payload = request
    else:
        payload = request

    return payload

# ################################################################################################################################

BZ2_EXTENSIONS = ('.tar.bz2', '.tbz')
XZ_EXTENSIONS = ('.tar.xz', '.txz', '.tlz', '.tar.lz', '.tar.lzma')
ZIP_EXTENSIONS = ('.zip', '.whl')
TAR_EXTENSIONS = ('.tar.gz', '.tgz', '.tar')
ARCHIVE_EXTENSIONS = (ZIP_EXTENSIONS + BZ2_EXTENSIONS + TAR_EXTENSIONS + XZ_EXTENSIONS)

# ################################################################################################################################

def splitext(path):
    """Like os.path.splitext, but take off .tar too"""
    base, ext = os.path.splitext(path)
    if base.lower().endswith('.tar'):
        ext = base[-4:] + ext
        base = base[:-4]
    return base, ext

# ################################################################################################################################

def is_archive_file(name):
    """Return True if `name` is a considered as an archive file."""
    ext = splitext(name)[1].lower()
    if ext in ARCHIVE_EXTENSIONS:
        return True
    return False

# ################################################################################################################################

def is_python_file(name):
    """ Is it a Python file we can import Zato services from?
    """
    for suffix in('py', 'pyw'):
        if name.endswith(suffix):
            return True

# ################################################################################################################################
# ################################################################################################################################

class _DummyLink:
    """ A dummy class for staying consistent with pip's API in certain places
    below.
    """
    def __init__(self, url):
        self.url = url

# ################################################################################################################################
# ################################################################################################################################

class ModuleInfo:
    def __init__(self, file_name, module):
        self.file_name = file_name
        self.module = module

# ################################################################################################################################

def import_module_from_path(file_name, base_dir=None):

    if not os.path.isabs(file_name):
        file_name = os.path.normpath(os.path.join(base_dir, file_name))

    if not os.path.exists(file_name):
        raise ValueError('Module could not be imported, path:`{}` does not exist'.format(file_name))

    _, mod_file = os.path.split(file_name)
    mod_name, _ = os.path.splitext(mod_file)

    # Delete compiled bytecode if it exists so that importlib actually picks up the source module
    for suffix in('c', 'o'):
        path = file_name + suffix
        if os.path.exists(path):
            os.remove(path)

    spec = importlib.util.spec_from_file_location(mod_name, file_name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    return ModuleInfo(file_name, mod)

# ################################################################################################################################

def visit_py_source(
    dir_name,  # type: str
    order_patterns=None # type: strlistnone
) -> 'any_':

    # We enter here if we are not given any patterns on input ..
    if not order_patterns:

        # .. individual Python files will be deployed in this order ..
        order_patterns = [
            'common*',
            'util*',
            'model*',
            '*'
        ]

        # .. now, append the .py extension to each time so that we can find such files below ..
        for idx, elem in enumerate(order_patterns):
            new_item = f'{elem}.py'
            order_patterns[idx] = new_item

    # For storing names of files that we have already deployed,
    # to ensure that there will be no duplicates.
    already_visited:'strset' = set()

    # .. append the default ones, unless they are already there ..
    for default in ['*.py', '*.pyw']:
        if default not in order_patterns:
            order_patterns.append(default)

    for pattern in order_patterns:
        pattern = pattern.strip()
        glob_path = os.path.join(dir_name, pattern)
        for py_path in sorted(glob(glob_path)):
            if py_path in already_visited:
                continue
            else:
                already_visited.add(py_path)
                yield py_path

# ################################################################################################################################

def _os_remove(path):
    """ A helper function so it's easier to mock it in unittests.
    """
    return os.remove(path)

# ################################################################################################################################

def hot_deploy(parallel_server, file_name, path, delete_path=True, notify=True, should_deploy_in_place=False):
    """ Hot-deploys a package if it looks like a Python module or archive.
    """
    logger.debug('About to hot-deploy `%s`', path)
    now = datetime.utcnow()
    di = dumps(deployment_info('hot-deploy', file_name, now.isoformat(), path, should_deploy_in_place=should_deploy_in_place))

    # Insert the package into the DB ..
    package_id = parallel_server.odb.hot_deploy(
        now, di, file_name, open(path, 'rb').read(), parallel_server.id)

    # .. and optionally notify all the servers they're to pick up a delivery
    if notify:
        parallel_server.notify_new_package(package_id)

    if delete_path:
        _os_remove(path)

    return package_id

# ################################################################################################################################

# As taken from http://wiki.python.org/moin/SortingListsOfDictionaries
def multikeysort(items, columns):
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0

    if PY3:
        return sorted(items, key=cmp_to_key(comparer))
    else:
        return sorted(items, cmp=comparer)

# ################################################################################################################################

# From http://docs.python.org/release/2.7/library/itertools.html#recipes
def grouper(n, iterable, fillvalue=None) -> 'any_':
    """ grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

# ################################################################################################################################

def translation_name(system1, key1, value1, system2, key2):
    return KVDB.SEPARATOR.join((KVDB.TRANSLATION, system1, key1, value1, system2, key2))

# ################################################################################################################################

def dict_item_name(system, key, value):
    return KVDB.SEPARATOR.join((system, key, value))

# ################################################################################################################################

# From http://docs.python.org/release/2.7/library/itertools.html#recipes
def pairwise(iterable):
    """ s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

# ################################################################################################################################

def from_local_to_utc(dt, tz_name, dayfirst=True):
    """ What is the UTC time given the local time and the timezone's name?
    """
    if not isinstance(dt, datetime):
        dt = dt_parse(dt, dayfirst=dayfirst)

    dt = pytz.timezone(tz_name).localize(dt)
    utc_dt = pytz.utc.normalize(dt.astimezone(pytz.utc))
    return utc_dt

# ################################################################################################################################

def from_utc_to_local(dt, tz_name):
    """ What is the local time in the user-provided time zone name?
    """
    if not isinstance(dt, datetime):
        dt = dt_parse(dt)

    local_tz = pytz.timezone(tz_name)
    dt = local_tz.normalize(dt.astimezone(local_tz))
    return dt

# ################################################################################################################################

def _utcnow():
    """ See zato.common.util.utcnow for docstring.
    """
    return datetime.utcnow()

# ################################################################################################################################

def utcnow():
    """ A thin wrapper around datetime.utcnow added so that tests can mock it
    out and return their own timestamps at will.
    """
    return _utcnow()

# ################################################################################################################################

def _now(tz):
    """ See zato.common.util.utcnow for docstring.
    """
    return datetime.now(tz)

# ################################################################################################################################

def now(tz=None):
    """ A thin wrapper around datetime.now added so that tests can mock it
    out and return their own timestamps at will.
    """
    return _now(tz)

# ################################################################################################################################

def datetime_to_seconds(dt):
    """ Converts a datetime object to a number of seconds since UNIX epoch.
    """
    return (dt - _epoch).total_seconds()

# ################################################################################################################################

# Inspired by http://stackoverflow.com/a/9283563
def uncamelify(s, separator='-', elem_func=unicode.lower):
    """ Converts a CamelCaseName into a more readable one, e.g.
    will turn ILikeToReadWSDLDocsNotReallyNOPENotMeQ into
    i-like-to-read-wsdl-docs-not-really-nope-not-me-q or a similar one,
    depending on the value of separator and elem_func.
    """
    return separator.join(elem_func(elem) for elem in re.sub(_uncamelify_re, r' \1', s).split())

# ################################################################################################################################

def get_component_name(prefix='parallel'):
    """ Returns a name of the component issuing a given request so it's possible
    to trace which Zato component issued it.
    """
    return '{}/{}/{}/{}'.format(prefix, current_host(), os.getpid(), current_thread().name)

# ################################################################################################################################

def dotted_getattr(o, path):
    return reduce(getattr, path.split('.'), o)

# ################################################################################################################################

def hexlify(item, _hexlify=binascii_hexlify):
    """ Returns a nice hex version of a string given on input.
    """
    item = item if isinstance(item, unicode) else item.decode('utf8')
    return ' '.join(hex(ord(elem)) for elem in item)

# ################################################################################################################################

def validate_input_dict(cid, *validation_info):
    """ Checks that input belongs is one of allowed values.
    """
    for key_name, key, source in validation_info:
        if not source.has(key):
            msg = 'Invalid {}:[{}]'.format(key_name, key)
            log_msg = '{} (attrs: {})'.format(msg, source.attrs)

            logger.warning(log_msg)
            raise ZatoException(cid, msg)

# ################################################################################################################################

# Code below taken from tripod https://github.com/shayne/tripod/blob/master/tripod/sampler.py and slightly modified
# under the terms of LGPL (see LICENSE.txt file for details).

class SafePrettyPrinter(PrettyPrinter):
    def format(self, obj, context, maxlevels, level):
        try:
            return super(SafePrettyPrinter, self).format(
                obj, context, maxlevels, level)
        except Exception:
            return object.__repr__(obj)[:-1] + ' (bad repr)>', True, False

def spformat(obj, depth=None):
    return SafePrettyPrinter(indent=1, width=76, depth=depth).pformat(obj)

def formatvalue(v):
    s = spformat(v, depth=1).replace('\n', '')
    if len(s) > 12500:
        s = object.__repr__(v)[:-1] + ' (really long repr)>'
    return '=' + s

def get_stack(f, with_locals=False):
    limit = getattr(sys, 'tracebacklimit', None)

    frames = []
    n = 0
    while f is not None and (limit is None or n < limit):
        lineno, co = f.f_lineno, f.f_code
        name, filename = co.co_name, co.co_filename
        args = inspect.getargvalues(f)

        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None

        frames.append((filename, lineno, name, line, f.f_locals, args))
        f = f.f_back
        n += 1
    frames.reverse()

    out = []
    for filename, lineno, name, line, localvars, args in frames:
        out.append(' File "%s", line %d, in %s' % (filename, lineno, name))
        if line:
            out.append(' %s' % line.strip())

        if with_locals:
            args = inspect.formatargvalues(formatvalue=formatvalue, *args)
            out.append('\n Arguments: %s%s' % (name, args))

        if with_locals and localvars:
            out.append(' Local variables:\n')
            try:
                reprs = spformat(localvars)
            except Exception:
                reprs = 'failed to format local variables'
            out += [' ' + line for line in reprs.splitlines()]
            out.append('')
    return '\n'.join(out)

# ################################################################################################################################

def get_threads_traceback(pid):
    result = {}
    id_name = {th.ident: th.name for th in threading.enumerate()}

    for thread_id, frame in iteritems(sys._current_frames()):
        key = '{}:{}'.format(pid, id_name.get(thread_id, '(No name)'))
        result[key] = get_stack(frame, True)

    return result

# ################################################################################################################################

def get_greenlets_traceback(pid):
    result = {}
    for item in gc.get_objects():
        if not isinstance(item, (Greenlet, Hub)):
            continue
        if not item:
            continue

        key = '{}:{}'.format(pid, repr(item))
        result[key] = ''.join(get_stack(item.gr_frame, True))

    return result

# ################################################################################################################################

def dump_stacks(*ignored):
    pid = os.getpid()

    table = Texttable()
    table.set_cols_width((30, 90))
    table.set_cols_dtype(['t', 't'])

    rows = [['Proc:Thread/Greenlet', 'Traceback']]

    rows.extend(sorted(iteritems(get_threads_traceback(pid))))
    rows.extend(sorted(iteritems(get_greenlets_traceback(pid))))

    table.add_rows(rows)
    logger.info('\n' + table.draw())

# ################################################################################################################################

def register_diag_handlers():
    """ Registers diagnostic handlers dumping stacks, threads and greenlets on receiving a signal.
    """
    signal.signal(signal.SIGURG, dump_stacks)

# ################################################################################################################################

def parse_simple_type(value:'any_', convert_bool:'bool'=True) -> 'any_':
    if convert_bool:
        try:
            value = is_boolean(value)
        except VdtTypeError:
            # It's cool, not a boolean
            pass

    try:
        value = is_integer(value)
    except VdtTypeError:
        # OK, not an integer
        pass

    # Could be a dict or another simple type then
    value = parse_literal_dict(value)

    # Either parsed out or as it was received
    return value

# ################################################################################################################################

def parse_literal_dict(value:'str') -> 'str | anydict':
    try:
        value = literal_eval(value)
    except Exception:
        pass
    finally:
        return value

# ################################################################################################################################

def parse_extra_into_dict(lines:'str | bytes', convert_bool:'bool'=True):
    """ Creates a dictionary out of key=value lines.
    """
    if isinstance(lines, bytes):
        lines = lines.decode('utf8')

    _extra = {}

    if lines:
        extra = ';'.join(lines.splitlines())

        for line in extra.split(';'):
            original_line = line
            if line:

                line = line.replace(r'\r', '')
                line = line.strip()

                if line.startswith('#'):
                    continue

                line = line.split('=', 1)
                if not len(line) == 2:
                    raise ValueError('Each line must be a single key=value entry, not `{}`'.format(original_line))

                key, value = line
                value = value.strip()
                value = parse_simple_type(value, convert_bool)

                # OK, let's just treat it as string
                _extra[key.strip()] = value

    return _extra

# ################################################################################################################################

# Taken from http://plumberjack.blogspot.cz/2009/09/how-to-treat-logger-like-output-stream.html

class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

# ################################################################################################################################

def validate_xpath(expr):
    """ Evaluates an XPath expression thus confirming it is correct.
    """
    etree.XPath(expr)
    return True

# ################################################################################################################################

def get_haproxy_agent_pidfile(component_dir):
    json_config = loads(
        open(os.path.join(component_dir, 'config', 'repo', 'lb-agent.conf'), encoding='utf8').read()
        )
    return os.path.abspath(os.path.join(component_dir, json_config['pid_file']))

def store_pidfile(component_dir, pidfile=MISC.PIDFILE):
    open(os.path.join(component_dir, pidfile), 'w', encoding='utf8').write('{}'.format(os.getpid()))

# ################################################################################################################################

def get_kvdb_config_for_log(config):
    config = copy.deepcopy(config)
    if config.shadow_password_in_logs:
        config.password = SECRET_SHADOW
    return config

# ################################################################################################################################

def validate_tls_from_payload(payload, is_key=False):

    with NamedTemporaryFile(prefix='zato-tls-') as tf:
        payload = payload.encode('utf8') if isinstance(payload, unicode) else payload
        tf.write(payload)
        tf.flush()

        pem = open(tf.name, encoding='utf8').read()

        cert_info = crypto.load_certificate(crypto.FILETYPE_PEM, pem)
        cert_info = sorted(cert_info.get_subject().get_components())
        cert_info = '; '.join('{}={}'.format(k.decode('utf8'), v.decode('utf8')) for k, v in cert_info)

        if is_key:
            key_info = crypto.load_privatekey(crypto.FILETYPE_PEM, pem)
            key_info = '{}; {} bits'.format(TLS_KEY_TYPE[key_info.type()], key_info.bits())
            return '{}; {}'.format(key_info, cert_info)
        else:
            return cert_info

get_tls_from_payload = validate_tls_from_payload

# ################################################################################################################################

def get_tls_full_path(root_dir, component, info):
    return os.path.join(root_dir, component, fs_safe_name(info) + '.pem')

# ################################################################################################################################

def get_tls_ca_cert_full_path(root_dir, info):
    return get_tls_full_path(root_dir, TLS.DIR_CA_CERTS, info)

# ################################################################################################################################

def get_tls_key_cert_full_path(root_dir, info):
    return get_tls_full_path(root_dir, TLS.DIR_KEYS_CERTS, info)

# ################################################################################################################################

def store_tls(root_dir, payload, is_key=False):

    # Raises exception if it's not really a certificate.
    info = get_tls_from_payload(payload, is_key)

    pem_file_path = get_tls_full_path(root_dir, TLS.DIR_KEYS_CERTS if is_key else TLS.DIR_CA_CERTS, info)
    pem_file = open(pem_file_path, 'w', encoding='utf8')

    if has_portalocker:
        exception_to_catch = portalocker.LockException
    else:
        # Purposefully, catch an exception that will never be raised
        # so that we can actually get the traceback.
        exception_to_catch = ZeroDivisionError

    try:
        if has_portalocker:
            portalocker.lock(pem_file, portalocker.LOCK_EX)

        pem_file.write(payload)
        pem_file.close()

        os.chmod(pem_file_path, 0o640)

        return pem_file_path

    except exception_to_catch:
        pass # It's OK, something else is doing the same thing right now

# ################################################################################################################################

def replace_private_key(orig_payload):
    if isinstance(orig_payload, basestring):
        if isinstance(orig_payload, bytes):
            orig_payload = orig_payload.decode('utf8')
        for item in TLS.BEGIN_END:
            begin = '-----BEGIN {}PRIVATE KEY-----'.format(item)
            if begin in orig_payload:
                end = '-----END {}PRIVATE KEY-----'.format(item)

                begin_last_idx = orig_payload.find(begin) + len(begin) + 1
                end_preceeding_idx = orig_payload.find(end) -1

                return orig_payload[0:begin_last_idx] + SECRET_SHADOW + orig_payload[end_preceeding_idx:]

    # No private key at all in payload
    return orig_payload

# ################################################################################################################################

def delete_tls_material_from_fs(server, info, full_path_func):
    try:
        os.remove(full_path_func(server.tls_dir, info))
    except OSError as e:
        if e.errno == errno.ENOENT:
            # It's ok - some other worker must have deleted it already
            pass
        else:
            raise

# ################################################################################################################################

def ping_solr(config):
    result = urlparse(config.address)
    requests.get('{}://{}{}'.format(result.scheme, result.netloc, config.ping_path))

# ################################################################################################################################

def ping_odoo(conn):
    user_model = conn.get_model('res.users')
    ids = user_model.search([('login', '=', conn.login)])
    user_model.read(ids, ['login'])[0]['login']

# ################################################################################################################################

def ping_sap(conn):
    conn.ping()

# ################################################################################################################################

class StaticConfig(Bunch):
    def __init__(self, base_dir):
        # type: (str) -> None
        super(StaticConfig, self).__init__()
        self.base_dir = base_dir

    def read_file(self, full_path, file_name):
        # type: (str, str) -> None
        f = open(full_path, encoding='utf8')
        file_contents = f.read()
        f.close()

        # Convert to a Path object to prepare to manipulations ..
        full_path = Path(full_path)

        # .. this is the path to the directory containing the file
        # relative to the base directory, e.g. the "config/repo/static" part
        # in "/home/zato/server1/config/repo/static" ..
        relative_dir = Path(full_path.parent).relative_to(self.base_dir)

        # .. now, convert all the components from relative_dir into a nested Bunch of Bunch instances ..
        relative_dir_elems = list(relative_dir.parts)

        # .. start with ourselves ..
        _bunch = self

        # .. if there are no directories leading to the file, simply assign
        # its name to self and return ..
        if not relative_dir_elems:
            _bunch[file_name] = file_contents
            return

        # .. otherwise, if there are directories leading to the file,
        # iterate until they exist and convert their names to Bunch keys ..
        while relative_dir_elems:

            # .. name of a directory = a Bunch key ..
            elem = relative_dir_elems.pop(0)

            # .. attach to the parent Bunch as a new Bunch instance ..
            _bunch = _bunch.setdefault(elem, Bunch())

            # .. this was the last directory to visit so we can now attach the file name and its contents
            # to the Bunch instance representing this directory.
            if not relative_dir_elems:
                _bunch[file_name] = file_contents

    def read_directory(self, root_dir):
        for elem in Path(root_dir).rglob('*'): # type: Path
            full_path = str(elem)
            try:
                if elem.is_file():
                    self.read_file(full_path, elem.name)
            except Exception as e:
                logger.warning('Could not read file `%s`, e:`%s`', full_path, e.args)

# ################################################################################################################################

def get_basic_auth_credentials(auth):

    if not auth:
        return None, None

    prefix = 'Basic '
    if not auth.startswith(prefix):
        return None, None

    _, auth = auth.split(prefix)
    auth = b64decode(auth.strip())

    return auth.split(':', 1)

# ################################################################################################################################

def parse_tls_channel_security_definition(value):
    # type: (bytes) -> iterable(str, str)
    if not value:
        raise ValueError('No definition given `{}`'.format(repr(value)))
    else:
        if isinstance(value, bytes):
            value = value.decode('utf8')

    for line in value.splitlines():
        line = line.strip()

        if not line:
            continue

        if not '=' in line:
            raise ValueError("Line `{}` has no '=' key/value separator".format(line))

        # It's possible we will have multiple '=' symbols.
        sep_index = line.find('=')
        key, value = line[:sep_index], line[sep_index+1:]

        if not key:
            raise ValueError('Key missing in line `{}`'.format(line))

        if not value:
            raise ValueError('Value missing in line `{}`'.format(line))

        yield 'HTTP_X_ZATO_TLS_{}'.format(key.upper()), value

# ################################################################################################################################

def get_http_json_channel(name, service, cluster, security):
    return HTTPSOAP(None, '{}.json'.format(name), True, True, 'channel', 'plain_http', None, '/zato/json/{}'.format(name),
        None, '', None, SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster, security=security)

# ################################################################################################################################

def get_engine(args):
    return sa.create_engine(get_engine_url(args))

# ################################################################################################################################

def get_session(engine):
    session = orm.sessionmaker() # noqa
    session.configure(bind=engine)
    return session()

# ################################################################################################################################

def get_crypto_manager_from_server_config(config, repo_dir):

    priv_key_location = os.path.abspath(os.path.join(repo_dir, config.crypto.priv_key_location))

    cm = CryptoManager(priv_key_location=priv_key_location)
    cm.load_keys()

    return cm

# ################################################################################################################################

def get_odb_session_from_server_config(config, cm, odb_password_encrypted):

    engine_args = Bunch()
    engine_args.odb_type = config.odb.engine
    engine_args.odb_user = config.odb.username
    engine_args.odb_host = config.odb.host
    engine_args.odb_port = config.odb.port
    engine_args.odb_db_name = config.odb.db_name

    if odb_password_encrypted:
        engine_args.odb_password = cm.decrypt(config.odb.password) if config.odb.password else ''
    else:
        engine_args.odb_password = config.odb.password

    return get_session(get_engine(engine_args))

# ################################################################################################################################

def get_odb_session_from_component_dir(component_dir, config_file, CryptoManagerClass):

    repo_dir = get_repo_dir_from_component_dir(component_dir)
    cm = CryptoManagerClass.from_repo_dir(None, repo_dir, None)
    secrets_conf = get_config(repo_dir, 'secrets.conf', needs_user_config=False)
    config = get_config(repo_dir, config_file, crypto_manager=cm, secrets_conf=secrets_conf)

    return get_odb_session_from_server_config(config, None, False)

# ################################################################################################################################

def get_odb_session_from_server_dir(server_dir):

    # Zato
    from zato.common.crypto.api import ServerCryptoManager

    return get_odb_session_from_component_dir(server_dir, 'server.conf', ServerCryptoManager)

# ################################################################################################################################

def get_server_client_auth(
    config,
    repo_dir,
    cm,
    odb_password_encrypted,
    *,
    url_path=None,
) -> 'any_':
    """ Returns credentials to authenticate with against Zato's own inocation channels.
    """
    # This is optional on input
    url_path = url_path or ServiceConst.API_Admin_Invoke_Url_Path

    session = get_odb_session_from_server_config(config, cm, odb_password_encrypted)

    with closing(session) as session:

        # This will exist if config is read from server.conf,
        # otherwise, it means that it is based on scheduler.conf.
        token = config.get('main', {}).get('token')

        # This is server.conf ..
        if token:
            cluster = session.query(Server).\
                filter(Server.token == config.main.token).\
                one().cluster

        # .. this will be scheduler.conf.
        else:
            cluster_id = config.get('cluster', {}).get('id')
            cluster_id = cluster_id or 1
            cluster = session.query(Cluster).\
                filter(Cluster.id == cluster_id).\
                one()

        channel = session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id == cluster.id).\
            filter(HTTPSOAP.url_path == url_path).\
            filter(HTTPSOAP.connection== 'channel').\
            one()

        if channel.security_id:
            security = session.query(HTTPBasicAuth).\
                filter(HTTPBasicAuth.id == channel.security_id).\
                first()

            if security:
                if password:= security.password:
                    password = security.password.replace(SECRETS.PREFIX, '')
                    if password.startswith(SECRETS.Encrypted_Indicator):
                        if cm:
                            password = cm.decrypt(password)
                else:
                    password = ''
                return (security.username, password)

# ################################################################################################################################

def get_client_from_server_conf(
    server_dir,          # type: str
    require_server=True, # type: bool
    stdin_data=None,     # type: strnone
    *,
    url_path=None,       # type: strnone
    initial_wait_time=60 # type: int
) -> 'ZatoClient':

    # Imports go here to avoid circular dependencies
    from zato.client import get_client_from_server_conf as client_get_client_from_server_conf

    # Get the client object ..
    client = client_get_client_from_server_conf(
        server_dir,
        get_server_client_auth,
        get_config,
        stdin_data=stdin_data,
        url_path=url_path
    )

    # .. make sure the server is available ..
    if require_server:
        wait_for_zato_ping(client.address, initial_wait_time)

    # .. return the client to our caller now.
    return client

# ################################################################################################################################

def get_repo_dir_from_component_dir(component_dir:'str') -> 'str':
    return os.path.join(os.path.abspath(os.path.join(component_dir)), 'config', 'repo')

# ################################################################################################################################

django_sa_mappings = {
    'NAME': 'db_name',
    'HOST': 'host',
    'PORT': 'port',
    'USER': 'username',
    'PASSWORD': 'password',
    'odb_type': 'engine',
    'db_type': 'engine',
}

cli_sa_mappings = {
    'odb_db_name': 'db_name',
    'odb_host': 'host',
    'odb_port': 'port',
    'odb_user': 'username',
    'odb_password': 'password',
    'odb_type': 'engine',
}

# ################################################################################################################################

def get_engine_url(args):
    attrs = {}
    is_sqlite = False
    is_django = 'NAME' in args
    has_get = getattr(args, 'get', False)

    odb_type = getattr(args, 'odb_type', None)
    if odb_type:
        is_sqlite = odb_type == 'sqlite'
    else:
        is_sqlite = args.get('engine') == 'sqlite' or args.get('db_type') == 'sqlite'

    names = (
        'engine', 'username', 'password', 'host', 'port', 'name', 'db_name', 'db_type', 'sqlite_path', 'odb_type',
        'odb_user', 'odb_password', 'odb_host', 'odb_port', 'odb_db_name', 'odb_type', 'ENGINE', 'NAME', 'HOST', 'USER',
        'PASSWORD', 'PORT'
    )

    for name in names:
        if has_get:
            attrs[name] = args.get(name, '')
        else:
            attrs[name] = getattr(args, name, '')

    # Re-map Django params into SQLAlchemy params
    if is_django:
        for name in django_sa_mappings:
            value = attrs.get(name, ZATO_NOT_GIVEN)
            if value != ZATO_NOT_GIVEN:
                if not value and (name in 'db_type', 'odb_type'):
                    continue
                attrs[django_sa_mappings[name]] = value

    # Zato CLI to SQLAlchemy
    if not attrs.get('engine'):
        for name in cli_sa_mappings:
            value = attrs.get(name, ZATO_NOT_GIVEN)
            if value != ZATO_NOT_GIVEN:
                attrs[cli_sa_mappings[name]] = value

    # Re-map server ODB params into SQLAlchemy params
    if attrs['engine'] == 'sqlite':
        db_name = attrs.get('db_name')
        sqlite_path = attrs.get('sqlite_path')

        if db_name:
            attrs['sqlite_path'] = db_name

        if sqlite_path:
            attrs['db_name'] = sqlite_path

    return (engine_def_sqlite if is_sqlite else engine_def).format(**attrs)

# ################################################################################################################################

def startup_service_payload_from_path(name, value, repo_location):
    """ Reads payload from a local file. Abstracted out to ease in testing.
    """
    orig_path = value.replace('file://', '')
    if not os.path.isabs(orig_path):
        path = os.path.normpath(os.path.join(repo_location, orig_path))
    else:
        path = orig_path

    try:
        payload = open(path, encoding='utf8').read()
    except Exception:
        logger.warning(
            'Could not open payload path:`%s` `%s`, skipping startup service:`%s`, e:`%s`', orig_path, path, name, format_exc())
    else:
        return payload

# ################################################################################################################################

def invoke_startup_services(source, key, fs_server_config, repo_location, broker_client=None, service_name=None,
    skip_include=True, worker_store=None, is_sso_enabled=False):
    """ Invoked when we are the first worker and we know we have a broker client and all the other config is ready
    so we can publish the request to execute startup services. In the worst case the requests will get back to us but it's
    also possible that other workers are already running. In short, there is no guarantee that any server or worker in particular
    will receive the requests, only that there will be exactly one.
    """
    for name, payload in iteritems(fs_server_config.get(key, {})):

        # Don't invoke SSO services if the feature is not enabled
        if not is_sso_enabled:
            if 'zato.sso' in name:
                continue

        if service_name:

            # We are to skip this service:
            if skip_include:
                if name == service_name:
                    continue

            # We are to include this service only, any other is rejected
            else:
                if name != service_name:
                    continue

        if isinstance(payload, basestring) and payload.startswith('file://'):
            payload = startup_service_payload_from_path(name, payload, repo_location)
            if not payload:
                continue

        cid = new_cid()

        msg = {}
        msg['action'] = SERVICE.PUBLISH.value
        msg['service'] = name
        msg['payload'] = payload
        msg['cid'] = cid
        msg['channel'] = CHANNEL.STARTUP_SERVICE

        if broker_client:
            broker_client.invoke_async(msg)
        else:
            worker_store.on_message_invoke_service(msg, msg['channel'], msg['action'])

# ################################################################################################################################

def timeouting_popen(command, timeout, timeout_msg, rc_non_zero_msg, common_msg=''):
    """ Runs a command in background and returns its return_code, stdout and stderr.
    stdout and stderr will be None if return code = 0
    """
    stdout, stderr = None, None

    # Run the command
    p = Popen(command, stdout=PIPE, stderr=PIPE)

    # Sleep as long as requested and poll for results
    sleep(timeout)
    p.poll()

    if p.returncode is None:
        msg = timeout_msg + common_msg + 'command:[{}]'.format(command)
        raise Exception(msg.format(timeout))
    else:
        if p.returncode != 0:
            stdout, stderr = p.communicate()
            msg = rc_non_zero_msg + common_msg + 'command:[{}], return code:[{}], stdout:[{}], stderr:[{}] '.format(
                command, p.returncode, stdout, stderr)
            raise Exception(msg)

    return p.returncode

# ################################################################################################################################

def spawn_greenlet(callable, *args, **kwargs):
    """ Spawns a new greenlet and waits up to timeout seconds for its response. It is expected that the response never arrives
    because if it does, it means that there were some errors.
    """
    try:
        timeout = kwargs.pop('timeout', 0.2)
        g = spawn(callable, *args, **kwargs)
        gevent_sleep(0)
        g.join(timeout)

        if g.exception:
            type_, value, traceback = g.exc_info
            exc_type = Exception(value, str(g.exception))
            raise_(exc_type, None, traceback)

    except Timeout:
        pass # Timeout = good = no errors
    else:
        return g

# ################################################################################################################################

def get_logger_for_class(class_):
    return logging.getLogger('{}.{}'.format(inspect.getmodule(class_).__name__, class_.__name__))

# ################################################################################################################################

def get_worker_pids_by_parent(parent_pid:'int') -> 'intlist':
    """ Returns all children PIDs of the process whose PID is given on input.
    """
    # psutil
    import psutil

    return sorted(elem.pid for elem in psutil.Process(parent_pid).children())

# ################################################################################################################################

def get_worker_pids():
    """ Returns all sibling worker PIDs of the server process we are being invoked on, including our own worker too.
    """
    # psutil
    import psutil

    # This is our own process ..
    current_process = psutil.Process()

    # .. and this is its parent PID ..
    parent_pid = current_process.ppid()

    # .. now, we can return PIDs of all the workers.
    return get_worker_pids_by_parent(parent_pid)

# ################################################################################################################################

def update_bind_port(data, idx):
    address_info = urlparse(data.address)
    base, port = address_info.netloc.split(':')
    port = int(port) + idx

    data.address = '{}://{}:{}{}'.format(address_info.scheme, base, port, address_info.path)
    data.bind_port = port

# ################################################################################################################################

def start_connectors(worker_store, service_name, data):

    for idx, pid in enumerate(get_worker_pids()):

        if 'socket_method' in data and data.socket_method == ZMQ.METHOD_NAME.BIND:
            update_bind_port(data, idx)

        worker_store.server.invoke(service_name, data, pid=pid, is_async=True, data_format=DATA_FORMAT.DICT)

# ################################################################################################################################

def require_tcp_port(address):
    if not ':' in address:
        raise Exception('No TCP port in {}'.format(address))

    port = address.split(':')[-1]
    if not port.strip():
        raise Exception('No TCP port in {}'.format(address))

    try:
        int(port)
    except ValueError:
        raise Exception('Invalid TCP port in {}'.format(address))

# ################################################################################################################################

def update_apikey_username_to_channel(config):
    config.header = 'HTTP_{}'.format(config.get('header', '').upper().replace('-', '_'))

# ################################################################################################################################

def get_response_value(response):
    """ Extracts the actual response string from a response object produced by services.
    """
    return (response.payload.getvalue() if hasattr(response.payload, 'getvalue') else response.payload) or ''

# ################################################################################################################################

def get_lb_agent_json_config(repo_dir):
    return loads(open(os.path.join(repo_dir, 'lb-agent.conf'), encoding='utf8').read())

# ################################################################################################################################

def parse_cmd_line_options(argv):
    options = argv.split(CLI_ARG_SEP)
    options = '\n'.join(options)
    return parse_extra_into_dict(options)

# ################################################################################################################################

def get_sa_model_columns(model):
    """ Returns all columns (as string) of an input SQLAlchemy model.
    """
    return [elem.key for elem in model.__table__.columns]

# ################################################################################################################################

def is_class_pubsub_hook(class_):
    """ Returns True if input class subclasses PubSubHook.
    """
    # Imported here to avoid circular dependencies
    from zato.server.service import PubSubHook
    return issubclass(class_, PubSubHook) and (class_ is not PubSubHook)

# ################################################################################################################################

def ensure_pubsub_hook_is_valid(self, input, instance, attrs):
    """ An instance hook that validates if an optional pub/sub hook given on input actually subclasses PubSubHook.
    """
    if input.get('hook_service_id'):
        impl_name = self.server.service_store.id_to_impl_name[input.hook_service_id]
        details = self.server.service_store.services[impl_name]
        if not is_class_pubsub_hook(details['service_class']):
            raise ValueError('Service `{}` is not a PubSubHook subclass'.format(details['name']))

# ################################################################################################################################

def is_func_overridden(func):
    """ Returns True if input func was overridden by user in a subclass - used to decide
    whether users implemented a given hook. If there is a special internal marker in input arguments,
    it means that it is an internal function from parent class, not a user-defined one.
    """
    if func and is_method(func):
        func_defaults = func.__defaults__ if PY3 else func.im_func.func_defaults

        # Only internally defined methods will fulfill conditions that they have default arguments
        # and one of them is our no-op marker, hence if we negate it and the result is True,
        # it means it must have been a user-defined method.
        if not (func_defaults and isinstance(func_defaults, tuple) and zato_no_op_marker in func_defaults):
            return True

# ################################################################################################################################

def get_sql_engine_display_name(engine, fs_sql_config):
    display_name = None
    for key, value in fs_sql_config.items():
        if key == engine:
            display_name = value.get('display_name')
            break

    if not display_name:
        raise ValueError('Could not find display name for engine `{}` in config `{}`'.format(
            engine, fs_sql_config))
    else:
        return display_name

# ################################################################################################################################

def pretty_format_float(value):
    return ('%f' % value).rstrip('0').rstrip('.') if value else value

# ################################################################################################################################

def wait_for_predicate(
    predicate_func, # type: callable_
    timeout,        # type: int
    interval,       # type: float
    log_msg_details=None, # type: strnone
    needs_log=True,       # type: bool
    *args,   # type: any_
    **kwargs # type: any_
) -> 'bool':

    # Try out first, perhaps it already fulfilled
    is_fulfilled = bool(predicate_func(*args, **kwargs))

    # Use an explicit loop index for reporting
    loop_idx = 1

    # After that many seconds, we are going to start logging the fact that we are still waiting.
    # In this way, we do not need to log information about all the predicates that finish quickly.
    log_after_seconds = 5

    # Perhaps we can already return and we enter this branch if we cannot ..
    if not is_fulfilled:

        # For later use
        start = datetime.utcnow()

        # The time at which we will start to log details
        log_after  = start + timedelta(seconds=log_after_seconds)

        # We will wait for the predicate until this time
        wait_until = start + timedelta(seconds=timeout)

        # Optionally, we may already have something to log
        if (datetime.utcnow() > log_after) and needs_log and log_msg_details:
            logger.info('Waiting for %s (#%s -> %ss)', log_msg_details, loop_idx, interval)

        # Keep looping until the predicate is fulfilled ..
        while not is_fulfilled:

            # .. sleep for a moment ..
            gevent_sleep(interval)

            # .. for later use ..
            now = datetime.utcnow()

            # .. return if we have run out of time ..
            if now > wait_until:
                break

            # .. optionally, log the current state ..
            if (now > log_after) and needs_log and log_msg_details:
                logger.info('Waiting for %s (#%s -> %ss)', log_msg_details, loop_idx, interval)

            # .. otherwise, check if we have the predicate fulfilled already ..
            is_fulfilled = predicate_func(*args, **kwargs)

            # .. keep looping ..
            loop_idx += 1

    # .. at this point, the predicate is fulfilled or we have run out of time ..
    # .. but, in either case, we can return the result to our caller.
    return is_fulfilled

# ################################################################################################################################

def wait_for_dict_key_by_get_func(
    get_key_func, # type: callable_
    key,          # type: any_
    timeout=9999,# type: int
    interval=0.01 # type: float
) -> 'any_':

    # In this function, we wait for a key through a user-provided get-key function,
    # which may be different than dict.get, e.g. topic_api.get_topic_by_name.

    def _predicate_dict_key(*_ignored_args, **_ignored_kwargs) -> 'any_':
        try:
            value = get_key_func(key)
            return value
        except KeyError:
            return False

    return wait_for_predicate(_predicate_dict_key, timeout, interval, log_msg_details=f'dict key -> `{key}`')

# ################################################################################################################################

def wait_for_dict_key(
    _dict,        # type: anydict
    key,          # type: any_
    timeout=9999, # type: int
    interval=0.01 # type: float
) -> 'any_':

    # In this function, we wait for a key by accessing the dict object directly,
    # using the dict's own .get method.

    def _predicate_dict_key(*_ignored_args, **_ignored_kwargs) -> 'any_':
        value = _dict.get(key)
        return value

    return wait_for_dict_key_by_get_func(_predicate_dict_key, key, timeout, interval)

# ################################################################################################################################

def wait_for_file(full_path:'str', timeout:'int'=9999, interval:'float'=0.01) -> 'any_':

    def _predicate_wait_for_file(*_ignored_args, **_ignored_kwargs) -> 'any_':

        file_exists = os.path.exists(full_path)

        # If the file already exists, wait a little longer to make sure
        # that everything that needs to be saved in there is actually saved.
        if file_exists:
            sleep(0.2)

        return file_exists

    return wait_for_predicate(_predicate_wait_for_file, timeout, interval, log_msg_details=f'path -> `{full_path}`')

# ################################################################################################################################

def hex_sequence_to_bytes(elems):
    # type: (str) -> bytes

    elems = [int(elem.strip(), 16) for elem in elems.split()]
    elems = [chr(elem) for elem in elems]
    elems = [bytes(elem, 'utf8') for elem in elems]

    return b''.join(elems)

# ################################################################################################################################

def tabulate_dictlist(data:'dictlist', skip_keys:'listnone'=None) -> 'str':

    # stdlib
    from copy import deepcopy

    # Tabulate
    from tabulate import tabulate

    # Return early if there is not anything that we can tabulate
    if not data:
        return ''

    # If we have keys to skip, we need re-build the dictionary without these keys first.
    if skip_keys:
        skip_keys = skip_keys if isinstance(skip_keys, list) else [skip_keys]
        _data = []
        for elem in data:
            _elem = deepcopy(elem)
            for key in skip_keys:
                _elem.pop(key, None)
            _data.append(_elem)
        data = _data

    # We assume that all elements will have the same keys
    elem0 = data[0]
    len_keys = len(elem0)

    # We align all the columns to the left hand side
    col_align = ('left',) * len_keys

    return tabulate(data, headers='keys', tablefmt='pretty', colalign=col_align)

# ################################################################################################################################

def needs_suffix(item:'any_') -> 'bool':
    if isinstance(item, int):
        len_item = item
    else:
        len_item = len(item)
    return len_item == 0 or len_item > 1

# ################################################################################################################################

def get_new_tmp_full_path(file_name:'str'='', *, prefix:'str'='', suffix:'str'='', random_suffix:'str'='') -> 'str':

    if prefix:
        prefix = f'{prefix}-'

    if not random_suffix:
        random_suffix = uuid4().hex

    # This may be provided by users on input
    file_name = file_name or 'zato-tmp-' + prefix + random_suffix

    if suffix:
        file_name += f'-{suffix}'

    tmp_dir = gettempdir()
    full_path = os.path.join(tmp_dir, file_name)

    return full_path

# ################################################################################################################################

def get_ipc_pid_port_path(cluster_name:'str', server_name:'str', pid:'int') -> 'str':

    # This is where the file name itself ..
    file_name = ModuleCtx.PID_To_Port_Pattern.format(
        cluster_name=cluster_name,
        server_name=server_name,
        pid=pid,
    )

    # .. make sure the name is safe to use in the file-system ..
    file_name = fs_safe_name(file_name)

    # .. now, we can obtain a full path to a temporary directory ..
    full_path = get_new_tmp_full_path(file_name)

    # .. and return the result to our caller.
    return full_path

# ################################################################################################################################

def save_ipc_pid_port(cluster_name:'str', server_name:'str', pid:'int', port:'int') -> 'None':

    # Make sure we store a string ..
    port = str(port)

    # .. get a path where we can save it ..
    path = get_ipc_pid_port_path(cluster_name, server_name, pid)

    # .. and do save it now.
    with open_w(path) as f:
        _ = f.write(port)
        f.flush()

# ################################################################################################################################

def load_ipc_pid_port(cluster_name:'str', server_name:'str', pid:'int') -> 'int':

    # Get a path to load the port from ..
    path = get_ipc_pid_port_path(cluster_name, server_name, pid)

    # .. wait until the file exists (which may be required when the server starts up) ..
    wait_for_file(path, interval=2.5)

    # .. load it now ..
    with open_r(path) as f:
        data = f.read()
        data = data.strip()
        out = int(data)

    return out

# ################################################################################################################################

def make_list_from_string_list(value:'str', separator:'str') -> 'strlist':

    value = value.split(separator) # type: ignore
    value = [elem.strip() for elem in value if elem] # type: ignore

    return value

# ################################################################################################################################

def validate_python_syntax(data:'str') -> 'None':
    _ = ast.parse(data)

# ################################################################################################################################

class _DemoPyFsLocations:
    pickup_incoming_full_path:'str'
    work_dir_full_path:'str'

def get_demo_py_fs_locations(base_dir:'str') -> '_DemoPyFsLocations':

    # Local variables
    file_name = 'demo.py'

    out = _DemoPyFsLocations()
    out.pickup_incoming_full_path = os.path.join(base_dir, 'pickup', 'incoming', 'services', file_name)
    out.work_dir_full_path = os.path.join(base_dir, 'work', 'hot-deploy', 'current', 'demo.py')

    return out

# ################################################################################################################################
