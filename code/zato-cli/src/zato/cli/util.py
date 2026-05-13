# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from argparse import Namespace
    from zato.common.typing_ import any_, anydict
    Namespace = Namespace

# ################################################################################################################################

# ################################################################################################################################

def run_cli_command(command_class:'any_', config:'anydict', path:'any_') -> 'None':

    # stdlib
    import os

    # Bunch
    from zato.common.ext.bunch import Bunch

    args = Bunch()
    args.verbose = True
    args.store_log = False
    args.store_config = False
    args.path = path or os.environ['ZATO_SERVER_BASE_DIR']
    args.password = None
    args.skip_stdout = False
    args.update(config)

    command = command_class(args)
    command.execute(args)

# ################################################################################################################################
