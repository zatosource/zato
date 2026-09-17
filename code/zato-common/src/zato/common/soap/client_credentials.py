# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The body credentials of an outgoing SOAP connection - the username and password a body-authenticated
# endpoint expects as children of the operation element, where the connection's mapping says they go, and
# the names of those children so an audit record can mask them. The mapping and the values are the
# `body_credentials` dict of the client's config and every function here reads them from it.

# stdlib
from operator import itemgetter

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import SOAPException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist, strnone
    any_ = any_
    anydict = anydict
    anylist = anylist
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The lowest position a body credential mapping may name. Positions are 1-based, matching what the
# dashboard shows, so 1 means the operation's first child.
Minimum_Credential_Position = 1

# What body credentials look like when a connection enables them without spelling out
# a mapping of its own - one element per credential, each named after what it carries.
Default_Body_Credential_Mappings = [
    {'name': 'username', 'source': 'username'},
    {'name': 'password', 'source': 'password'},
]

# ################################################################################################################################
# ################################################################################################################################

def credential_mappings(body_credentials:'stranydict') -> 'anylist':
    """ Returns the body-credential mapping rows this connection injects by, which is the
    default pair of a username and a password element when it spells out no mapping of its own.
    """
    out = body_credentials.get('mappings')

    if not out:
        out = Default_Body_Credential_Mappings

    return out

# ################################################################################################################################

def inject_body_credentials(body_credentials:'stranydict', operation:'any_') -> 'None':
    """ Injects the configured credentials as child elements of the operation element -
    by default as its first children in mapping order, or at explicit 1-based positions.
    The elements inherit the operation's namespace, so they sit in the message like any
    other field, which is what body-authenticated endpoints such as CDC IIS require.
    """
    namespace = None
    if operation.tag.startswith('{'):
        namespace = operation.tag[1:].partition('}')[0]

    mappings = credential_mappings(body_credentials)

    # Rows without a position prepend in mapping order, positioned rows slot in afterwards.
    default_rows = []
    positioned_rows = []

    for row in mappings:
        position = row.get('position')

        if position is None:
            default_rows.append(row)
            continue

        # A position is 1-based, so anything below 1 is a configuration error. Left unchecked it
        # becomes a negative index, which lxml reads from the end of the children - a credential
        # that was meant to lead the message ends up trailing it, in a place the receiving
        # endpoint does not look, and the request fails authentication for no visible reason.
        if position < Minimum_Credential_Position:
            name = row['name']
            raise SOAPException(
                f'Body credential position must be at least {Minimum_Credential_Position}, not `{position}` -> `{name}`')

        positioned_rows.append(row)

    # The default rows go in ahead of whatever the operation already carries. They are built
    # first and inserted in one reversed pass at the front, so each one is placed without
    # walking past the elements the previous ones were placed at.
    default_elements = []

    for row in default_rows:
        default_elements.append(_new_credential_element(body_credentials, row, namespace))

    for element in reversed(default_elements):
        operation.insert(0, element)

    positioned_rows.sort(key=itemgetter('position'))

    for row in positioned_rows:
        element = _new_credential_element(body_credentials, row, namespace)
        operation.insert(row['position'] - 1, element)

# ################################################################################################################################

def _new_credential_element(body_credentials:'stranydict', row:'anydict', namespace:'strnone') -> 'any_':
    """ Builds one credential element out of a mapping row and the configured credentials.
    """
    source = row.get('source') or row['name']
    value = body_credentials[source]

    if namespace:
        element = etree.Element(f'{{{namespace}}}{row["name"]}')
    else:
        element = etree.Element(row['name'])

    element.text = value

    return element

# ###############################################################################################################################

def body_credential_names(body_credentials:'stranydict') -> 'strlist | None':
    """ Returns the names of the operation children that carry credentials, if any do.

    Only the connection knows them, since they come from its own mapping rather than from
    anything in the message, and an audit record cannot mask what it cannot name.
    """
    if not body_credentials:
        return None

    out = []

    for row in credential_mappings(body_credentials):
        out.append(row['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################
