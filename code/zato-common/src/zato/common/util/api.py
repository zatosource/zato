# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import copy
import errno
import gc
import imp
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
import unicodedata
from ast import literal_eval
from base64 import b64decode
from binascii import hexlify as binascii_hexlify
from contextlib import closing
from datetime import datetime, timedelta
from getpass import getuser as getpass_getuser
from glob import glob
from hashlib import sha256
from inspect import isfunction, ismethod
from itertools import tee
from io import StringIO
from operator import itemgetter
from os import getuid
from os.path import abspath, isabs, join
from pprint import pprint as _pprint, PrettyPrinter
from pwd import getpwuid
from string import Template
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from threading import current_thread
from time import sleep
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# ConfigObj
from configobj import ConfigObj

# dateutil
from dateutil.parser import parse

# gevent
from gevent import sleep as gevent_sleep, spawn, Timeout
from gevent.greenlet import Greenlet
from gevent.hub import Hub

# lxml
from lxml import etree, objectify

# OpenSSL
from OpenSSL import crypto

# portalocker
import portalocker

# psutil
import psutil

# pytz
import pytz

# requests
import requests

# SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import orm

# Texttable
from texttable import Texttable

# validate
from validate import is_boolean, is_integer, VdtTypeError

# Python 2/3 compatibility
from builtins import bytes
from future.moves.itertools import zip_longest
from future.utils import iteritems, raise_
from past.builtins import basestring, cmp, reduce, unicode
from six import PY3
from six.moves.urllib.parse import urlparse
from zato.common.py23_ import ifilter, izip
from zato.common.py23_.spring_ import CAValidatingHTTPSConnection, SSLClientTransport

if PY3:
    from functools import cmp_to_key

# Zato
from zato.common.api import CHANNEL, CLI_ARG_SEP, DATA_FORMAT, engine_def, engine_def_sqlite, KVDB, MISC, \
     SECRET_SHADOW, SIMPLE_IO, TLS, TRACE1, zato_no_op_marker, ZATO_NOT_GIVEN, ZMQ
from zato.common.broker_message import SERVICE
from zato.common.const import SECRETS
from zato.common.crypto.api import CryptoManager
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP, IntervalBasedJob, Job, Server, Service
from zato.common.util.tcp import get_free_port, is_port_taken, wait_for_zato_ping, wait_until_port_free, wait_until_port_taken
from zato.common.util.eval_ import as_bool, as_list
from zato.common.util.file_system import fs_safe_name
from zato.common.xml_ import soap_body_path, soap_body_xpath

# ################################################################################################################################

random.seed()

logger = logging.getLogger(__name__)
logging.addLevelName(TRACE1, "TRACE1")

_repr_template = Template('<$class_name at $mem_loc$attrs>')
_uncamelify_re = re.compile(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))')

_epoch = datetime.utcfromtimestamp(0) # Start of UNIX epoch

cid_symbols = '0123456789abcdefghjkmnpqrstvwxyz'
encode_cid_symbols = {idx: elem for (idx, elem) in enumerate(cid_symbols)}
cid_base = len(cid_symbols)

# ################################################################################################################################

asbool = as_bool
aslist = as_list

# ################################################################################################################################

# Kept here for backward compatibility
get_free_port = get_free_port
is_port_taken = is_port_taken
wait_until_port_free = wait_until_port_free
wait_until_port_taken = wait_until_port_taken

# ################################################################################################################################

# We can initialize it once per process here
_hostname = socket.gethostname()
_fqdn = socket.getfqdn()
_current_host = '{}/{}'.format(_hostname, _fqdn)
_current_user = getpwuid(getuid()).pw_name

# ################################################################################################################################

TLS_KEY_TYPE = {
    crypto.TYPE_DSA: 'DSA',
    crypto.TYPE_RSA: 'RSA'
}

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
    if hasattr(obj, "items"):
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

# Based on
# http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored
class ColorFormatter(logging.Formatter):

    # TODO: Make it all configurable

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"

    COLORS = {
      'WARNING': YELLOW,
      'INFO': WHITE,
      'DEBUG': BLUE,
      'CRITICAL': YELLOW,
      'ERROR': RED,
      'TRACE1': YELLOW
    }

    def __init__(self, fmt):
        self.use_color = True
        super(ColorFormatter, self).__init__(fmt)

    def formatter_msg(self, msg, use_color=True):
        if use_color:
            msg = msg.replace("$RESET", self.RESET_SEQ).replace("$BOLD", self.BOLD_SEQ)
        else:
            msg = msg.replace("$RESET", "").replace("$BOLD", "")
        return msg

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            fore_color = 30 + self.COLORS[levelname]
            levelname_color = self.COLOR_SEQ % fore_color + levelname + self.RESET_SEQ
            record.levelname = levelname_color

        return logging.Formatter.format(self, record)

