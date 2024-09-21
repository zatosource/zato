# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from pathlib import Path
from traceback import format_exc
from urllib.parse import parse_qsl, urlparse, urlunparse

# Bunch
from bunch import Bunch

# parse
from parse import PARSE_RE as parse_re

# Zato
from zato.common.api import EnvConfigCtx, EnvVariable, SCHEDULER, Secret_Shadow, URLInfo
from zato.common.const import SECRETS
from zato.common.ext.configobj_ import ConfigObj
from zato.common.util.tcp import get_current_ip

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.crypto.api import CryptoManager
    from zato.common.typing_ import any_, strdict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Values of these generic attributes may contain query string elements that have to be masked out
mask_attrs = ['address']

# ################################################################################################################################
# ################################################################################################################################

zato_sys_current_ip = 'Zato_Sys_Current_IP'

# ################################################################################################################################
# ################################################################################################################################

def get_url_protocol_from_config_item(use_tls:'bool') -> 'str':
    return 'https' if use_tls else 'http'

# ################################################################################################################################

def get_scheduler_api_client_for_server_auth_required(args:'any_') -> 'str':

    if not (value := os.environ.get(SCHEDULER.Env.Server_Auth_Required)):
        if not (value := getattr(args, 'scheduler_api_client_for_server_auth_required', None)):
            value = SCHEDULER.Default_API_Client_For_Server_Auth_Required

    return value

# ################################################################################################################################

def get_scheduler_api_client_for_server_username(args:'any_') -> 'str':

    if not (value := os.environ.get(SCHEDULER.Env.Server_Username)):
        if not (value := getattr(args, 'scheduler_api_client_for_server_username', None)):
            value = SCHEDULER.Default_API_Client_For_Server_Username

    return value

# ################################################################################################################################

def get_scheduler_api_client_for_server_password(
    args:'any_',
    cm:'CryptoManager',
    *,
    initial_password:'str'='',
    needs_encrypt:'bool'=False
) -> 'str':

    if not (value := os.environ.get(SCHEDULER.Env.Server_Password)):
        if not (value := getattr(args, 'scheduler_api_client_for_server_password', None)):
            if not (value := initial_password):
                value = cm.generate_password()
                if needs_encrypt:
                    value = cm.encrypt(value)
                value = value.decode('utf8')

    return value

# ################################################################################################################################

def make_name_env_compatible(name:'str') -> 'str':
    return name.replace('.', '__').replace('-','__')

# ################################################################################################################################

def get_env_config_ctx(file_path:'str | any_') -> 'EnvConfigCtx':

    # Our response that will be populated
    out = EnvConfigCtx()

    if file_path and isinstance(file_path, str):

        file_path = file_path.lower()

        if 'server' in file_path:
            component = 'Server'
        elif 'scheduler' in file_path:
            component = 'Scheduler'
        elif ('web-admin' in file_path) or ('dashboard' in file_path):
            component = 'Dashboard'
        elif 'user-conf' in file_path:
            component = 'User_Config'
        else:
            component = 'Unknown'

        file_name = Path(file_path).name

    else:
        component = 'Not_Applicable_component'
        file_name = 'Not_Applicable_Zato_file_path'

    # Now, we can return the response to our caller
    out.component = component
    out.file_name = file_name

    return out

# ################################################################################################################################
# ################################################################################################################################

