# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import os
import socket
import sys
from datetime import datetime, timedelta, timezone
from json import dumps

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509.oid import NameOID

# Zato
from zato.common.api import Lets_Encrypt

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class DevCA:
    """ Settings of the local ACME server (Pebble) used in development.
    """

    # Must resolve to Loopback in /etc/hosts
    Host = 'zato.test'
    Loopback = '127.0.0.1'

    ACME_Port = 14000
    Management_Port = 15000
    HTTP_Challenge_Port = 5002
    TLS_Challenge_Port = 5001

    Default_Dir = '~/env/lets-encrypt-dev-ca'

    # In seconds - 90 days and 6 days
    Default_Validity = 7776000
    Short_Lived_Validity = 518400

    Validity_Days = 3650

    Pebble_Binary_Name = 'pebble'
    Env_File_Name = 'env.sh'

# ################################################################################################################################
# ################################################################################################################################

def _check_hosts() -> 'None':
    """ Raises an exception if DevCA.Host does not resolve to the loopback address.
    """
    try:
        address = socket.gethostbyname(DevCA.Host)
    except socket.gaierror:
        raise Exception(f'Add "{DevCA.Loopback} {DevCA.Host}" to /etc/hosts') from None

    if address != DevCA.Loopback:
        raise Exception(f'{DevCA.Host} points to {address} instead of {DevCA.Loopback} in /etc/hosts')

# ################################################################################################################################

def _write(path:'str', data:'str') -> 'None':
    with open(path, 'w') as output_file:
        _ = output_file.write(data)

# ################################################################################################################################

def _key_pem(key:'ec.EllipticCurvePrivateKey') -> 'str':
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode()
    return out

# ################################################################################################################################

def _certificate_pem(certificate:'x509.Certificate') -> 'str':
    out = certificate.public_bytes(Encoding.PEM).decode()
    return out

# ################################################################################################################################

def _build_certificate(
    subject:'x509.Name',
    issuer:'x509.Name',
    public_key:'ec.EllipticCurvePublicKey',
    signing_key:'ec.EllipticCurvePrivateKey',
    is_ca:'bool',
    names:'strlist',
) -> 'x509.Certificate':
    """ Builds a certificate for the given names, or a CA if there are none.
    """
    now = datetime.now(timezone.utc)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(now + timedelta(days=DevCA.Validity_Days))
    builder = builder.add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=True)

    if names:
        alt_names = []
        for name in names:
            try:
                alt_names.append(x509.IPAddress(ipaddress.ip_address(name)))
            except ValueError:
                alt_names.append(x509.DNSName(name))
        builder = builder.add_extension(x509.SubjectAlternativeName(alt_names), critical=False)

    out = builder.sign(signing_key, hashes.SHA256())
    return out

# ################################################################################################################################

def _name(common_name:'str') -> 'x509.Name':
    out = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Zato Dev CA'),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    return out

# ################################################################################################################################

def _generate_pebble_certificates(pebble_dir:'str') -> 'str':
    """ Generates the CA and Pebble's server certificate if they do not exist yet and returns the path to the CA certificate.
    """
    ca_cert_path = os.path.join(pebble_dir, 'ca.crt')
    server_cert_path = os.path.join(pebble_dir, 'server.crt')
    server_key_path = os.path.join(pebble_dir, 'server.key')

    if os.path.exists(ca_cert_path):
        return ca_cert_path

    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_name = _name('Zato Dev CA')
    ca_cert = _build_certificate(ca_name, ca_name, ca_key.public_key(), ca_key, True, [])

    server_key = ec.generate_private_key(ec.SECP256R1())
    server_cert = _build_certificate(_name('localhost'), ca_name, server_key.public_key(), ca_key, False,
        ['localhost', DevCA.Loopback])

    _write(ca_cert_path, _certificate_pem(ca_cert))
    _write(server_cert_path, _certificate_pem(server_cert))
    _write(server_key_path, _key_pem(server_key))

    return ca_cert_path

# ################################################################################################################################

def _generate_auto_pem(ssl_dir:'str') -> 'None':
    """ Generates the self-signed auto.pem if it does not exist yet.
    """
    auto_pem_path = os.path.join(ssl_dir, Lets_Encrypt.File.Auto_PEM)

    if os.path.exists(auto_pem_path):
        return

    key = ec.generate_private_key(ec.SECP256R1())
    name = _name('localhost')
    certificate = _build_certificate(name, name, key.public_key(), key, False, ['localhost', DevCA.Loopback])

    _write(auto_pem_path, _certificate_pem(certificate) + _key_pem(key))

