# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml.etree import SubElement

# Zato
from zato.common.b2b.ebms2.common import Description_Language, EbMS2Exception, ErrorCode, NS, Version
from zato.common.util.xml_.core import from_timestamp, qname, XMLException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, strlist, strnone
    any_ = any_
    datetime = datetime
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The namespace prefix every ebMS element is written with.
EB_Prefix = 'eb'

# The prefix map of the outermost ebMS element of each header block and body element.
EB_Nsmap = {EB_Prefix: NS.EB}

# The attributes of the SOAP 1.1 envelope namespace that header blocks carry.
SOAP_Must_Understand = qname(NS.SOAP, 'mustUnderstand')
SOAP_Actor = qname(NS.SOAP, 'actor')

# The value of SOAP:mustUnderstand on every ebMS header block.
Must_Understand_Value = '1'

XML_Lang = qname(NS.XML, 'lang')

# The lexical forms of xsd:boolean.
_boolean_values = {
    'true':  True,
    '1':     True,
    'false': False,
    '0':     False,
}

# ################################################################################################################################
# ################################################################################################################################

def eb_tag(local_name:'str') -> 'str':
    """ Returns the qualified name of an element of the ebMS 2.0 namespace.
    """
    out = qname(NS.EB, local_name)
    return out

# ################################################################################################################################

def location(*names:'str') -> 'str':
    """ Returns the location of an element in an error, as the path of its ebMS names.
    """
    steps:'strlist' = []

    for name in names:
        step = f'{EB_Prefix}:{name}'
        steps.append(step)

    out = '/'.join(steps)
    return out

# ################################################################################################################################
# ################################################################################################################################

def add_eb(parent:'any_', name:'str', text:'str'='', *, is_outermost:'bool'=False) -> 'any_':
    """ Appends a child element of the ebMS 2.0 namespace, with the given text if there is any. The outermost
    element of a header block or of a body element declares the namespace prefix for the elements below it.
    """
    child_tag = eb_tag(name)

    if is_outermost:
        out = SubElement(parent, child_tag, nsmap=EB_Nsmap)
    else:
        out = SubElement(parent, child_tag)

    if text:
        out.text = text

    return out

# ################################################################################################################################

def set_eb_attribute(element:'any_', name:'str', value:'str') -> 'None':
    """ Sets an attribute of the ebMS 2.0 namespace, which the schema qualifies, unless the value is empty.
    """
    if value:
        attribute_name = eb_tag(name)
        element.set(attribute_name, value)

# ################################################################################################################################

def add_header_block(parent:'any_', name:'str') -> 'any_':
    """ Appends an ebMS 2.0 header block with the attributes every header block requires.
    """
    out = add_eb(parent, name, is_outermost=True)
    out.set(SOAP_Must_Understand, Must_Understand_Value)
    set_eb_attribute(out, 'version', Version)

    return out

# ################################################################################################################################

def add_body_element(parent:'any_', name:'str') -> 'any_':
    """ Appends an ebMS 2.0 body element with the attributes every body element requires.
    """
    out = add_eb(parent, name, is_outermost=True)
    set_eb_attribute(out, 'version', Version)

    return out

# ################################################################################################################################

def add_description(parent:'any_', text:'str', language:'str'=Description_Language) -> 'None':
    element = add_eb(parent, 'Description', text)
    element.set(XML_Lang, language)

# ################################################################################################################################
# ################################################################################################################################

def get_eb_attribute(element:'any_', name:'str') -> 'strnone':
    """ Returns an attribute that the schema qualifies, or None. Senders that write the attribute
    unqualified are accepted as well.
    """
    qualified_name = eb_tag(name)

    if (out := element.get(qualified_name)) is None:
        out = element.get(name)

    return out

# ################################################################################################################################

def require_eb_attribute(element:'any_', name:'str', where:'str') -> 'str':
    if (out := get_eb_attribute(element, name)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Attribute `{name}` is missing', where)

    return out

# ################################################################################################################################

def check_extension(element:'any_', where:'str', *, is_header:'bool') -> 'None':
    """ Rejects a header block or a body element without the attributes the schema requires of it.
    """
    version = require_eb_attribute(element, 'version', where)

    if version != Version:
        raise EbMS2Exception(ErrorCode.Not_Supported, f'Version `{version}` is not supported', where)

    if is_header:
        must_understand = element.get(SOAP_Must_Understand)

        if must_understand is None:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'Attribute `SOAP:mustUnderstand` is missing', where)

        if must_understand != Must_Understand_Value:
            raise EbMS2Exception(ErrorCode.Inconsistent, f'Attribute `SOAP:mustUnderstand` is `{must_understand}`', where)

# ################################################################################################################################

def find_eb(element:'any_', name:'str') -> 'any_':
    """ Returns the first child element of the ebMS 2.0 namespace with the given name, or None.
    """
    child_tag = eb_tag(name)

    out = element.find(child_tag)
    return out

# ################################################################################################################################

def find_all_eb(element:'any_', name:'str') -> 'any_':
    child_tag = eb_tag(name)

    out = element.findall(child_tag)
    return out

# ################################################################################################################################

def require_eb(element:'any_', name:'str', where:'str') -> 'any_':
    """ Returns a child element that the schema requires.
    """
    if (out := find_eb(element, name)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Element `{name}` is missing', where)

    return out

# ################################################################################################################################

def require_text(element:'any_', where:'str') -> 'str':
    """ Returns the text of an element whose content the schema declares non-empty.
    """
    out = element.text

    if out is None:
        out = ''

    out = out.strip()

    if not out:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element is empty', where)

    return out

# ################################################################################################################################

def require_eb_text(element:'any_', name:'str', where:'str') -> 'str':
    """ Returns the text of a child element that the schema requires.
    """
    child = require_eb(element, name, where)

    out = require_text(child, where)
    return out

# ################################################################################################################################

def optional_eb_text(element:'any_', name:'str', where:'str') -> 'str':
    """ Returns the text of an optional child element, or an empty string when it is absent.
    """
    if (child := find_eb(element, name)) is None:
        out = ''
    else:
        out = require_text(child, where)

    return out

# ################################################################################################################################

def parse_timestamp(text:'str', where:'str') -> 'datetime':
    """ Returns the xsd:dateTime a message holds.
    """
    try:
        out = from_timestamp(text)
    except XMLException:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Not a timestamp -> `{text}`', where)

    return out

# ################################################################################################################################

def parse_boolean(text:'str', where:'str') -> 'bool':
    """ Returns the xsd:boolean an attribute holds.
    """
    if (out := _boolean_values.get(text)) is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Not a boolean -> `{text}`', where)

    return out

# ################################################################################################################################
# ################################################################################################################################
