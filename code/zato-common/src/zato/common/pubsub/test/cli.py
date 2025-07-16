# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import os
import sys
from json import dumps
from logging import basicConfig, getLogger
from pathlib import Path

# Zato
from zato.common.pubsub.test.message_sender import MessageSender

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_absolute_path(relative_path):
    """ Return an absolute path based on this program's location.
    """
    # Get directory where the program is located
    program_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(program_dir, relative_path))

# ################################################################################################################################
# ################################################################################################################################

def parse_args():
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run PubSub message sender')

    _ = parser.add_argument('--config',
                      type=str,
                      default='sender_config.yaml',
                      help='Path to sender configuration file (relative to script directory or absolute)')

    _ = parser.add_argument('--log-level',
                      type=str,
                      default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level')

    _ = parser.add_argument('--output-file',
                      type=str,
                      help='Save statistics to output file (optional)')

    _ = parser.add_argument('--pretty',
                      action='store_true',
                      help='Pretty print JSON output')

    return parser.parse_args()

# ################################################################################################################################
# ################################################################################################################################

def main():
    """ Main entry point.
    """
    args = parse_args()

    # Configure logging
    log_level = getattr(sys.modules['logging'], args.log_level)
    basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Determine configuration file path
    if os.path.isabs(args.config):
        config_path = args.config
    else:
        config_path = get_absolute_path(args.config)

    logger.info(f'Using configuration from: {config_path}')

    try:
        # Initialize and run the sender
        sender = MessageSender(config_path)
        results = sender.start()

        # Format the results
        indent = 2
        json_output = dumps(results, indent=indent)

        # Output to file if specified
        if args.output_file:
            output_path = args.output_file
            with open(output_path, 'w') as f:
                _ = f.write(json_output)
            logger.info(f'Statistics written to: {output_path}')
        else:
            print(json_output)

        # Display summary information
        sent = results['summary']['total_sent']
        failed = results['summary']['failed']
        rate = results['summary']['rate_per_second']
        duration = results['summary']['duration_seconds']

        logger.info(f'Summary: Sent {sent} messages ({failed} failed) in {duration:.2f} seconds ({rate:.2f} msgs/sec)')

        # Return success only if there were no failed messages
        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f'Error running message sender: {e}', exc_info=True)
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