# ################################################################################################################################

def object_attrs(_object, ignore_double_underscore, to_avoid_list, sort):
    attrs = dir(_object)

    if ignore_double_underscore:
        attrs = ifilter(lambda elem: not elem.startswith("__"), attrs)

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
    attrs = object_attrs(_object, True, "repr_to_avoid", False)
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

def new_cid(bits=96, _random=random.getrandbits):
    """ Returns a new 96-bit correlation identifier. It's *not* safe to use the ID
    for any cryptographical purposes, it's only meant to be used as a conveniently
    formatted ticket attached to each of the requests processed by Zato servers.
    Changed in 2.0: The number is now 28 characters long not 40, like in previous versions.
    Changed in 3.0: The number is now 96 bits rather than 128, 24 characters, with no constant prefix.
    """
    return hex(_random(bits))[2:-1]

# ################################################################################################################################

def get_user_config_name(file_name):
    return file_name.split('.')[0]

# ################################################################################################################################

def _get_config(conf, bunchified, needs_user_config, repo_location=None):
    # type: (bool, bool, str) -> Bunch

    conf = bunchify(conf) if bunchified else conf

    if needs_user_config:
        conf.user_config_items = {}

        user_config = conf.get('user_config')
        if user_config:
            for name, path in user_config.items():
                path = absolutize(path, repo_location)
                if not os.path.exists(path):
                    logger.warn('User config not found `%s`, name:`%s`', path, name)
                else:
                    user_conf = ConfigObj(path)
                    user_conf = bunchify(user_conf) if bunchified else user_conf
                    conf.user_config_items[name] = user_conf

    return conf

# ################################################################################################################################

def get_config(repo_location, config_name, bunchified=True, needs_user_config=True, crypto_manager=None, secrets_conf=None):
    """ Returns the configuration object. Will load additional user-defined config files, if any are available.
    """
    # type: (str, str, bool, bool, object, object) -> Bunch
    conf_location = os.path.join(repo_location, config_name)
    conf = ConfigObj(conf_location , zato_crypto_manager=crypto_manager, zato_secrets_conf=secrets_conf)

    return _get_config(conf, bunchified, needs_user_config, repo_location)

# ################################################################################################################################

def get_config_from_string(data):
    """ A simplified version of get_config which creates a config object from string, skipping any user-defined config files.
    """
    # type: (str) -> Bunch
    buff = StringIO()
    buff.write(data)
    buff.seek(0)

    conf = ConfigObj(buff)
    out = _get_config(conf, True, False)

    buff.close()
    return out

# ################################################################################################################################

def _get_ioc_config(location, config_class):
    """ Instantiates an Inversion of Control container from the given location if the location exists at all.
    """
    stat = os.stat(location)
    if stat.st_size:
        config = config_class(location)
    else:
        config = None

    return config

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

def deployment_info(method, object_, timestamp, fs_location, remote_host='', remote_user=''):
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

def payload_from_request(cid, request, data_format, transport):
    """ Converts a raw request to a payload suitable for usage with SimpleIO.
    """
    if request is not None:
        if data_format == DATA_FORMAT.XML:
            if transport == 'soap':
                if isinstance(request, objectify.ObjectifiedElement):
                    soap = request
                else:
                    soap = objectify.fromstring(request)
                body = soap_body_xpath(soap)
                if not body:
                    raise ZatoException(cid, 'Client did not send `{}` element'.format(soap_body_path))
                payload = get_body_payload(body)
            else:
                if isinstance(request, objectify.ObjectifiedElement):
                    payload = request
                elif len(request) == 0:
                    payload = objectify.fromstring('<empty/>')
                else:
                    payload = objectify.fromstring(request)
        elif data_format in(DATA_FORMAT.DICT, DATA_FORMAT.JSON):
            if not request:
                return ''
            if isinstance(request, basestring) and data_format == DATA_FORMAT.JSON:
                try:
                    request = request.decode('utf8') if isinstance(request, bytes) else request
                    payload = loads(request)
                except ValueError:
                    logger.warn('Could not parse request as JSON:`{}`, e:`{}`'.format(request, format_exc()))
                    raise
            else:
                payload = request
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

