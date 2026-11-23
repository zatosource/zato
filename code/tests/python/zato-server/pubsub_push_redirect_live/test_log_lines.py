# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines that a running server writes to its log for each redirect of a push that it follows.

# stdlib
from http.client import PERMANENT_REDIRECT, TEMPORARY_REDIRECT

# pytest
import pytest

# Test support
from redirect_live_support import get_endpoint, get_scenario_id, get_source_path, get_target_path, LiveConfig, \
    Log_Scenarios, Loopback_First, publish, redirect_to, wait_for_requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redirect_live_support import Scenario
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# What the line of each followed redirect contains
_redirect_text = 'redirected with'

# What the line of a permanent redirect adds
_moved_text = 'moved permanently'

# The status that each scenario redirects with
_statuses = {
    'log-temporary': TEMPORARY_REDIRECT,
    'log-permanent': PERMANENT_REDIRECT,
}

# ################################################################################################################################
# ################################################################################################################################

def _get_redirect_lines(msg_id:'str') -> 'strlist':
    """ Returns the lines of the server log that describe a followed redirect of the message.
    """
    out:'strlist' = []

    with open(LiveConfig.server_log_path) as log_file:
        for line in log_file:

            if msg_id not in line:
                continue

            if _redirect_text in line:
                line = line.rstrip('\n')
                out.append(line)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Log_Scenarios, ids=get_scenario_id)
def test_one_line_per_followed_redirect(scenario:'Scenario') -> 'None':

    first = get_endpoint(Loopback_First)
    status = _statuses[scenario.name]

    source_path = get_source_path(scenario)
    target_path = get_target_path(scenario)

    source = first.http_base + source_path
    target = first.http_base + target_path

    response = redirect_to(target, status)
    first.set_responses(source_path, [response])

    data = f'Order 1 of Jane Doe, scenario {scenario.name}'
    msg_id = publish(scenario, data)

    _ = wait_for_requests(first, target_path, 1)

    lines = _get_redirect_lines(msg_id)
    line_count = len(lines)

    assert line_count == 1, lines

    # The line is at the INFO level and names the status, the source and the target ..
    line = lines[0]

    assert 'INFO' in line
    assert f' {status} ' in line
    assert f'`{source}`' in line
    assert f'`{target}`' in line

    # .. and only a permanent redirect states that the endpoint moved.
    is_moved = _moved_text in line
    assert is_moved == (status == PERMANENT_REDIRECT)

# ################################################################################################################################
# ################################################################################################################################
