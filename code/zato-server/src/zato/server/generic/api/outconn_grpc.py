# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from importlib import import_module
from inspect import isclass
from logging import getLogger

# gRPC
import grpc
import grpc_tools
from grpc.experimental.gevent import init_gevent
from grpc_tools import protoc

# Zato
from zato.common.api import GRPC
from zato.common.util.file_system import fs_safe_name
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, strlist
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Make the gRPC C-core cooperate with gevent - this must run once per process, before any channels are created.
init_gevent()

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_grpc_config_defaults:'dict[str, object]' = {
    'address': GRPC.Default.Address,
    'username': '',
    'is_tls': True,
    'tls_ca_certs_file': '',
    'proto_path': '',
    'stub_module': '',
    'stub_class': '',
    'ping_timeout': GRPC.Default.Ping_Timeout,
    'max_send_message_size': GRPC.Default.Max_Message_Size,
    'max_recv_message_size': GRPC.Default.Max_Message_Size,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_grpc_int_config_keys = ('ping_timeout', 'max_send_message_size', 'max_recv_message_size')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_grpc_bool_config_keys = ('is_tls',)

# The file name suffixes the protobuf compiler gives to the modules it generates.
_pb2_suffix      = '_pb2'
_pb2_grpc_suffix = '_pb2_grpc'

# ################################################################################################################################
# ################################################################################################################################

def generate_stub_modules(proto_path:'str', target_dir:'str') -> 'str':
    """ Runs the protobuf compiler against a .proto file, writing the generated Python modules to target_dir.
    All the .proto files from the input file's directory are compiled together so that imports between them resolve.
    Returns the name of the module with the gRPC stub generated out of the input file.
    """

    # The directory with the input file is where imports between .proto files resolve
    proto_dir = os.path.dirname(proto_path)

    # Where the well-known google.protobuf types live, in case user protos import them
    grpc_tools_dir = os.path.dirname(grpc_tools.__file__)
    well_known_dir = os.path.join(grpc_tools_dir, '_proto')

    # Make sure there is a directory to write the generated modules to
    os.makedirs(target_dir, exist_ok=True)

    # Compile every .proto file from the directory so that generated modules
    # exist for all the files the input file may import.
    proto_file_list:'strlist' = []

    for file_name in sorted(os.listdir(proto_dir)):
        if file_name.endswith('.proto'):
            full_path = os.path.join(proto_dir, file_name)
            proto_file_list.append(full_path)

    # Arguments for the protobuf compiler - the first one is the program name it expects
    compiler_args = [
        'protoc',
        f'--proto_path={proto_dir}',
        f'--proto_path={well_known_dir}',
        f'--python_out={target_dir}',
        f'--grpc_python_out={target_dir}',
    ]
    compiler_args.extend(proto_file_list)

    # Run the compiler now ..
    result = protoc.main(compiler_args)

    # .. and report the failure if it did not succeed - the compiler itself
    # writes the details of what went wrong to stderr.
    if result != 0:
        raise Exception(f'Could not compile proto file `{proto_path}` (exit code -> {result})')

    # Any generated modules already imported are removed from the module cache
    # so that the next import re-executes them, picking up the newly generated code.
    for file_name in os.listdir(target_dir):
        if file_name.endswith('.py'):
            module_name = file_name[:-len('.py')]
            _ = sys.modules.pop(module_name, None)

    # The stub module's name follows from the input file's name,
    # with the characters that would be invalid in a module name replaced.
    proto_file_name = os.path.basename(proto_path)
    module_stem = proto_file_name[:-len('.proto')]
    module_stem = module_stem.replace('-', '_').replace('.', '_')

    out = module_stem + _pb2_grpc_suffix
    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_stub_class(module:'any_', stub_class_name:'str') -> 'any_':
    """ Returns the gRPC stub class from a generated module - either the one explicitly named
    or the only one found in the module.
    """

    # If we were given an explicit name, that settles it ..
    if stub_class_name:
        out = getattr(module, stub_class_name)
        return out

    # .. otherwise, collect all the stub classes the module defines ..
    stub_class_list:'anylist' = []

    for name in dir(module):
        if name.endswith('Stub'):
            item = getattr(module, name)
            if isclass(item):
                stub_class_list.append(item)

    # .. and there needs to be exactly one for the choice to be unambiguous.
    stub_class_count = len(stub_class_list)

    if stub_class_count != 1:
        raise Exception(f'Expected exactly one stub class in module `{module.__name__}`, found {stub_class_count} - ' + \
            'set the stub class name in the connection\'s configuration to indicate which one to use')

    out = stub_class_list[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnGRPCWrapper(Wrapper):
    """ Wraps a gRPC channel along with the stub built over it.
    """
    wrapper_type = 'gRPC connection'

    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        super(OutconnGRPCWrapper, self).__init__(config, server)
        self.channel:'grpc.Channel | None' = None

# ################################################################################################################################

    def _get_stub_class(self) -> 'any_':
        """ Resolves the stub class - either from modules generated out of the connection's .proto file
        or from modules the user deployed themselves, imported by name at build time so that redeployments
        are picked up on the next rebuild.
        """

        # A .proto file is given, so the server generates the modules itself ..
        if proto_path := self.config.proto_path:

            # .. each connection keeps its generated modules in its own directory ..
            dir_name = fs_safe_name(self.config.name)
            target_dir = os.path.join(self.server.work_dir, GRPC.Stub_Dir, dir_name)

            # .. generate the modules now ..
            module_name = generate_stub_modules(proto_path, target_dir)

            # .. and make them importable.
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)

        # .. otherwise, the user deployed pre-generated modules and tells us which one holds the stub.
        else:
            module_name = self.config.stub_module

        # Import the module and find the stub class in it.
        module = import_module(module_name)

        out = extract_stub_class(module, self.config.stub_class)
        return out

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with self.update_lock:

            # Message size limits for the channel
            channel_options = [
                ('grpc.max_send_message_length', self.config.max_send_message_size),
                ('grpc.max_receive_message_length', self.config.max_recv_message_size),
            ]

            # A TLS channel is the default, with an optional CA certificates file
            # to verify the remote end's certificate against ..
            if self.config.is_tls:

                if self.config.tls_ca_certs_file:
                    with open(self.config.tls_ca_certs_file, 'rb') as ca_certs_file:
                        ca_certs = ca_certs_file.read()
                else:
                    ca_certs = None

                credentials = grpc.ssl_channel_credentials(root_certificates=ca_certs)
                self.channel = grpc.secure_channel(self.config.address, credentials, options=channel_options)

            # .. a plaintext channel needs to be chosen explicitly.
            else:
                self.channel = grpc.insecure_channel(self.config.address, options=channel_options)

            # Resolve the stub class and build the stub over the channel -
            # the stub is what user-facing invokers call methods on.
            stub_class = self._get_stub_class()
            self._impl = stub_class(self.channel)

            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':
        if self.channel:
            self.channel.close()

# ################################################################################################################################

    def _ping(self) -> 'None':

        # This blocks until the channel is ready or raises an error on timeout.
        future = grpc.channel_ready_future(self.channel)
        _ = future.result(timeout=self.config.ping_timeout)

# ################################################################################################################################
# ################################################################################################################################
