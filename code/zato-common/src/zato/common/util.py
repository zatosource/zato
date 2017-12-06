# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import copy
import errno
import gc
import imp
import inspect
import json
import linecache
import logging
import os
import re
import signal
import string
import threading
import traceback
import sys
from ast import literal_eval
from contextlib import closing
from cStringIO import StringIO
from datetime import datetime, timedelta
from glob import glob
from hashlib import sha256
from importlib import import_module
from itertools import ifilter, izip, izip_longest, tee
from operator import itemgetter
from os import getuid
from os.path import abspath, isabs, join
from pprint import pprint as _pprint, PrettyPrinter
from pwd import getpwuid
from socket import gethostname, getfqdn
from string import Template
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from threading import current_thread
from time import sleep
from traceback import format_exc
from urlparse import urlparse

# alembic
from alembic import op

# anyjson
from anyjson import dumps, loads

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

# numpy
from numpy.random import bytes as random_bytes, seed as numpy_seed

# OpenSSL
from OpenSSL import crypto

# pip
from pip.download import unpack_file_url

# portalocker
import portalocker

# psutil
import psutil

# pytz
import pytz

# requests
import requests

# Spring Python
from springpython.context import ApplicationContext
from springpython.remoting.http import CAValidatingHTTPSConnection
from springpython.remoting.xmlrpc import SSLClientTransport

# SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError, ProgrammingError

# Texttable
from texttable import Texttable

# validate
from validate import is_boolean, is_integer, VdtTypeError

# Zato
from zato.common import CHANNEL, CLI_ARG_SEP, curdir as common_curdir, DATA_FORMAT, engine_def, engine_def_sqlite, KVDB, MISC, \
     SECRET_SHADOW, SIMPLE_IO, soap_body_path, soap_body_xpath, TLS, TRACE1, ZatoException, ZATO_NOT_GIVEN, ZMQ
from zato.common.broker_message import SERVICE
from zato.common.crypto import CryptoManager
from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, IntervalBasedJob, Job, Server, Service
from zato.common.odb.query import _service as _service

# ################################################################################################################################

logger = logging.getLogger(__name__)
logging.addLevelName(TRACE1, "TRACE1")

_repr_template = Template('<$class_name at $mem_loc$attrs>')
_uncamelify_re = re.compile(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))')

_epoch = datetime.utcfromtimestamp(0) # Start of UNIX epoch

cid_symbols = '0123456789abcdefghjkmnpqrstvwxyz'
encode_cid_symbols = {idx: elem for (idx, elem) in enumerate(cid_symbols)}
cid_base = len(cid_symbols)

# ################################################################################################################################

numpy_seed()

# ################################################################################################################################

TLS_KEY_TYPE = {
    crypto.TYPE_DSA: 'DSA',
    crypto.TYPE_RSA: 'RSA'
}

# ################################################################################################################################

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def aslist(obj, sep=None, strip=True):
    if isinstance(obj, (str, unicode)):
        lst = obj.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(obj, (list, tuple)):
        return obj
    elif obj is None:
        return []
    else:
        return [obj]

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
    """ Turns a relative path to an absolute one or returns it as is if it's already absolute.
    """
    if not isabs(path):
        path = os.path.expanduser(path)

    if not isabs(path):
        path = os.path.normpath(os.path.join(base, path))

    return path

# ################################################################################################################################

def current_host():
    return gethostname() + '/' + getfqdn()

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

def encrypt(data, priv_key, b64=True):
    """ Encrypt data using a public key derived from the private key.
    data - data to be encrypted
    priv_key - private key to use (as a PEM string)
    b64 - should the encrypted data be BASE64-encoded before being returned, defaults to True
    """

    cm = CryptoManager(priv_key=priv_key)
    cm.load_keys()

    return cm.encrypt(data, b64)

# ################################################################################################################################

def decrypt(data, priv_key, b64=True):
    """ Decrypts data using the given private key.
    data - data to be encrypted
    priv_key - private key to use (as a PEM string)
    b64 - should the data be BASE64-decoded before being decrypted, defaults to True
    """

    cm = CryptoManager(priv_key=priv_key)
    cm.load_keys()

    return cm.decrypt(data, b64)

# ################################################################################################################################

def get_executable():
    """ Returns the wrapper buildout uses for executing Zato commands. This has
    all the dependencies added to PYTHONPATH.
    """
    return os.path.join(os.path.dirname(sys.executable), 'py')

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
            buff.write(' ')
            buff.write('\n%s:`%r`' % (attr, attr_obj))

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