# ################################################################################################################################

def _build_pebble_config(pebble_dir:'str') -> 'str':
    """ Writes Pebble's configuration and returns the path to it.
    """
    config = {
        'pebble': {
            'listenAddress': f'{DevCA.Loopback}:{DevCA.ACME_Port}',
            'managementListenAddress': f'{DevCA.Loopback}:{DevCA.Management_Port}',
            'certificate': os.path.join(pebble_dir, 'server.crt'),
            'privateKey': os.path.join(pebble_dir, 'server.key'),
            'httpPort': DevCA.HTTP_Challenge_Port,
            'tlsPort': DevCA.TLS_Challenge_Port,
            'ocspResponderURL': '',
            'externalAccountBindingRequired': False,
            'domainBlocklist': [],
            'retryAfter': {
                'authz': 1,
                'order': 1,
            },
            'keyAlgorithm': 'ecdsa',
            'profiles': {
                Lets_Encrypt.DNS_Profile: {
                    'description': 'The default profile',
                    'validityPeriod': DevCA.Default_Validity,
                },
                Lets_Encrypt.IP_Profile: {
                    'description': 'The profile of IP address certificates',
                    'validityPeriod': DevCA.Short_Lived_Validity,
                },
            },
        }
    }

    out = os.path.join(pebble_dir, 'pebble-config.json')
    _write(out, dumps(config, indent=4))

    return out

# ################################################################################################################################

def build_environ(base_dir:'str', ca_cert_path:'str') -> 'strstrdict':
    """ Returns the environment variables that point a server at this CA.
    """
    directory_url = f'https://{DevCA.Loopback}:{DevCA.ACME_Port}/dir'

    out = {
        Lets_Encrypt.Env.Server: directory_url,
        Lets_Encrypt.Env.Staging_Server: directory_url,
        Lets_Encrypt.Env.CA_File: ca_cert_path,
        Lets_Encrypt.Env.Port: str(DevCA.TLS_Challenge_Port),
        Lets_Encrypt.Env.Public_IP: DevCA.Loopback,
        Lets_Encrypt.Env.Subject_Alt_Name: f'subjectAltName=DNS:{DevCA.Host},IP:{DevCA.Loopback}',
        Lets_Encrypt.Env.SSL_Dir: os.path.join(base_dir, 'ssl'),
        Lets_Encrypt.Env.HAProxy_Config: os.path.join(base_dir, 'haproxy.cfg'),
    }

    return out

# ################################################################################################################################

def main(base_dir:'str') -> 'None':
    """ Prepares the directory and runs Pebble in the foreground.
    """
    _check_hosts()

    pebble_dir = os.path.join(base_dir, 'pebble')
    ssl_dir = os.path.join(base_dir, 'ssl')

    os.makedirs(pebble_dir, exist_ok=True)
    os.makedirs(ssl_dir, exist_ok=True)

    ca_cert_path = _generate_pebble_certificates(pebble_dir)
    _generate_auto_pem(ssl_dir)
    config_path = _build_pebble_config(pebble_dir)

    environ = build_environ(base_dir, ca_cert_path)
    exports = [f'export {name}="{value}"' for name, value in environ.items()]
    env_file_path = os.path.join(base_dir, DevCA.Env_File_Name)
    _write(env_file_path, '\n'.join(exports) + '\n')

    print(f'Dev CA at https://{DevCA.Loopback}:{DevCA.ACME_Port}/dir')
    print(f'Before starting the server, run: source {env_file_path}')
    print('')
    for export in exports:
        print(export)
    print('')

    # Without these, Pebble sleeps before each validation and rejects a share of nonces on purpose
    pebble_env = dict(os.environ)
    pebble_env['PEBBLE_VA_NOSLEEP'] = '1'
    pebble_env['PEBBLE_WFE_NONCEREJECT'] = '0'

    pebble_path = os.path.join(os.path.dirname(sys.executable), DevCA.Pebble_Binary_Name)

    sys.stdout.flush()
    os.execvpe(pebble_path, [pebble_path, '-config', config_path], pebble_env)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.expanduser(DevCA.Default_Dir)

    main(os.path.abspath(base_dir))

# ################################################################################################################################
# ################################################################################################################################
