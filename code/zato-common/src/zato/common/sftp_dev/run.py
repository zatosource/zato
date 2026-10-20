# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Development SFTP servers for local file transfer work - three OpenSSH servers in containers on fixed ports,
# started from the repository Makefile target `make sftp`, with the output of each logged under its own label.

# stdlib
import logging
import os
import signal
import sys
import time

# Zato
from zato.common.sftp_dev.constants import Port_Password_User1, Port_Password_User2, Port_Public_Key_User3, \
    User1_Password, User1_Username, User2_Password, User2_Username, User3_Username, default_data_dir, \
    sample_tree_for_port
from zato.common.sftp_dev.server import Auth_Mode, DevSFTPServer, load_login_user_public_keys, pull_image

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# How often the main thread wakes up while the servers run, in seconds
_main_loop_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _configure_logging() -> 'None':
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

# ################################################################################################################################

def _new_server(
    port:'int',
    auth_mode:'Auth_Mode',
    username:'str',
    password:'str',
    public_key_paths:'strlist',
    data_dir:'str',
) -> 'DevSFTPServer':
    sample_directories, sample_files = sample_tree_for_port(port)
    log_label = 'sftp-{}'.format(port)
    server_data_dir = os.path.join(data_dir, 'server-{}'.format(port))

    out = DevSFTPServer(
        port,
        auth_mode,
        username,
        password,
        public_key_paths,
        server_data_dir,
        log_label,
        sample_directories,
        sample_files,
    )

    return out

# ################################################################################################################################

def _build_servers(data_dir:'str') -> 'list':
    public_key_paths = load_login_user_public_keys()

    if not public_key_paths:
        message = 'No public keys found under ~/.ssh for the public-key server on port {}. Expected one of: id_ed25519.pub, id_rsa.pub, id_ecdsa.pub'
        raise Exception(message.format(Port_Public_Key_User3))

    servers = [
        _new_server(
            Port_Password_User1,
            'password',
            User1_Username,
            User1_Password,
            [],
            data_dir,
        ),
        _new_server(
            Port_Password_User2,
            'password',
            User2_Username,
            User2_Password,
            [],
            data_dir,
        ),
        _new_server(
            Port_Public_Key_User3,
            'publickey',
            User3_Username,
            '',
            public_key_paths,
            data_dir,
        ),
    ]

    return servers

# ################################################################################################################################

def main() -> 'None':
    _configure_logging()

    data_dir = default_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    servers = _build_servers(data_dir)

    pull_image()

    for server in servers:
        server.start()

    shutdown = False

    def on_signal(signum:'int', _frame:'object') -> 'None':
        nonlocal shutdown
        shutdown = True

    _ = signal.signal(signal.SIGINT, on_signal)
    _ = signal.signal(signal.SIGTERM, on_signal)

    while not shutdown:
        time.sleep(_main_loop_interval)

    for server in servers:
        server.stop()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
