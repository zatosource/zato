# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist, stranydict, strlist

# Map of object types to their display names
type_display_names = {
    'security': 'security definition',
    'groups': 'security group',
    'channel_rest': 'REST channel',
    'cache': 'cache',
    'odoo': 'Odoo connection',
    'email_smtp': 'SMTP connection',
    'email_imap': 'IMAP connection',
    'sql': 'SQL connection',
    'scheduler': 'scheduler job',
    'confluence': 'Confluence connection',
    'jira': 'Jira connection',
    'ldap': 'LDAP connection',
    'microsoft_365': 'Microsoft 365 connection',
    'search_es': 'ElasticSearch connection'
}

# ################################################################################################################################
# ################################################################################################################################


class Enmasse(ZatoCommand):

    opts:'dictlist' = [

        {'name':'--import', 'help':'Import definitions from a local file (excludes --export-*)', 'action':'store_true'},
        {'name':'--export', 'help':'Export server objects to a file', 'action':'store_true'},

        {'name':'--input', 'help':'Path to input file with objects to import'},
        {'name':'--output', 'help':'Path to a file to export data to', 'action':'store'},

        {'name':'--include-type', 'help':'A list of definition types to include in an export', 'action':'store', 'default':'all'},
        {'name':'--include-name', 'help':'Only objects containing any of the names provided will be exported', 'action':'store', 'default':'all'},

        {'name':'--ignore-missing-includes', 'help':'Ignore include files that do not exist', 'action':'store_true'},
        {'name':'--exit-on-missing-file', 'help':'If input file does not exist, exit with status code 0', 'action':'store_true'},

        {'name':'--initial-wait-time', 'help':'How many seconds to initially wait for a server', 'default':10},
        {'name':'--missing-wait-time', 'help':'How many seconds to wait for missing objects', 'default':1},

        {'name':'--env-file', 'help':'Path to an .ini file with environment variables'},

        {'name':'--replace', 'help':'Ignored. Kept for backward compatibility', 'action':'store_true'},
        {'name':'--replace-odb-objects', 'help':'Ignored. Kept for backward compatibility', 'action':'store_true'},
        {'name':'--export-odb', 'help':'Same as --export. Kept for backward compatibility', 'action':'store_true'},

        # zato enmasse --import --input=/path/to/input-enmasse.yaml   ~/qs-1/server1     --verbose
        # zato enmasse --export --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose

        # zato enmasse --export --include-type=cache               --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose
        # zato enmasse --export --include-type=cloud-microsoft-365 --output /path/to/output-enmasse.yaml ~/env/qs-1/server1 --verbose
    ]

    def get_cluster_id(self, args):
        return 1 # Always this value because there is always going to be one cluster only

    def execute(self, args) -> 'None':

        # stdlib
        import os
        import sys
        import yaml

        # Zato
        from zato.cli.enmasse.client import get_session_from_server_dir
        from zato.cli.enmasse.config import ModuleCtx
        from zato.cli.enmasse.exporter import EnmasseYAMLExporter
        from zato.cli.enmasse.importer import EnmasseYAMLImporter
        from zato.common.util.api import get_client_from_server_conf

        # Get server path from the command line arguments
        server_path = args.path

        # Store cluster ID for exporters and importers
        ModuleCtx.Cluster_ID = self.get_cluster_id(args)

        # Set component_dir - needed by importer/exporter
        self.component_dir = server_path

        # Process environment variables if specified
        if getattr(args, 'env_file', None):
            self.logger.info('Loading environment variables from %s', args.env_file)

            # ConfigObj for parsing the file
            from zato.common.ext.configobj_ import ConfigObj

            # Load the environment variables
            env_config = ConfigObj(args.env_file)

            # Set environment variables
            for section in env_config:
                for key, value in env_config[section].items():
                    os.environ[key] = value

        # Get session from server directory
        session = get_session_from_server_dir(server_path)

        # Handle export
        if getattr(args, 'export', False) or getattr(args, 'export_odb', False):
            self.logger.info('Exporting objects to YAML')

            # Make sure we have an output file
            if not args.output:
                self.logger.error('Output file path (--output) is required for export')
                sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

            try:
                # Export to dictionary
                exporter = EnmasseYAMLExporter()
                data_dict: 'stranydict' = exporter.export_to_dict(session)

                # Filter by type if specified
                if args.include_type != 'all':
                    types: 'strlist' = [t.strip() for t in args.include_type.split(',')]
                    data_dict = {k: v for k, v in data_dict.items() if k in types}

                # Filter by name if specified
                if args.include_name != 'all':
                    names: 'strlist' = [n.strip().lower() for n in args.include_name.split(',')]
                    for key, items in data_dict.items():
                        data_dict[key] = [item for item in items
                                         if any(name in str(item.get('name', '')).lower() for name in names)]

                # Write output to file
                with open(args.output, 'w') as f:
                    yaml.dump(data_dict, f, default_flow_style=False, indent=4)

                self.logger.info('Exported configuration to %s', args.output)

            except Exception as e:
                self.logger.error('Error during export: %s', str(e))
                sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # Handle import
        elif getattr(args, 'import', False):

            # Make sure we have an input file
            if not args.input:
                self.logger.error('Input file path (--input) is required for import')
                sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

            # Check if file exists
            if not os.path.exists(args.input) and args.exit_on_missing_file:
                self.logger.warning('Input file %s not found, exiting', args.input)
                sys.exit(0)

            # Import from YAML
            importer = EnmasseYAMLImporter()

            try:
                # Load configuration from file
                yaml_config:'stranydict' = importer.from_path(args.input)

                # Set import context
                ModuleCtx.ignore_missing_includes = args.ignore_missing_includes

                # Sync objects ..
                _ = importer.sync_from_yaml(
                    yaml_config,
                    session,
                    server_dir=self.component_dir,
                    wait_for_services_timeout=args.missing_wait_time
                )

                # .. build an invoker ..
                client = get_client_from_server_conf(
                    server_dir=server_path,
                    require_server=True,
                    initial_wait_time=int(args.initial_wait_time)
                )

                # .. reload the configuration ..
                _ = client.invoke('zato.server.invoker', {'func_name':'reload_config'})

                # .. and confirm it all went fine.
                self.logger.info('⭐ Enmasse OK (%s)', args.input)

            except Exception as e:
                self.logger.error('Error during import: %s', str(e))
                sys.exit(self.SYS_ERROR.INVALID_INPUT)

        else:
            self.logger.error('Either --export or --import must be specified')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        session.close()

# ################################################################################################################################

    @staticmethod
    def format_object_name(item):

        # For groups objects, display name and members but never ID
        if isinstance(item, dict):
            if 'members' in item and 'name' in item:
                return {
                    'name': item['name'],
                    'members': item['members']
                }

        # For regular objects, just return the name
        return getattr(item, 'name', str(item))

# ################################################################################################################################
# ################################################################################################################################
