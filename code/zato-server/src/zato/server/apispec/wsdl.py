# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import load
from string import whitespace

# Bunch
from bunch import bunchify

# regex
import regex

# ################################################################################################################################

wsdl_template = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<wsdl:definitions
xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:api="{target_ns}"
xmlns="{target_ns}"
name="api"
targetNamespace="{target_ns}"
>

  <wsdl:types>
    <xsd:schema targetNamespace="{target_ns}" elementFormDefault="qualified">

<!-- ####################################################################### -->

      <xsd:element name="zato_env">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="cid" type="xsd:string"/>
            <xsd:element name="result" type="xsd:string"/>
            <xsd:element name="details" type="xsd:string" minOccurs="0"/>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>

<!-- ####################################################################### -->

      <!-- zato_msg_list -->
      {zato_msg_list}

<!-- ####################################################################### -->

    </xsd:schema>
  </wsdl:types>

<!-- ####################################################################### -->

     <!-- wsdl_msg_part_list -->
     {wsdl_msg_part_list}

<!-- ####################################################################### -->

  <wsdl:portType name="api-port-type">

<!-- ####################################################################### -->

     <!-- wsdl_op_io_list -->
     {wsdl_op_io_list}

<!-- ####################################################################### -->


  </wsdl:portType>

  <wsdl:binding name="api-binding" type="api:api-port-type">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>

<!-- ####################################################################### -->

     <!-- wsdl_op_body_list -->
     {wsdl_op_body_list}

<!-- ####################################################################### -->

  </wsdl:binding>

  <wsdl:service name="api-services">
    <wsdl:port binding="api:api-binding" name="api-port">
      <soap:address location="http://localhost:17010/zato/soap"/>
    </wsdl:port>
  </wsdl:service>

</wsdl:definitions>
"""

zato_msg_template = """
<xsd:element name="{elem_name}">
  <xsd:complexType>
    <xsd:sequence>
{sequence}
    </xsd:sequence>
  </xsd:complexType>
</xsd:element>
""".strip()

xs_elem_template = '<xsd:element name="{name}" type="{type}" minOccurs="{min_occurs}" maxOccurs="{max_occurs}"/>'

wsdl_msg_part_template = """
  <wsdl:message name="{service_name}_request_message">
    <wsdl:part element="api:{service_name}_request" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="{service_name}_response_message">
    <wsdl:part element="api:{service_name}_response" name="parameters"/>
  </wsdl:message>
""".strip()

wsdl_op_io_template = """
<wsdl:operation name="{service_name}">
  <wsdl:input message="api:{service_name}_request_message"/>
  <wsdl:output message="api:{service_name}_response_message"/>
</wsdl:operation>
""".strip()

wsdl_op_body_template = """
<wsdl:operation name="{service_name}">
  <soap:operation soapAction="{service_name}"/>
  <wsdl:input>
    <soap:body use="literal"/>
  </wsdl:input>
  <wsdl:output>
    <soap:body use="literal"/>
  </wsdl:output>
</wsdl:operation>
""".strip()

# ################################################################################################################################

class WSDLGenerator(object):
    """ Generates WSDL 1.1 output in document/literal style for input services
    based on their SimpleIO definitions extracted from API spec.
    """
    def __init__(self, services, target_ns):
        self.services = services
        self.target_ns = target_ns

# ################################################################################################################################

    def slugify(self, value):
        return regex.sub(whitespace, '_', value) # Replacing whitespace will suffice

# ################################################################################################################################

    def append_xs_elem(self, destination, elem, min_occ, max_occ):
        destination.append(xs_elem_template.format(**{
            'name': elem.name,
            'type': elem.subtype,
            'min_occurs': min_occ,
            'max_occurs': max_occ,
        }))

# ################################################################################################################################

    def get_zato_msg(self, service_name, msg_name, sio_req, sio_opt):
        return zato_msg_template.format(**{
            'elem_name': msg_name,
            'sequence': '\n'.join(sio_req) + '\n'.join(sio_opt).lstrip()
        })

# ################################################################################################################################

    def get_wsdl_msg_part(self, service_name):
        return wsdl_msg_part_template.format(**{
            'service_name': service_name,
        })

# ################################################################################################################################

    def get_wsdl_op_io(self, service_name):
        return wsdl_op_io_template.format(**{
            'service_name': service_name,
        })

# ################################################################################################################################

    def get_wsdl_op_body(self, service_name):
        return wsdl_op_body_template.format(**{
            'service_name': service_name,
        })

# ################################################################################################################################

    def get_wsdl(self, target_ns, zato_msg_list, wsdl_msg_part_list, wsdl_op_io_list, wsdl_op_body_list):
        return wsdl_template.format(**{
            'target_ns': target_ns,
            'zato_msg_list': '\n'.join(zato_msg_list),
            'wsdl_msg_part_list': '\n'.join(wsdl_msg_part_list),
            'wsdl_op_io_list': '\n'.join(wsdl_op_io_list),
            'wsdl_op_body_list': '\n'.join(wsdl_op_body_list),
        })

# ################################################################################################################################

    def generate(self):

        zato_msg_list = []
        wsdl_msg_part_list = []
        wsdl_op_io_list = []
        wsdl_op_body_list = []

        for service in self.services:
            service_name = self.slugify(service.name)

            if 'soap_12' not in service.simple_io:
                continue

            sio = service.simple_io.soap_12

            sio_input_req = []
            sio_input_opt = []

            sio_output_req = []
            sio_output_opt = []

            # First, collect all I/O elements

            for elem in sio.input_required:
                self.append_xs_elem(sio_input_req, elem, 1, 1)

            for elem in sio.input_optional:
                self.append_xs_elem(sio_input_opt, elem, 0, 1)

            for elem in sio.output_required:
                self.append_xs_elem(sio_output_req, elem, 1, 1)

            for elem in sio.output_optional:
                self.append_xs_elem(sio_output_opt, elem, 0, 1)

            # Current service's request and response names
            req_msg_name = '{}_{}'.format(service_name, 'request')
            resp_msg_name = '{}_{}'.format(service_name, 'response')

            # Current service's actual XSD request/response elements
            zato_msg_list.append(self.get_zato_msg(service_name, req_msg_name, sio_input_req, sio_input_opt))
            zato_msg_list.append(self.get_zato_msg(service_name, resp_msg_name, sio_output_req, sio_output_opt))

            # Request/response for WSDL itself
            wsdl_msg_part_list.append(self.get_wsdl_msg_part(service_name))

            # Add this list to the list of operations and their bindings (which are 1:1)
            wsdl_op_io_list.append(self.get_wsdl_op_io(service_name))
            wsdl_op_body_list.append(self.get_wsdl_op_body(service_name))

        # We are ready now to generate the final WSDL
        return self.get_wsdl(self.target_ns, zato_msg_list, wsdl_msg_part_list, wsdl_op_io_list, wsdl_op_body_list)

# ################################################################################################################################

if __name__ == '__main__':
    data = load(open('apispec.json', 'rb'))

    services = bunchify(data['services'])
    target_ns = 'urn:zato-apispec'

    g = WSDLGenerator(services, target_ns)
    wsdl = g.generate()

# ################################################################################################################################

