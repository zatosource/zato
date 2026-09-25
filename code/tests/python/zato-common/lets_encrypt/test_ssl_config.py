# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import os
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509.oid import NameOID

# pytest
import pytest

# Zato
from conftest import PebbleCtx
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.actions import check_port_now, get_ssl_config, obtain_now, set_lets_encrypt
from zato.common.lets_encrypt.certificate import get_certificate_info
from zato.common.lets_encrypt.client import check_port, obtain, use_generated
from zato.common.lets_encrypt.config import get_config
from zato.common.lets_encrypt.paths import get_paths
from zato.common.lets_encrypt.state import acquire_lock, get_running_operation, load_status, LockBusy, save_certificate_check, \
     save_is_enabled, save_port_check

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name the generated certificate is issued to and by, as with the one the container generates.
    Generated_Common_Name = 'localhost'
    Generated_DNS_Name = 'localhost'
    Generated_IP_Address = '127.0.0.1'
    Generated_Validity_Days = 30

    # The issuer of all the certificates Pebble signs.
    Pebble_Issuer_Prefix = 'Pebble Intermediate CA'

    # A name that never resolves, so that the challenge can never be validated.
    Unresolvable_Host = 'no-such-host.invalid'

    Public_IP = '203.0.113.10'
    Invalid_Port = 'no-such-port'
    Check_Error = 'The check failed'

# ################################################################################################################################
# ################################################################################################################################

def _get_offline_environ(tmp_path:'Path') -> 'strstrdict':
    """ Returns the environment variables that need no ACME server, because nothing in the test runs the ACME client.
    """
    out:'strstrdict' = {
        Lets_Encrypt.Env.SSL_Dir: str(tmp_path),
        Lets_Encrypt.Env.Public_IP: ModuleCtx.Public_IP,
        Lets_Encrypt.Env.HAProxy_Config: str(tmp_path / 'haproxy.cfg'),
    }
    return out

# ################################################################################################################################

