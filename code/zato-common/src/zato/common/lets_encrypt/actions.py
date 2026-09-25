# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.certificate import get_certificate_info
from zato.common.lets_encrypt.client import CertificateNotObtained, check_port, connect, install_pem, obtain, read_file, \
     use_generated
from zato.common.lets_encrypt.config import get_config, get_haproxy_config, get_public_ip, is_enabled
from zato.common.lets_encrypt.paths import get_paths
from zato.common.lets_encrypt.state import clear_progress, LockBusy, load_progress, load_status, save_certificate_check, \
     save_is_enabled, save_port_check, save_progress

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import anydict, strnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_ssl_config(environ:'strstrdict') -> 'anydict':
    """ Returns what the SSL config page shows.
    """
    paths = get_paths(environ)
    status = load_status(paths)
    progress = load_progress(paths)
    is_lets_encrypt_enabled = is_enabled(environ)

    if is_lets_encrypt_enabled:
        certificate = get_certificate_info(paths)
    else:
        certificate = None

    if certificate is None:
        certificate_dict = None
    else:
        certificate_dict = certificate.to_dict()

    if progress is None:
        progress_dict = None
    else:
        progress_dict = progress.to_dict()

    out = {
        'is_enabled': is_lets_encrypt_enabled,
        'progress': progress_dict,
        'certificate': certificate_dict,
        'status': status.to_dict(),
    }

    return out

# ################################################################################################################################

def _get_public_dns_name(public_ip:'str') -> 'strnone':
    """ Returns the name the public IP address resolves back to, or None if it has no reverse DNS entry.
    """
    try:
        host_name, _, _ = socket.gethostbyaddr(public_ip)
    except OSError as exception:
        logger.info('Public IP %s has no reverse DNS entry: %s', public_ip, exception)
        return None

    return host_name

# ################################################################################################################################

def get_public_endpoint(environ:'strstrdict') -> 'anydict':
    """ Returns the public IP address of this host and its reverse DNS name, both None if the internet cannot be reached.
    """
    if Lets_Encrypt.Env.Public_IP in environ:
        public_ip = environ[Lets_Encrypt.Env.Public_IP]
    else:
        try:
            public_ip = get_public_ip(Lets_Encrypt.Default.Public_IP_URL)
        except Exception as exception:
            logger.warning('Public IP could not be checked: %s', exception)
            public_ip = None

    if public_ip is None:
        public_dns_name = None
    else:
        public_dns_name = _get_public_dns_name(public_ip)

    out = {
        'public_ip': public_ip,
        'public_dns_name': public_dns_name,
    }

    return out

# ################################################################################################################################

def set_lets_encrypt(environ:'strstrdict', is_enabled:'bool') -> 'None':
    """ Stores the setting from the Dashboard and, when disabling, reinstalls the generated certificate.
    """
    paths = get_paths(environ)
    save_is_enabled(paths, is_enabled)
    clear_progress(paths)

    if not is_enabled:
        haproxy_config = get_haproxy_config(environ)
        _ = use_generated(paths, haproxy_config, needs_reload=True)

# ################################################################################################################################

def _has_valid_certificate(paths:'SSLPaths') -> 'bool':
    """ Returns whether a certificate from Let's Encrypt was obtained before and has not expired yet.
    """
    certificate = get_certificate_info(paths)

    if certificate is None:
        return False

    not_after = datetime.fromisoformat(certificate.not_after_utc)
    now = datetime.now(timezone.utc)

    out = not_after > now
    return out

# ################################################################################################################################

def enable_now(environ:'strstrdict') -> 'None':
    """ Installs an existing valid certificate or obtains a new one, recording each step in the progress file.
    """
    paths = get_paths(environ)
    step = Lets_Encrypt.Step.Install

    try:
        config = get_config(environ)

        # A certificate from before is good enough, so there is nothing to ask Let's Encrypt for ..
        if _has_valid_certificate(paths):
            save_progress(paths, step, Lets_Encrypt.Progress_State.Running)
            pem = read_file(paths.lego_pem)
            _ = install_pem(paths, config.haproxy_config, pem, needs_reload=True)
            save_progress(paths, step, Lets_Encrypt.Progress_State.Done)
            return

        # .. otherwise Let's Encrypt must be able to reach this host ..
        step = Lets_Encrypt.Step.Port
        is_ready = check_port(config)

        # .. which check_port has already recorded the reason for if it cannot ..
        if not is_ready:
            return

        # .. and this host must be able to reach Let's Encrypt ..
        step = Lets_Encrypt.Step.Connect
        save_progress(paths, step, Lets_Encrypt.Progress_State.Running)
        connect(config)

        # .. and only then is a certificate requested, which records the remaining steps itself.
        step = Lets_Encrypt.Step.Request
        _ = obtain(config, needs_reload=True)

    except LockBusy:
        logger.info('Certificate check skipped, another one is running')
        save_progress(paths, step, Lets_Encrypt.Progress_State.Error, 'Another check is running')

    # A failure of the ACME client itself is already in the status and the progress ..
    except CertificateNotObtained as exception:
        logger.warning('%s', exception)

    # .. whereas anything that failed before it ran is not.
    except Exception as exception:
        save_certificate_check(paths, False, str(exception))
        save_progress(paths, step, Lets_Encrypt.Progress_State.Error, str(exception))
        logger.warning('Certificate could not be obtained: %s', exception)

# ################################################################################################################################

def check_port_now(environ:'strstrdict') -> 'None':
    """ Checks whether Let's Encrypt can reach this host through port 443, recording the outcome in the status.
    """
    paths = get_paths(environ)
    clear_progress(paths)

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