def enrich_config_from_environment(file_name:'str', config:'Bunch') -> 'Bunch':

    # stdlib
    from io import StringIO

    # Local variables
    _env_key_prefix = EnvVariable.Key_Prefix

    # Make the file name use only the characters that an environment variable can have
    file_name = make_name_env_compatible(file_name)

    # This is the basic context of the configuration file that we are processing ..
    ctx = get_env_config_ctx(file_name)

    # This is a map of stanzas to key/value pairs that exist in the environment for this stanza
    # but do not exist in the stanza itself. These new keys will be merged into each such stanza.
    extra = {}

    # .. go through each of the stanzas ..
    for stanza in config:

        # .. make sure the name is what an environment variable would use ..
        stanza = make_name_env_compatible(stanza)

        # .. populate it because we may need to use it ..
        extra[stanza] = {}

        # .. find all the keys in the environment that correspond to this stanza ..
        env_key_prefix = f'{_env_key_prefix}_{ctx.component}_{ctx.file_name}_{stanza}_'
        for env_name, env_value in os.environ.items():
            if env_name.startswith(env_key_prefix):
                key_name = env_name.replace(env_key_prefix, '')
                extra[stanza][key_name] = env_value

    # .. build a temporary string object that ConfigObj will parse in a moment below ..
    extra_str = StringIO()

    for stanza, key_values in extra.items():
        _ = extra_str.write(f'[{stanza}]\n')
        for key, value in key_values.items():
            _ = extra_str.write(f'{key}={value}\n\n')

    _ = extra_str.seek(0)

    # .. the file has to based to a temporary location now, which is what ConfigObject expects ..

    # .. build a new ConfigObj from the extra data, ..
    # .. which we need because we want for the ConfigObj's parser ..
    # .. to parse string environment variables to Python objects ..
    extra_config = ConfigObj(extra_str)

    # .. go through all the extra pieces of configuration ..
    for stanza, extra_key_values in extra_config.items():

        # .. if we have anything new for that stanza ..
        if extra_key_values:

            # .. do assign it to the original config object ..
            orig_stanza = config[stanza]
            for new_extra_key, new_extra_value in extra_key_values.items(): # type: ignore
                orig_stanza[new_extra_key] = new_extra_value

    # .. now, we are ready to return the enriched the configuration to our caller.
    return config

# ################################################################################################################################
# ################################################################################################################################

def get_env_config_value(
    component:'str',
    file_name:'str',
    stanza:'str',
    key:'str',
    use_default:'bool'=True
) -> 'str':

    # Local variables
    _env_key_prefix = EnvVariable.Key_Prefix

    # Make sure the individual components are what an environment variable can use
    file_name = make_name_env_compatible(file_name)
    stanza = make_name_env_compatible(stanza)
    key = make_name_env_compatible(key)

    # This is the name of an environment variable that we will be looking up ..
    env_name = f'{_env_key_prefix}_{component}_{file_name}_{stanza}_{key}'

    # .. use what we find in the environment ..
    if value := os.environ.get(env_name, ''):

        # .. store an entry that we did find it ..
        logger.info('Found env. key -> %s', env_name)

    # .. or, optionally,  build a default value if there is no such key ..
    else:

        if use_default:
            value = env_name + EnvVariable.Key_Missing_Suffix

    # .. now, we can return the value to our caller.
    return value

# ################################################################################################################################

def resolve_name(name:'str') -> 'str':

    suffix = '.' + zato_sys_current_ip

    if isinstance(name, str): # type: ignore
        if name.endswith(suffix):
            current_ip = get_current_ip()
            name = name.replace(zato_sys_current_ip, current_ip)

    return name

# ################################################################################################################################

def resolve_value(key, value, decrypt_func=None, _default=object(), _secrets=SECRETS):
    """ Resolves final value of a given variable by looking it up in environment if applicable.
    """
    # Skip non-resolvable items
    if not isinstance(value, str):
        return value

    if not value:
        return value

    value = value.decode('utf8') if isinstance(value, bytes) else value

    # It may be an environment variable ..
    if value.startswith('$'):

        # .. but not if it's $$ which is a signal to skip this value ..
        if value.startswith('$$'):
            return value

        # .. a genuine pointer to an environment variable.
        else:

            # .. we support for exact and upper-case forms ..
            env_key = value[1:].strip()
            env_key1 = env_key
            env_key2 = env_key.upper()
            env_keys = [env_key1, env_key2]

            for item in env_keys:
                value = os.environ.get(item, _default)
                if value is not _default:
                    break
            else:
                # .. use a placeholder if none of the keys matched
                value = 'Env_Key_Missing_{}'.format(env_key)

    # It may be an encrypted value
    elif key in _secrets.PARAMS and value.startswith(_secrets.PREFIX):
        value = decrypt_func(value)

    # Pre-processed, we can assign this pair to output
    return value

# ################################################################################################################################

def resolve_env_variables(data):
    """ Given a Bunch instance on input, iterates over all items and resolves all keys/values to ones extracted
    from environment variables.
    """
    out = Bunch()
    for key, value in data.items():
        out[key] = resolve_value(None, value)

    return out

