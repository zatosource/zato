# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Local imports
from zato.common.pubsub.test.message_sender import MessageSender

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def parse_args() -> 'argparse.Namespace':
    """ Parse command line arguments for the PubSub message sender.
    """
    # Get the directory where this script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    default_config = script_dir / 'sender_config.yaml'

    parser = argparse.ArgumentParser(
        description='Zato PubSub Message Sender CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    _ = parser.add_argument(
        '-c', '--config',
        required=False,
        dest='config_path',
        default=str(default_config),
        help=f'Path to the configuration YAML file (default: {default_config})'
    )

    _ = parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Path to save results JSON (defaults to stdout)'
    )

    _ = parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the CLI.
    """
    args = parse_args()

    # Set log level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize the message sender
        start_time = datetime.now()
        logger.info(f'Starting PubSub message sender at {start_time.isoformat()}')
        logger.info(f'Using configuration from {args.config_path}')

        sender = MessageSender(args.config_path)

        # Start sending messages
        results = sender.start()

        # Format results
        if args.output_file:

            # Save to file
            with open(args.output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f'Results saved to {args.output_file}')

        else:
            # Print to stdout
            print(json.dumps(results, indent=2))

        # Summary to console
        summary = results['summary']
        logger.info(f'Completed: Sent {summary["total_sent"]} messages ' + \
                   f'({summary["failed"]} failed) in {summary["duration_seconds"]:.2f} seconds ' + \
                   f'({summary["rate_per_second"]:.2f} msgs/sec)')

        return 0

    except Exception as e:
        logger.error(f'Error running message sender: {e}', exc_info=True)
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
