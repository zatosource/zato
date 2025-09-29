#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import sys

# Zato
from zato.common.util.api import wait_for_200_ok

# ################################################################################################################################
# ################################################################################################################################

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    if len(sys.argv) != 2:
        logger.error('Invalid number of arguments')
        print('Usage: wait_for_200_ok.py <address>', file=sys.stderr)
        sys.exit(1)

    address = sys.argv[1]
    logger.debug('Starting to wait for 200 OK response from address: %s', address)
    _ = wait_for_200_ok(address)
    logger.debug('Finished waiting for 200 OK response from address: %s', address)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
