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

# Whether the connections arriving at the MLLP frontend open with a PROXY protocol header. This is
# off unless something in front of HAProxy is known to send one, because the directive it turns on
# is mandatory - a frontend that requires the header refuses a sender that connects without it.
Env_MLLP_Expect_Proxy = 'Zato_MLLP_Expect_Proxy'

# The generated directives live between these markers, one pair per frontend, so that the block
# can be replaced without the rest of the frontend being touched.
Block_Start = '#<zato-forwarded-headers>'
Block_End   = '#</zato-forwarded-headers>'

# The same arrangement for the MLLP frontend, which is TCP and so carries no header directives.
MLLP_Block_Start = '#<zato-mllp-expect-proxy>'
MLLP_Block_End   = '#</zato-mllp-expect-proxy>'

def _build_block_pattern(start_marker:'str', end_marker:'str') -> 're.Pattern':
    """ Matches one marked block along with the indentation of its opening marker, which the generated
    lines reuse so the result stays aligned with the surrounding directives.
    """
    out = re.compile(
        r'([ \t]*)' + re.escape(start_marker) + r'.*?' + re.escape(end_marker),
        re.DOTALL,
    )
    return out

_block_pattern      = _build_block_pattern(Block_Start, Block_End)
_mllp_block_pattern = _build_block_pattern(MLLP_Block_Start, MLLP_Block_End)

# ################################################################################################################################

def _is_env_enabled(variable_name:'str', environ:'dict | None') -> 'bool':
    """ Returns whether an on-off environment variable is on, an absent one counting as off.
    """
    if environ is None:
        environ = dict(os.environ)

    # These variables are genuinely optional, so absence is the same as the setting being off
    raw_value = environ.get(variable_name)

    if raw_value is None:
        out = False
    else:
        out = raw_value.strip().lower() in Trust_Enabled_Values

    return out

# ################################################################################################################################

def is_trust_enabled(environ:'dict | None'=None) -> 'bool':
    """ Returns whether the forwarding headers reaching HAProxy are to be trusted.
    """
    out = _is_env_enabled(Env_Trust_Forwarded_Headers, environ)
    return out

# ################################################################################################################################

def is_mllp_expect_proxy_enabled(environ:'dict | None'=None) -> 'bool':
    """ Returns whether the MLLP frontend requires each connection to open with a PROXY header.
    """
    out = _is_env_enabled(Env_MLLP_Expect_Proxy, environ)
    return out

# ################################################################################################################################

def _build_marked_block(start_marker:'str', end_marker:'str', directives:'list', indent:'str') -> 'str':
    """ Wraps generated directives in the markers that make the block replaceable.
    """
    lines = [indent + start_marker]

    for directive in directives:
        lines.append(indent + directive)

    lines.append(indent + end_marker)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def build_forwarded_headers_block(is_trusted:'bool', indent:'str'='    ') -> 'str':
    """ Builds the HAProxy directives that decide what the client address reported to Zato is,
    wrapped in the markers that make the block replaceable.
    """
    if is_trusted:

        # Whatever is in front reported an address, so the last element is taken - that is the one
        # the nearest proxy appended, whereas the first is whatever the caller put there itself.
        set_header = f'http-request set-header {Header_Zato_Forwarded_For}'
        was_reported = f'{{ req.hdr({Header_Forwarded_For}) -m found }}'

        directives = [
            f'http-request del-header {Header_Zato_Forwarded_For}',
            f'{set_header} %[req.hdr({Header_Forwarded_For},-1)] if {was_reported}',
            f'{set_header} %[src] unless {was_reported}',
        ]
    else:

        # Nothing in front is known to set these, so both are dropped and the address is the one
        # this frontend itself sees.
        directives = [
            f'http-request del-header {Header_Forwarded_For}',
            f'http-request del-header {Header_Zato_Forwarded_For}',
            f'http-request set-header {Header_Zato_Forwarded_For} %[src]',
        ]

    out = _build_marked_block(Block_Start, Block_End, directives, indent)
    return out

# ################################################################################################################################

def build_mllp_expect_proxy_block(is_expected:'bool', indent:'str'='    ') -> 'str':
    """ Builds the MLLP frontend directive that decides whether a connection has to open with a
    PROXY protocol header, wrapped in the markers that make the block replaceable.
    """
    if is_expected:

        # Something in front reports the sender's address this way, and the directive is mandatory
        # once present, so a connection arriving without the header is closed rather than served.
        directives = ['tcp-request connection expect-proxy layer4']
    else:

        # Nothing in front is known to send one, so the address is whatever this frontend itself sees
        directives = []

    out = _build_marked_block(MLLP_Block_Start, MLLP_Block_End, directives, indent)
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

def _rewrite_blocks(config_path:'str', pattern:'re.Pattern', builder:'object', description:'str') -> 'int':
    """ Rewrites every block the pattern marks out in the configuration file. Returns how many
    blocks were replaced, which is zero for a configuration that carries no markers and zero
    for one whose blocks already say what they are being set to.
    """
    with open(config_path, 'r') as config_file:
        content = config_file.read()

    def replace_one(match:'re.Match') -> 'str':
        indent = match.group(1)
        return builder(indent) # type: ignore[operator]

    updated_content, block_count = pattern.subn(replace_one, content)

    # Rewriting an unchanged file would still reload HAProxy for nothing, so it is skipped
    if updated_content == content:
        logger.info('%s blocks in %s already up to date', description, config_path)
        return 0

    with open(config_path, 'w') as config_file:
        _ = config_file.write(updated_content)

    logger.info('Rewrote %d %s block(s) in %s', block_count, description, config_path)

    return block_count

# ################################################################################################################################

def set_forwarded_headers_trust(config_path:'str', is_trusted:'bool') -> 'int':
    """ Rewrites every marked forwarded-headers block in the configuration file. Returns how many
    blocks were replaced, which is zero for a configuration that carries no markers.
    """
    def builder(indent:'str') -> 'str':
        return build_forwarded_headers_block(is_trusted, indent)

    out = _rewrite_blocks(config_path, _block_pattern, builder, 'forwarded-headers')
    return out

# ################################################################################################################################

def set_mllp_expect_proxy(config_path:'str', is_expected:'bool') -> 'int':
    """ Rewrites the marked MLLP expect-proxy block in the configuration file. Returns how many
    blocks were replaced, which is zero for a configuration that carries no markers.
    """
    def builder(indent:'str') -> 'str':
        return build_mllp_expect_proxy_block(is_expected, indent)

    out = _rewrite_blocks(config_path, _mllp_block_pattern, builder, 'MLLP expect-proxy')
    return out

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

def apply_env(config_path:'str', needs_reload:'bool'=True) -> 'None':
    """ Brings every generated block in the configuration file in line with the environment
    variables that drive it and, unless told otherwise, has a running HAProxy pick the change up.
    """
    if not os.path.exists(config_path):
        logger.info('No HAProxy configuration at %s, nothing to update', config_path)
        return

    block_count = set_forwarded_headers_trust(config_path, is_trust_enabled())
    block_count += set_mllp_expect_proxy(config_path, is_mllp_expect_proxy_enabled())

    # A file that did not change cannot need a reload
    if needs_reload and block_count:
        _ = reload_haproxy(config_path)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Applies the environment variables to the configuration file named on the command line.
    Used at container start, where HAProxy has not been started yet and needs no reload.
    """
    config_path = sys.argv[1]
    apply_env(config_path, needs_reload=False)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
