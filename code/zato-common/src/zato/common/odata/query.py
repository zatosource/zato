# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import quote
from uuid import UUID

# Zato
from zato.common.odata.common import ODataException, ODataVersion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# Characters that stay unescaped in a query option value - RFC 3986 unreserved characters
# plus the sub-delimiters the OData ABNF allows inside query strings.
_query_safe = "'(),*/:$=!@ "

# ################################################################################################################################
# ################################################################################################################################

def format_literal(value:'any_', odata_version:'str'=ODataVersion.V4) -> 'str':
    """ Formats one Python value as an OData primitive literal - strings are quoted
    with embedded quotes doubled, booleans and None map to their keywords, GUIDs
    are bare in V4 and wrapped in guid'..' in V2, numbers pass through as they are.
    """
    if value is None:
        out = 'null'

    elif isinstance(value, bool):
        out = 'true' if value else 'false'

    elif isinstance(value, UUID):
        if odata_version == ODataVersion.V2:
            out = f"guid'{value}'"
        else:
            out = str(value)

    elif isinstance(value, str):
        escaped = value.replace("'", "''")
        out = f"'{escaped}'"

    # Anything else is a number, which both versions serialize verbatim.
    else:
        out = str(value)

    return out

# ################################################################################################################################
# ################################################################################################################################

def format_key(key:'any_', odata_version:'str'=ODataVersion.V4) -> 'str':
    """ Formats an entity key as the parenthesized predicate of a resource path -
    a single value renders alone, a dict renders as comma-joined name=value pairs
    the way multi-part keys require.
    """
    if isinstance(key, dict):
        parts:'strlist' = []
        for name, value in key.items():
            literal = format_literal(value, odata_version)
            parts.append(f'{name}={literal}')

        out = ','.join(parts)

    else:
        out = format_literal(key, odata_version)

    return out

# ################################################################################################################################
# ################################################################################################################################

class Query:
    """ A builder of OData system query options - each option is optional and the result
    is a dict of parameters ready to travel in a URL's query string. Custom parameters,
    e.g. sap-client or cross-company, ride along with the system ones.
    """
    def __init__(
        self,
        *,
        filter:'strnone'=None,   # noqa: A002
        select:'str | strlist | None'=None,
        expand:'str | strlist | None'=None,
        orderby:'str | strlist | None'=None,
        top:'int | None'=None,
        skip:'int | None'=None,
        count:'bool | None'=None,
        search:'strnone'=None,
        apply:'strnone'=None,    # noqa: A002
        custom:'strdict | None'=None,
        ) -> 'None':

        self.filter = filter
        self.select = select
        self.expand = expand
        self.orderby = orderby
        self.top = top
        self.skip = skip
        self.count = count
        self.search = search
        self.apply = apply
        self.custom = custom

# ################################################################################################################################

    def _join(self, value:'str | strlist') -> 'str':
        """ Returns a comma-separated option value - lists are joined, strings pass through.
        """
        if isinstance(value, str):
            out = value
        else:
            out = ','.join(value)

        return out

# ################################################################################################################################

    def to_params(self, odata_version:'str'=ODataVersion.V4) -> 'strdict':
        """ Returns the query options as a dict of parameters - $count in V4 becomes
        $inlinecount in V2, everything else is spelled the same in both versions.
        """

        # Our response to produce
        out:'strdict' = {}

        if self.filter is not None:
            out['$filter'] = self.filter

        if self.select is not None:
            out['$select'] = self._join(self.select)

        if self.expand is not None:
            out['$expand'] = self._join(self.expand)

        if self.orderby is not None:
            out['$orderby'] = self._join(self.orderby)

        if self.top is not None:
            out['$top'] = str(self.top)

        if self.skip is not None:
            out['$skip'] = str(self.skip)

        # The inline count option changed both its name and its values between the versions.
        if self.count is not None:
            if odata_version == ODataVersion.V2:
                out['$inlinecount'] = 'allpages' if self.count else 'none'
            else:
                out['$count'] = 'true' if self.count else 'false'

        # $search and $apply exist in V4 only.
        if self.search is not None:
            if odata_version == ODataVersion.V2:
                raise ODataException('$search is not available in OData 2.0')
            out['$search'] = self.search

        if self.apply is not None:
            if odata_version == ODataVersion.V2:
                raise ODataException('$apply is not available in OData 2.0')
            out['$apply'] = self.apply

        if self.custom:
            out.update(self.custom)

        return out

# ################################################################################################################################

    def to_query_string(self, odata_version:'str'=ODataVersion.V4) -> 'str':
        """ Returns the query options as an encoded query string, without the leading '?'.
        """
        params = self.to_params(odata_version)

        out = encode_params(params)
        return out

# ################################################################################################################################
# ################################################################################################################################

def encode_params(params:'strdict') -> 'str':
    """ Encodes parameters into a query string, percent-encoding what RFC 3986 requires
    while leaving the characters the OData grammar allows in query options intact.
    """
    parts:'strlist' = []

    for name, value in params.items():
        encoded_name = quote(name, safe='$')
        encoded_value = quote(value, safe=_query_safe).replace(' ', '%20')
        parts.append(f'{encoded_name}={encoded_value}')

    out = '&'.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_query(query:'Query | None'=None, **options:'any_') -> 'Query':
    """ Returns a Query out of an existing one or keyword options - what client methods
    accept as their query input.
    """
    if query is not None:
        out = query
    else:
        out = Query(**options)

    return out

# ################################################################################################################################
# ################################################################################################################################

def format_function_params(params:'anydict', odata_version:'str'=ODataVersion.V4) -> 'str':
    """ Formats function parameters as the parenthesized part of a V4 function call,
    e.g. GetNearestAirport(lat=33,lon=-118).
    """
    parts:'strlist' = []

    for name, value in params.items():
        literal = format_literal(value, odata_version)
        parts.append(f'{name}={literal}')

    out = ','.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
