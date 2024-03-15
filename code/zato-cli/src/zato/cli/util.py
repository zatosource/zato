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

def get_totp_info_from_args(args, default_key_label=None): # type: ignore
    """ Returns a key and its label extracted from command line arguments
    or auto-generates a new pair if they are missing in args.
    """

    # PyOTP
    import pyotp

    # Zato
    from zato.common.crypto.totp_ import TOTPManager
    from zato.common.api import TOTP

    default_key_label = default_key_label or TOTP.default_label # type: ignore

    # If there was a key given on input, we need to validate it,
    # this reports an error if the key cannot be used.
    if args.key:
        totp = pyotp.TOTP(args.key)
        _ = totp.now()

        # If we are here, it means that the key was valid
        key = args.key # type: ignore
    else:
        key = TOTPManager.generate_totp_key()

    return key, args.key_label if args.key_label else default_key_label # type: ignore

# ################################################################################################################################

def run_cli_command(command_class:'any_', config:'anydict', path:'any_') -> 'None':

    # stdlib
    import os

    # Bunch
    from bunch import Bunch

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
