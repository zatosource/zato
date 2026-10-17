# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The data masking logic of the MCP gateway wizard, run by Node against the industry sets the server loads.

# stdlib
import os
import subprocess

# Zato
from zato.common.json_internal import dumps
from zato.common.util.safeguards.masking import get_masking_config

# ################################################################################################################################
# ################################################################################################################################

# The repository's code directory, four levels above this file.
_code_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# The script under test and the wizard scripts it loads.
_script_path     = os.path.join(_code_directory, 'tests', 'js', 'zato-web-admin', 'mcp-wizard-masking.js')
_static_directory = os.path.join(_code_directory, 'zato-web-admin', 'src', 'zato', 'admin', 'static', 'js', 'gateway',
    'mcp-wizard')

# How long the script may run for, in seconds.
_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def test_the_wizard_masking_logic() -> 'None':

    # The sets go to the script in the form the page embeds them ..
    sets_text = dumps(get_masking_config())

    result = subprocess.run(
        ['node', _script_path, _static_directory],
        input=sets_text,
        capture_output=True,
        text=True,
        timeout=_timeout,
    )

    # .. and every case the script runs must pass.
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'not ok' not in result.stdout, result.stdout

# ################################################################################################################################
# ################################################################################################################################
