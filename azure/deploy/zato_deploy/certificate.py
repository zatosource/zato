# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import platform
import shutil
import tarfile
import tempfile
import urllib.request

# Zato
from zato_deploy.common import Config, Lego, Path, Port, Stage_ID, StageFailed
from zato_deploy.process import run_logged
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

_Download_Timeout = 120
_Lego_Mode        = 0o755
_Self_Signed_Days = 30

# ################################################################################################################################
# ################################################################################################################################

def _download_lego(progress:'Progress') -> 'None':
    """ Installs the same ACME client that the container runs.
    """
    machine = platform.machine()
    architecture = Lego.Architectures[machine]
    url = Lego.URL_Template.format(version=Lego.Version, architecture=architecture)

    progress.log(f'Downloading lego {Lego.Version}')

    with tempfile.TemporaryDirectory() as temp_dir:

        # Get the archive ..
        archive_path = os.path.join(temp_dir, 'lego.tar.gz')
        with urllib.request.urlopen(url, timeout=_Download_Timeout) as response:
            with open(archive_path, 'wb') as archive_file:
                shutil.copyfileobj(response, archive_file)

        # .. and take the binary out of it.
        with tarfile.open(archive_path) as archive:
            archive.extract('lego', temp_dir, filter='data')

        binary_path = os.path.join(temp_dir, 'lego')
        _ = shutil.move(binary_path, Path.Lego)

    os.chmod(Path.Lego, _Lego_Mode)

# ################################################################################################################################

def _run_lego(progress:'Progress', config:'Config') -> 'None':
    """ Obtains the certificate with the very arguments the container uses, so that it finds this one and keeps renewing it.
    """
    command = [
        Path.Lego,
        '--log.format', 'text',
        'run',
        '--accept-tos',
        '--server', Lego.Server,
        '--path', Path.Lets_Encrypt_Dir,
        '--cert.name', Lego.Cert_Name,
        '--tls',
        '--tls.address', f':{Port.ACME}',
        '--pem',
        '--no-random-sleep',
        '--force-cert-domains',
        '--domains', config.fqdn,
        '--profile', Lego.Profile,
    ]

    run_logged(progress, command)

# ################################################################################################################################

def _create_self_signed(progress:'Progress', config:'Config') -> 'None':
    """ Creates the certificate the page is served with when Let's Encrypt could not issue one.
    """
    command = [
        'openssl', 'req', '-x509',
        '-newkey', 'ec',
        '-pkeyopt', 'ec_paramgen_curve:prime256v1',
        '-nodes',
        '-days', str(_Self_Signed_Days),
        '-subj', f'/CN={config.fqdn}',
        '-addext', f'subjectAltName=DNS:{config.fqdn}',
        '-keyout', Path.Self_Signed_Key,
        '-out', Path.Self_Signed_Cert,
    ]

    run_logged(progress, command)

    with open(Path.Self_Signed_Cert) as cert_file:
        cert = cert_file.read()

    with open(Path.Self_Signed_Key) as key_file:
        key = key_file.read()

    with open(Path.Self_Signed_PEM, 'w') as pem_file:
        _ = pem_file.write(cert + key)

    os.chmod(Path.Self_Signed_PEM, 0o600)

# ################################################################################################################################
# ################################################################################################################################

def obtain_certificate(progress:'Progress', config:'Config') -> 'str':
    """ Returns the path to the certificate the page is served with, which is the one from Let's Encrypt if it could be obtained.
    """
    progress.advance_to(Stage_ID.Certificate)
    os.makedirs(Path.Lets_Encrypt_Dir, exist_ok=True)

    # Obtain the certificate ..
    try:
        _download_lego(progress)
        _run_lego(progress, config)

    # .. and if Let's Encrypt did not issue it, the deployment goes on with a self-signed one,
    # while the container keeps asking Let's Encrypt itself.
    except (OSError, StageFailed) as exception:
        progress.log(f'Let\'s Encrypt certificate not obtained: {exception}', 'error')
        _create_self_signed(progress, config)
        out = Path.Self_Signed_PEM

    else:
        progress.log(f'Certificate for {config.fqdn} obtained', 'ok')
        out = Path.Lets_Encrypt_PEM

    return out

# ################################################################################################################################
# ################################################################################################################################