def get_lb_client(lb_host, lb_agent_port, ssl_ca_certs, ssl_key_file, ssl_cert_file, timeout):
    """ Returns an SSL XML-RPC client to the load-balancer.
    """
    from zato.agent.load_balancer.client import LoadBalancerAgentClient

    agent_uri = "https://{host}:{port}/RPC2".format(host=lb_host, port=lb_agent_port)

    # See the 'Problems with XML-RPC over SSL' thread for details
    # https://lists.springsource.com/archives/springpython-users/2011-June/000480.html
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

    return LoadBalancerAgentClient(
        agent_uri, ssl_ca_certs, ssl_key_file, ssl_cert_file, transport=transport, timeout=timeout)

# ################################################################################################################################

def tech_account_password(password_clear, salt):
    return sha256(password_clear+ ':' + salt).hexdigest()

# ################################################################################################################################

def new_cid(random_bytes=random_bytes):
    """ Returns a new 96-bit correlation identifier. It's *not* safe to use the ID
    for any cryptographical purposes, it's only meant to be used as a conveniently
    formatted ticket attached to each of the requests processed by Zato servers.
    Changed in 2.0: The number is now 28 characters long not 40, like in previous versions.
    Changed in 3.0: The number is now 96 bits rather than 128, 24 characters, with no constant prefix.
    """
    return random_bytes(12).encode('hex')

# ################################################################################################################################

def get_user_config_name(file_name):
    return file_name.split('.')[0]

# ################################################################################################################################

def get_config(repo_location, config_name, bunchified=True, needs_user_config=True):
    """ Returns the configuration object. Will load additional user-defined config files,
    if any are available at all.
    """
    conf = ConfigObj(os.path.join(repo_location, config_name))
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

def get_app_context(config):
    """ Returns the Zato's Inversion of Control application context.
    """
    ctx_class_path = config['spring']['context_class']
    ctx_class_path = ctx_class_path.split('.')
    mod_name, class_name = '.'.join(ctx_class_path[:-1]), ctx_class_path[-1:][0]
    mod = import_module(mod_name)
    class_ = getattr(mod, class_name)()
    return ApplicationContext(class_)

# ################################################################################################################################

def get_crypto_manager(repo_location, app_context, config, load_keys=True, crypto_manager=None):
    """ Returns a tool for crypto manipulations.
    """
    crypto_manager = crypto_manager or app_context.get_object('crypto_manager')

    priv_key_location = config['crypto']['priv_key_location']
    cert_location = config['crypto']['cert_location']
    ca_certs_location = config['crypto']['ca_certs_location']

    priv_key_location = absjoin(repo_location, priv_key_location)
    cert_location = absjoin(repo_location, cert_location)
    ca_certs_location = absjoin(repo_location, ca_certs_location)

    crypto_manager.priv_key_location = priv_key_location
    crypto_manager.cert_location = cert_location
    crypto_manager.ca_certs_location = ca_certs_location

    if load_keys:
        crypto_manager.load_keys()

    return crypto_manager

# ################################################################################################################################

def get_current_user():
    return getpwuid(getuid()).pw_name

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
        'remote_host': remote_host,
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
                    raise ZatoException(cid, 'Client did not send the [{}] element'.format(soap_body_path))
                payload = get_body_payload(body)
            else:
                if isinstance(request, objectify.ObjectifiedElement):
                    payload = request
                else:
                    payload = objectify.fromstring(request)
        elif data_format in(DATA_FORMAT.DICT, DATA_FORMAT.JSON):
            if not request:
                return ''
            if isinstance(request, basestring) and data_format == DATA_FORMAT.JSON:
                payload = loads(request)
            else:
                payload = request
        else:
            payload = request
    else:
        payload = request

    return payload

# ################################################################################################################################

def is_python_file(name):
    """ Is it a Python file we can import Zato services from?
    """
    for suffix in('py', 'pyw'):
        if name.endswith(suffix):
            return True

# ################################################################################################################################

def fs_safe_name(value):
    return re.sub('[{}]'.format(string.punctuation + string.whitespace), '_', value)

# ################################################################################################################################

def fs_safe_now():
    """ Returns a UTC timestamp with any characters unsafe for filesystem names
    removed.
    """
    return fs_safe_name(str(datetime.utcnow()))

# ################################################################################################################################

class _DummyLink(object):
    """ A dummy class for staying consistent with pip's API in certain places
    below.
    """
    def __init__(self, url):
        self.url = url

# ################################################################################################################################

