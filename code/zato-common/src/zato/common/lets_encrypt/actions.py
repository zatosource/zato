# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.common.lets_encrypt.certificate import get_certificate_info
from zato.common.lets_encrypt.client import CertificateNotObtained, check_port, obtain, use_generated
from zato.common.lets_encrypt.config import get_config, get_haproxy_config, is_enabled
from zato.common.lets_encrypt.paths import get_paths
from zato.common.lets_encrypt.state import get_running_operation, LockBusy, load_status, save_certificate_check, \
     save_is_enabled, save_port_check

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_ssl_config(environ:'strstrdict') -> 'anydict':
    """ Returns everything the SSL config page in the Dashboard shows, all of it from Let's Encrypt only.
    """
    paths = get_paths(environ)
    status = load_status(paths)
    is_lets_encrypt_enabled = is_enabled(environ)

    if is_lets_encrypt_enabled:
        certificate = get_certificate_info(paths)
    else:
        certificate = None

    if certificate is None:
        certificate_dict = None
    else:
        certificate_dict = certificate.to_dict()

    out = {
        'is_enabled': is_lets_encrypt_enabled,
        'running_operation': get_running_operation(paths),
        'certificate': certificate_dict,
        'status': status.to_dict(),
    }

    return out

# ################################################################################################################################

def set_lets_encrypt(environ:'strstrdict', is_enabled:'bool') -> 'None':
    """ Stores the setting from the Dashboard. Enabling Let's Encrypt only stores it, because obtaining
    a certificate takes a while, and disabling it makes HAProxy present the generated certificate at once.
    """
    paths = get_paths(environ)
    save_is_enabled(paths, is_enabled)

    if not is_enabled:
        haproxy_config = get_haproxy_config(environ)
        _ = use_generated(paths, haproxy_config, needs_reload=True)

# ################################################################################################################################

def obtain_now(environ:'strstrdict') -> 'None':
    """ Obtains the certificate right after Let's Encrypt was enabled in the Dashboard, recording any failure in the status,
    which is where the Dashboard reads it from.
    """
    paths = get_paths(environ)

    try:
        config = get_config(environ)
        _ = obtain(config, needs_reload=True)
    except LockBusy:
        logger.info('Certificate check skipped, another one is running')

    # A failure of the ACME client itself is already in the status ..
    except CertificateNotObtained as exception:
        logger.warning('%s', exception)

    # .. whereas anything that failed before it ran is not.
    except Exception as exception:
        save_certificate_check(paths, False, str(exception))
        logger.warning('Certificate could not be obtained: %s', exception)

# ################################################################################################################################

def check_port_now(environ:'strstrdict') -> 'None':
    """ Checks whether Let's Encrypt can reach this host through port 443, recording the outcome in the status.
    """
    paths = get_paths(environ)

    try:
        config = get_config(environ)
        _ = check_port(config)
    except LockBusy:
        logger.info('Port check skipped, another check is running')
    except Exception as exception:
        save_port_check(paths, False, str(exception))
        logger.warning('Port could not be checked: %s', exception)

# ################################################################################################################################

def get_environ() -> 'strstrdict':
    """ Returns the environment variables the settings are read from.
    """
    out = dict(os.environ)
    return out

# ################################################################################################################################
# ################################################################################################################################
