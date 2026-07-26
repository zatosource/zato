# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from re import compile as re_compile

# Zato
from zato.common.api import MISC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intnone, strnone
    any_ = any_
    anylist = anylist
    intnone = intnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

openapi_channel_name = 'zato.channel.openapi.get'
openapi_channel_url_path = '/openapi/{name}'
openapi_service_name = 'zato.server.service.internal.helpers.OpenAPIHandler'

as2_mdn_service_name = 'zato.server.service.internal.channel.as2.AS2MDNEndpoint'

# The longest URL path a channel may have, which is the width of the database column it is stored in.
Channel_URL_Path_Max_Length = 200

# What a path parameter's name may be built of - the same set the runtime compiles its matcher from.
_url_path_param_name_pattern = re_compile(r'^[\w $.\-:|=~^/]+$')

# The runtime joins a method, an Accept header and a URL path with this, so a path cannot carry it.
_target_separator = MISC.SEPARATOR

# What opens and closes a path parameter in a channel's URL path
_url_path_param_start = '{'
_url_path_param_end = '}'

# What a path parameter stands for while two URL paths are compared against one another - not a
# value a literal segment of a channel's path can be, so a parameter is never taken for a literal.
_url_path_probe = '\x00probe'

# ################################################################################################################################
# ################################################################################################################################