def _build_self_signed_pem() -> 'str':
    """ Returns a self-signed certificate followed by its key, in the same form that the container generates auto.pem in.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())

    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ModuleCtx.Generated_Common_Name)])
    now = datetime.now(timezone.utc)
    not_after = now + timedelta(days=ModuleCtx.Generated_Validity_Days)

    alt_names = x509.SubjectAlternativeName([
        x509.DNSName(ModuleCtx.Generated_DNS_Name),
        x509.IPAddress(ipaddress.ip_address(ModuleCtx.Generated_IP_Address)),
    ])

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(not_after)
    builder = builder.add_extension(alt_names, critical=False)

    certificate = builder.sign(private_key, hashes.SHA256())

    certificate_pem = certificate.public_bytes(Encoding.PEM).decode()
    key_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode()

    out = certificate_pem + key_pem
    return out

# ################################################################################################################################

def _write_file(path:'str', contents:'str') -> 'None':
    with open(path, 'w') as output_file:
        _ = output_file.write(contents)

# ################################################################################################################################

def _read_file(path:'str') -> 'str':
    with open(path) as input_file:
        out = input_file.read()
    return out

# ################################################################################################################################

def _write_generated(paths:'SSLPaths') -> 'str':
    """ Writes auto.pem the way the container does before HAProxy starts and returns what it wrote.
    """
    out = _build_self_signed_pem()
    _write_file(paths.auto_pem, out)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_status_empty(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_offline_environ(tmp_path))
    status = load_status(paths)

    assert status.last_check_utc is None
    assert status.is_last_check_ok is None
    assert status.last_check_error == ''
    assert status.port_check_utc is None
    assert status.is_port_ready is None
    assert status.port_check_error == ''

# ################################################################################################################################

def test_status_checks_kept_apart(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_offline_environ(tmp_path))

    save_certificate_check(paths, False, ModuleCtx.Check_Error)
    save_port_check(paths, True, '')

    status = load_status(paths)

    assert status.last_check_utc is not None
    assert status.is_last_check_ok is False
    assert status.last_check_error == ModuleCtx.Check_Error

    assert status.port_check_utc is not None
    assert status.is_port_ready is True
    assert status.port_check_error == ''

# ################################################################################################################################

def test_lock_busy(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_offline_environ(tmp_path))

    assert get_running_operation(paths) == ''

    with acquire_lock(paths, Lets_Encrypt.Operation.Port):

        assert get_running_operation(paths) == Lets_Encrypt.Operation.Port

        with pytest.raises(LockBusy):
            with acquire_lock(paths, Lets_Encrypt.Operation.Certificate):
                pass

    assert get_running_operation(paths) == ''

    # Once released, the lock can be taken again.
    with acquire_lock(paths, Lets_Encrypt.Operation.Certificate):
        assert get_running_operation(paths) == Lets_Encrypt.Operation.Certificate

# ################################################################################################################################

def test_obtain_while_locked(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)
    config = get_config(environ)

    with acquire_lock(config.paths, Lets_Encrypt.Operation.Port):
        with pytest.raises(LockBusy):
            _ = obtain(config, needs_reload=False)

    status = load_status(config.paths)
    assert status.last_check_utc is None

# ################################################################################################################################

def test_use_generated(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)
    paths = get_paths(environ)

    generated_pem = _write_generated(paths)
    _write_file(paths.user_pem, _build_self_signed_pem())

    is_changed = use_generated(paths, environ[Lets_Encrypt.Env.HAProxy_Config], needs_reload=False)
    assert is_changed
    assert _read_file(paths.user_pem) == generated_pem

    is_changed = use_generated(paths, environ[Lets_Encrypt.Env.HAProxy_Config], needs_reload=False)
    assert not is_changed

# ################################################################################################################################

def test_certificate_info_none(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_offline_environ(tmp_path))
    assert get_certificate_info(paths) is None

# ################################################################################################################################

def test_certificate_info_ignores_other_certificates(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_offline_environ(tmp_path))

    # Neither the generated certificate, nor the user's own one, nor what HAProxy presents is from Let's Encrypt.
    generated_pem = _write_generated(paths)
    _write_file(paths.user_pem, generated_pem)
    _write_file(paths.own_pem, _build_self_signed_pem())

    assert get_certificate_info(paths) is None

# ################################################################################################################################

def test_get_ssl_config_own_certificate(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)
    environ[Lets_Encrypt.Env.Use_Lets_Encrypt] = 'True'

    paths = get_paths(environ)
    own_pem = _build_self_signed_pem()
    _write_file(paths.own_pem, own_pem)
    _write_file(paths.user_pem, own_pem)

    ssl_config = get_ssl_config(environ)

    assert ssl_config['is_enabled'] is False
    assert ssl_config['running_operation'] == ''
    assert ssl_config['certificate'] is None
    assert ssl_config['status']['last_check_utc'] is None

# ################################################################################################################################

def test_get_ssl_config_disabled(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)

    paths = get_paths(environ)
    generated_pem = _write_generated(paths)
    _write_file(paths.user_pem, generated_pem)

    ssl_config = get_ssl_config(environ)

    assert ssl_config['is_enabled'] is False
    assert ssl_config['certificate'] is None

# ################################################################################################################################

def test_obtain_now_failure_before_client(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)
    environ[Lets_Encrypt.Env.Port] = ModuleCtx.Invalid_Port

    obtain_now(environ)

    status = load_status(get_paths(environ))

    assert status.is_last_check_ok is False
    assert ModuleCtx.Invalid_Port in status.last_check_error

# ################################################################################################################################

def test_check_port_now_failure_before_client(tmp_path:'Path') -> 'None':
    environ = _get_offline_environ(tmp_path)
    environ[Lets_Encrypt.Env.Port] = ModuleCtx.Invalid_Port

    check_port_now(environ)

    status = load_status(get_paths(environ))

    assert status.is_port_ready is False
    assert ModuleCtx.Invalid_Port in status.port_check_error
    assert status.last_check_utc is None

# ################################################################################################################################

def test_certificate_info_lets_encrypt(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)
    _ = _write_generated(config.paths)

    _ = obtain(config, needs_reload=False)

    info = get_certificate_info(config.paths)
    assert info is not None

    assert info.names == [PebbleCtx.Host]
    assert info.issuer.startswith(ModuleCtx.Pebble_Issuer_Prefix)

    not_after = datetime.fromisoformat(info.not_after_utc)
    assert not_after > datetime.now(timezone.utc)

# ################################################################################################################################

def test_get_ssl_config_lets_encrypt(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)
    _ = _write_generated(config.paths)

    _ = obtain(config, needs_reload=False)

    ssl_config = get_ssl_config(lets_encrypt_environ)

    assert ssl_config['is_enabled'] is True
    assert ssl_config['running_operation'] == ''
    assert ssl_config['certificate']['names'] == [PebbleCtx.Host]
    assert ssl_config['status']['is_last_check_ok'] is True

# ################################################################################################################################

def test_disabled_while_obtaining(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)

    # This is what the Dashboard stores when Let's Encrypt is disabled while the ACME client runs.
    save_is_enabled(config.paths, False)

    is_changed = obtain(config, needs_reload=False)

    assert not is_changed
    assert not os.path.exists(config.paths.user_pem)

# ################################################################################################################################

def test_set_lets_encrypt_disable(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)
    generated_pem = _write_generated(config.paths)

    _ = obtain(config, needs_reload=False)
    assert _read_file(config.paths.user_pem) != generated_pem

    set_lets_encrypt(lets_encrypt_environ, False)

    ssl_config = get_ssl_config(lets_encrypt_environ)

    assert ssl_config['is_enabled'] is False
    assert ssl_config['certificate'] is None
    assert _read_file(config.paths.user_pem) == generated_pem

# ################################################################################################################################

def test_set_lets_encrypt_enable(lets_encrypt_environ:'strstrdict') -> 'None':

    # The environment variable is off, so only the Dashboard can enable Let's Encrypt.
    lets_encrypt_environ[Lets_Encrypt.Env.Use_Lets_Encrypt] = 'False'

    paths = get_paths(lets_encrypt_environ)
    _ = _write_generated(paths)

    set_lets_encrypt(lets_encrypt_environ, True)
    obtain_now(lets_encrypt_environ)

    ssl_config = get_ssl_config(lets_encrypt_environ)

    assert ssl_config['is_enabled'] is True
    assert ssl_config['certificate']['names'] == [PebbleCtx.Host]
    assert ssl_config['status']['is_last_check_ok'] is True

# ################################################################################################################################

def test_check_port_ready(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)

    is_ready = check_port(config)
    assert is_ready

    status = load_status(config.paths)

    assert status.port_check_utc is not None
    assert status.is_port_ready is True
    assert status.port_check_error == ''

    # The check never touches the certificate that HAProxy presents nor the account the real certificates are obtained with.
    assert not os.path.exists(config.paths.user_pem)
    assert not os.path.exists(config.paths.lego_pem)
    assert status.last_check_utc is None

# ################################################################################################################################

def test_check_port_not_ready(lets_encrypt_environ:'strstrdict') -> 'None':
    lets_encrypt_environ[Lets_Encrypt.Env.Subject_Alt_Name] = f'subjectAltName=DNS:{ModuleCtx.Unresolvable_Host}'

    config = get_config(lets_encrypt_environ)

    is_ready = check_port(config)
    assert not is_ready

    status = load_status(config.paths)

    assert status.is_port_ready is False
    assert ModuleCtx.Unresolvable_Host in status.port_check_error

# ################################################################################################################################
# ################################################################################################################################
