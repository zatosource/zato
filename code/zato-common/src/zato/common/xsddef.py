# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import new
import sys
import logging
import itertools
from operator import attrgetter
from cStringIO import StringIO

# TODO: Use logger
logger = logging.getLogger("xsddef")

# All XSD attributes we may ever encounter
xsd_attrs = ("name", "abstract", "extension", "restriction", "substitution",
              "fixed", "form", "id", "maxOccurs", "minOccurs", "nillable",
              "ref", "substitutionGroup", "type", "base", "value", "use")

class Element(object):
    """ All concrete XSD elements are subclasses of this one.
    """
    _counter = itertools.count()

    def __init__(self, name=""):
        self.count = Element._counter.next()
        self._xsd_name = name

    def __str__(self):
        return "<%s [%s] %s %s>" % (self.__class__.__name__,
                    self.name, self.count, hex(id(self)))

class ElementContainer(object):
    """ A class for elements which may contain other elements, such as a sequence.
    """
    def __init__(self):
        self._elems = []
        self._attrs = {}

        for item_name in dir(self):
            elem = getattr(self, item_name)
            if item_name in xsd_attrs:
                self._attrs[item_name] = elem
            elif isinstance(elem, Element):
                elem.name = item_name
                self._elems.append(elem)
            else:
                try:
                    issubclass(elem, ElementContainer)
                except TypeError, e:
                    pass
                else:
                    if elem is not self.__class__:
                        self._elems.append(elem())

        self._elems.sort(key=attrgetter("count"))

    def _as_xsd(self):
        attrs = []
        elems = []

        for attr_name in self._attrs:
            if attr_name in self._xsd_attrs:
                attr_value = getattr(self, attr_name)
                if isinstance(attr_value, Element):
                    value = attr_value.value
                else:
                    value = attr_value
                attrs.append('%s="%s"' % (attr_name, value))

        for elem in self._elems:
            elems.append(elem.as_xsd())

        attrs = " " + " ".join(attrs) if attrs else ""
        elems = "\n" + "\n".join(elems) if elems else ""

        return attrs, elems

class schema(ElementContainer):
    """ Conveys all other XSD elements.
    """
    def as_xsd(self):
        start = '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"' \
              ' elementFormDefault="qualified"' \
              ' attributeFormDefault="unqualified"%s>'
        end = "</xsd:schema>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class SimpleElement(Element):
    """ A super-class for all simple XSD elements.
    """
    def as_xsd(self):
        return '<xsd:element name="%s" type="xsd:%s"/>' % (self.name, self.xsd_type)

'''
class element(Element):
    """ An XSD element type.
    """
    def __init__(self, type="", ref="", name="", minOccurs=None, maxOccurs=None):
        super(element, self).__init__(name)
        self.type = type
        self.ref = ref
        self.minOccurs = minOccurs
        self.maxOccurs = maxOccurs

    def as_xsd(self):
        buf = StringIO()

        if self.ref:
            buf.write('<xsd:element ref="%s"' % self.ref.name)
        else:
            buf.write('<xsd:element name="%s" ' % self.name)
            if self.type:
                if hasattr(self.type, "type"):
                    _type = "xsd:%s" % self.type.type.xsd_type
                else:
                    _type = self.type.__class__.__name__
                buf.write('type="%s"' % _type)
            else:
                raise ValueError("One of 'type' or 'ref' must be specified"
                                 " name=[%s], type=[%s], ref=[%s]" % (self.name, self.type, self.ref))
        if self.minOccurs is not None:
            buf.write(' minOccurs="%s"' % self.minOccurs)

        if self.maxOccurs is not None:
            buf.write(' maxOccurs="%s"' % self.maxOccurs)

        buf.write("/>")

        value = buf.getvalue()
        buf.close()

        return value
'''

_simple_elements = ("string", "normalizedString", "token", "base64Binary",
    "hexBinary", "integer", "positiveInteger", "negativeInteger",
    "nonNegativeInteger", "nonPositiveInteger", "long", "unsignedLong", "int",
    "unsignedInt", "short", "unsignedShort", "byte", "unsignedByte", "decimal",
    "float", "double", "boolean", "duration", "dateTime", "date", "time",
    "gYear", "gYearMonth", "gMonth", "gMonthDay", "gDay", "ID", "NMTOKEN")

