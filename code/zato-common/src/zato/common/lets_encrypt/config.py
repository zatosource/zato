# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# requests
import requests

# Zato
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.paths import get_paths
from zato.common.lets_encrypt.state import load_is_enabled
from zato.common.util.eval_ import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import strlist, strnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_Subject_Alt_Name_Prefix = 'subjectAltName='
_DNS_Prefix = 'DNS:'

_Public_IP_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LetsEncryptConfig:

    # The directory of the ACME server certificates are requested from.
    server: 'str'

    # The ACME server that checks whether this host can be reached, without issuing a certificate that counts.
    staging_server: 'str'

    # The CA that the ACME server's own certificate is trusted through, set only when it is not a public one.
    ca_file: 'strnone'

    # The DNS names the certificate is for, or the public IP address if there are no DNS names.
    domains: 'strlist'

    # Whether the certificate is for an IP address, which requires the short-lived profile.
    is_ip: 'bool'

    # The port the ACME client listens on while the ACME server validates the challenge.
    port: 'int'

    # The files that certificates are kept in.
    paths: 'SSLPaths'

    # The configuration of the HAProxy process that is reloaded after each new certificate.
    haproxy_config: 'str'

# ################################################################################################################################
# ################################################################################################################################

def has_own_certificate(paths:'SSLPaths') -> 'bool':
    """ Returns whether the user provided a certificate of their own, in which case Let's Encrypt is never used.
    """
    out = os.path.exists(paths.own_pem)
    return out

# ################################################################################################################################

def is_enabled(environ:'strstrdict') -> 'bool':
    """ Returns whether certificates are to be obtained from Let's Encrypt.
    """
    paths = get_paths(environ)

    # A certificate of the user's own always takes precedence ..
    if has_own_certificate(paths):
        return False

    # .. then comes what was set in the Dashboard ..
    is_enabled_in_dashboard = load_is_enabled(paths)

    if is_enabled_in_dashboard is not None:
        return is_enabled_in_dashboard

    # .. and only then the environment variable, with an absent one meaning that the feature is off.
    if Lets_Encrypt.Env.Use_Lets_Encrypt not in environ:
        return False

    out = as_bool(environ[Lets_Encrypt.Env.Use_Lets_Encrypt])
    return out

# ################################################################################################################################

def parse_dns_names(subject_alt_name:'str') -> 'strlist':
    """ Returns the DNS names from a subjectAltName value, such as subjectAltName=DNS:example.com,IP:127.0.0.1.
    """
    out:'strlist' = []

    value = subject_alt_name.strip()
    value = value.removeprefix(_Subject_Alt_Name_Prefix)

    for entry in value.split(','):
        entry = entry.strip()

        # IP addresses in the list are the ones of the self-signed certificate, not of this host ..
        if not entry.startswith(_DNS_Prefix):
            continue

        name = entry.removeprefix(_DNS_Prefix)

        # .. and names without a dot, such as localhost, are never issued by a public CA.
        if '.' not in name:
            continue

        out.append(name)

    return out

# ################################################################################################################################

def get_public_ip(url:'str') -> 'str':
    """ Returns the IP address that this host is reached through from the internet.
    """
    response = requests.get(url, timeout=_Public_IP_Timeout)
    response.raise_for_status()

    out = response.text.strip()
    return out

# ################################################################################################################################

def _get_value(environ:'strstrdict', name:'str', default:'str') -> 'str':
    """ Returns the value of a variable that has a default of its own.
    """
    if name in environ:
        out = environ[name]
    else:
        out = default

    return out

# ################################################################################################################################

def get_check_interval(environ:'strstrdict') -> 'int':
    """ Returns how many seconds pass between checks whether the certificate is due for renewal.
    """
    check_interval = _get_value(environ, Lets_Encrypt.Env.Check_Interval, str(Lets_Encrypt.Default.Check_Interval))

    out = int(check_interval)
    return out

# ################################################################################################################################

def get_haproxy_config(environ:'strstrdict') -> 'str':
    """ Returns the configuration of the HAProxy process that is reloaded after each new certificate.
    """
    out = _get_value(environ, Lets_Encrypt.Env.HAProxy_Config, Lets_Encrypt.Default.HAProxy_Config)
    return out

# ################################################################################################################################

def get_config(environ:'strstrdict') -> 'LetsEncryptConfig':
    """ Builds the configuration from environment variables.
    """
    out = LetsEncryptConfig()

    out.server = _get_value(environ, Lets_Encrypt.Env.Server, Lets_Encrypt.Default.Server)
    out.staging_server = _get_value(environ, Lets_Encrypt.Env.Staging_Server, Lets_Encrypt.Default.Staging_Server)
    out.paths = get_paths(environ)
    out.haproxy_config = get_haproxy_config(environ)

    port = _get_value(environ, Lets_Encrypt.Env.Port, str(Lets_Encrypt.Default.Port))
    out.port = int(port)

    # Only a non-public ACME server needs a CA of its own ..
    if Lets_Encrypt.Env.CA_File in environ:
        out.ca_file = environ[Lets_Encrypt.Env.CA_File]
    else:
        out.ca_file = None

    # .. the DNS names are the same ones that the self-signed certificate would be for ..
    if Lets_Encrypt.Env.Subject_Alt_Name in environ:
        dns_names = parse_dns_names(environ[Lets_Encrypt.Env.Subject_Alt_Name])
    else:
        dns_names = []

    # .. and if there are none, the certificate is for the public IP address of the host.
    if dns_names:
        out.domains = dns_names
        out.is_ip = False
    else:
        if Lets_Encrypt.Env.Public_IP in environ:
            public_ip = environ[Lets_Encrypt.Env.Public_IP]
        else:
            public_ip = get_public_ip(Lets_Encrypt.Default.Public_IP_URL)
        out.domains = [public_ip]
        out.is_ip = True

    return out

# ################################################################################################################################
# ################################################################################################################################
