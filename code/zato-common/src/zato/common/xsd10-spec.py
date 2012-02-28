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
from cStringIO import StringIO

# xsddef
from xsddef import *

# lxml
from lxml import etree

"""
<xsd:complexType name="USAddress" >
  <xsd:sequence>
    <xsd:element name="name" type="xsd:string"/>
    <xsd:element name="street" type="xsd:string"/>
    <xsd:element name="city" type="xsd:string"/>
    <xsd:element name="state" type="xsd:string"/>
    <xsd:element name="zip" type="xsd:decimal"/>
  </xsd:sequence>
  <xsd:attribute name="country" type="xsd:NMTOKEN" fixed="US"/>
</xsd:complexType>
"""

"""
<xsd:complexType name="PurchaseOrderType">
  <xsd:sequence>
    <xsd:element name="shipTo" type="USAddress"/>
    <xsd:element name="billTo" type="USAddress"/>
    <xsd:element ref="comment" minOccurs="0"/>
    <xsd:element name="items"  type="Items"/>
  </xsd:sequence>
  <xsd:attribute name="orderDate" type="xsd:date"/>
</xsd:complexType>
"""

'''
class USAddress(complexType):
    class _(sequence):
        name = string()
        street = string()
        city = string()
        state = string()
        zip = decimal()

    country = attribute(NMTOKEN(), fixed="US")

class USAddressSchema(schema):
    _ = USAddress()

comment = element(name="comment", type=string())

class PurchaseOrderTypeSchema(schema):
    class PurchaseOrderType(complexType):
        class _(sequence):
            shipTo = element(USAddress())
            billTo = element(USAddress())
            comment = element(ref=comment, minOccurs=0)
        name = attribute(date())

"""
  <xsd:complexType name="Items">
    <xsd:sequence>
      <xsd:element name="item" minOccurs="0" maxOccurs="unbounded">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="productName" type="xsd:string"/>
            <xsd:element name="quantity">
              <xsd:simpleType>
                <xsd:restriction base="xsd:positiveInteger">
                  <xsd:maxExclusive value="100"/>
                </xsd:restriction>
              </xsd:simpleType>
            </xsd:element>
            <xsd:element name="USPrice"  type="xsd:decimal"/>
            <xsd:element ref="comment"   minOccurs="0"/>
            <xsd:element name="shipDate" type="xsd:date" minOccurs="0"/>
          </xsd:sequence>
          <xsd:attribute name="partNum" type="SKU" use="required"/>
        </xsd:complexType>
      </xsd:element>
    </xsd:sequence>
  </xsd:complexType>
"""

class Items(complexType):
    class _(sequence):
        class item(complexType):
            pass

class ItemsSchema(schema):
    _ = Items()
'''

class SKU(attribute):
    name = "partNum"
    type = "SKU"
    use = "required"

class e1(schema):
    class x(complexType):
        name = "Items"
        class x(sequence):
            class x(element):
                name = "item"
                minOccurs = 0
                maxOccurs = "unbounded"
                class x(complexType):
                    class x(sequence):
                        class x(element):
                            name = "productName"
                            type = "xsd:string"
                        class x2(element):
                            name = "quantity"
                            class x(simpleType):
                                class x(restriction):
                                    base = "xsd:positiveInteger"
                                    class x(maxExclusive):
                                        value = 100
                        class x3(element):
                            name = "USPrice"
                            type = "xsd:decimal"

                        class x4(element):
                            ref = "comment"
                            minOccurs = 0

                        class x5(element):
                            name = "shipDate"
                            type = "xsd:date"
                            minOccurs = 0
        class m(SKU):
            pass

for value in sorted(globals().values()):
    #print value
    try:
        if issubclass(value, schema) and value is not schema:
            xsd = value().as_xsd()
            print "NAME", value, xsd
            print
            xsd = etree.parse(StringIO(xsd))
            try:
                xsd = etree.XMLSchema(xsd)
            except Exception, e:
                print "ERROR in %s" % value, e
    except TypeError, e:
        print "TypeError2", e