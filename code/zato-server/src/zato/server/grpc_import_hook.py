# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server process imports grpc only when a component needs it, e.g. an outgoing gRPC connection, the gRPC export
# of the audit log or a user service, and every channel such a component creates requires the gevent integration
# of gRPC. The finder of this module runs that integration the moment grpc itself is imported in the process.

# stdlib
import sys
from importlib import import_module
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Sequence
    from types import ModuleType
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The package whose import runs the gevent integration
    GRPC_Module_Name = 'grpc'

    # The module that runs the gevent integration of gRPC when it is imported
    GRPC_Gevent_Module_Name = 'zato.common.grpc_gevent'

# ################################################################################################################################
# ################################################################################################################################

class GRPCLoader(Loader):
    """ Executes the package grpc through its own loader and then runs the gevent integration of gRPC.
    """
    def __init__(self, loader:'Loader') -> 'None':
        self.loader = loader

    def __getattr__(self, name:'str') -> 'any_':

        # Resource readers and the other optional methods of a loader are answered by the loader of grpc itself.
        out = getattr(self.loader, name)
        return out

    def create_module(self, spec:'ModuleSpec') -> 'ModuleType | None':
        out = self.loader.create_module(spec)
        return out

    def exec_module(self, module:'ModuleType') -> 'None':

        # The package is complete when its own loader returns ..
        self.loader.exec_module(module)

        # .. so the integration, which imports submodules of grpc, can run before any channel exists.
        _ = import_module(ModuleCtx.GRPC_Gevent_Module_Name)

# ################################################################################################################################
# ################################################################################################################################

class GRPCImportFinder(MetaPathFinder):
    """ Gives the package grpc a loader that runs the gevent integration of gRPC after the package is executed.
    """
    def find_spec(
        self,
        fullname:'str',
        path:'Sequence[str] | None',
        target:'ModuleType | None'=None,
        ) -> 'ModuleSpec | None':

        if fullname != ModuleCtx.GRPC_Module_Name:
            return None

        spec = PathFinder.find_spec(fullname, path, target)

        # A process without grpc installed keeps the finder, and each later import of grpc fails as it would without it.
        if spec is None:
            return None

        if spec.loader is None:
            return None

        spec.loader = GRPCLoader(spec.loader)

        # The package is imported once per process, so the finder leaves the search path of later imports. The import system
        # stops iterating the finders once one returns a specification, so the removal does not affect this import.
        sys.meta_path.remove(self)

        return spec

# ################################################################################################################################
# ################################################################################################################################

def install_grpc_import_hook() -> 'None':
    """ Places the finder of grpc in front of the other finders of the process.
    """
    sys.meta_path.insert(0, GRPCImportFinder())

# ################################################################################################################################
# ################################################################################################################################
