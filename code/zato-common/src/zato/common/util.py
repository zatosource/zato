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
import logging
from base64 import b64encode
from binascii import hexlify, unhexlify
from cStringIO import StringIO
from hashlib import sha1, sha256
from itertools import ifilter
from os.path import abspath, isabs, join
from pprint import pprint as _pprint
from socket import gethostname, getfqdn
from string import Template
from threading import Thread

# M2Crypto
from M2Crypto import BIO, EVP, RSA

# ZeroMQ
import zmq

# Bunch
from bunch import Bunch

# Zato
from zato.agent.load_balancer.client import LoadBalancerAgentClient
from zato.common import ZATO_PARALLEL_SERVER, ZATO_SINGLETON_SERVER

logger = logging.getLogger(__name__)

TRACE1 = 6
logging.addLevelName(TRACE1, "TRACE1")

_repr_template = Template("<$class_name at $mem_loc$attrs>")

################################################################################

security_def_type = Bunch()
security_def_type.basic_auth = 'basic-auth'
security_def_type.client_cert = 'client-cert'
security_def_type.tech_account = 'tech-account'
security_def_type.wss_username_password = 'wss-username-password'

################################################################################

def zmq_inproc_name(component):
    """ Returns a name suitable for passing around between ZeroMQ 'inproc'
    sockets.
    """
    return 'inproc://zato/{0}'.format(component)

class ZMQPull(object):
    
    def __init__(self, name, zmq_context, on_message_handler, keep_running=True):
        self.name = name
        self.on_message_handler = on_message_handler
        self.keep_running = keep_running
        self.socket_type = zmq.PULL
        
        self.socket = zmq_context.socket(self.socket_type)
        self.socket.bind(name)

    def start(self):
        Thread(args=(self.socket,), target=self.listen).start()
        
    def stop(self, socket=None):
        self.keep_running = False
        if socket:
            socket.close()
    
    def listen(self, socket):
        logger.debug('Starting [{0}]/[{1}]'.format(self.__class__.__name__, self.name))
        
        while self.keep_running:
            try:
                msg = socket.recv()
            except zmq.ZMQError, e:
                msg = 'Caught ZMQError [{0}], quitting.'.format(e.strerror)
                logger.warn(msg)
                self.stop(socket)
            else:
                if msg == 'ZATO;STOP':
                    self.stop(socket)
                else:
                    self.on_message_handler(msg)
                
class ZMQPush(object):
    def __init__(self, name, zmq_context):
        self.name = name
        self.zmq_context = zmq_context
        self.socket_type = zmq.PUSH 
        
        self.socket = self.zmq_context.socket(self.socket_type)
        self.socket.connect(self.name)
        
    def send(self, msg):
        try:
            self.socket.send(msg)
        except zmq.ZMQError, e:
            msg = 'Caught ZMQError [{0}], continuing anyway.'.format(e.strerror)
            logger.warn(msg)
        
    def stop(self):
        msg = 'Stopping [{0}/{1}]'.format(self.name, self.socket_type)
        logger.info(msg)
        self.socket.close()
        
zmq_names = Bunch()
zmq_names.inproc = Bunch()

zmq_names.inproc.singleton_to_parallel = zmq_inproc_name('singleton-to-parallel')
zmq_names.inproc.parallel_to_singleton = zmq_inproc_name('parallel-to-singleton')

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
            buff.write("%s=[%s]" % (attr, attr_obj))

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
    return LoadBalancerAgentClient(agent_uri, ssl_ca_certs, ssl_key_file, ssl_cert_file,
                                         timeout=timeout)

def tech_account_password(password_clear, salt):
    return sha256(password_clear+ ':' + salt).hexdigest()