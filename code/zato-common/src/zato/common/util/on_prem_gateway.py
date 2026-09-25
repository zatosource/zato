# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import platform
import subprocess
import time
from logging import basicConfig, getLogger, INFO

# requests
import requests

# Zato
from zato.common.api import On_Prem_Gateway

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The names the release assets use for the machine types the container runs on.
_Architecture_Map = {
    'x86_64': 'amd64',
    'aarch64': 'arm64',
}

_Request_Timeout = 30
_Binary_Mode = 0o755

# The hub releases its listeners on shutdown, so a new one is started only once the old one has exited.
_Stop_Wait_Attempts = 50
_Stop_Wait_Interval = 0.2

# ################################################################################################################################
# ################################################################################################################################

def is_installed() -> 'bool':
    """ Whether this environment has the gateway binary, which is the case in the container only.
    """
    return os.path.exists(On_Prem_Gateway.Update.Binary_Path)

# ################################################################################################################################

def get_installed_version() -> 'str':
    """ Returns the version of the installed binary, e.g. 4.1.c9020c1.
    """
    output = subprocess.check_output([On_Prem_Gateway.Update.Binary_Path, 'version'], text=True)
    return output.split()[-1]

# ################################################################################################################################

def get_latest_version() -> 'str':
    """ Returns the version of the latest published release.
    """
    response = requests.head(On_Prem_Gateway.Update.Latest_URL, allow_redirects=True, timeout=_Request_Timeout)
    response.raise_for_status()

    # The latest release redirects to the page of its own tag.
    return response.url.rsplit('/', 1)[-1]

# ################################################################################################################################

def update_binary() -> 'bool':
    """ Replaces the installed binary with the latest release and returns True if it was replaced.
    """
    installed_version = get_installed_version()
    latest_version = get_latest_version()

    if installed_version == latest_version:
        logger.info('On-prem gateway %s is the latest version', installed_version)
        return False

    architecture = _Architecture_Map[platform.machine()]
    url = On_Prem_Gateway.Update.Download_URL.format(version=latest_version, architecture=architecture)

    response = requests.get(url, timeout=_Request_Timeout)
    response.raise_for_status()

    binary_path = On_Prem_Gateway.Update.Binary_Path
    new_path = binary_path + '.new'

    with open(new_path, 'wb') as new_file:
        _ = new_file.write(response.content)

    os.chmod(new_path, _Binary_Mode)

    # A rename replaces the file without affecting a hub that is running from it.
    os.replace(new_path, binary_path)

    logger.info('On-prem gateway updated from %s to %s', installed_version, latest_version)
    return True

# ################################################################################################################################

def restart_hub(log_dir:'str') -> 'None':
    """ Stops the hub and starts it again from the binary installed now.
    """
    command_line = On_Prem_Gateway.Update.Binary_Path + ' hub'

    _ = subprocess.run(['pkill', '-f', command_line], capture_output=True)

    for _ignored in range(_Stop_Wait_Attempts):
        result = subprocess.run(['pgrep', '-f', command_line], capture_output=True)
        if result.returncode != 0:
            break
        time.sleep(_Stop_Wait_Interval)

    log_path = os.path.join(log_dir, On_Prem_Gateway.Update.Log_File)

    with open(log_path, 'a') as log_file:
        _ = subprocess.Popen(
            [On_Prem_Gateway.Update.Binary_Path, 'hub'],
            stdout=log_file,
            stderr=log_file,
            start_new_session=True
        )

    logger.info('On-prem gateway hub restarted')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # The container runs this before it starts the hub, so the binary is replaced and nothing is restarted.
    if is_installed():
        _ = update_binary()

# ################################################################################################################################
# ################################################################################################################################
