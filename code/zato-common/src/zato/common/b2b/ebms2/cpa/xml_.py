# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from datetime import timedelta

# Zato
from zato.common.b2b.ebms2.agreement import Duration
from zato.common.b2b.ebms2.common import CPAException, NS
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strfloatdict, strnone
    any_ = any_
    anylist = anylist
    strfloatdict = strfloatdict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# An xsd:duration, without a sign because no duration of an agreement is negative.
_duration_date_pattern = r'^P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?'
_duration_time_pattern = r'(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$'
_duration_pattern = re.compile(_duration_date_pattern + _duration_time_pattern)

# The number of days a year and a month of a duration count as, since an agreement period has no calendar anchor.
_days_per_year = 365
_days_per_month = 30

# ################################################################################################################################
# ################################################################################################################################

def tag(local_name:'str') -> 'str':
    """ Returns the qualified name of an element of the CPP/A namespace.
    """
    out = qname(NS.CPA, local_name)
    return out

# ################################################################################################################################

def local_name(element:'any_') -> 'str':
    """ Returns the name of an element without its namespace.
    """
    _, _, out = element.tag.rpartition('}')
    return out

# ################################################################################################################################

def get_attribute(element:'any_', name:'str') -> 'strnone':
    """ Returns an attribute of the CPP/A namespace, which the schema qualifies, or None. Documents that
    write the attribute unqualified are accepted as well.
    """
    qualified_name = tag(name)

    if (out := element.get(qualified_name)) is None:
        out = element.get(name)

    return out

# ################################################################################################################################

def require_attribute(element:'any_', name:'str') -> 'str':
    """ Returns an attribute that the schema requires.
    """
    if (out := get_attribute(element, name)) is None:
        element_name = local_name(element)
        raise CPAException(element_name, f'Attribute `{name}` is missing')

    return out

# ################################################################################################################################

def optional_attribute(element:'any_', name:'str') -> 'str':
    """ Returns an optional attribute, or an empty string when it is absent.
    """
    if (out := get_attribute(element, name)) is None:
        out = ''

    return out

# ################################################################################################################################

def children(element:'any_', name:'str') -> 'anylist':
    """ Returns the child elements of the CPP/A namespace with the given name.
    """
    qualified_name = tag(name)

    out = element.findall(qualified_name)
    return out

# ################################################################################################################################

def optional_child(element:'any_', name:'str') -> 'any_':
    """ Returns the first child element with the given name, or None.
    """
    qualified_name = tag(name)

    out = element.find(qualified_name)
    return out

# ################################################################################################################################

def require_child(element:'any_', name:'str') -> 'any_':
    """ Returns the first child element with the given name, which the schema requires.
    """
    if (out := optional_child(element, name)) is None:
        element_name = local_name(element)
        raise CPAException(element_name, f'Element `{name}` is missing')

    return out

# ################################################################################################################################

def require_text(element:'any_') -> 'str':
    """ Returns the text of an element whose content the schema declares non-empty.
    """
    out = element.text

    if out is None:
        out = ''

    out = out.strip()

    if not out:
        element_name = local_name(element)
        raise CPAException(element_name, 'Element is empty')

    return out

# ################################################################################################################################

def optional_text(element:'any_', name:'str') -> 'str':
    """ Returns the text of an optional child element, or an empty string when the child is absent.
    """
    if (child := optional_child(element, name)) is None:
        out = ''
    else:
        out = require_text(child)

    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_duration(element:'any_') -> 'Duration':
    """ Returns the xsd:duration an element holds.
    """
    text = require_text(element)

    if not (match := _duration_pattern.match(text)):
        element_name = local_name(element)
        raise CPAException(element_name, f'Not a duration -> `{text}`')

    # The pattern lets through a designator with no component after it, which xsd:duration does not.
    is_empty = text == 'P'
    has_empty_time = text.endswith('T')

    for is_invalid in (is_empty, has_empty_time):
        if is_invalid:
            element_name = local_name(element)
            raise CPAException(element_name, f'Duration has a designator without a component -> `{text}`')

    groups = match.groupdict()

    # Each absent component counts as zero.
    components:'strfloatdict' = {}

    for name, value in groups.items():
        if value is None:
            components[name] = 0.0
        else:
            components[name] = float(value)

    years_as_days = components['years'] * _days_per_year
    months_as_days = components['months'] * _days_per_month
    days = components['days'] + years_as_days + months_as_days

    value = timedelta(days=days, hours=components['hours'], minutes=components['minutes'], seconds=components['seconds'])

    out = Duration()
    out.text = text
    out.value = value

    return out

# ################################################################################################################################
# ################################################################################################################################
