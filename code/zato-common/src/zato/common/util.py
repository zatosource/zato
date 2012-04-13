# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os, sys
from base64 import b64encode
from cStringIO import StringIO
from datetime import datetime
from hashlib import sha1, sha256
from importlib import import_module
from itertools import ifilter
from os import getuid
from os.path import abspath, isabs, join
from pprint import pprint as _pprint
from pwd import getpwuid
from random import getrandbits
from socket import gethostname, getfqdn
from string import Template

# lxml
from lxml import objectify

# M2Crypto
from M2Crypto import BIO, RSA

# ConfigObj
from configobj import ConfigObj

# Bunch
from bunch import Bunch

# ConfigObj
from configobj import ConfigObj

# anyjson
from anyjson import dumps, loads

# Spring Python
from springpython.context import ApplicationContext
from springpython.remoting.http import CAValidatingHTTPSConnection
from springpython.remoting.xmlrpc import SSLClientTransport

# Zato
from zato.common import SIMPLE_IO, soap_body_xpath, ZatoException
from zato.agent.load_balancer.client import LoadBalancerAgentClient

logger = logging.getLogger(__name__)

TRACE1 = 6
logging.addLevelName(TRACE1, "TRACE1")

_repr_template = Template("<$class_name at $mem_loc$attrs>")

################################################################################

security_def_type = Bunch()
security_def_type.basic_auth = 'basic_auth'
security_def_type.tech_account = 'tech_acc'
security_def_type.wss = 'wss'

################################################################################

def absolutize_path(base, path):
    """ Turns a path into an absolute path if it's relative to the base
    location. If the path is already an absolute path, it is returned as-is.
    """
    if isabs(path):
        return path
    
    return abspath(join(base, path))

def current_host():
    return gethostname() + '/' + getfqdn()

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

def decrypt(data, priv_key, padding=RSA.pkcs1_padding, hexlified=True):
    """ Decrypt data using the given private key.
    data - data to be decrypted
    priv_key - private key to use
    padding - padding to use, defaults to PKCS#1
    hexlified - should the data be hex-decoded before being decrypted,
                defaults to True
    """

def encrypt(data, pub_key, padding=RSA.pkcs1_padding, b64=True):
    """ Encrypt data using the given public key.
    data - data to be encrypted
    pub_key - public key to use
    padding - padding to use, defaults to PKCS#1
    b64 - should the encrypted data be BASE64-encoded before being returned,
                defaults to True
    """
    logger.debug("Using pub_key=[%s]" % pub_key)

    bio = BIO.MemoryBuffer(pub_key)
    bio.close()
    rsa = RSA.load_pub_key_bio(bio)

    encrypted = rsa.public_encrypt(data, padding)

    if b64:
        encrypted = b64encode(encrypted)

    return encrypted

def sign(data, priv_key):
    """ Signs the data using a private key from the given path and returns
    the BASE64-encoded signature.
    """
    sig = priv_key.sign(sha1(data).digest())
    return b64encode(sig)

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

    def __init__(self, log_format, date_format, use_color=True):
        # Note that date_format is ignored.
        msg = self.formatter_msg(log_format, use_color)
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def formatter_msg(self, msg, use_color = True):
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

def make_repr(_object, ignore_double_underscore=True, to_avoid_list="repr_to_avoid", sort=True):
    """ Makes a nice string representation of an object, suitable for logging
    purposes.
    """
    attrs = object_attrs(_object, ignore_double_underscore, to_avoid_list, sort)
    buff = StringIO()

    for attr in attrs:

        #if logger.isEnabledFor(TRACE1):
        #    logger.log(TRACE1, "attr=[%s]" % attr)

        attr_obj = getattr(_object, attr)
        if not callable(attr_obj):
            buff.write(" ")
            buff.write("%r=[%r]" % (attr, attr_obj))

    out = _repr_template.safe_substitute(class_name=_object.__class__.__name__,
                            mem_loc=hex(id(_object)), attrs=buff.getvalue())
    buff.close()

    return out


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

def get_lb_client(lb_host, lb_agent_port, ssl_ca_certs, ssl_key_file, ssl_cert_file, timeout):
    """ Returns an SSL XML-RPC client to the load-balancer.
    """
    agent_uri = "https://{host}:{port}/RPC2".format(host=lb_host, port=lb_agent_port)

    # See the 'Problems with XML-RPC over SSL' thread for details
    # https://lists.springsource.com/archives/springpython-users/2011-June/000480.html
    if sys.version_info >= (2, 7):
        class Python27CompatTransport(SSLClientTransport):
            def make_connection(self, host):
                return CAValidatingHTTPSConnection(host, strict=self.strict, ca_certs=self.ca_certs,
                        keyfile=self.keyfile, certfile=self.certfile, cert_reqs=self.cert_reqs,
                        ssl_version=self.ssl_version, timeout=self.timeout)
        transport = Python27CompatTransport
    else:
        transport = None
    
    return LoadBalancerAgentClient(agent_uri, ssl_ca_certs, ssl_key_file, ssl_cert_file,
                                transport=transport, timeout=timeout)

