# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# XML display views - turns an XML document into the generic name/value/children nodes
# the dashboard's grid renderer consumes and into its pretty-printed text form.

from __future__ import annotations

# lxml
from lxml import etree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    any_ = any_
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Reject external entities, network access and DTDs so parsing untrusted XML cannot trigger XXE or entity expansion.
_xml_parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)

# ################################################################################################################################
# ################################################################################################################################

def _parse(data:'str') -> 'any_':
    """ Parses XML into its root element - anything that does not parse becomes None.
    """
    data_bytes = data.encode('utf-8')

    try:
        out = etree.fromstring(data_bytes, _xml_parser)
    except Exception:
        return None

    return out

# ################################################################################################################################

def _element_name(element:'any_') -> 'str':
    """ The display name of an element - its prefix and local name, the way the document reads.
    """
    qname = etree.QName(element)

    if element.prefix:
        out = f'{element.prefix}:{qname.localname}'
    else:
        out = qname.localname

    return out

# ################################################################################################################################

def _attribute_name(name:'str') -> 'str':
    """ The display name of an attribute - a namespaced one keeps its local name only.
    """
    if name.startswith('{'):
        qname = etree.QName(name)
        out = qname.localname
    else:
        out = name

    return out

# ################################################################################################################################

def _element_to_grid_node(element:'any_') -> 'stranydict':
    """ Turns one element into a grid node - attributes become marked leaves,
    child elements nest, text becomes the value or a leaf of its own.
    """
    name = _element_name(element)
    children:'anylist' = []

    # Attributes come first, the way they read in the document ..
    for attribute_name, attribute_value in element.attrib.items():

        display_name = _attribute_name(attribute_name)
        attribute_node = {'name': display_name, 'value': attribute_value, 'kind': 'attribute', 'children': []}

        children.append(attribute_node)

    # .. then the child elements - comments and processing instructions,
    # whose tag is not a string, have nothing to show in a grid ..
    for child in element:
        if isinstance(child.tag, str):
            child_node = _element_to_grid_node(child)
            children.append(child_node)

    # .. and the element's own text last - None means no text at all
    # and whitespace-only text is layout, not content.
    text = element.text

    if text is not None:
        text = text.strip()
    else:
        text = ''

    value = ''

    if text:

        # An element that also has attributes or children keeps its text
        # as a leaf of its own, a plain element keeps it as the value
        if children:
            text_node = {'name': 'text()', 'value': text, 'kind': 'element', 'children': []}
            children.append(text_node)
        else:
            value = text

    out = {'name': name, 'value': value, 'kind': 'element', 'children': children}
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_grid_nodes(data:'str') -> 'anylist':
    """ Turns an XML document into grid view nodes - an empty list when it does not parse.
    """
    root = _parse(data)

    if root is None:
        out = []
        return out

    root_node = _element_to_grid_node(root)

    out = [root_node]
    return out

# ################################################################################################################################

def pretty_print(data:'str') -> 'str':
    """ Pretty-prints an XML document - an empty string when it does not parse.
    """
    root = _parse(data)

    if root is None:
        out = ''
        return out

    # Whitespace-only text between elements is layout, re-indenting replaces it
    etree.indent(root)

    out = etree.tostring(root, encoding='unicode', pretty_print=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