def create_openapi_channel(session, cluster, service):
    """ Creates the OpenAPI handler channel.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import HTTPSOAP

    channel = HTTPSOAP(
        None, openapi_channel_name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, openapi_channel_url_path, None, '', None, DATA_FORMAT.JSON,
        service=service, cluster=cluster)
    session.add(channel)

    return channel

# ################################################################################################################################
# ################################################################################################################################

def ensure_openapi_channel_exists(session, cluster_id):
    """ Checks if OpenAPI channel exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == openapi_channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    service = session.query(Service).filter(
        Service.name == openapi_service_name,
        Service.cluster_id == cluster_id,
    ).first()

    if not service:
        service = Service(None, openapi_service_name, True, openapi_service_name, True, cluster)
        session.add(service)
        session.flush()

    channel = HTTPSOAP(
        None, openapi_channel_name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, openapi_channel_url_path, None, '', None, DATA_FORMAT.JSON,
        service=service, cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_channel_exists(session, cluster_id):
    """ Checks if the AS2 inbound channel exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import AS2, CONNECTION, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == AS2.Default.Channel_Name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    # The dispatcher handles AS2 channels itself, so there is no service to point to,
    # and the data format is None so the raw MIME body arrives untouched.
    channel = HTTPSOAP(
        None, AS2.Default.Channel_Name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.AS2, None, AS2.Default.Channel_URL_Path, None, '', None, None,
        cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def validate_channel_url_path(url_path:'str') -> 'None':
    """ Checks that a channel's URL path is one a match target can be compiled from, raising
    an exception that names the first problem found.
    """
    if not url_path.startswith('/'):
        raise Exception(f'A channel URL path has to start with a slash, this one does not: `{url_path}`')

    path_length = len(url_path)

    if path_length > Channel_URL_Path_Max_Length:
        limit_part = f'A channel URL path takes up to {Channel_URL_Path_Max_Length} characters,'
        raise Exception(f'{limit_part} this one has {path_length}: `{url_path}`')

    if _target_separator in url_path:
        raise Exception(f'A channel URL path cannot contain `{_target_separator}`: `{url_path}`')

    # Each parameter's name is kept as it is found, which is what tells a name used twice
    # from one used once, and each parameter's end tells whether the next one follows it directly.
    names = []
    position = 0
    previous_end = -1

    while True:

        start = url_path.find('{', position)

        # Nothing opens a parameter from here on, so what is left is literal
        if start == -1:
            break

        # The literal part in front of this parameter cannot close one of its own
        literal = url_path[position:start]
        if '}' in literal:
            raise Exception(f'A channel URL path closes a path parameter that was never opened: `{url_path}`')

        end = url_path.find('}', start)
        if end == -1:
            raise Exception(f'A channel URL path opens a path parameter that is never closed: `{url_path}`')

        name = url_path[start+1:end]

        if '{' in name:
            raise Exception(f'A channel URL path cannot nest path parameters: `{url_path}`')

        if not name:
            raise Exception(f'A channel URL path cannot have a path parameter with no name: `{url_path}`')

        if not _url_path_param_name_pattern.match(name):
            raise Exception(f'Path parameter `{name}` uses characters a channel URL path cannot: `{url_path}`')

        if name in names:
            raise Exception(f'Path parameter `{name}` is used more than once in `{url_path}`')

        # Two parameters with nothing between them have no boundary to divide the path on,
        # and each of them matches a run of any length, so the cost of trying every division
        # grows with the length of the URL a caller sends.
        if start == previous_end + 1:
            raise Exception(f'Path parameters need something between them, `{url_path}` has none')

        names.append(name)
        previous_end = end
        position = end + 1

    # What follows the last parameter is literal too and cannot close one either
    if '}' in url_path[position:]:
        raise Exception(f'A channel URL path closes a path parameter that was never opened: `{url_path}`')

# ################################################################################################################################
# ################################################################################################################################

def find_channel_collision(
    url_path,       # type: str
    http_accept,    # type: strnone
    http_method,    # type: strnone
    existing_items, # type: anylist
    skip_id         # type: intnone
) -> 'strnone':
    """ The one collision rule for HTTP channels - a candidate collides with an existing channel
    when both sit at the same URL path and their HTTP method and Accept header are equal too.
    Each existing item carries id, name, url_path, method and http_accept, and the item whose id
    is skip_id is the candidate itself, which an edit compares against everything but itself.
    Returns the name of the colliding channel or None. Callers differ only in how they load
    the existing items - zato.http-soap.create with its per-candidate query, enmasse with
    its one SELECT for everything.
    """
    for item in existing_items:

        # A different URL path can never collide ..
        if item['url_path'] != url_path:
            continue

        # .. and an edit does not collide with the channel it is editing ..
        if item['id'] == skip_id:
            continue

        # .. it takes both the same method and the same Accept header to collide.
        if item['method'] == http_method:
            if item['http_accept'] == http_accept:
                return item['name']

    return None

# ################################################################################################################################
# ################################################################################################################################

def _url_path_literal_length(url_path:'str') -> 'int':
    """ How much of a channel's URL path is matched literally, i.e. everything outside its path
    parameters. A parameter's name is no part of what the channel matches, so two paths that
    differ in nothing but the names of their parameters come to the same length here.
    """
    out = 0
    position = 0

    while True:

        start = url_path.find(_url_path_param_start, position)

        # What is left opens no parameter, so all of it is literal
        if start == -1:
            out += len(url_path) - position
            break

        out += start - position

        end = url_path.find(_url_path_param_end, start)

        # A parameter that is never closed is literal too, name and all
        if end == -1:
            out += len(url_path) - start
            break

        position = end + 1

    return out

# ################################################################################################################################

def channel_specificity(url_path:'str', http_accept:'strnone', http_method:'strnone') -> 'tuple':
    """ Returns how far a channel narrows down the requests that reach it, which is what decides
    between two channels a request matches both of. Each element is negated, so that ordering
    channels by this puts the one that leaves the least open first.

    A path parameter takes in whole segments and, unless the channel says otherwise, several of
    them, so what a channel spells out literally is what tells its own requests from another's.
    """
    # Everything up to the first path parameter is matched literally, and a channel with more
    # of it before anything is left open speaks about a narrower set of paths ..
    literal_prefix_end = url_path.find(_url_path_param_start)

    if literal_prefix_end == -1:
        literal_prefix_length = len(url_path)
    else:
        literal_prefix_length = literal_prefix_end

    # .. what a channel spells out past that point narrows it down further ..
    # .. and a channel that names an Accept value or a method of its own is reached by fewer
    # requests than one that takes whatever arrives.
    out = (-literal_prefix_length, -_url_path_literal_length(url_path), not http_accept, not http_method)

    return out

# ################################################################################################################################

def channel_security_key(security_id:'any_', security_groups:'anylist | None') -> 'tuple':
    """ Returns what a channel authenticates its requests against, in a form two channels' can be
    compared by. Ids arrive as numbers from the database and as strings from the Dashboard.
    """
    if security_id:
        definition = int(security_id)
    else:
        definition = None

    if security_groups:
        groups = tuple(sorted(int(elem) for elem in security_groups))
    else:
        groups = ()

    out = (definition, groups)
    return out

# ################################################################################################################################

def _url_path_segments(url_path:'str') -> 'anylist':
    """ Splits a channel's URL path into the segments a request's own path is compared against.
    """
    out = [elem for elem in url_path.split('/') if elem]
    return out

# ################################################################################################################################

def _is_param_segment(segment:'str') -> 'bool':
    """ Whether the whole of a segment is one path parameter, which is what makes it stand for
    whatever a caller sends there. A segment that merely carries a parameter within it, such as
    `invoice-{id}`, is compared as the literal it mostly is.
    """
    if not segment.startswith('{'):
        return False

    if not segment.endswith('}'):
        return False

    out = segment.count('{') == 1
    return out

# ################################################################################################################################

def _probe_segments(segments:'anylist') -> 'anylist':
    """ Returns the segments with a value standing in for each parameter, which turns a channel's
    path into one concrete path that channel is reached by.
    """
    out = [_url_path_probe if _is_param_segment(elem) else elem for elem in segments]
    return out

# ################################################################################################################################

def _channel_reaches(pattern:'anylist', path:'anylist', match_slash:'bool') -> 'bool':
    """ Whether a channel whose URL path is the given pattern is reached by the given path.
    A parameter takes in one segment, or one and more when the channel matches across slashes.
    """
    # How far into the path each way of matching the pattern so far has come
    reached = {0}

    for elem in pattern:

        next_reached = set()

        for position in reached:

            # Nothing is left of the path for this part of the pattern to take in
            if position >= len(path):
                continue

            if _is_param_segment(elem):

                # A parameter that matches across slashes takes in every run of segments
                # from here on, so each of those is a way for the rest of the pattern to go
                if match_slash:
                    for end in range(position + 1, len(path) + 1):
                        next_reached.add(end)
                else:
                    next_reached.add(position + 1)

            elif path[position] == elem:
                next_reached.add(position + 1)

        reached = next_reached

        # No way of matching the pattern is left, so there is nothing to carry on with
        if not reached:
            return False

    # The pattern is matched only by a path it took the whole of in
    out = len(path) in reached
    return out

# ################################################################################################################################

def url_paths_overlap(first:'str', second:'str', first_match_slash:'bool', second_match_slash:'bool') -> 'bool':
    """ Whether some one path a caller may send is matched by both channels' URL paths.

    Each path is turned into a concrete one by standing a value in for its parameters, and that is
    tried against the other channel - both ways round, since either may be the broader of the two.
    """
    first_segments = _url_path_segments(first)
    second_segments = _url_path_segments(second)

    if _channel_reaches(first_segments, _probe_segments(second_segments), first_match_slash):
        return True

    if _channel_reaches(second_segments, _probe_segments(first_segments), second_match_slash):
        return True

    return False

# ################################################################################################################################

def _slots_overlap(first:'strnone', second:'strnone') -> 'bool':
    """ Whether two channels' method slots, or their Accept slots, are reached by one request.
    A channel that names nothing there takes whatever arrives.
    """
    if not first:
        return True

    if not second:
        return True

    out = first == second
    return out

# ################################################################################################################################

def find_channel_conflict(
    url_path,       # type: str
    http_accept,    # type: strnone
    http_method,    # type: strnone
    match_slash,    # type: bool
    security,       # type: tuple
    existing_items, # type: anylist
    skip_id         # type: intnone
) -> 'strnone':
    """ Returns the name of a channel that one request could reach either of, with the candidate,
    while the two secure that request differently and neither of them is the narrower one - or None
    when there is no such channel.

    Of two channels a request matches, the narrower one answers it, so this leaves the pairs where
    neither is narrower and their names are all there is to order them by. A name is no way to
    settle which of two channels secures a request, so such a pair is refused.
    """
    specificity = channel_specificity(url_path, http_accept, http_method)

    for item in existing_items:

        # An edit does not conflict with the channel it is editing ..
        if item['id'] == skip_id:
            continue

        # .. two channels that secure a request the same way answer it the same way either ..
        if item['security'] == security:
            continue

        # .. one of them being the narrower one is what decides between them ..
        if channel_specificity(item['url_path'], item['http_accept'], item['method']) != specificity:
            continue

        # .. and neither has anything to do with the other unless a request can reach both.
        if not _slots_overlap(item['method'], http_method):
            continue

        if not _slots_overlap(item['http_accept'], http_accept):
            continue

        if url_paths_overlap(url_path, item['url_path'], match_slash, item['match_slash']):
            return item['name']

    return None

# ################################################################################################################################
# ################################################################################################################################

def get_channel_collision_items(session:'any_', cluster_id:'int') -> 'anylist':
    """ Returns every channel in the cluster with the fields the collision and conflict rules compare.
    """
    from zato.common.api import CONNECTION
    from zato.common.odb.model import HTTPSOAP
    from zato.common.util.sql import parse_instance_opaque_attr
    from zato.common.util.url_dispatcher import resolve_match_slash

    existing_ones = session.query(HTTPSOAP).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
        all()

    out = []

    for item in existing_ones:
        opaque = parse_instance_opaque_attr(item)
        out.append({
            'id': item.id,
            'name': item.name,
            'url_path': item.url_path,
            'method': item.method,
            'http_accept': opaque.get('http_accept'),
            'match_slash': resolve_match_slash(opaque.get('match_slash')),
            'security': channel_security_key(item.security_id, opaque.get('security_groups')),
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_channel_definitions_are_unique(session:'any_', cluster_id:'int', channel_defs:'anylist') -> 'None':
    """ Checks a batch of channel definitions against the channels already in the cluster and
    against each other, the same way the create and edit services check a single one.
    """
    existing_items = get_channel_collision_items(session, cluster_id)

    # What the batch itself has already claimed, so that one batch cannot define
    # two channels that resolve to the same match target.
    claimed = {}

    for channel_def in channel_defs:

        name = channel_def['name']
        url_path = channel_def['url_path']

        validate_channel_url_path(url_path)

        # A definition that says nothing about either of these matches the way the services do
        # when they are not given: any method, and any Accept header.
        method = channel_def.get('method')
        if not method:
            method = ''

        http_accept = channel_def.get('http_accept')

        # An update carries the id of the channel it updates, which it does not collide with
        skip_id = channel_def.get('id')

        colliding_name = find_channel_collision(url_path, http_accept, method, existing_items, skip_id)

        if colliding_name:
            raise Exception(f'Channel `{name}` has the URL path, method and Accept header of `{colliding_name}`: `{url_path}`')

        target = (url_path, method, http_accept)

        if claimed_name := claimed.get(target):
            both_part = f'Channels `{claimed_name}` and `{name}` both have the URL path,'
            raise Exception(f'{both_part} method and Accept header: `{url_path}`')

        claimed[target] = name

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_mdn_channel_exists(session, cluster_id):
    """ Checks if the channel for incoming asynchronous AS2 MDNs exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import AS2, CONNECTION, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == AS2.Default.MDN_Channel_Name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    service = session.query(Service).filter(
        Service.name == as2_mdn_service_name,
        Service.cluster_id == cluster_id,
    ).first()

    if not service:
        service = Service(None, as2_mdn_service_name, True, as2_mdn_service_name, True, cluster)
        session.add(service)
        session.flush()

    # The data format is None so the raw MDN body arrives untouched.
    channel = HTTPSOAP(
        None, AS2.Default.MDN_Channel_Name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, AS2.Default.MDN_Channel_URL_Path, None, '', None, None,
        service=service, cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################