def splitext(path):
    """Like os.path.splitext, but take off .tar too"""
    base, ext = os.path.splitext(path)
    if base.lower().endswith('.tar'):
        ext = base[-4:] + ext
        base = base[:-4]
    return base, ext

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

class _DummyLink(object):
    """ A dummy class for staying consistent with pip's API in certain places
    below.
    """
    def __init__(self, url):
        self.url = url

# ################################################################################################################################

class ModuleInfo(object):
    def __init__(self, file_name, module):
        self.file_name = file_name
        self.module = module

# ################################################################################################################################

def import_module_from_path(file_name, base_dir=None):

    if not os.path.isabs(file_name):
        file_name = os.path.normpath(os.path.join(base_dir, file_name))

    if not os.path.exists(file_name):
        raise ValueError("Module could not be imported, path:`{}` doesn't exist".format(file_name))

    _, mod_file = os.path.split(file_name)
    mod_name, _ = os.path.splitext(mod_file)

    # Delete compiled bytecode if it exists so that imp.load_source actually picks up the source module
    for suffix in('c', 'o'):
        path = file_name + suffix
        if os.path.exists(path):
            os.remove(path)

    return ModuleInfo(file_name, imp.load_source(mod_name, file_name))

# ################################################################################################################################

def visit_py_source(dir_name):
    for pattern in('*.py', '*.pyw'):
        glob_path = os.path.join(dir_name, pattern)
        for py_path in sorted(glob(glob_path)):
            yield py_path

# ################################################################################################################################

def _os_remove(path):
    """ A helper function so it's easier to mock it in unittests.
    """
    return os.remove(path)

# ################################################################################################################################

def hot_deploy(parallel_server, file_name, path, delete_path=True, notify=True):
    """ Hot-deploys a package if it looks like a Python module or archive.
    """
    logger.debug('About to hot-deploy `%s`', path)
    now = datetime.utcnow()
    di = dumps(deployment_info('hot-deploy', file_name, now.isoformat(), path))

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
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

# ################################################################################################################################

def translation_name(system1, key1, value1, system2, key2):
    return KVDB.SEPARATOR.join((KVDB.TRANSLATION, system1, key1, value1, system2, key2))

# ################################################################################################################################

def dict_item_name(system, key, value):
    return KVDB.SEPARATOR.join((system, key, value))

# ################################################################################################################################

# From http://docs.python.org/release/2.7/library/itertools.html#recipes
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

# ################################################################################################################################

def from_local_to_utc(dt, tz_name, dayfirst=True):
    """ What is the UTC time given the local time and the timezone's name?
    """
    if not isinstance(dt, datetime):
        dt = parse(dt, dayfirst=dayfirst)

    dt = pytz.timezone(tz_name).localize(dt)
    utc_dt = pytz.utc.normalize(dt.astimezone(pytz.utc))
    return utc_dt

# ################################################################################################################################

def from_utc_to_local(dt, tz_name):
    """ What is the local time in the user-provided time zone name?
    """
    if not isinstance(dt, datetime):
        dt = parse(dt)

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

def clear_locks(kvdb, server_token, kvdb_config=None, decrypt_func=None):
    """ Clears out any KVDB locks held by Zato servers.
    """
    if kvdb_config:
        kvdb.config = kvdb_config

    if decrypt_func:
        kvdb.decrypt_func = decrypt_func

    kvdb.init()

    for name in kvdb.conn.keys('{}*{}*'.format(KVDB.LOCK_PREFIX, server_token)):
        value = kvdb.conn.get(name)
        logger.debug('Deleting lock:[{}], value:[{}]'.format(name, value))
        kvdb.conn.delete(name)

    kvdb.close()

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

def add_startup_jobs(cluster_id, odb, jobs, stats_enabled):
    """ Adds internal jobs to the ODB. Note that it isn't being added
    directly to the scheduler because we want users to be able to fine-tune the job's
    settings.
    """
    with closing(odb.session()) as session:
        now = datetime.utcnow()
        for item in jobs:

            if not stats_enabled and item['name'].startswith('zato.stats'):
                continue

            try:
                extra = item.get('extra', '')
                if isinstance(extra, basestring):
                    extra = extra.encode('utf-8')
                else:
                    if item.get('is_extra_list'):
                        extra = '\n'.join(extra)
                    else:
                        extra = dumps(extra)

                if extra:
                    if not isinstance(extra, bytes):
                        extra = extra.encode('utf8')

                service = session.query(Service).\
                    filter(Service.name==item['service']).\
                    filter(Cluster.id==cluster_id).\
                    one()

                cluster = session.query(Cluster).\
                    filter(Cluster.id==cluster_id).\
                    one()

                existing_one = session.query(Job).\
                    filter(Job.name==item['name']).\
                    filter(Job.cluster_id==cluster_id).\
                    first()

                if existing_one:
                    continue

                job = Job(None, item['name'], True, 'interval_based', now, cluster=cluster, service=service, extra=extra)

                kwargs = {}
                for name in('seconds', 'minutes'):
                    if name in item:
                        kwargs[name] = item[name]

                ib_job = IntervalBasedJob(None, job, **kwargs)

                session.add(job)
                session.add(ib_job)
                session.commit()

            except Exception:
                logger.warn(format_exc())

            else:
                logger.info('Initial job added `%s`', job.name)

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

            logger.warn(log_msg)
            raise ZatoException(cid, msg)