def tech_account_password(password_clear, salt):
    return sha256(password_clear+ ':' + salt).hexdigest()

def new_cid():
    """ Returns a new 64-bit correlation identifier. It's *not* safe to use the ID
    for any cryptographical purposes, it's only meant to be used as a conveniently
    formatted ticket attached to each of the requests processed by Zato servers.
    """
    
    # The number below (24) needs to be kept in sync with zato.common.log_message.CID_LENGTH
    return '{0:0>24}'.format(getrandbits(64))

def get_config(repo_location, config_name):
    """ Returns the configuration object.
    """
    return ConfigObj(os.path.join(repo_location, config_name))

def _get_ioc_config(location, config_class):
    """ Instantiates an Inversion of Control container from the given location
    if the location exists at all.
    """
    stat = os.stat(location)
    if stat.st_size:
        config = config_class(location)
    else:
        config = None

    return config

def get_app_context(config):
    """ Returns the Zato's Inversion of Control application context.
    """
    ctx_class_path = config['spring']['context_class']
    ctx_class_path = ctx_class_path.split('.')
    mod_name, class_name = '.'.join(ctx_class_path[:-1]), ctx_class_path[-1:][0]
    mod = import_module(mod_name)
    class_ = getattr(mod, class_name)()
    return ApplicationContext(class_)

def get_crypto_manager(repo_location, app_context, config, load_keys=True):
    """ Returns a tool for crypto manipulations.
    """
    crypto_manager = app_context.get_object('crypto_manager')
    
    priv_key_location = config['crypto']['priv_key_location']
    pub_key_location = config['crypto']['pub_key_location']
    cert_location = config['crypto']['cert_location']
    ca_certs_location = config['crypto']['ca_certs_location']
    
    priv_key_location = absolutize_path(repo_location, priv_key_location)
    pub_key_location = absolutize_path(repo_location, pub_key_location)
    cert_location = absolutize_path(repo_location, cert_location)
    ca_certs_location = absolutize_path(repo_location, ca_certs_location)
    
    crypto_manager.priv_key_location = priv_key_location
    crypto_manager.pub_key_location = pub_key_location
    crypto_manager.cert_location = cert_location
    crypto_manager.ca_certs_location = ca_certs_location
    
    if load_keys:
        crypto_manager.load_keys()
        
    return crypto_manager

def service_name_from_impl(impl_name):
    """ Turns a Zato internal service's implementation name into a shorter
    service name
    """
    return impl_name.replace('server.service.internal.', '')

def deployment_info(method, remote_host='', remote_user=''):
    """ Returns a JSON document containing information who deployed a service
    onto a cluster, where from and when it was.
    """
    return dumps({
            'method': method,
            'remote_host': remote_host,
            'remote_user': remote_user,
            'current_host': current_host(),
            'current_user': getpwuid(getuid()).pw_name,
            'timestamp': datetime.utcnow().isoformat()
        })

def get_body_payload(body):
    body_children_count = body[0].countchildren()

    if body_children_count == 0:
        body_payload = None
    elif body_children_count == 1:
        body_payload = body[0].getchildren()[0]
    else:
        body_payload = body[0].getchildren()

    return body_payload

def payload_from_request(request, data_format, transport):
    """ Converts a raw request to a payload suitable for usage with SimpleIO.
    """
    if request:
        if data_format == SIMPLE_IO.FORMAT.XML:
            if transport == 'soap':
                soap = objectify.fromstring(request)
                body = soap_body_xpath(soap)
                if not body:
                    raise ZatoException(cid, 'Client did not send the [{1}] element'.format(body_path))
                payload = get_body_payload(body)
            else:
                payload = objectify.fromstring(request)
        elif data_format == SIMPLE_IO.FORMAT.JSON:
            payload = loads(request)
        else:
            payload = request
    else:
        payload = request

    return payload

def is_python_file(name):
    """ Is it a Python file we can import Zato services from?
    """
    for suffix in('py', 'pyw', 'pyc', 'pyo'):
        if name.endswith(suffix):
            return True