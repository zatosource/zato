# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

class Enmasse(ZatoCommand):

    opts:'dictlist' = [

        {'name':'--import', 'help':'Import definitions from a local YAML file', 'action':'store_true'},
        {'name':'--export', 'help':'Export server objects to a YAML file', 'action':'store_true'},

        {'name':'--input', 'help':'Path to input YAML file with objects to import'},
        {'name':'--output', 'help':'Path to a file to export data to', 'action':'store'},

        {'name':'--ignore-missing-includes', 'help':'Ignore include files that do not exist', 'action':'store_true'},
        {'name':'--exit-on-missing-file', 'help':'If input file does not exist, exit with status code 0', 'action':'store_true'},

        {'name':'--initial-wait-time', 'help':'How many seconds to initially wait for a server', 'default':10},

        {'name':'--env-file', 'help':'Path to an .ini file with environment variables'},
    ]

    def execute(self, args) -> 'None':

        # stdlib
        import json
        import os
        import sys

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        server_path = args.path

        # Process environment variables if specified
        if getattr(args, 'env_file', None):
            self.logger.info('Loading environment variables from %s', args.env_file)
            from zato.common.ext.configobj_ import ConfigObj
            env_config = ConfigObj(args.env_file)
            for section in env_config:
                for key, value in env_config[section].items():
                    if isinstance(value, (int, float)):
                        value = str(value)
                    os.environ[key] = value

        # Build client to the running server
        client = get_client_from_server_conf(
            server_dir=server_path,
            require_server=True,
            initial_wait_time=int(args.initial_wait_time)
        )

        # Handle export
        if getattr(args, 'export', False):
            self.logger.info('Exporting objects to YAML')

            if not args.output:
                self.logger.error('Output file path (--output) is required for export')
                sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

            response = client.invoke('zato.server.invoker', {'func_name': 'export_enmasse'})
            yaml_data = response.data if isinstance(response.data, str) else str(response.data)

            with open(args.output, 'w') as f:
                f.write(yaml_data)

            self.logger.info('Exported configuration to %s', args.output)

        # Handle import
        elif getattr(args, 'import', False):

            if not args.input:
                self.logger.error('Input file path (--input) is required for import')
                sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

            if not os.path.exists(args.input) and args.exit_on_missing_file:
                self.logger.warning('Input file %s not found, exiting', args.input)
                sys.exit(0)

            with open(args.input) as f:
                file_content = f.read()

            file_content = os.path.expandvars(file_content)

            response = client.invoke('zato.server.invoker', {
                'func_name': 'import_enmasse',
                'file_content': file_content,
                'file_name': os.path.basename(args.input),
            })

            response_data = response.data if isinstance(response.data, str) else str(response.data)

            try:
                result = json.loads(response_data) if response_data else {}
            except (json.JSONDecodeError, TypeError):
                result = {'is_ok': False, 'stderr': response_data}

            if result.get('is_ok'):
                self.logger.info('Enmasse OK (%s)', args.input)
            else:
                self.logger.error('Enmasse import failed: %s', result.get('stderr', ''))
                sys.exit(1)

        else:
            self.logger.error('Either --export or --import must be specified')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

# ################################################################################################################################
# ################################################################################################################################
