# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.client import build_command
from zato.common.lets_encrypt.config import get_check_interval, get_config, is_enabled, parse_dns_names
from zato.common.lets_encrypt.paths import get_paths
from zato.common.lets_encrypt.state import save_is_enabled

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Public_IP = '203.0.113.10'
    Own_PEM_Contents = 'The certificate of the user\'s own'

# ################################################################################################################################
# ################################################################################################################################

def _get_environ(tmp_path:'Path', use_lets_encrypt:'str') -> 'strstrdict':
    """ Returns the environment variables of a container whose SSL directory is a temporary one.
    """
    out:'strstrdict' = {
        Lets_Encrypt.Env.SSL_Dir: str(tmp_path),
    }

    if use_lets_encrypt:
        out[Lets_Encrypt.Env.Use_Lets_Encrypt] = use_lets_encrypt

    return out

# ################################################################################################################################

def _write_own_certificate(environ:'strstrdict') -> 'None':
    paths = get_paths(environ)

    with open(paths.own_pem, 'w') as own_file:
        _ = own_file.write(ModuleCtx.Own_PEM_Contents)

# ################################################################################################################################
# ################################################################################################################################

def test_parse_dns_names_keeps_dns_entries_only() -> 'None':
    names = parse_dns_names('subjectAltName=DNS:zato.test,IP:127.0.0.1,DNS:api.zato.test')
    assert names == ['zato.test', 'api.zato.test']

# ################################################################################################################################

def test_parse_dns_names_without_prefix() -> 'None':
    names = parse_dns_names('DNS:zato.test, DNS:api.zato.test')
    assert names == ['zato.test', 'api.zato.test']

# ################################################################################################################################

def test_parse_dns_names_skips_names_without_dot() -> 'None':
    names = parse_dns_names('subjectAltName=DNS:localhost,IP:127.0.0.1')
    assert names == []

# ################################################################################################################################

def test_is_enabled_absent(tmp_path:'Path') -> 'None':
    assert not is_enabled(_get_environ(tmp_path, ''))

# ################################################################################################################################

def test_is_enabled_true(tmp_path:'Path') -> 'None':
    assert is_enabled(_get_environ(tmp_path, 'True'))
    assert is_enabled(_get_environ(tmp_path, 'true'))

# ################################################################################################################################

def test_is_enabled_false(tmp_path:'Path') -> 'None':
    assert not is_enabled(_get_environ(tmp_path, 'False'))

# ################################################################################################################################

def test_is_enabled_own_certificate(tmp_path:'Path') -> 'None':
    environ = _get_environ(tmp_path, 'True')
    _write_own_certificate(environ)

    assert not is_enabled(environ)

# ################################################################################################################################

def test_is_enabled_own_certificate_over_dashboard(tmp_path:'Path') -> 'None':
    environ = _get_environ(tmp_path, '')
    save_is_enabled(get_paths(environ), True)
    _write_own_certificate(environ)

    assert not is_enabled(environ)

# ################################################################################################################################

def test_is_enabled_dashboard_over_environment_variable(tmp_path:'Path') -> 'None':

    enabled_environ = _get_environ(tmp_path / 'enabled', 'False')
    save_is_enabled(get_paths(enabled_environ), True)

    disabled_environ = _get_environ(tmp_path / 'disabled', 'True')
    save_is_enabled(get_paths(disabled_environ), False)

    assert is_enabled(enabled_environ)
    assert not is_enabled(disabled_environ)

# ################################################################################################################################

