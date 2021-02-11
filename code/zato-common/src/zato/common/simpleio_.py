# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato - Cython
from zato.simpleio import BoolConfig, IntConfig, SecretConfig, SIOServerConfig

# Python 2/3 compatibility
from past.builtins import basestring, unicode

# ################################################################################################################################

if 0:
    from zato.cy.simpleio import BoolConfig as PyBoolConfig
    from zato.cy.simpleio import IntConfig as PyIntConfig
    from zato.cy.simpleio import SecretConfig as PySecretConfig
    from zato.cy.simpleio import SIOServerConfig as PySIOServerConfig

    PyBoolConfig = PyBoolConfig
    PyIntConfig  = PyIntConfig
    PySecretConfig = PySecretConfig
    PySIOServerConfig = PySIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

def get_bytes_to_str_encoding():
    return 'utf8'

# ################################################################################################################################

default_input_required_name = 'input_required'
default_input_optional_name = 'input_optional'
default_output_required_name = 'output_required'
default_output_optional_name = 'output_optional'
default_value = 'default_value'
default_input_value = 'default_input_value'
default_output_value = 'default_output_value'
default_response_elem = 'response'
default_skip_empty_keys = False
default_skip_empty_request_keys = False
default_skip_empty_response_keys = False

default_prefix_as_is     = 'a'
default_prefix_bool      = 'b'
default_prefix_csv       = 'c'
default_prefix_date      = 'date'
default_prefix_date_time = 'dt'
default_prefix_dict      = 'd'
default_prefix_dict_list = 'dl'
default_prefix_float     = 'f'
default_prefix_int       = 'i'
default_prefix_list      = 'l'
default_prefix_text      = 't'
default_prefix_uuid      = 'u'

simple_io_conf_contents = f"""
[bool]
exact=
prefix=by_, has_, is_, may_, needs_, should_
suffix=

[int]
exact=id
prefix=
suffix=_count, _id, _size, _size_min, _size_max, _timeout

[secret]
exact=auth_data, auth_token, password, password1, password2, secret_key, tls_pem_passphrase, token
prefix=
suffix=

[bytes_to_str]
encoding={{bytes_to_str_encoding}}

[default]
default_value=
default_input_value=
default_output_value=
response_elem=response

skip_empty_keys = False
skip_empty_request_keys = False
skip_empty_response_keys = False

# Configuration below is reserved for future use

input_required_name  = "input_required"
input_optional_name  = "input_optional"
output_required_name = "output_required"
output_optional_name = "output_optional"

prefix_as_is     = {default_prefix_as_is}
prefix_bool      = {default_prefix_bool}
prefix_csv       = {default_prefix_csv}
prefix_date      = {default_prefix_date}
prefix_date_time = {default_prefix_date_time}
prefix_dict      = {default_prefix_dict}
prefix_dict_list = {default_prefix_dict_list}
prefix_float     = {default_prefix_float}
prefix_int       = {default_prefix_int}
prefix_list      = {default_prefix_list}
prefix_text      = {default_prefix_text}
prefix_uuid      = {default_prefix_uuid}
""".lstrip()

# ################################################################################################################################

def c18n_sio_fs_config(sio_fs_config):

    for name in 'bool', 'int', 'secret':
        config_entry = sio_fs_config[name]

        exact = config_entry.get('exact') or []
        exact = exact if isinstance(exact, list) else [exact]

        prefix = config_entry.get('prefix') or []
        prefix = prefix if isinstance(prefix, list) else [prefix]

        suffix = config_entry.get('suffix') or []
        suffix = suffix if isinstance(suffix, list) else [suffix]

        config_entry.exact = set(exact)
        config_entry.prefix = set(prefix)
        config_entry.suffix = set(suffix)

    for key, value in sio_fs_config.get('default', {}).items():
        if isinstance(value, basestring):
            if not isinstance(value, unicode):
                value = value.decode('utf8')
                sio_fs_config.default[key] = value

# ################################################################################################################################

