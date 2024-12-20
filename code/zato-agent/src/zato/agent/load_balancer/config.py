# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from string import punctuation

# PyParsing
from pyparsing import Or, Word, Literal, nums, alphanums, alphas, restOfLine

# Zato
from zato.common.haproxy import http_log, Config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pyparsing import ParserElement
    ParserElement = ParserElement

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# It's something Zato can understood and treat accordingly if such a token is
# found on any HAProxy configuration file's line.
zato_item_token = '# ZATO '

# PyParsing grammar for config values.

uri = Word(alphanums + punctuation)
backend_server = Literal('server').suppress() + Word(alphanums + '.-_') + \
                             Word(alphanums + '.-_') + Literal(':').suppress() + \
                             Word(nums) + restOfLine
simple_option = Literal('option').suppress() + Word(alphas)
frontend_bind = Literal('bind').suppress() + Or('*' | Word(alphanums + '.-_')) + Literal(':').suppress() + Word(nums)
maxconn = Literal('maxconn').suppress() + Word(nums)
timeout = Literal('timeout').suppress() + Word(alphas).suppress() + Word(nums)

global_log = Literal('log').suppress() + Word(alphanums + '.-_') + Literal(':').suppress() + \
                   Word(nums) + Word(alphanums) + Word(alphanums)
option_httpchk = Literal('option httpchk').suppress() + Word(alphas) + uri
monitor_uri = Literal('monitor-uri').suppress() + uri
stats_uri = Literal('stats uri').suppress() + uri
stats_socket = Literal('stats socket').suppress() + uri

# Config tokens recognized by the parser -> PyParsing grammar for their respective
# values.
config_tokens_grammar = {
    'global:log':global_log,
    'global:stats_socket':stats_socket,
    'defaults:timeout connect':timeout,
    'defaults:timeout client':timeout,
    'defaults:timeout server':timeout,
    'defaults:stats uri':stats_uri,
    'backend bck_http_plain:server': backend_server,
    'backend bck_http_plain:option httpchk': option_httpchk,
    'frontend front_http_plain:monitor-uri':monitor_uri,
    'frontend front_http_plain:option log-http-requests':simple_option,
    'frontend front_http_plain:bind':frontend_bind,
    'frontend front_http_plain:maxconn':maxconn,
}

backend_template = 'server {server_type}--{server_name} '
backend_template += '{address}:{port} {extra} '
backend_template += '{zato_item_token}backend {backend_type}:server--{server_name}'

def config_from_string(data):
    """ Given a string representing a HAProxy configuration, returns a Config
    object representing it.
    """
    config = Config()

    for line in data.split('\n'):
        if zato_item_token not in line:
            continue
        value, config_token_name = line.split(zato_item_token)
        value = value.strip()
        if value.startswith('#'):
            continue

        for token_name in config_tokens_grammar:
            if config_token_name.startswith(token_name):
                parser_elem = config_tokens_grammar[token_name] # type: ParserElement|None
                if parser_elem:
                    result = parser_elem.parseString(value)
                    config.set_value(token_name, result)
    return config

def string_from_config(config, config_template):
    """ Given a Config object and the current HAProxy configuration returns
    a string representing the new HAProxy configuration, which can be validated
    by HAProxy and optionally saved.
    """

    # Keys are HAProxy options understood by Zato. Values are two-element lists,
    # index 0 is a template to use for the new value and index 1 is the values
    # from the configuration to use in the template. Note that not all items
    # understood by Zato are given here, that's because not all of them are editable
    # by users and we simply won't receive them on input in the 'config' object.
    zato_item_dispatch = {
        'global:log': ('log {host}:{port} {facility} {level}', config['global_']['log']),

        'defaults:timeout connect': ('timeout connect {timeout_connect}', config['defaults']),
        'defaults:timeout client': ('timeout client {timeout_client}', config['defaults']),
        'defaults:timeout server': ('timeout server {timeout_server}', config['defaults']),

        'frontend front_http_plain:monitor-uri': ('monitor-uri {monitor_uri}', config['frontend']['front_http_plain']),
        'frontend front_http_plain:bind': ('bind {address}:{port}', config['frontend']['front_http_plain']['bind']),
        'frontend front_http_plain:maxconn': ('maxconn {maxconn}', config['frontend']['front_http_plain']),

        # That below, it looks .. well you know what I mean. But that's the price of
        # using a generic dispatch dictionary. Basically, it boils down to
        # getting a value to use for logging but in the HAProxy format. We were
        # given a string representing an integer and we need to translate it
        # back to a format understood by HAProxy, so that '1' translates into 'nolog' etc.

        'frontend front_http_plain:option log-http-requests':                                                               # noqa
          ('option {value}', dict(value=http_log[int(config['frontend']['front_http_plain']['log_http_requests'])][0])), # noqa
    }

    new_config = []
    for line in config_template:

        # Make sure we don't accidentally overwrite something that's not ours.
        if zato_item_token in line:
            if 'bck_http' in line or [key for key in zato_item_dispatch if key in line]:

                # Let's see how much the line was indented in the template
                indent = len(line) - len(line.strip()) - 1 # -1 because of the \n
                new_line = ' ' * indent

                # Let's see to the simple options first..
                for zato_item, (template, value) in zato_item_dispatch.items():
                    if zato_item_token + zato_item in line:
                        new_line += template.format(**value) + ' ' + zato_item_token + zato_item # pylint: disable=not-a-mapping

                # .. and the more complex ones now.
                if zato_item_token + 'backend' in line and '--' in line:
                    line = line.split(zato_item_token + 'backend')
                    backend_info = line[1].split('--')
                    backend_type, server_name = (backend_info[0].strip().split(':')[0], backend_info[1].strip())
                    server_type = backend_type.split('bck_')[1]

                    backend_values = {
                        'backend_type': backend_type,
                        'server_name':server_name,
                        'server_type':server_type,
                        'zato_item_token': zato_item_token
                    }
                    backend_values.update(config['backend'][backend_type][server_name])

                    new_line += backend_template.format(**backend_values)
                else:
                    for name in ('begin', 'end'):
                        prefix = '{}{}'.format(zato_item_token, name)
                        if line.startswith(prefix):
                            new_line += line
                new_line += '\n'
                new_config.append(new_line)
            else:
                new_config.append(line)
        else:
            new_config.append(line)

    return ''.join(new_config)
