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

# New connections to the Dashboard's port go to this program for as long as the rule exists,
# while connections that were accepted already stay where they are.
_Rule = ['-p', 'tcp', '--dport', str(Port.Dashboard), '-j', 'REDIRECT', '--to-ports', str(Port.Deploy)]

# How the rule reads in the output of iptables -S.
_Rule_Listed = f'--dport {Port.Dashboard} -j REDIRECT --to-ports {Port.Deploy}'

_Rule_Prefix = '-A PREROUTING '

# ################################################################################################################################
# ################################################################################################################################

def _iptables(arguments:'strlist') -> 'CommandResult':

    command = ['iptables', '-t', 'nat']
    command.extend(arguments)

    out = run_command(command)
    return out

# ################################################################################################################################

def _get_rule_numbers() -> 'tuple[bool, list[int]]':
    """ Returns whether the rule is the first one in PREROUTING and the numbers of all its copies there.
    """
    result = _iptables(['-S', 'PREROUTING'])
    listed = result.stdout.splitlines()

    numbers:'list[int]' = []
    rule_number = 0

    for line in listed:
        if not line.startswith(_Rule_Prefix):
            continue
        rule_number += 1
        if _Rule_Listed in line:
            numbers.append(rule_number)

    is_first = 1 in numbers

    out = (is_first, numbers)
    return out

# ################################################################################################################################
# ################################################################################################################################

def add_redirect() -> 'None':
    """ Sends new connections to the Dashboard's port to this program.
    """
    arguments = ['-I', 'PREROUTING', '1']
    arguments.extend(_Rule)

    result = _iptables(arguments)

    if result.exit_code != 0:
        logger.warning('Redirect could not be added: %s', result.stderr)

# ################################################################################################################################

def keep_redirect_first() -> 'None':
    """ Moves the rule back to the top of PREROUTING, because Docker adds rules of its own there.
    """
    is_first, numbers = _get_rule_numbers()

    if is_first:
        return

    # Inserting the rule first means there is no moment without one ..
    add_redirect()

    # .. and the copies further down, now one position lower each, are deleted from the bottom up.
    for number in reversed(numbers):
        position = str(number + 1)
        _ = _iptables(['-D', 'PREROUTING', position])

# ################################################################################################################################

def remove_redirect() -> 'None':
    """ Hands the Dashboard's port over to the container, for each new connection from now on.
    """
    check = ['-C', 'PREROUTING']
    check.extend(_Rule)

    delete = ['-D', 'PREROUTING']
    delete.extend(_Rule)

    while True:
        result = _iptables(check)
        if result.exit_code != 0:
            break
        _ = _iptables(delete)

# ################################################################################################################################
# ################################################################################################################################