# ################################################################################################################################

# Code below taken from tripod https://github.com/shayne/tripod/blob/master/tripod/sampler.py and slightly modified
# under the terms of LGPL (see LICENSE.txt file for details).

class SafePrettyPrinter(PrettyPrinter, object):
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
                reprs = "failed to format local variables"
            out += [' ' + l for l in reprs.splitlines()]
            out.append('')
    return '\n'.join(out)

# ################################################################################################################################

def get_threads_traceback(pid):
    result = {}
    id_name = dict([(th.ident, th.name) for th in threading.enumerate()])

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

def parse_simple_type(value, convert_bool=True):
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
    try:
        value = literal_eval(value)
    except Exception:
        pass

    # Either parsed out or as it was received
    return value

# ################################################################################################################################

def parse_extra_into_dict(lines, convert_bool=True):
    """ Creates a dictionary out of key=value lines.
    """
    _extra = {}

    if lines:
        extra = ';'.join(lines.splitlines())

        for line in extra.split(';'):
            original_line = line
            if line:

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
    json_config = loads(open(os.path.join(component_dir, 'config', 'repo', 'lb-agent.conf')).read())
    return os.path.abspath(os.path.join(component_dir, json_config['pid_file']))

def store_pidfile(component_dir, pidfile=MISC.PIDFILE):
    open(os.path.join(component_dir, pidfile), 'w').write('{}'.format(os.getpid()))

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

        pem = open(tf.name).read()

        cert_info = crypto.load_certificate(crypto.FILETYPE_PEM, pem)
        cert_info = sorted(cert_info.get_subject().get_components())
        cert_info = '; '.join('{}={}'.format(k, v) for k, v in cert_info)

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
    pem_file = open(pem_file_path, 'w')

    try:
        portalocker.lock(pem_file, portalocker.LOCK_EX)

        pem_file.write(payload)
        pem_file.close()

        os.chmod(pem_file_path, 0o640)

        return pem_file_path

    except portalocker.LockException:
        pass # It's OK, something else is doing the same thing right now

# ################################################################################################################################

def replace_private_key(orig_payload):
    if isinstance(orig_payload, basestring):
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
        super(StaticConfig, self).__init__()
        self.base_dir = base_dir
        #self.read()

    def read_file(self, name):
        f = open(os.path.join(self.base_dir, name))
        value = f.read()
        f.close()

        name = name.split('.')
        _bunch = self

        while name:

            if len(name) == 1:
                break

            elem = name.pop(0)
            _bunch = _bunch.setdefault(elem, Bunch())

        _bunch[name[0]] = value

    def read(self):
        for item in os.listdir(self.base_dir):
            self.read_file(item)

# ################################################################################################################################

def add_scheduler_jobs(api, odb, cluster_id, spawn=True):
    for(id, name, is_active, job_type, start_date, extra, service_name, _,
        _, weeks, days, hours, minutes, seconds, repeats, cron_definition)\
            in odb.get_job_list(cluster_id):

        if is_active:
            job_data = Bunch({'id':id, 'name':name, 'is_active':is_active,
                'job_type':job_type, 'start_date':start_date,
                'extra':extra, 'service':service_name, 'weeks':weeks,
                'days':days, 'hours':hours, 'minutes':minutes,
                'seconds':seconds, 'repeats':repeats,
                'cron_definition':cron_definition})
            api.create_edit('create', job_data, spawn=spawn)

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
    if not value:
        raise ValueError('No definition given `{}`'.format(repr(value)))

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

def get_http_soap_channel(name, service, cluster, security):
    return HTTPSOAP(None, name, True, True, 'channel', 'soap', None, '/zato/soap', None, name, '1.1',
        SIMPLE_IO.FORMAT.XML, service=service, cluster=cluster, security=security)

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

