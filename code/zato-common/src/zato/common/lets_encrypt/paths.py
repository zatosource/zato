# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# Zato
from zato.common.api import Lets_Encrypt

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SSLPaths:

    # The directory that all the files below are in.
    ssl_dir: 'str'

    # The file HAProxy reads the certificate and its key from.
    user_pem: 'str'

    # The self-signed certificate generated when the container starts.
    auto_pem: 'str'

    # The certificate of the user's own, which takes precedence over all the others.
    own_pem: 'str'

    # Where the ACME client keeps its account and the certificates it obtained.
    data_dir: 'str'

    # The certificate and its key as the ACME client stores them.
    lego_pem: 'str'

    # Whether Let's Encrypt is enabled, as set in the Dashboard.
    settings: 'str'

    # The outcome of the most recent checks.
    status: 'str'

    # Held by whichever process runs the ACME client, so that no two of them listen on the same port at once.
    lock: 'str'

# ################################################################################################################################
# ################################################################################################################################

def get_paths(environ:'strstrdict') -> 'SSLPaths':
    """ Returns the paths to all the files that certificates are kept in.
    """
    if Lets_Encrypt.Env.SSL_Dir in environ:
        ssl_dir = environ[Lets_Encrypt.Env.SSL_Dir]
    else:
        ssl_dir = Lets_Encrypt.Default.SSL_Dir

    data_dir = os.path.join(ssl_dir, Lets_Encrypt.File.Data_Dir)

    out = SSLPaths()
    out.ssl_dir = ssl_dir
    out.user_pem = os.path.join(ssl_dir, Lets_Encrypt.File.User_PEM)
    out.auto_pem = os.path.join(ssl_dir, Lets_Encrypt.File.Auto_PEM)
    out.own_pem = os.path.join(ssl_dir, Lets_Encrypt.File.Own_PEM)
    out.data_dir = data_dir
    out.lego_pem = os.path.join(data_dir, 'certificates', Lets_Encrypt.Cert_Name + '.pem')
    out.settings = os.path.join(data_dir, Lets_Encrypt.File.Settings)
    out.status = os.path.join(data_dir, Lets_Encrypt.File.Status)
    out.lock = os.path.join(data_dir, Lets_Encrypt.File.Lock)

    return out

# ################################################################################################################################
# ################################################################################################################################