def decompress(archive, dir_name):
    """ Decompresses an archive into a directory, the directory must already exist.
    """
    unpack_file_url(_DummyLink('file:' + archive), dir_name)

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
    return sorted(items, cmp=comparer)

# ################################################################################################################################

# From http://docs.python.org/release/2.7/library/itertools.html#recipes
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

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

def get_service_by_name(session, cluster_id, name):
    logger.debug('Looking for name:`%s` in cluster_id:`%s`'.format(name, cluster_id))
    return _service(session, cluster_id).\
           filter(Service.name==name).\
           one()

# ################################################################################################################################

def add_startup_jobs(cluster_id, odb, jobs, stats_enabled):
    """ Adds internal jobs to the ODB. Note that it isn't being added
    directly to the scheduler because we want users to be able to fine-tune the job's
    settings.
    """
    with closing(odb.session()) as session:
        for item in jobs:

            if not stats_enabled and item['name'].startswith('zato.stats'):
                continue

            try:
                service_id = get_service_by_name(session, cluster_id, item['service'])[0]

                now = datetime.utcnow()

                job = Job(None, item['name'], True, 'interval_based', now, item.get('extra', '').encode('utf-8'),
                          cluster_id=cluster_id, service_id=service_id)

                kwargs = {}
                for name in('seconds', 'minutes'):
                    if name in item:
                        kwargs[name] = item[name]

                ib_job = IntervalBasedJob(None, job, **kwargs)

                session.add(job)
                session.add(ib_job)
                session.commit()
            except(IntegrityError, ProgrammingError), e:
                session.rollback()
                logger.debug('Caught an expected error, carrying on anyway, e:`%s`', format_exc(e).decode('utf-8'))

# ################################################################################################################################

def hexlify(item):
    """ Returns a nice hex version of a string given on input.
    """
    return ' '.join([elem1+elem2 for (elem1, elem2) in grouper(2, item.encode('hex'))])

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

    for thread_id, frame in sys._current_frames().items():
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

    rows.extend(sorted(get_threads_traceback(pid).items()))
    rows.extend(sorted(get_greenlets_traceback(pid).items()))

    table.add_rows(rows)
    logger.info('\n' + table.draw())

# ################################################################################################################################

# Taken from https://stackoverflow.com/a/16589622
def get_full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. if an exception is present
        del stack[-1]    # remove call of full_stack, the printed exception will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))

    if exc is not None:
        stackstr += '  ' + traceback.format_exc().decode('utf-8').lstrip(trc)

    return stackstr

# ################################################################################################################################

def register_diag_handlers():
    """ Registers diagnostic handlers dumping stacks, threads and greenlets on receiving a signal.
    """
    signal.signal(signal.SIGURG, dump_stacks)

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
                line = line.split('=')
                if not len(line) == 2:
                    raise ValueError('Each line must be a single key=value entry, not `{}`'.format(original_line))

                key, value = line
                value = value.strip()

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

def get_free_port(start=30000):
    port = start
    while is_port_taken(port):
        port += 1
    return port

# ################################################################################################################################

# Taken from http://grodola.blogspot.com/2014/04/reimplementing-netstat-in-cpython.html
def is_port_taken(port):
    for conn in psutil.net_connections(kind='tcp'):
        if conn.laddr[1] == port and conn.status == psutil.CONN_LISTEN:
            return True
    return False

# ################################################################################################################################

def _is_port_ready(port, needs_taken):
    taken = is_port_taken(port)
    return taken if needs_taken else not taken

def _wait_for_port(port, timeout, interval, needs_taken):
    port_ready = _is_port_ready(port, needs_taken)

    if not port_ready:
        start = datetime.utcnow()
        wait_until = start + timedelta(seconds=timeout)

        while not port_ready:
            sleep(interval)
            port_ready = _is_port_ready(port, needs_taken)
            if datetime.utcnow() > wait_until:
                break

    return port_ready

# ################################################################################################################################

def wait_until_port_taken(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes taken, i.e. a process binds to a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, True)

# ################################################################################################################################

def wait_until_port_free(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes free, i.e. a process releases a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, False)

# ################################################################################################################################

def get_haproxy_agent_pidfile(component_dir):
    json_config = json.loads(open(os.path.join(component_dir, 'config', 'repo', 'lb-agent.conf')).read())
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

def has_redis_sentinels(config):
    return asbool(config.get('use_redis_sentinels', False))

# ################################################################################################################################