for elem in _simple_elements:
    cls = new.classobj(elem, (SimpleElement,), {})
    cls.xsd_type = elem
    setattr(sys.modules[__name__], elem, cls)

del _simple_elements

class element(Element, ElementContainer):
    """ An XSD element.
    """
    _xsd_attrs = ("name", "abstract", "extension", "restriction", "substitution",
                  "fixed", "form", "id", "maxOccurs", "minOccurs", "nillable",
                  "ref", "substitutionGroup", "type")
    def __init__(self):
        super(element, self).__init__()
        ElementContainer.__init__(self)

    def as_xsd(self):
        '''start_buf = StringIO()
        start_buf.write("<xsd:element")
        xsd_attrs = [attr for attr in dir(self) if attr.startswith("_xsd")]

        for attr in xsd_attrs:
            value = getattr(self, attr)
            if value:
                attr = attr.replace("_xsd", "", 1)
                start_buf.write(' %s="%s"' % (attr, value))

        start_buf.write(">")
        start = start_buf.getvalue()
        start_buf.close()'''

        attrs, elems =  self._as_xsd()

        start = "<xsd:element%s>"
        end = "\n</xsd:element>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class complexType(Element, ElementContainer):
    """ XSD complexType, may contain other elements.
    """
    _xsd_attrs = ("name", )

    def __init__(self):
        super(Element, self).__init__()
        super(complexType, self).__init__()

    def as_xsd(self):
        start = "<xsd:complexType%s>"
        end = "\n</xsd:complexType>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class simpleType(Element, ElementContainer):
    """ XSD simpleType, may contain other elements.
    """
    _xsd_attrs = ("name", )

    def __init__(self):
        super(Element, self).__init__()
        super(simpleType, self).__init__()

    def as_xsd(self):
        start = "<xsd:simpleType%s>"
        end = "\n</xsd:simpleType>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class restriction(Element, ElementContainer):
    """ XSD restriction, may contain other elements.
    """
    _xsd_attrs = ("base", )

    def __init__(self):
        super(Element, self).__init__()
        super(restriction, self).__init__()

    def as_xsd(self):
        start = "<xsd:restriction%s>"
        end = "\n</xsd:restriction>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class minInclusive(Element, ElementContainer):
    """ XSD minInclusive, may not contain other elements.
    """
    _xsd_attrs = ("value", )

    def __init__(self):
        super(Element, self).__init__()
        super(minInclusive, self).__init__()

    def as_xsd(self):
        start = "<xsd:minInclusive%s />"
        end = ""

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class maxExclusive(Element, ElementContainer):
    """ XSD maxExclusive, may not contain other elements.
    """
    _xsd_attrs = ("value", )

    def __init__(self):
        super(Element, self).__init__()
        super(maxExclusive, self).__init__()

    def as_xsd(self):
        start = "<xsd:maxExclusive%s />"
        end = ""

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class complexContent(Element, ElementContainer):
    """ XSD complexType, may contain other elements.
    """
    def __init__(self):
        super(Element, self).__init__()
        super(complexContent, self).__init__()

    def as_xsd(self):
        start = '<xsd:complexContent>'
        end = "\n</xsd:complexContent>"
        return self._as_xsd(start, end)

class sequence(Element, ElementContainer):
    """ XSD sequence, may contain other elements.
    """
    def __init__(self):
        self._xsd_elems = []
        self.min_occurs = 0
        self.max_occurs = "unbounded"

        super(Element, self).__init__()
        super(sequence, self).__init__()

    def as_xsd(self):
        start = "<xsd:sequence%s>"
        end = "\n</xsd:sequence>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end

class attribute(Element, ElementContainer):
    """ XSD sequence, may contain other elements.
    """
    _xsd_attrs = ("name", "type", "use")
    def __init__(self):
        self._xsd_elems = []

        super(attribute, self).__init__()
        ElementContainer.__init__(self)

    def as_xsd(self):
        start = "<xsd:attribute%s>"
        end = "\n</xsd:attribute>"

        attrs, elems = self._as_xsd()

        return (start % attrs) + elems + end