def get_server_client_auth(config, repo_dir, cm, odb_password_encrypted):
    """ Returns credentials to authenticate with against Zato's own /zato/admin/invoke channel.
    """
    session = get_odb_session_from_server_config(config, cm, odb_password_encrypted)

    with closing(session) as session:
        cluster = session.query(Server).\
            filter(Server.token == config.main.token).\
            one().cluster

        channel = session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id == cluster.id).\
            filter(HTTPSOAP.url_path == '/zato/admin/invoke').\
            filter(HTTPSOAP.connection== 'channel').\
            one()

        if channel.security_id:
            security = session.query(HTTPBasicAuth).\
                filter(HTTPBasicAuth.id == channel.security_id).\
                first()

            if security:
                password = security.password.replace(SECRETS.PREFIX, '')
                return (security.username, cm.decrypt(password))

def get_client_from_server_conf(server_dir, require_server=True):

    # Imports go here to avoid circular dependencies
    from zato.client import get_client_from_server_conf as client_get_client_from_server_conf

    # Get the client object ..
    client = client_get_client_from_server_conf(server_dir, get_server_client_auth, get_config)

    # .. make sure the server is available ..
    if require_server:
        wait_for_zato_ping(client.address)

    # .. return the client to our caller now.
    return client

# ################################################################################################################################

def get_repo_dir_from_component_dir(component_dir):
    # type: (str) -> str
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

    names = ('engine', 'username', 'password', 'host', 'port', 'name', 'db_name', 'db_type', 'sqlite_path', 'odb_type',
             'odb_user', 'odb_password', 'odb_host', 'odb_port', 'odb_db_name', 'odb_type', 'ENGINE', 'NAME', 'HOST', 'USER',
             'PASSWORD', 'PORT')

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
        payload = open(path).read()
    except Exception:
        logger.warn(
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
    """ Spawns a new greenlet and wait up to timeout seconds for its response. It is expected that the response never arrives
    because if it does, it means that there were some errors.
    """
    try:
        timeout = kwargs.pop('timeout', 0.2)
        g = spawn(callable, *args, **kwargs)
        gevent_sleep(0)
        g.join(timeout)

        if g.exception:
            type_, value, traceback = g.exc_info
            raise_(type_(value), None, traceback)

    except Timeout:
        pass # Timeout = good = no errors
    else:
        return g

# ################################################################################################################################

def get_logger_for_class(class_):
    return logging.getLogger('{}.{}'.format(inspect.getmodule(class_).__name__, class_.__name__))

# ################################################################################################################################

def get_worker_pids():
    """ Returns all sibling worker PIDs of the server process we are being invoked on, including our own worker too.
    """
    return sorted(elem.pid for elem in psutil.Process(psutil.Process().ppid()).children())

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
    config.username = 'HTTP_{}'.format(config.get('username', '').upper().replace('-', '_'))

# ################################################################################################################################

def get_response_value(response):
    """ Extracts the actual response string from a response object produced by services.
    """
    return (response.payload.getvalue() if hasattr(response.payload, 'getvalue') else response.payload) or ''

# ################################################################################################################################

def get_lb_agent_json_config(repo_dir):
    return loads(open(os.path.join(repo_dir, 'lb-agent.conf')).read())

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
    return issubclass(class_, PubSubHook) and (not class_ is PubSubHook)

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
# The slugify function below is taken from Django:

"""
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

def slugify(value, allow_unicode=False):
    """ Convert to ASCII if 'allow_unicode' is False. Convert spaces to underscores.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
        value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
        return re.sub('[-\s]+', '_', value, flags=re.U)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '_', value)

# ################################################################################################################################

def wait_for_predicate(predicate_func, timeout, interval, *args, **kwargs):
    # type: (object, int, float, *object, **object) -> bool

    is_fulfilled = predicate_func(*args, **kwargs)

    if not is_fulfilled:
        start = datetime.utcnow()
        wait_until = start + timedelta(seconds=timeout)

        while not is_fulfilled:
            gevent_sleep(interval)
            is_fulfilled = predicate_func(*args, **kwargs)
            if datetime.utcnow() > wait_until:
                break

    return is_fulfilled

# ################################################################################################################################

def wait_for_dict_key(_dict, key, timeout=30, interval=0.01):
    # type: (dict, object, int, float) -> bool

    def _predicate_dict_key(*_ignored_args, **_ignored_kwargs):
        return key in _dict

    return wait_for_predicate(_predicate_dict_key, timeout, interval)

# ################################################################################################################################
