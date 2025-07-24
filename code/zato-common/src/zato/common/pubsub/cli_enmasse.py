# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import argparse
import logging
import os
import sys
import tempfile
from logging import basicConfig, getLogger, INFO
from traceback import format_exc

# Zato
from zato.common.test.enmasse_.base import BaseEnmasseTestCase

# ################################################################################################################################
# ################################################################################################################################

# Setup basic logging
basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(process)s:%(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Embedded YAML configuration
ENMASSE_YAML_CONFIG = """
security:
  - name: demo
    type: basic_auth
    username: demo
    password: demo

pubsub_topic:
  - name: demo.1
    description: Demo topic 1

  - name: demo.2
    description: Demo topic 2

  - name: demo.3
    description: Demo topic 3

pubsub_permission:
  - security: demo
    pub:
      - demo.*
    sub:
      - demo.*

pubsub_subscription:
  - security: demo
    delivery_type: pull
    topic_list:
      - demo.1
      - demo.2
      - demo.3
"""

# ################################################################################################################################
# ################################################################################################################################

class EnmasseCLI(BaseEnmasseTestCase):

    def run_enmasse_import(self, yaml_content:'str') -> 'bool':
        """ Run enmasse import with the given YAML content.
        """
        temp_file_path = None

        try:
            # Create temporary file with YAML content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
                _ = temp_file.write(yaml_content)
                temp_file_path = temp_file.name

            logger.info(f'Created temporary YAML file: {temp_file_path}')
            logger.info('Running enmasse import...')

            # Run enmasse import
            _ = self.invoke_enmasse(temp_file_path, require_ok=True)

            logger.info('Enmasse import completed successfully')
            return True

        except Exception as e:
            logger.error(f'Error running enmasse import: {e}')
            logger.error(format_exc())
            return False

        finally:
            # Clean up temporary file
            try:
                if temp_file_path:
                    _  = os.unlink(temp_file_path)
            except:
                pass

# ################################################################################################################################
# ################################################################################################################################

def get_parser() -> 'argparse.ArgumentParser':
    """ Create and return the command line argument parser.
    """
    parser = argparse.ArgumentParser(description='Zato PubSub Enmasse CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Enmasse command
    enmasse_parser = subparsers.add_parser('enmasse', help='Run enmasse import with demo configuration')
    _ = enmasse_parser.add_argument('--has_debug', action='store_true', help='Enable debug mode')

    return parser

# ################################################################################################################################

def run_enmasse_command(args:'argparse.Namespace') -> 'int':
    """ Run the enmasse command.
    """
    try:
        if args.has_debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        logger.info('Starting enmasse import with demo configuration')
        
        # Create CLI instance and run enmasse
        cli = EnmasseCLI()
        success = cli.run_enmasse_import(ENMASSE_YAML_CONFIG)
        
        if success:
            logger.info('Enmasse import completed successfully')
            return 0
        else:
            logger.error('Enmasse import failed')
            return 1
            
    except Exception as e:
        logger.error(f'Error in enmasse command: {e}')
        logger.error(format_exc())
        return 1

# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the CLI.
    """
    parser = get_parser()
    args = parser.parse_args()

    if args.command == 'enmasse':
        return run_enmasse_command(args)
    else:
        parser.print_help()
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