def alter_column_nullable_false(table_name, column_name, default_value, column_type):
    column = sa.sql.table(table_name, sa.sql.column(column_name))
    op.execute(column.update().values({column_name:default_value}))
    op.alter_column(table_name, column_name, type_=column_type, existing_type=column_type, nullable=False)

# ################################################################################################################################

def validate_tls_from_payload(payload, is_key=False):
    with NamedTemporaryFile(prefix='zato-tls-') as tf:
        tf.write(payload)
        tf.flush()

        pem = open(tf.name).read()

        cert_info = crypto.load_certificate(crypto.FILETYPE_PEM, pem)
        cert_info = sorted(dict(cert_info.get_subject().get_components()).items())
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
    except OSError, e:
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
    user_model.read(ids[0], ['login'])['login']

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
    auth = auth.strip().decode('base64')

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

def get_odb_session_from_server_config(config, cm):

    engine_args = Bunch()
    engine_args.odb_type = config.odb.engine
    engine_args.odb_user = config.odb.username
    engine_args.odb_password = cm.decrypt(config.odb.password) if config.odb.password else ''
    engine_args.odb_host = config.odb.host
    engine_args.odb_port = config.odb.port
    engine_args.odb_db_name = config.odb.db_name

    return get_session(get_engine(engine_args))

# ################################################################################################################################

def get_server_client_auth(config, repo_dir):
    """ Returns credentials to authenticate with against Zato's own /zato/admin/invoke channel.
    """
    session = get_odb_session_from_server_config(config, get_crypto_manager_from_server_config(config, repo_dir))

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
                return (security.username, security.password)

def get_client_from_server_conf(server_dir):
    from zato.client import get_client_from_server_conf as client_get_client_from_server_conf
    return client_get_client_from_server_conf(server_dir, get_server_client_auth, get_config)

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
    except Exception, e:
        logger.warn(
            'Could not open payload path:`%s` `%s`, skipping startup service:`%s`, e:`%s`', orig_path, path, name, format_exc(e))
    else:
        return payload

# ################################################################################################################################

def invoke_startup_services(
        source, key, fs_server_config, repo_location, broker_client=None, service_name=None, skip_include=True, worker_store=None):
    """ Invoked when we are the first worker and we know we have a broker client and all the other config is ready
    so we can publish the request to execute startup services. In the worst case the requests will get back to us but it's
    also possible that other workers are already running. In short, there is no guarantee that any server or worker in particular
    will receive the requests, only that there will be exactly one.
    """
    for name, payload in fs_server_config.get(key, {}).items():

        if service_name:

            # We are to skip this service:
            if skip_include:
                if name == service_name:
                    continue

            # We are to include this service only, any other is rejected
            else:
                if name != service_name:
                    continue

        if payload.startswith('file://'):
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
        g = spawn(callable, *args, **kwargs)
        gevent_sleep(0)
        g.join(kwargs.pop('timeout', 0.2))

        if g.exception:
            type_, value, traceback = g.exc_info
            raise type_(value), None, traceback

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

def get_brython_js():
    code_root = os.path.normpath(os.path.join(common_curdir, '..', '..', '..', '..'))
    brython_path = os.path.join(
        code_root, 'zato-web-admin', 'src', 'zato', 'admin', 'static', 'brython', '_brython', 'brython.js')

    f = open(brython_path)
    brython = f.read()
    f.close()

    # To make it 100% certain that we are returning the correct file
    expected = '450c1a7fcab574947c5a5299b81512be2f251649c326209e7c612ed1be6f35e5'
    actual = sha256(brython).hexdigest()

    if actual != expected:
        raise ValueError('Failed to validate hash of `{}`'.format(brython_path))

    return brython

# ################################################################################################################################

def update_apikey_username(config):
    config.username = 'HTTP_{}'.format(config.get('username', '').upper().replace('-', '_'))

# ################################################################################################################################

def get_response_value(response):
    """ Extracts the actual response string from a response object produced by services.
    """
    return (response.payload.getvalue() if hasattr(response.payload, 'getvalue') else response.payload) or ''

# ################################################################################################################################

def get_lb_agent_json_config(repo_dir):
    return json.loads(open(os.path.join(repo_dir, 'lb-agent.conf')).read())

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
    if input.hook_service_id:
        impl_name = self.server.service_store.id_to_impl_name[input.hook_service_id]
        details = self.server.service_store.services[impl_name]
        if not is_class_pubsub_hook(details['service_class']):
            raise ValueError('Service `{}` is not a PubSubHook subclass'.format(details['name']))

# ################################################################################################################################
