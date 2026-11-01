# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The throwaway certificates of the pub/sub database containers. A plain chain has one CA that issues the server
# certificate directly. A bundle chain is arranged like the certificate bundle of Amazon RDS, in which the trust file
# holds the roots and the intermediate CAs of all regions and the server presents only its own certificate.
# A rotation chain is arranged like the Azure root certificates during a root rotation, in which the trust file holds
# two roots and the server presents its certificate together with the intermediate CA that issued it.

# stdlib
import ipaddress
import os
from datetime import timedelta

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

    certificatelist = list[x509.Certificate]
    generalnamelist = list[x509.GeneralName]

# ################################################################################################################################
# ################################################################################################################################

# How a CA issues the server certificate.
Chain_Plain    = 'plain'
Chain_Bundle   = 'bundle'
Chain_Rotation = 'rotation'

# How long the throwaway certificates are valid and how large their keys are.
_validity_days = 7
_key_size = 2048
_public_exponent = 65537

# The certificates are read by the database server in the container, which runs under the same user as the tests.
_certificate_mode = 0o644
_key_mode = 0o600

# The names of the certificate authorities.
_ca_name = 'Zato pub/sub test CA'
_other_region_root_name = 'Zato pub/sub test root CA - other region'
_previous_root_name = 'Zato pub/sub test root CA - previous'
_intermediate_name = 'Zato pub/sub test intermediate CA'

# ################################################################################################################################
# ################################################################################################################################

def _new_key() -> 'rsa.RSAPrivateKey':
    out = rsa.generate_private_key(public_exponent=_public_exponent, key_size=_key_size)
    return out

# ################################################################################################################################

def _write_key(path:'str', key:'rsa.RSAPrivateKey') -> 'None':
    data = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption())

    with open(path, 'wb') as key_file:
        _ = key_file.write(data)

    os.chmod(path, _key_mode)

# ################################################################################################################################

def _write_certificates(path:'str', certificates:'certificatelist') -> 'None':
    """ Writes one or more certificates into one PEM file, in the order given.
    """
    with open(path, 'wb') as certificate_file:
        for certificate in certificates:
            data = certificate.public_bytes(serialization.Encoding.PEM)
            _ = certificate_file.write(data)

    os.chmod(path, _certificate_mode)

# ################################################################################################################################

def _get_alternative_names(host_names:'strlist') -> 'generalnamelist':
    """ Turns host names and IP addresses into the subject alternative names of a certificate.
    """
    out:'generalnamelist' = []

    for host_name in host_names:
        try:
            address = ipaddress.ip_address(host_name)
            out.append(x509.IPAddress(address))
        except ValueError:
            out.append(x509.DNSName(host_name))

    return out

# ################################################################################################################################

def _issue(subject:'str', key:'rsa.RSAPrivateKey', issuer:'str', issuer_key:'rsa.RSAPrivateKey', is_ca:'bool',
    host_names:'strlist') -> 'x509.Certificate':
    """ Issues one certificate, a CA's own or one signed by a CA, valid for the given host names.
    """
    now = utcnow()
    not_before = now - timedelta(days=1)
    not_after = now + timedelta(days=_validity_days)

    subject_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)])
    issuer_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer)])
    constraints = x509.BasicConstraints(ca=is_ca, path_length=None)
    public_key = key.public_key()
    serial_number = x509.random_serial_number()

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject_name)
    builder = builder.issuer_name(issuer_name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(serial_number)
    builder = builder.not_valid_before(not_before)
    builder = builder.not_valid_after(not_after)
    builder = builder.add_extension(constraints, critical=True)

    if host_names:
        names = _get_alternative_names(host_names)
        alternative_names = x509.SubjectAlternativeName(names)
        builder = builder.add_extension(alternative_names, critical=False)

    algorithm = hashes.SHA256()

    out = builder.sign(issuer_key, algorithm)
    return out

# ################################################################################################################################

def _new_root(name:'str') -> 'tuple[x509.Certificate, rsa.RSAPrivateKey]':
    key = _new_key()
    certificate = _issue(name, key, name, key, True, [])

    out = (certificate, key)
    return out

# ################################################################################################################################

def generate_certificates(directory:'str', host_names:'strlist', client_name:'str', chain:'str'=Chain_Plain) -> 'None':
    """ Writes the trust file of the clients as ca.crt, the server certificate with its key, and a client certificate
    into a directory, with the server certificate issued according to the chain.
    """
    root_cert, root_key = _new_root(_ca_name)

    # A plain chain issues the server certificate from the root ..
    if chain == Chain_Plain:
        issuer_name = _ca_name
        issuer_key = root_key
        trusted = [root_cert]
        presented:'certificatelist' = []

    # .. a bundle chain issues it from an intermediate CA, which the trust file holds next to the root
    # .. and to the root of another region ..
    elif chain == Chain_Bundle:
        other_root_cert, _ = _new_root(_other_region_root_name)
        intermediate_key = _new_key()
        intermediate_cert = _issue(_intermediate_name, intermediate_key, _ca_name, root_key, True, [])

        issuer_name = _intermediate_name
        issuer_key = intermediate_key
        trusted = [other_root_cert, root_cert, intermediate_cert]
        presented = []

    # .. and a rotation chain issues it from an intermediate CA that the server presents itself,
    # .. while the trust file holds the previous root and the current one.
    else:
        previous_root_cert, _ = _new_root(_previous_root_name)
        intermediate_key = _new_key()
        intermediate_cert = _issue(_intermediate_name, intermediate_key, _ca_name, root_key, True, [])

        issuer_name = _intermediate_name
        issuer_key = intermediate_key
        trusted = [previous_root_cert, root_cert]
        presented = [intermediate_cert]

    server_key = _new_key()
    server_cert = _issue('localhost', server_key, issuer_name, issuer_key, False, host_names)

    client_key = _new_key()
    client_cert = _issue(client_name, client_key, _ca_name, root_key, False, [])

    ca_path = os.path.join(directory, 'ca.crt')
    server_cert_path = os.path.join(directory, 'server.crt')
    server_key_path = os.path.join(directory, 'server.key')
    client_cert_path = os.path.join(directory, 'client.crt')
    client_key_path = os.path.join(directory, 'client.key')

    server_chain = [server_cert]
    server_chain.extend(presented)

    _write_certificates(ca_path, trusted)
    _write_certificates(server_cert_path, server_chain)
    _write_key(server_key_path, server_key)
    _write_certificates(client_cert_path, [client_cert])
    _write_key(client_key_path, client_key)

# ################################################################################################################################
# ################################################################################################################################
