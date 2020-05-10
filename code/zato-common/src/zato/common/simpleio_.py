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
from six import PY3

# ################################################################################################################################
# ################################################################################################################################

def get_bytes_to_str_encoding():
    return 'utf8' if PY3 else ''

# ################################################################################################################################

simple_io_conf_contents = """
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
encoding={bytes_to_str_encoding}

[default]
default_value=
default_input_value=
default_output_value=
response_elem=

skip_empty_keys = False
skip_empty_request_keys = False
skip_empty_response_keys = False

# Configuration below is reserved for future use

input_required_name  = "input_required"
input_optional_name  = "input_optional"
output_required_name = "output_required"
output_optional_name = "output_optional"

prefix_as_is     = "a"
prefix_bool      = "b"
prefix_csv       = "c"
prefix_date      = "date"
prefix_date_time = "dt"
prefix_dict      = "d"
prefix_dict_list = "dl"
prefix_float     = "f"
prefix_int       = "i"
prefix_list      = "l"
prefix_text      = "t"
prefix_uuid      = "u"
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

    sio_server_config = SIOServerConfig()

    bool_config = BoolConfig()
    bool_config.exact = sio_fs_config.bool.exact
    bool_config.prefixes = sio_fs_config.bool.prefix
    bool_config.suffixes = sio_fs_config.bool.suffix

    int_config = IntConfig()
    int_config.exact = sio_fs_config.int.exact
    int_config.prefixes = sio_fs_config.int.prefix
    int_config.suffixes = sio_fs_config.int.suffix

    secret_config = SecretConfig()
    secret_config.exact = sio_fs_config.secret.exact
    secret_config.prefixes = sio_fs_config.secret.prefix
    secret_config.suffixes = sio_fs_config.secret.suffix

    sio_server_config.bool_config = bool_config
    sio_server_config.int_config = int_config
    sio_server_config.secret_config = secret_config

    sio_fs_config_default = sio_fs_config.get('default')

    if sio_fs_config_default:

        sio_server_config.input_required_name = sio_fs_config.default.input_required_name
        sio_server_config.input_optional_name = sio_fs_config.default.input_optional_name
        sio_server_config.output_required_name = sio_fs_config.default.output_required_name
        sio_server_config.output_optional_name = sio_fs_config.default.output_optional_name
        sio_server_config.default_value = sio_fs_config.default.default_value
        sio_server_config.default_input_value = sio_fs_config.default.default_input_value
        sio_server_config.default_output_value = sio_fs_config.default.default_output_value

        sio_server_config.response_elem = sio_fs_config.default.response_elem

        sio_server_config.skip_empty_keys = sio_fs_config.default.skip_empty_keys
        sio_server_config.skip_empty_request_keys = sio_fs_config.default.skip_empty_request_keys
        sio_server_config.skip_empty_response_keys = sio_fs_config.default.skip_empty_response_keys

        sio_server_config.prefix_as_is = sio_fs_config.default.prefix_as_is
        sio_server_config.prefix_bool = sio_fs_config.default.prefix_bool
        sio_server_config.prefix_csv = sio_fs_config.default.prefix_csv
        sio_server_config.prefix_date = sio_fs_config.default.prefix_date
        sio_server_config.prefix_date_time = sio_fs_config.default.prefix_date_time
        sio_server_config.prefix_dict = sio_fs_config.default.prefix_dict
        sio_server_config.prefix_dict_list = sio_fs_config.default.prefix_dict_list
        sio_server_config.prefix_float = sio_fs_config.default.prefix_float
        sio_server_config.prefix_int = sio_fs_config.default.prefix_int
        sio_server_config.prefix_list = sio_fs_config.default.prefix_list
        sio_server_config.prefix_text = sio_fs_config.default.prefix_text
        sio_server_config.prefix_uuid = sio_fs_config.default.prefix_uuid

    else:

        sio_server_config.input_required_name = 'input_required'
        sio_server_config.input_optional_name = 'input_optional'
        sio_server_config.output_required_name = 'output_required'
        sio_server_config.output_optional_name = 'output_optional'
        sio_server_config.default_value = 'default_value'
        sio_server_config.default_input_value = 'default_input_value'
        sio_server_config.default_output_value = 'default_output_value'

        sio_server_config.response_elem = 'response'

        sio_server_config.skip_empty_keys = 'skip_empty_keys'
        sio_server_config.skip_empty_request_keys = 'skip_empty_request_keys'
        sio_server_config.skip_empty_response_keys = 'skip_empty_response_keys'

    bytes_to_str_encoding = sio_fs_config.bytes_to_str.encoding
    if not isinstance(bytes_to_str_encoding, unicode):
        bytes_to_str_encoding = bytes_to_str_encoding.decode('utf8')

    sio_server_config.bytes_to_str_encoding = bytes_to_str_encoding

    return sio_server_config

# ################################################################################################################################

def drop_sio_elems(elems, *to_drop):
    out = list(set(elems))
    for elem in to_drop:
        out.remove(elem)
    return out

# ################################################################################################################################
