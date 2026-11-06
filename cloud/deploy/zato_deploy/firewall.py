# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato_deploy.common import Port, strlist
from zato_deploy.process import CommandResult, run_command

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Rule_Prefix = '-A PREROUTING '

# ################################################################################################################################
# ################################################################################################################################

def _get_rule(port:'int') -> 'strlist':
    """ Returns the rule that sends new connections to a port of this host to this program for as long as it exists,
    while connections that were accepted already stay where they are. The connections that the container opens
    to the same port elsewhere pass through PREROUTING as well, which is why only the addresses of this host match.
    """
    out = [
        '-p', 'tcp',
        '-m', 'addrtype', '--dst-type', 'LOCAL',
        '--dport', str(port),
        '-j', 'REDIRECT', '--to-ports', str(Port.Deploy),
    ]
    return out

# ################################################################################################################################

def _get_rule_listed(port:'int') -> 'str':
    """ Returns how the rule reads in the output of iptables -S.
    """
    out = f'--dport {port} -j REDIRECT --to-ports {Port.Deploy}'
    return out

# ################################################################################################################################

def _iptables(arguments:'strlist') -> 'CommandResult':

    command = ['iptables', '-t', 'nat']
    command.extend(arguments)

    out = run_command(command)
    return out

# ################################################################################################################################

def _get_rule_numbers(port:'int') -> 'tuple[bool, list[int]]':
    """ Returns whether the rule is the first one in PREROUTING and the numbers of all its copies there.
    """
    result = _iptables(['-S', 'PREROUTING'])
    listed = result.stdout.splitlines()
    rule_listed = _get_rule_listed(port)

    numbers:'list[int]' = []
    rule_number = 0

    for line in listed:
        if not line.startswith(_Rule_Prefix):
            continue
        rule_number += 1
        if rule_listed in line:
            numbers.append(rule_number)

    is_first = 1 in numbers

    out = (is_first, numbers)
    return out

# ################################################################################################################################
# ################################################################################################################################

def add_redirect(port:'int') -> 'None':
    """ Sends new connections to the port of the progress page to this program.
    """
    arguments = ['-I', 'PREROUTING', '1']
    arguments.extend(_get_rule(port))

    result = _iptables(arguments)

    if result.exit_code != 0:
        logger.warning('Redirect could not be added: %s', result.stderr)

# ################################################################################################################################

def keep_redirect_first(port:'int') -> 'None':
    """ Moves the rule back to the top of PREROUTING, because Docker adds rules of its own there.
    """
    is_first, numbers = _get_rule_numbers(port)

    if is_first:
        return

    # Inserting the rule first means there is no moment without one ..
    add_redirect(port)

    # .. and the copies further down, now one position lower each, are deleted from the bottom up.
    for number in reversed(numbers):
        position = str(number + 1)
        _ = _iptables(['-D', 'PREROUTING', position])

# ################################################################################################################################

def remove_redirect(port:'int') -> 'None':
    """ Hands the port of the progress page over to the container, for each new connection from now on.
    """
    rule = _get_rule(port)

    check = ['-C', 'PREROUTING']
    check.extend(rule)

    delete = ['-D', 'PREROUTING']
    delete.extend(rule)

    while True:
        result = _iptables(check)
        if result.exit_code != 0:
            break
        _ = _iptables(delete)

# ################################################################################################################################
# ################################################################################################################################
