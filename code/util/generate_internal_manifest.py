#!/usr/bin/env python3

"""
Generates _internal_manifest.json for O(1) internal service startup.
Run during CI/CD build: python -m util.generate_internal_manifest
The output goes to zato-server/src/zato/server/service/_internal_manifest.json
"""

# stdlib
import inspect
import json
import os
import sys

def main():

    # Ensure the source tree is importable
    code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for sub in ('zato-common/src', 'zato-server/src', 'zato-broker/src'):
        path = os.path.join(code_dir, sub)
        if os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)

    from zato.common.util.api import find_internal_modules
    from zato.server.service import Service, internal
    from inspect import isclass, getmro

    deploy_internal = find_internal_modules(internal)
    if not deploy_internal:
        print('ERROR: No internal modules found')
        sys.exit(1)

    from importlib import import_module

    manifest = []

    for module_name in sorted(deploy_internal):
        try:
            mod = import_module(module_name)
        except Exception as e:
            print(f'WARNING: could not import {module_name}: {e}')
            continue

        for attr_name in sorted(dir(mod)):
            obj = getattr(mod, attr_name)
            if not isclass(obj):
                continue
            if not issubclass(obj, Service):
                continue
            if obj is Service:
                continue
            if obj.__module__ != module_name:
                continue
            if getattr(obj, 'DONT_DEPLOY_ATTR_NAME', None):
                continue

            manifest.append({
                'module': module_name,
                'class': attr_name,
            })

    out_path = os.path.join(
        code_dir, 'zato-server', 'src', 'zato', 'server', 'service', '_internal_manifest.json'
    )

    with open(out_path, 'w') as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(f'Wrote {len(manifest)} entries to {out_path}')

if __name__ == '__main__':
    main()