def get_sio_server_config(sio_fs_config):
    c18n_sio_fs_config(sio_fs_config)

    sio_server_config = SIOServerConfig() # type: PySIOServerConfig

    bool_config = BoolConfig() # type: PyBoolConfig
    bool_config.exact = sio_fs_config.bool.exact
    bool_config.prefixes = sio_fs_config.bool.prefix
    bool_config.suffixes = sio_fs_config.bool.suffix

    int_config = IntConfig() # type: PyIntConfig
    int_config.exact = sio_fs_config.int.exact
    int_config.prefixes = sio_fs_config.int.prefix
    int_config.suffixes = sio_fs_config.int.suffix

    secret_config = SecretConfig() # type: PySecretConfig
    secret_config.exact = sio_fs_config.secret.exact
    secret_config.prefixes = sio_fs_config.secret.prefix
    secret_config.suffixes = sio_fs_config.secret.suffix

    sio_server_config.bool_config = bool_config
    sio_server_config.int_config = int_config
    sio_server_config.secret_config = secret_config

    sio_fs_config_default = sio_fs_config.get('default')

    if sio_fs_config_default:

        sio_server_config.input_required_name = sio_fs_config.default.get('input_required_name', default_input_required_name)
        sio_server_config.input_optional_name = sio_fs_config.default.get('input_optional_name', default_input_optional_name)
        sio_server_config.output_required_name = sio_fs_config.default.get('output_required_name', default_output_required_name)
        sio_server_config.output_optional_name = sio_fs_config.default.get('output_optional_name', default_output_optional_name)
        sio_server_config.default_value = sio_fs_config.default.get('default_value', default_value)
        sio_server_config.default_input_value = sio_fs_config.default.get('default_input_value', default_input_value)
        sio_server_config.default_output_value = sio_fs_config.default.get('default_output_value', default_output_value)

        sio_server_config.response_elem = sio_fs_config.default.get('response_elem', default_response_elem)

        sio_server_config.skip_empty_keys = sio_fs_config.default.get('skip_empty_keys', default_skip_empty_keys)
        sio_server_config.skip_empty_request_keys = sio_fs_config.default.get(
            'skip_empty_request_keys', default_skip_empty_request_keys)
        sio_server_config.skip_empty_response_keys = sio_fs_config.default.get(
            'skip_empty_response_keys', default_skip_empty_response_keys)

        sio_server_config.prefix_as_is = sio_fs_config.default.get('prefix_as_is', default_prefix_as_is)
        sio_server_config.prefix_bool = sio_fs_config.default.get('prefix_bool', default_prefix_bool)
        sio_server_config.prefix_csv = sio_fs_config.default.get('prefix_csv', default_prefix_csv)
        sio_server_config.prefix_date = sio_fs_config.default.get('prefix_date', default_prefix_date)
        sio_server_config.prefix_date_time = sio_fs_config.default.get('prefix_date_time', default_prefix_date_time)
        sio_server_config.prefix_dict = sio_fs_config.default.get('prefix_dict', default_prefix_dict)
        sio_server_config.prefix_dict_list = sio_fs_config.default.get('prefix_dict_list', default_prefix_dict_list)
        sio_server_config.prefix_float = sio_fs_config.default.get('prefix_float', default_prefix_float)
        sio_server_config.prefix_int = sio_fs_config.default.get('prefix_int', default_prefix_int)
        sio_server_config.prefix_list = sio_fs_config.default.get('prefix_list', default_prefix_list)
        sio_server_config.prefix_text = sio_fs_config.default.get('prefix_text', default_prefix_text)
        sio_server_config.prefix_uuid = sio_fs_config.default.get('prefix_uuid', default_prefix_uuid)

    else:

        sio_server_config.input_required_name = default_input_required_name
        sio_server_config.input_optional_name = default_input_optional_name
        sio_server_config.output_required_name = default_output_required_name
        sio_server_config.output_optional_name = default_output_optional_name
        sio_server_config.default_value = default_value
        sio_server_config.default_input_value = default_input_value
        sio_server_config.default_output_value = default_output_value

        sio_server_config.response_elem = default_response_elem

        sio_server_config.skip_empty_keys = default_skip_empty_keys
        sio_server_config.skip_empty_request_keys = default_skip_empty_request_keys
        sio_server_config.skip_empty_response_keys = default_skip_empty_response_keys

    bytes_to_str_encoding = sio_fs_config.bytes_to_str.encoding
    if not isinstance(bytes_to_str_encoding, unicode):
        bytes_to_str_encoding = bytes_to_str_encoding.decode('utf8')

    sio_server_config.bytes_to_str_encoding = bytes_to_str_encoding
    sio_server_config.json_encoder.bytes_to_str_encoding = bytes_to_str_encoding

    return sio_server_config

# ################################################################################################################################

def drop_sio_elems(elems, *to_drop):
    out = list(set(elems))
    for elem in to_drop:
        out.remove(elem)
    return out

# ################################################################################################################################
