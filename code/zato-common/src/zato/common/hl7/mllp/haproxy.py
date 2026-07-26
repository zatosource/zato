# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fcntl
import os
import re
import sys
import tempfile
from logging import getLogger

# Zato
from zato.common.defaults import http_plain_server_port
from zato.common.haproxy.config import find_haproxy_config, reload_haproxy

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

__all__ = ('ensure_mllp_backend_server', 'find_haproxy_config', 'reload_haproxy', 'resolve_internal_port')

# ################################################################################################################################
# ################################################################################################################################

# The internal port of the first server in a cluster. Each further server is as far above this
# as its own port is above the first server's, so a server's MLLP port follows from its identity
# and never has to be discovered.
Internal_Port_Base = 31312

# If this environment variable is set, the internal MLLP server binds to exactly this port
Env_Port_Name = 'Zato_HL7_MLLP_Port'

# The name a server is known by when the environment does not say otherwise
Default_Server_Name = 'server1'

# Where the generated server lines live inside the mllp_backend section
Servers_Block_Start = '#<zato-mllp-servers>'
Servers_Block_End   = '#</zato-mllp-servers>'

# Matches the whole generated block along with the indentation of its opening marker
_servers_block_pattern = re.compile(
    r'([ \t]*)' + re.escape(Servers_Block_Start) + r'.*?' + re.escape(Servers_Block_End),
    re.DOTALL,
)

# Matches one generated server line, capturing the name so a server can find its own
_server_line_pattern = re.compile(r'^\s*server\s+(\S+)\s')

# What each server line asks HAProxy to prefix the connection with - the sender's address and,
# on the TLS bind, the common name of the certificate that was verified there.
_Server_Line_Options = 'send-proxy-v2-ssl-cn'

# Anything outside this set is replaced in a server name, because HAProxy takes the name as
# a bare token on the server line.
_unsafe_name_pattern = re.compile(r'[^A-Za-z0-9_.-]')

# ################################################################################################################################

def resolve_internal_port(server_port:'int'=http_plain_server_port) -> 'int':
    """ Returns the internal port the MLLP listener of a server on the given port binds to.
    """

    # An explicitly configured port always wins - this is what tests use to know the port upfront
    env_port = os.environ.get(Env_Port_Name)

    if env_port:
        out = int(env_port)
        logger.info('Using internal MLLP port %d from %s', out, Env_Port_Name)
        return out

    # Every server sits as far above the MLLP base as it does above the first server's own port,
    # so two servers never collide and neither has to probe for a free port.
    out = Internal_Port_Base + server_port - http_plain_server_port

    logger.info('Resolved internal MLLP port %d for server port %d', out, server_port)

    return out

# ################################################################################################################################

def _to_server_line_name(server_name:'str') -> 'str':
    """ Turns a server name into something HAProxy accepts as a bare token on a server line.
    """
    out = _unsafe_name_pattern.sub('-', server_name)
    return out

# ################################################################################################################################

def _build_servers_block(server_lines:'dict', indent:'str') -> 'str':
    """ Renders the generated block from the server lines it is to hold, in name order so that
    two servers writing it in either order arrive at the same file.
    """
    lines = [indent + Servers_Block_Start]

    for name in sorted(server_lines):
        lines.append(indent + server_lines[name])

    lines.append(indent + Servers_Block_End)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _read_servers_block(content:'str') -> 'dict':
    """ Reads the server lines the generated block currently holds, keyed by server name.
    """
    out:'dict' = {}
    match = _servers_block_pattern.search(content)

    if not match:
        return out

    for line in match.group(0).split('\n'):

        line_match = _server_line_pattern.match(line)

        if line_match:
            out[line_match.group(1)] = line.strip()

    return out

# ################################################################################################################################

def _write_atomically(config_path:'str', content:'str') -> 'None':
    """ Replaces the configuration file in one step, so that a reader either sees all of the
    previous content or all of the new content and never a half-written file.
    """
    directory = os.path.dirname(config_path)

    # The temporary file has to share the directory, because a rename is only atomic within one filesystem
    handle, temporary_path = tempfile.mkstemp(dir=directory, prefix='haproxy.cfg.')

    try:
        with os.fdopen(handle, 'w') as temporary_file:
            _ = temporary_file.write(content)

        # The replacement inherits the permissions of what it replaces rather than the stricter
        # ones a temporary file is created with
        existing_mode = os.stat(config_path).st_mode
        os.chmod(temporary_path, existing_mode & 0o777)

        os.replace(temporary_path, config_path)

    except Exception:
        os.unlink(temporary_path)
        raise

# ################################################################################################################################

def ensure_mllp_backend_server(config_path:'str', server_name:'str', internal_port:'int') -> 'bool':
    """ Makes sure the mllp_backend section carries this server's line and no stale version of it.
    Returns whether the file was changed, which is False on every start after the first.
    """

    line_name = _to_server_line_name(server_name)
    wanted_line = f'server {line_name} 127.0.0.1:{internal_port} {_Server_Line_Options}'

    # Servers of one cluster share the file, so the read, the edit and the write are held together
    lock_path = config_path + '.lock'

    with open(lock_path, 'w') as lock_file:

        fcntl.flock(lock_file, fcntl.LOCK_EX)

        try:
            with open(config_path, 'r') as config_file:
                content = config_file.read()

            match = _servers_block_pattern.search(content)

            # Without the markers there is nowhere to write, which is the case for a configuration
            # that predates them - the server carries on and HAProxy keeps whatever it already had
            if not match:
                logger.info('No MLLP server block in %s, leaving it alone', config_path)
                return False

            server_lines = _read_servers_block(content)

            if server_lines.get(line_name) == wanted_line:
                return False

            server_lines[line_name] = wanted_line
            indent = match.group(1)

            updated_content = content[:match.start()] + _build_servers_block(server_lines, indent) + content[match.end():]

            _write_atomically(config_path, updated_content)

        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)

    logger.info('Wrote MLLP backend line for `%s` on port %d to %s', line_name, internal_port, config_path)

    return True

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Writes the local server's MLLP backend line into the configuration file named on the
    command line. Used at container start, before HAProxy runs, so that no reload is ever needed.
    """
    config_path = sys.argv[1]

    if not os.path.exists(config_path):
        logger.info('No HAProxy configuration at %s, nothing to update', config_path)
        return

    server_name = os.environ.get('Zato_Server_Name') or Default_Server_Name
    server_port = int(os.environ.get('Zato_Port_Server') or http_plain_server_port)

    _ = ensure_mllp_backend_server(config_path, server_name, resolve_internal_port(server_port))

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
