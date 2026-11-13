# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels with generated URL paths are matched by the REST channel router exactly as by the Python matcher,
# including the parameters captured, the order among overlapping channels and the methods a 405 response allows.

# hypothesis
from hypothesis import event, given, HealthCheck, settings, strategies as st

# Zato
from router_compare import compare, pinned_time
from router_environment import Clock, make_channel, RouterWorld
from router_requests import make_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_start_us = 1_794_571_200_000_000

_parameter_names = ['id', 'name', 'item_id', 'x1']

_literal_alphabet = 'abZ09_-.~+*?()[]^$|\\:;=@!, %\u017c'

_value_alphabet = 'abZ09_-.~+:;=@!, %/\u017c'

_literals = st.text(alphabet=_literal_alphabet, min_size=1, max_size=5)

# ################################################################################################################################
# ################################################################################################################################

@st.composite
def _url_paths(draw:'any_') -> 'str':
    """ Returns the URL path of a channel - literal segments, parameter segments and segments mixing both.
    """
    segment_count = draw(st.integers(min_value=1, max_value=4))
    names = draw(st.permutations(_parameter_names))

    segments = []

    for _ in range(segment_count):
        kind = draw(st.sampled_from(['literal', 'literal', 'parameter', 'mixed']))

        if kind == 'literal':
            segment = draw(_literals)

        elif names:
            name = names.pop()
            if kind == 'parameter':
                segment = '{' + name + '}'
            else:
                prefix = draw(st.sampled_from(['', 'v', 'a.']))
                suffix = draw(st.sampled_from(['', '.json', '-x']))
                segment = prefix + '{' + name + '}' + suffix

        else:
            segment = draw(_literals)

        segments.append(segment)

    trailing = draw(st.sampled_from(['', '/']))
    out = '/' + '/'.join(segments) + trailing

    return out

# ################################################################################################################################

def _fill(url_path:'str', values:'anylist') -> 'str':
    """ Returns a request path of a channel URL path, with each parameter replaced by the next of the values.
    """
    out = ''
    index = 0
    position = 0

    while position < len(url_path):
        character = url_path[position]

        if character == '{':
            end = url_path.index('}', position)
            out += values[index % len(values)]
            index += 1
            position = end + 1
        else:
            out += character
            position += 1

    return out

# ################################################################################################################################

@st.composite
def _scenarios(draw:'any_') -> 'any_':
    """ Returns the channels of one world and the requests sent to them.
    """
    channel_count = draw(st.integers(min_value=1, max_value=3))

    definitions = []

    for index in range(channel_count):
        url_path = draw(_url_paths())
        definition = make_channel(
            f'generated.{index}',
            draw(st.sampled_from(['', 'GET', 'POST'])),
            url_path,
            match_slash=draw(st.sampled_from([None, True, False, ''])),
        )
        definitions.append(definition)

    request_count = draw(st.integers(min_value=1, max_value=6))
    requests = []

    for _ in range(request_count):
        definition = draw(st.sampled_from(definitions))
        values = draw(st.lists(st.text(alphabet=_value_alphabet, max_size=6), min_size=1, max_size=4))

        if draw(st.booleans()):
            path = _fill(definition['url_path'], values)
        else:
            path = '/' + '/'.join(values)

        method = draw(st.sampled_from(['GET', 'POST', 'DELETE']))
        requests.append(make_request(method, path))

    out = (definitions, requests)
    return out

# ################################################################################################################################
# ################################################################################################################################

@settings(max_examples=500, deadline=None, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(_scenarios())
def test_generated_channels(scenario:'any_') -> 'None':
    """ Any set of channels routes any request as the dispatcher does, and the router supports every one of them.
    """
    definitions, requests = scenario
    clock = Clock(_start_us)

    dispatcher_world = RouterWorld(definitions, clock)
    router_world = RouterWorld(definitions, clock)

    assert router_world.router.unsupported_channels() == []

    with pinned_time(clock):
        for request in requests:
            code = compare(dispatcher_world, router_world, request)
            event(f'Router outcome {code}')

# ################################################################################################################################
# ################################################################################################################################
