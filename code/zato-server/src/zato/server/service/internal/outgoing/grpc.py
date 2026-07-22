# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64encode
from contextlib import closing

# Zato
from zato.common.api import GRPC
from zato.common.exception import BadRequest
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.util.file_system import fs_safe_name
from zato.common.util.sql import get_instance_by_id
from zato.server.generic.api.outconn_grpc import generate_stub_modules
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class GetStubModules(AdminService):
    """ Returns the Python modules generated out of a gRPC connection's .proto file
    so that they can be downloaded, e.g. for code completion in one's editor.
    """
    name = 'zato.outgoing.grpc.get-stub-modules'

    input = Int('id')
    output = AsIs('files')

    def handle(self) -> 'None':

        # Look up the connection's name by its ID ..
        with closing(self.odb.session()) as session:
            instance = get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            name = instance.name

        # .. get the connection's configuration ..
        config = self.server.config_manager.outconn_grpc[name]

        # .. only connections built out of a .proto file have generated modules to offer ..
        proto_path = config['proto_path']
        if not proto_path:
            raise BadRequest(self.cid, f'Connection `{name}` uses pre-deployed stub modules, there is nothing to download')

        # .. generate the modules now so that the download is always up to date
        # .. with what is currently in the .proto file ..
        dir_name = fs_safe_name(name)
        target_dir = os.path.join(self.server.work_dir, GRPC.Stub_Dir, dir_name)
        _ = generate_stub_modules(proto_path, target_dir)

        # .. collect all the generated modules ..
        files = []

        for file_name in sorted(os.listdir(target_dir)):
            if file_name.endswith('.py'):
                full_path = os.path.join(target_dir, file_name)
                with open(full_path, 'rb') as module_file:
                    data = module_file.read()
                encoded = b64encode(data).decode('utf8')
                files.append({'name': file_name, 'data': encoded})

        # .. and return them to our caller.
        self.response.payload.files = files

# ################################################################################################################################
# ################################################################################################################################