# ################################################################################################################################

def _replace_query_string_items(server:'ParallelServer', data:'any_') -> 'str':

    # If there is no input, we can return immediately
    if not data:
        return ''

    # Local variables
    query_string_new = []

    # Parse the data ..
    data = urlparse(data)

    # .. extract the query string ..
    query_string = data.query
    query_string = parse_qsl(query_string)

    # .. convert the data to a list to make it possible to unparse it later on ..
    data = list(data)

    # .. replace all the required elements ..
    for key, value in query_string:

        # .. so we know if we matched something in the inner loops ..
        should_continue = True

        # .. check exact keys ..
        for name in server.sio_config.secret_config.exact:
            if key == name:
                value = Secret_Shadow
                should_continue = False
                break

        # .. check prefixes ..
        if should_continue:
            for name in server.sio_config.secret_config.prefixes:
                if key.startswith(name):
                    value = Secret_Shadow
                    should_continue = should_continue
                    break

        # .. check suffixes ..
        if should_continue:
            for name in server.sio_config.secret_config.suffixes:
                if key.endswith(name):
                    value = Secret_Shadow
                    break

        # .. if we are here, either it means that the value was replaced ..
        # .. or we are going to use as it was because it needed no replacing ..
        query_string_new.append(f'{key}={value}')

    # .. replace the query string ..
    query_string_new = '&'.join(query_string_new)

    # .. now, set the query string back ..
    data[-2] = query_string_new

    # .. build a full address once more ..
    data = urlunparse(data)

    # .. and return it to our caller.
    return data

# ################################################################################################################################

def replace_query_string_items(server:'ParallelServer', data:'any_') -> 'str':
    try:
        return _replace_query_string_items(server, data)
    except Exception:
        logger.info('Items could not be masked -> %s', format_exc())

# ################################################################################################################################

def replace_query_string_items_in_dict(server:'ParallelServer', data:'strdict') -> 'None':

    # Note that we use a list because we are going to modify the dict in place
    for key, value in list(data.items()):

        # Add a key with a value that is masked
        if key in mask_attrs:
            value_masked = str(value)
            value_masked = replace_query_string_items(server, value)
            key_masked = f'{key}_masked'
            data[key_masked] = value_masked

# ################################################################################################################################

def extract_param_placeholders(data:'str') -> 'any_':

    # Parse out groups for path parameters ..
    groups = parse_re.split(data)

    # .. go through each group ..
    for group in groups:

        # .. if it is a parameter placeholder ..
        if group and group[0] == '{':

            # .. yield it to our caller.
            yield group

# ################################################################################################################################

def get_config_object(repo_location:'str', conf_file:'str') -> 'Bunch | ConfigObj':

    # Zato
    from zato.common.util import get_config

    return get_config(repo_location, conf_file, bunchified=False)

# ################################################################################################################################

def update_config_file(config:'ConfigObj', repo_location:'str', conf_file:'str') -> 'None':
    conf_path = os.path.join(repo_location, conf_file)
    with open(conf_path, 'wb') as f:
        _ = config.write(f)

# ################################################################################################################################

def parse_url_address(address:'str', default_port:'int') -> 'URLInfo':

    # Our response to produce
    out = URLInfo()

    # Extract the details from the address
    parsed = urlparse(address)

    scheme = parsed.scheme.lower()
    use_tls = scheme == 'https'

    # If there is no scheme and netloc, the whole address will be something like '10.151.17.19',
    # and it will be found under .path actually ..
    if (not parsed.scheme) and (not parsed.netloc):
        host_port = parsed.path

    # .. otherwise, the address will be in the network location.
    else:
        host_port = parsed.netloc

    # We need to split it because we may have a port
    host_port = host_port.split(':')

    # It will be a two-element list if there is a port ..
    if len(host_port) == 2:
        host, port = host_port
        port = int(port)

    # .. otherwise, assume the scheduler's default port ..
    else:
        host = host_port[0]
        port = default_port

    # .. populate the response ..
    out.address = address
    out.host = host
    out.port = port
    out.use_tls = use_tls

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################
