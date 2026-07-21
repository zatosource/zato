# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The dynamic, dot-accessed XML message builder and parser.

Namespaces are resolved per element, using these rules:

1. Setting `message.namespace = 'urn:example'` (equivalently `message['namespace'] = ...`)
   qualifies that node and, through inheritance, every descendant that does not override it.

2. Any node can override its namespace with `message.Child['namespace'] = 'urn:other'` -
   the override re-roots that node and its whole subtree in the new namespace, while
   siblings keep inheriting from their nearest ancestor.

3. A node with no namespace of its own takes the nearest ancestor's, resolved at
   serialization time.

4. `serialize(message, tag, default_namespace='urn:example')` supplies a root namespace
   only when the message itself set none.

5. A message with no namespace anywhere serializes unqualified elements.

The bracket keys `namespace` and `text` are reserved - every other bracket key
is an XML attribute of the node.
"""

# stdlib
from base64 import b64encode
from datetime import date, datetime
from decimal import Decimal

# lxml
from lxml import etree

# Zato
from zato.common.util.message import Message
from zato.common.util.xml_.constants import NS
from zato.common.util.xml_.core import XMLException
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strnone
    any_ = any_
    anydict = anydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The bracket keys that are not XML attributes - one sets a per-node namespace override,
# the other sets the text of a node that also carries attributes or children.
_reserved_namespace_key = 'namespace'
_reserved_text_key = 'text'

_xsi_nil = f'{{{NS.XSI}}}nil'
_xop_include = f'{{{NS.XOP}}}Include'

# Maps content ids of MTOM parts to their bytes during parsing.
bytes_by_content_id = dict[str, bytes]

# ################################################################################################################################
# ################################################################################################################################

def _convert_str(value:'str') -> 'str':
    out = value
    return out

# ################################################################################################################################

def _convert_bool(value:'bool') -> 'str':
    out = 'true' if value else 'false'
    return out

# ################################################################################################################################

def _convert_int(value:'int') -> 'str':
    out = str(value)
    return out

# ################################################################################################################################

def _convert_float(value:'float') -> 'str':
    out = repr(value)
    return out

# ################################################################################################################################

def _convert_decimal(value:'Decimal') -> 'str':
    out = str(value)
    return out

# ################################################################################################################################

def _convert_datetime(value:'datetime') -> 'str':
    out = value.isoformat()
    return out

# ################################################################################################################################

def _convert_date(value:'date') -> 'str':
    out = value.isoformat()
    return out

# ################################################################################################################################

def _convert_bytes(value:'bytes') -> 'str':
    out = b64encode(value).decode('ascii')
    return out

# ################################################################################################################################

# The XML lexical form of each Python value type - bool must precede int conceptually
# but a lookup by exact type never confuses the two.
_lexical_converters = {
    str:      _convert_str,
    bool:     _convert_bool,
    int:      _convert_int,
    float:    _convert_float,
    Decimal:  _convert_decimal,
    datetime: _convert_datetime,
    date:     _convert_date,
    bytes:    _convert_bytes,
}

# ################################################################################################################################

def to_lexical(value:'any_') -> 'str':
    """ Returns the XML lexical form of a Python value - datetimes become xs:dateTime,
    booleans become true/false, bytes become base64, and so on.
    """
    if converter := _lexical_converters.get(type(value)):
        out = converter(value)
    else:
        raise XMLException(f'Unsupported value type `{type(value).__name__}` -> `{value!r}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

class XMLMessage(Message):
    """ A dynamic, dot-accessed XML message - the only data structure users ever touch.

    On top of the base Message tree it adds:

    1. Assignment order is wire order
    2. Brackets set and read XML attributes: slot['name'] = 'creationTime' - with `namespace` reserved
       for a per-node namespace override and `text` reserved for the text of a node that also has attributes
    3. The Python type of a value dictates its XML lexical form
    4. Reading gives the same shape back, with repeated elements as lists and xsi:nil as None
    """

    def __init__(self) -> 'None':
        super().__init__()
        object.__setattr__(self, '_attributes', {})
        object.__setattr__(self, '_namespace', None)
        object.__setattr__(self, '_text', None)

# ################################################################################################################################

    def __setattr__(self, name:'str', value:'any_') -> 'None':

        # The message-wide default namespace is set through plain dot access on any node.
        if name == _reserved_namespace_key:
            object.__setattr__(self, '_namespace', value)
            return

        # Everything else is a child element, handled by the base tree.
        super().__setattr__(name, value)

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':

        if name == _reserved_namespace_key:
            out = self._namespace
            return out

        # Everything else is a child element - the base tree handles the underscore
        # guard and the auto-vivification of missing children.
        out = super().__getattr__(name)
        return out

# ################################################################################################################################

    def __setitem__(self, key:'str', value:'any_') -> 'None':

        if key == _reserved_namespace_key:
            object.__setattr__(self, '_namespace', value)

        elif key == _reserved_text_key:
            object.__setattr__(self, '_text', value)

        # .. any other bracket key is an XML attribute.
        else:
            self._attributes[key] = value

# ################################################################################################################################

    def __getitem__(self, key:'str') -> 'any_':

        if key == _reserved_namespace_key:
            out = self._namespace

        elif key == _reserved_text_key:
            out = self._text

        # .. any other bracket key is an XML attribute.
        else:
            out = self._attributes[key]

        return out

# ################################################################################################################################

    def __contains__(self, key:'str') -> 'bool':
        out = key in self._attributes
        return out

# ################################################################################################################################

    def __bool__(self) -> 'bool':
        out = has_content(self)
        return out

# ################################################################################################################################

    def __len__(self) -> 'int':

        # Only children that actually carry content count - the check is the XML-aware one,
        # so children that hold only text or attributes count as well.
        out = 0

        for value in self._children.values():
            if _value_has_content(value):
                out += 1

        return out

# ################################################################################################################################

    def __str__(self) -> 'str':
        if self._text is None:
            out = ''
        else:
            out = str(self._text)

        return out

# ################################################################################################################################

    def __repr__(self) -> 'str':
        child_names = list(self._children)
        out = f'<{type(self).__name__} children={child_names} attributes={self._attributes} text={self._text!r}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

def has_content(message:'XMLMessage') -> 'bool':
    """ Returns True if a node carries anything worth serializing - text, attributes
    or at least one child with content. Nodes vivified by reads alone have none.
    """
    if message._text is not None:
        return True

    if message._attributes:
        return True

    for value in message._children.values():
        if _value_has_content(value):
            return True

    return False

# ################################################################################################################################

def _value_has_content(value:'any_') -> 'bool':
    """ Returns True if a child value carries content - scalars always do because
    only an assignment can have put them there, nodes are checked recursively.
    """
    if isinstance(value, XMLMessage):
        out = has_content(value)
    elif isinstance(value, list):
        out = False
        for item in value:
            if _value_has_content(item):
                out = True
                break
    else:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

def serialize(
    message:'XMLMessage',
    tag:'str',
    default_namespace:'strnone'=None,
    xop_parts:'any_'=None,
    ) -> 'any_':
    """ Serializes a message into an lxml element named by tag. The effective namespace of each node
    is its own override or the nearest ancestor's. With an xop_parts list given, bytes values become
    xop:Include references and their bytes are collected as MTOM parts instead of inline base64.
    """
    # The root namespace is the message's own or the caller-provided default.
    namespace = message._namespace
    if namespace is None:
        namespace = default_namespace

    element = _new_element(tag, namespace)
    _fill_element(element, message, namespace, xop_parts)

    return element

# ################################################################################################################################

def _new_element(tag:'str', namespace:'strnone') -> 'any_':
    """ Returns a fresh element, namespace-qualified when one is in effect.
    """
    if namespace:
        out = etree.Element(f'{{{namespace}}}{tag}')
    else:
        out = etree.Element(tag)

    return out

# ################################################################################################################################

def _fill_element(
    element:'any_',
    message:'XMLMessage',
    namespace:'strnone',
    xop_parts:'any_',
    ) -> 'None':
    """ Writes a node's attributes, text and children into an element, in assignment order.
    """
    for name, value in message._attributes.items():
        element.set(name, to_lexical(value))

    if message._text is not None:
        element.text = to_lexical(message._text)

    for name, value in message._children.items():

        # A list means repeated elements, one per item ..
        if isinstance(value, list):
            for item in value:
                _append_child(element, name, item, namespace, xop_parts)

        # .. everything else is a single element.
        else:
            _append_child(element, name, value, namespace, xop_parts)

# ################################################################################################################################

def _append_child(
    parent:'any_',
    name:'str',
    value:'any_',
    namespace:'strnone',
    xop_parts:'any_',
    ) -> 'None':
    """ Appends one child element for a value, whatever its type.
    """
    # A nested node inherits our namespace unless it overrides it - nodes
    # that never received any content are pruned rather than serialized.
    if isinstance(value, XMLMessage):
        if not has_content(value):
            return

        child_namespace = value._namespace
        if child_namespace is None:
            child_namespace = namespace

        child = _new_element(name, child_namespace)
        _fill_element(child, value, child_namespace, xop_parts)
        parent.append(child)
        return

    child = _new_element(name, namespace)

    # None means an explicit xsi:nil element ..
    if value is None:
        child.set(_xsi_nil, 'true')

    # .. bytes become an MTOM part when a collector is given ..
    elif isinstance(value, bytes):
        if xop_parts is None:
            child.text = to_lexical(value)
        else:
            content_id = new_content_id()

            part = Part()
            part.content_id = content_id
            part.content_type = 'application/octet-stream'
            part.data = value
            xop_parts.append(part)

            include = etree.SubElement(child, _xop_include)
            include.set('href', f'cid:{content_id}')

    # .. and every other value is inline text in its lexical form.
    else:
        child.text = to_lexical(value)

    parent.append(child)

# ################################################################################################################################
# ################################################################################################################################

def parse(
    source:'any_',
    parts:'bytes_by_content_id | None'=None,
    message_class:'type[XMLMessage]'=XMLMessage,
    ) -> 'XMLMessage':
    """ Parses XML into a message - dot access all the way down, namespaces stripped,
    repeated elements as lists, xsi:nil as None. With an MTOM parts map given,
    elements wrapping an xop:Include become the referenced bytes. The message_class
    parameter selects the node type, so parsing can produce any XMLMessage subclass.
    """
    if isinstance(source, bytes):
        element = etree.fromstring(source)
    else:
        element = source

    out = _element_to_node(element, parts, message_class)
    return out

# ################################################################################################################################

def _local_name(tag:'str') -> 'str':
    """ Strips the {namespace} prefix from an lxml tag or attribute name.
    """
    _, _, out = tag.rpartition('}')
    return out

# ################################################################################################################################

def _element_to_node(
    element:'any_',
    parts:'bytes_by_content_id | None',
    message_class:'type[XMLMessage]',
    ) -> 'XMLMessage':
    """ Builds a node from an element - attributes, text, and children in document order.
    """

    # Our response to produce
    out = message_class()

    for name, value in element.attrib.items():

        # xsi:nil is a value marker, not data, so it never surfaces as an attribute.
        if name == _xsi_nil:
            continue

        out._attributes[_local_name(name)] = value

    # Only meaningful text is kept - whitespace between child elements is formatting.
    if element.text:
        text = element.text.strip()
        if text:
            object.__setattr__(out, '_text', text)

    for child in element:

        # Comments and processing instructions have non-string tags and carry no data.
        if not isinstance(child.tag, str):
            continue

        name = _local_name(child.tag)
        value = _child_to_value(child, parts, message_class)

        # A repeated name collapses into a list, preserving document order.
        if name in out._children:
            existing = out._children[name]
            if isinstance(existing, list):
                existing.append(value)
            else:
                out._children[name] = [existing, value]
        else:
            out._children[name] = value

    return out

# ################################################################################################################################

def _child_to_value(
    element:'any_',
    parts:'bytes_by_content_id | None',
    message_class:'type[XMLMessage]',
    ) -> 'any_':
    """ Turns one child element into its Python value - bytes for MTOM references,
    None for xsi:nil, a plain string for text-only leaves and a node for everything else.
    """
    # An element whose content is a single xop:Include resolves to the referenced MTOM part.
    if parts is not None:
        include = element.find(_xop_include)
        if include is not None:
            href = include.get('href')
            content_id = href[4:]

            out = parts[content_id]
            return out

    if element.get(_xsi_nil) == 'true':
        return None

    # Elements with children or attributes become nodes ..
    has_element_children = False
    for child in element:
        if isinstance(child.tag, str):
            has_element_children = True
            break

    if has_element_children:
        out = _element_to_node(element, parts, message_class)
        return out

    if element.attrib:
        out = _element_to_node(element, parts, message_class)
        return out

    # .. and text-only leaves become plain strings.
    if element.text is None:
        out = ''
    else:
        out = element.text

    return out

# ################################################################################################################################
# ################################################################################################################################
