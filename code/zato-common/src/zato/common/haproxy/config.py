# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import signal
import subprocess
import sys
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Whether the forwarding headers arriving at HAProxy are taken at face value. This is off unless
# something in front of HAProxy is known to set them, in which case HAProxy has no way of telling
# that value apart from one a caller sent itself.
Env_Trust_Forwarded_Headers = 'Zato_Trust_Forwarded_Headers'

# The values that turn the setting on, compared case-insensitively.
Trust_Enabled_Values = ('true', 'yes', '1', 'on')

# The header the servers and the dashboard read the client address from.
Header_Zato_Forwarded_For = 'X-Zato-Forwarded-For'

# The header anything in front of HAProxy would use to report the address it saw.
Header_Forwarded_For = 'X-Forwarded-For'

# The generated directives live between these markers, one pair per frontend, so that the block
# can be replaced without the rest of the frontend being touched.
Block_Start = '#<zato-forwarded-headers>'
Block_End   = '#</zato-forwarded-headers>'

# Matches one marked block along with the indentation of its opening marker, which the generated
# lines reuse so the result stays aligned with the surrounding directives.
_block_pattern = re.compile(
    r'([ \t]*)' + re.escape(Block_Start) + r'.*?' + re.escape(Block_End),
    re.DOTALL,
)

# ################################################################################################################################

def is_trust_enabled(environ:'dict | None'=None) -> 'bool':
    """ Returns whether the forwarding headers reaching HAProxy are to be trusted.
    """
    if environ is None:
        environ = dict(os.environ)

    # The variable is genuinely optional, so its absence is the same as the setting being off
    raw_value = environ.get(Env_Trust_Forwarded_Headers)

    if raw_value is None:
        out = False
    else:
        out = raw_value.strip().lower() in Trust_Enabled_Values

    return out

# ################################################################################################################################

def build_forwarded_headers_block(is_trusted:'bool', indent:'str'='    ') -> 'str':
    """ Builds the HAProxy directives that decide what the client address reported to Zato is,
    wrapped in the markers that make the block replaceable.
    """
    if is_trusted:

        # Whatever is in front reported an address, so the last element is taken - that is the one
        # the nearest proxy appended, whereas the first is whatever the caller put there itself.
        directives = [
            f'http-request del-header {Header_Zato_Forwarded_For}',
            f'http-request set-header {Header_Zato_Forwarded_For} '
                f'%[req.hdr({Header_Forwarded_For},-1)] if {{ req.hdr({Header_Forwarded_For}) -m found }}',
            f'http-request set-header {Header_Zato_Forwarded_For} '
                f'%[src] unless {{ req.hdr({Header_Forwarded_For}) -m found }}',
        ]
    else:

        # Nothing in front is known to set these, so both are dropped and the address is the one
        # this frontend itself sees.
        directives = [
            f'http-request del-header {Header_Forwarded_For}',
            f'http-request del-header {Header_Zato_Forwarded_For}',
            f'http-request set-header {Header_Zato_Forwarded_For} %[src]',
        ]

    lines = [indent + Block_Start]

    for directive in directives:
        lines.append(indent + directive)

    lines.append(indent + Block_End)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def find_haproxy_config(server_base_directory:'str') -> 'str':
    """ Resolves the path to haproxy.cfg from the server's base directory.
    The server sits in e.g. /opt/zato/env/qs-1/server1 and haproxy.cfg
    is one level up at /opt/zato/env/qs-1/haproxy.cfg.
    """

    # Go up one level from the server directory to the environment root ..
    environment_directory = os.path.join(server_base_directory, '..')
    environment_directory = os.path.abspath(environment_directory)

    # .. and build the path to haproxy.cfg.
    out = os.path.join(environment_directory, 'haproxy.cfg')

    return out

# ################################################################################################################################

def set_forwarded_headers_trust(config_path:'str', is_trusted:'bool') -> 'int':
    """ Rewrites every marked forwarded-headers block in the configuration file. Returns how many
    blocks were replaced, which is zero for a configuration that carries no markers.
    """
    with open(config_path, 'r') as config_file:
        content = config_file.read()

    def replace_one(match:'re.Match') -> 'str':
        indent = match.group(1)
        return build_forwarded_headers_block(is_trusted, indent)

    updated_content, block_count = _block_pattern.subn(replace_one, content)

    # Rewriting an unchanged file would still reload HAProxy for nothing, so it is skipped
    if updated_content == content:
        logger.info('Forwarded-headers blocks in %s already set to is_trusted=%s', config_path, is_trusted)
        return 0

    with open(config_path, 'w') as config_file:
        _ = config_file.write(updated_content)

    logger.info('Set is_trusted=%s on %d forwarded-headers block(s) in %s', is_trusted, block_count, config_path)

    return block_count

# ################################################################################################################################

def reload_haproxy(config_path:'str') -> 'bool':
    """ Sends SIGHUP to the HAProxy master process for a graceful configuration reload.
    HAProxy must run in master-worker mode (the -W flag) - only the master process
    reloads the configuration on SIGHUP, a standalone process merely dumps its state.
    Returns True if the signal was sent successfully.
    """

    # Find the HAProxy master process running with our configuration file - matching
    # on the full path makes sure we do not signal an unrelated HAProxy instance,
    # and the -o flag returns the oldest matching process, which is the master
    # because workers are forked from it after startup ..
    result = subprocess.run(
        ['pgrep', '-o', '-f', f'haproxy.*{config_path}'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning('Could not find a running HAProxy process to reload')
        return False

    pid = result.stdout.strip()

    if not pid:
        logger.warning('pgrep returned empty output when looking for HAProxy')
        return False

    pid = int(pid)

    # .. and send SIGHUP to the master so it re-reads the configuration and replaces its workers.
    try:
        os.kill(pid, signal.SIGHUP)
        logger.info('Sent SIGHUP to HAProxy master process %d', pid)
        out = True
    except ProcessLookupError:
        logger.warning('HAProxy process %d no longer exists', pid)
        out = False
    except PermissionError:
        logger.warning('No permission to signal HAProxy process %d', pid)
        out = False

    return out

# ################################################################################################################################

def apply_trust_from_env(config_path:'str', needs_reload:'bool'=True) -> 'None':
    """ Brings the configuration file in line with the environment variable and, unless told
    otherwise, has a running HAProxy pick the change up.
    """
    if not os.path.exists(config_path):
        logger.info('No HAProxy configuration at %s, nothing to update', config_path)
        return

    is_trusted = is_trust_enabled()
    block_count = set_forwarded_headers_trust(config_path, is_trusted)

    # A file that did not change cannot need a reload
    if needs_reload and block_count:
        _ = reload_haproxy(config_path)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Applies the environment variable to the configuration file named on the command line.
    Used at container start, where HAProxy has not been started yet and needs no reload.
    """
    config_path = sys.argv[1]
    apply_trust_from_env(config_path, needs_reload=False)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