def test_get_paths(tmp_path:'Path') -> 'None':
    paths = get_paths(_get_environ(tmp_path, ''))
    data_dir = tmp_path / Lets_Encrypt.File.Data_Dir

    assert paths.ssl_dir == str(tmp_path)
    assert paths.user_pem == str(tmp_path / Lets_Encrypt.File.User_PEM)
    assert paths.auto_pem == str(tmp_path / Lets_Encrypt.File.Auto_PEM)
    assert paths.own_pem == str(tmp_path / Lets_Encrypt.File.Own_PEM)
    assert paths.data_dir == str(data_dir)
    assert paths.settings == str(data_dir / Lets_Encrypt.File.Settings)
    assert paths.status == str(data_dir / Lets_Encrypt.File.Status)
    assert paths.lock == str(data_dir / Lets_Encrypt.File.Lock)

# ################################################################################################################################

def test_get_config_defaults() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Use_Lets_Encrypt: 'True',
        Lets_Encrypt.Env.Subject_Alt_Name: 'subjectAltName=DNS:zato.test',
    }

    config = get_config(environ)

    assert config.server == Lets_Encrypt.Default.Server
    assert config.staging_server == Lets_Encrypt.Default.Staging_Server
    assert config.ca_file is None
    assert config.port == Lets_Encrypt.Default.Port
    assert config.paths.ssl_dir == Lets_Encrypt.Default.SSL_Dir
    assert config.haproxy_config == Lets_Encrypt.Default.HAProxy_Config

    assert get_check_interval(environ) == Lets_Encrypt.Default.Check_Interval

# ################################################################################################################################

def test_get_config_dns_names() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Subject_Alt_Name: 'subjectAltName=DNS:zato.test,DNS:api.zato.test,IP:127.0.0.1',
    }

    config = get_config(environ)

    assert config.domains == ['zato.test', 'api.zato.test']
    assert not config.is_ip

# ################################################################################################################################

def test_get_config_public_ip_without_dns_names() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Subject_Alt_Name: 'subjectAltName=DNS:localhost,IP:127.0.0.1',
        Lets_Encrypt.Env.Public_IP: ModuleCtx.Public_IP,
    }

    config = get_config(environ)

    assert config.domains == [ModuleCtx.Public_IP]
    assert config.is_ip

# ################################################################################################################################

def test_get_config_public_ip_without_subject_alt_name() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Public_IP: ModuleCtx.Public_IP,
    }

    config = get_config(environ)

    assert config.domains == [ModuleCtx.Public_IP]
    assert config.is_ip

# ################################################################################################################################

def test_build_command_dns_names() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Subject_Alt_Name: 'subjectAltName=DNS:zato.test,DNS:api.zato.test',
        Lets_Encrypt.Env.Port: '12345',
    }

    config = get_config(environ)
    command = build_command(config, config.server, config.paths.data_dir)

    assert command[command.index('--profile') + 1] == Lets_Encrypt.DNS_Profile
    assert command[command.index('--server') + 1] == Lets_Encrypt.Default.Server
    assert command[command.index('--path') + 1] == config.paths.data_dir
    assert command[command.index('--tls.address') + 1] == ':12345'
    assert command.count('--domains') == 2
    assert 'zato.test' in command
    assert 'api.zato.test' in command

# ################################################################################################################################

def test_build_command_public_ip() -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Public_IP: ModuleCtx.Public_IP,
    }

    config = get_config(environ)
    command = build_command(config, config.server, config.paths.data_dir)

    assert command[command.index('--profile') + 1] == Lets_Encrypt.IP_Profile
    assert command[command.index('--domains') + 1] == ModuleCtx.Public_IP
    assert command[command.index('--tls.address') + 1] == f':{Lets_Encrypt.Default.Port}'

# ################################################################################################################################

def test_build_command_staging_server(tmp_path:'Path') -> 'None':
    environ:'strstrdict' = {
        Lets_Encrypt.Env.Subject_Alt_Name: 'subjectAltName=DNS:zato.test',
    }

    config = get_config(environ)
    command = build_command(config, config.staging_server, str(tmp_path))

    assert command[command.index('--server') + 1] == Lets_Encrypt.Default.Staging_Server
    assert command[command.index('--path') + 1] == str(tmp_path)

# ################################################################################################################################
# ################################################################################################################################
