# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO, WARNING
from operator import itemgetter
from time import sleep

# colorama
from colorama import Fore, Style

# requests
from requests.exceptions import RequestException

# Zato
from zato.common.util.api import get_client_from_server_conf

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, stranydict, strdictlist

    # Dummy assignments to satisfy type checkers
    ZatoClient = ZatoClient
    strdictlist = strdictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.on-prem-gateway.'

# The host that a gateway on the same machine as the hub connects to
_Local_Host = 'localhost'

# How often, in seconds, Zato is checked for an active gateway while there is none
_Wait_Interval = 1

# The console output, which goes to stderr because stdout has the token only
_Log_Format      = f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} %(message)s'
_Log_Date_Format = '%Y-%m-%d %H:%M:%S'

# The client logs each request and response, including the token, at the INFO level
_Client_Logger_Name = 'zato.client'

# ################################################################################################################################
# ################################################################################################################################

def _invoke(client:'ZatoClient', name:'str', payload:'stranydict | None'=None) -> 'any_':
    """ Invokes one of the on-prem gateway services and returns its response, repeating the call
    while the server is unavailable or returns an error.
    """
    while True:

        # A server that is restarting closes the connection or refuses it ..
        try:
            response = client.invoke(_service_name_prefix + name, payload)
        except RequestException:
            logger.info(f'{Fore.YELLOW}Waiting for the Zato server{Style.RESET_ALL}')
            sleep(_Wait_Interval)
            continue

        # .. a server that responded successfully provides the result ..
        if response.ok:
            return response.data

        # .. and an error is reported before the next attempt.
        logger.info(f'{Fore.RED}{response.details}{Style.RESET_ALL}')
        sleep(_Wait_Interval)

# ################################################################################################################################

def _get_active_gateways(client:'ZatoClient') -> 'strdictlist':
    """ Returns the active gateways that exist in Zato.
    """
    gateways = _invoke(client, 'get-list')

    out = [item for item in gateways if item['is_active']]
    return out

# ################################################################################################################################

def get_enrollment_token(server_dir:'str') -> 'str':
    """ Resets the key of the first active gateway by name and returns a new enrollment token for it.
    """
    # The server may be unavailable at this point, which every invocation waits for.
    client = get_client_from_server_conf(server_dir, require_server=False)

    # The hub receives the gateways that exist in Zato, replacing the ones it had before ..
    _ = _invoke(client, 'sync')

    # .. the gateway to enroll is the first active one by name, which may be defined in the Dashboard after this point ..
    gateways = _get_active_gateways(client)

    while not gateways:
        logger.info(f'{Fore.YELLOW}Waiting for an active on-prem gateway to be defined in Zato{Style.RESET_ALL}')
        sleep(_Wait_Interval)
        gateways = _get_active_gateways(client)

    gateways = sorted(gateways, key=itemgetter('name'))
    gateway = gateways[0]
    name = gateway['name']

    # .. the hub accepts the token only if it has no key on file for the gateway ..
    _ = _invoke(client, 'reset-key', {'id': gateway['id']})

    # .. and the token has the address of the hub on this machine.
    response = _invoke(client, 'get-enrollment-token', {'id': gateway['id'], 'dashboard_host': _Local_Host})

    logger.info(f'{Fore.GREEN}Enrolling on-prem gateway {Style.BRIGHT}{name}{Style.RESET_ALL}')

    out = response['token']
    return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    basicConfig(stream=sys.stderr, level=INFO, format=_Log_Format, datefmt=_Log_Date_Format)
    getLogger(_Client_Logger_Name).setLevel(WARNING)

    parser = ArgumentParser()
    _ = parser.add_argument('--server-dir', required=True)

    args = parser.parse_args()

    token = get_enrollment_token(args.server_dir)
    print(token)

# ################################################################################################################################
# ################################################################################################################################
