<?xml version="1.0" encoding="UTF-8"?>
<!--Metadata: 
Owner: ebxml-bp (OASIS ebXML Business Process TC)
Product: ebxmlbp (aka ebBP)
Product Version: 2.0.4
Artifact Type: Schema
Stage: os (OASIS Standard)
Descriptive Name: SignalSchema
Revision: None
Language: en (English)
Form: xsd (schema)
Date: 20061221 (21 December 2006)
-->
<!--This schema has the element definitions for the signal messages used in the run time execution of ebBP.-->
<!-- OASIS takes no position regarding the validity or scope of any intellectual property or other rights that might be claimed to pertain to the implementation or use of the technology described in this document or the extent to which any license under such rights might or might not be available; neither does it represent that it has made any effort to identify any such rights. Information on OASIS's procedures with respect to rights in OASIS specifications can be found at the OASIS website. Copies of claims of rights made available for publication and any assurances of licenses to be made available, or the result of an attempt made to obtain a general license or permission for the use of such proprietary rights by implementors or users of this specification, can be obtained from the OASIS Executive Director. 
OASIS invites any interested party to bring to its attention any copyrights, patents or patent applications, or other proprietary rights which may cover technology that may be required to implement this specification. Please address the information to the OASIS Executive Director. 
Copyright © OASIS Open 2005, 2006. All Rights Reserved.
This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this paragraph are included on all such copies and derivative works. However, this document itself may not be modified in any way, such as by removing the copyright notice or references to OASIS, except as needed for the purpose of developing OASIS specifications, in which case the procedures for copyrights defined in the OASIS Intellectual Property Rights document must be followed, or as required to translate it into languages other than English. 
The limited permissions granted above are perpetual and will not be revoked by OASIS or its successors or assigns. 
This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.-->
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:bpssignal="http://docs.oasis-open.org/ebxml-bp/ebbp-signals-2.0" targetNamespace="http://docs.oasis-open.org/ebxml-bp/ebbp-signals-2.0" elementFormDefault="qualified" attributeFormDefault="unqualified" version="2.0">
	<xsd:import namespace="http://www.w3.org/1999/xlink" schemaLocation="http://www.oasis-open.org/committees/ebxml-msg/schema/xlink.xsd"/>
	<xsd:annotation>
		<xsd:documentation> The version of digital signature specification supported is identified
                                    using the namespace and schemalocation denoted below </xsd:documentation>
	</xsd:annotation>
	<xsd:import namespace="http://www.w3.org/2000/09/xmldsig#" schemaLocation="http://www.w3.org/TR/xmldsig-core/xmldsig-core-schema.xsd"/>
	<xsd:simpleType name="non-empty-string">
		<xsd:restriction base="xsd:string">
			<xsd:minLength value="1"/>
		</xsd:restriction>
	</xsd:simpleType>
	<xsd:complexType name="PartyInfoType">
		<xsd:annotation>
			<xsd:documentation> This type defines the structure for PartyInfo Definition. The "type"
				attribute identifies the type of PartyId which is the content for PartyInfo type
				being defined here. </xsd:documentation>
		</xsd:annotation>
		<xsd:simpleContent>
			<xsd:extension base="bpssignal:non-empty-string">
				<xsd:attribute name="type" type="bpssignal:non-empty-string"/>
			</xsd:extension>
		</xsd:simpleContent>
	</xsd:complexType>
	<xsd:complexType name="RoleType">
		<xsd:annotation>
			<xsd:documentation> This type defines the structure for Role Definition.
			</xsd:documentation>
		</xsd:annotation>
		<xsd:attribute name="name" type="bpssignal:non-empty-string" use="required"/>
		<xsd:attributeGroup ref="bpssignal:xlink.grp"/>
	</xsd:complexType>
	<xsd:attributeGroup name="xlink.grp">
		<xsd:annotation>
			<xsd:documentation> The "xlink:type" attribute has a FIXED value of "simple". This
				identifies the element as being an XLINK simple link. The "xlink:href" attribute
				SHALL have a value that is a URI that conforms to [RFC2396]. It identifies the
				location of the element or attribute within the Process-Specification document that
				defines the role in the context of the Business Collaboration. </xsd:documentation>
		</xsd:annotation>
		<xsd:attribute ref="xlink:type" fixed="simple"/>
		<xsd:attribute ref="xlink:href" use="required"/>
	</xsd:attributeGroup>
	<xsd:complexType name="ProcessSpecificationInfoType">
		<xsd:annotation>
			<xsd:documentation> This defines the content structure for identifying the
                root ProcessSpecification for which this business signal is being sent. "instanceVersion"
                attribute refers to the user-defined version of the ProcessSpecification identified by the "name"
                attribute. The "name" attribute is set to the same value as name
                attribute for the corresponding ProcessSpecification element within the
                Business Process Specification instance (For example, the @name attribute of "name" attributeGroup in ebBP). The "xlink:type" attribute has a FIXED
                value of "simple". This identifies the element as being an XLINK simple link. The
                "xlink:href" attribute has a value that is a URI that conforms to [RFC2396].
                It identifies the location of the Business Process Specification instance document that defines the
                Business Collaboration. The "uuid" attribute captures the unique identifier given to
                the Business Process Specification instance document that is being referred. It corresponds to the
                uuid attribute of "ProcessSpecification" element in the Business Process Specification instance document.
            </xsd:documentation>
		</xsd:annotation>
		<xsd:attribute name="instanceVersion" type="xsd:string" use="optional"/>
		<xsd:attribute name="name" type="xsd:string" use="optional"/>
		<xsd:attributeGroup ref="bpssignal:xlink.grp"/>
		<xsd:attribute name="uuid" type="xsd:string" use="required"/>
	</xsd:complexType>
	<xsd:complexType name="SignalIdentificationInformation">
		<xsd:annotation>
			<xsd:documentation>This defines the content structure for identiying various parameters
				pertaining to the business signal. "OriginalMessageIdentifier" captures the value of
				the transport message identifier for original message to which this business signal
				is being sent. If business message has an identifier, that can be captured by the
				"OriginalDocumentIdentifier" attribute. "OriginalMessageDateTime" is the time when
				the original message was sent. "ThisMessageDateTime" is the time when this signal
				message is being sent. The following optional elements are there to provide access
				to information that can be used by processing logic outside the business process
				engine. One example of this could be a monitoring application which can use this
				information to provide status of a collaboration. "FromPartyInfo" describes the
				party id that is sending the signal message. "ToPartyInfo" describes the party id
				that is being sent the signal message. The roles described below are based on the
				implicit relationship between the partner sending the signal message and the partner
				who sent the original message to which this particular signal is being sent. The
				role relationship between partner sending the business message and the partner
				receiving it is captured in the process definition (ebBP). "FromRole" captures the
				role being played by the party that is sending the signal message. "ToRole" captures
				the role played by the party that is being sent the signal message.
				"ProcessSpecificationInfo" type descibes the process information (ebBP) which
				defines the runtime collaborations for which this signal is being sent
				"CollaborationIdentifier" is the unique identifer that associates the signal with a
				particular collaboration. This could come from the business message itself or in
				case of ebXML MSH, could be the messaging level header "ConversationId"
				"BusinessActivityIdentifier" identifies the business Requesting or Responding
				activity to which this signal is being sent. This would identify the
				"BusinessAction" from the process definition (ebBP) and could be implemented using
				the "name" attribute on either the RequestingBusinessActivity or the
				RespondingBusinessActivity.</xsd:documentation>
		</xsd:annotation>
		<xsd:sequence>
			<xsd:element name="OriginalMessageIdentifier" type="bpssignal:non-empty-string"/>
			<xsd:element name="OriginalDocumentIdentifier" type="bpssignal:non-empty-string" minOccurs="0"/>
			<xsd:element name="OriginalMessageDateTime" type="xsd:dateTime"/>
			<xsd:element name="ThisMessageDateTime" type="xsd:dateTime"/>
			<xsd:element name="FromPartyInfo" type="bpssignal:PartyInfoType" minOccurs="0"/>
			<xsd:element name="ToPartyInfo" type="bpssignal:PartyInfoType" minOccurs="0"/>
			<xsd:element name="FromRole" type="bpssignal:RoleType" minOccurs="0"/>
			<xsd:element name="ToRole" type="bpssignal:RoleType" minOccurs="0"/>
			<xsd:element name="ProcessSpecificationInfo" type="bpssignal:ProcessSpecificationInfoType" minOccurs="0"/>
			<xsd:element name="CollaborationIdentifier" type="bpssignal:non-empty-string" minOccurs="0"/>
			<xsd:element name="BusinessActivityIdentifier" type="bpssignal:non-empty-string" minOccurs="0"/>
		</xsd:sequence>
	</xsd:complexType>
	<xsd:element name="Exception">
		<xsd:annotation>
			<xsd:documentation> This defines the content structure for messages that need to send an
				exception signals as a business signal message to a trading partner. For description
				of first nine elements, refer to documentation on SignalIdentificationInformation.
				"ExceptionType" is used to identify various exceptions that can occur during the
				execution of a Business Collaboration. Run time processing engine using ebBP based
				collaborations generates a "ReceiptException" if request message results in a
				negative Receipt Acknowledgement. This exception could be due to various problems
				like "Syntax validation" of business message", "Unauthorized execution of process",
				"Failure of Signature validation in incoming message", "Out of sequence message"
				corresponding respectively to "Syntax", "Authorization", "Signature", "Sequence".
				Run time processing engine using ebBP based collaborations generates a
				"AcceptanceException" if request message results in a negative Acceptance
				Acknowledgement. Please refer the technical specification for various reasons why
				negative Acceptance Acknowledgement may be sent. Run time processing engine using
				ebBP based collaborations can send a "GeneralException" if processing of a request
				message results in a catastrophic state where further processing can not continue.
				"Reason" can be used to send a message to convey the reason for exception being
				generated. "ExceptionMessage" can include a descriptive message corresponding to the
				exception </xsd:documentation>
		</xsd:annotation>
		<xsd:complexType>
			<xsd:complexContent>
				<xsd:extension base="bpssignal:SignalIdentificationInformation">
					<xsd:sequence>
						<xsd:element name="ExceptionType">
							<xsd:complexType>
								<xsd:choice>
									<xsd:element name="ReceiptException">
										<xsd:simpleType>
											<xsd:restriction base="xsd:string">
												<xsd:enumeration value="Syntax"/>
												<xsd:enumeration value="Authorization"/>
												<xsd:enumeration value="Signature"/>
												<xsd:enumeration value="Sequence"/>
											</xsd:restriction>
										</xsd:simpleType>
									</xsd:element>
									<xsd:element name="AcceptanceException">
										<xsd:simpleType>
											<xsd:restriction base="xsd:string">
												<xsd:enumeration value="Business"/>
												<xsd:enumeration value="Performance"/>
											</xsd:restriction>
										</xsd:simpleType>
									</xsd:element>
									<xsd:element name="GeneralException">
										<xsd:simpleType>
											<xsd:restriction base="xsd:string"/>
										</xsd:simpleType>
									</xsd:element>
								</xsd:choice>
							</xsd:complexType>
						</xsd:element>
						<xsd:element name="Reason" type="bpssignal:non-empty-string"/>
						<xsd:element name="ExceptionMessage" type="bpssignal:non-empty-string" minOccurs="0"/>
						<xsd:any namespace="##other" minOccurs="0"/>
					</xsd:sequence>
				</xsd:extension>
			</xsd:complexContent>
		</xsd:complexType>
	</xsd:element>
	<xsd:element name="ReceiptAcknowledgement">
		<xsd:annotation>
			<xsd:documentation> This defines the content structure for messages that need to send an
				ReceiptAcknowledgement signals as a business signal message to a trading partner.
				Please refer to the ebBP technical specification for detailed description of
				ReceiptAcknowledgement. This element is used for conforming to
				NonRepudiationofReceipt(NRR) by including the "NonRepudiationInformation" child
				element as described below. For NonRepudiationofOrigin the originating business
				message will have nonrepudiation information. Signals are outside of this
				requirement. For description of first nine elements, refer to documentation on
				SignalIdentificationInformation. ReceiptAcknowledgement signals can include
				non-repudiation information if requested in the process definition.
				"NonRepudiationInformation" captures this data for each of the message parts that
				comprise the request message that was sent. Each "MessagePartNRInformation"
				describes non-repudiation information for a message part identified by
				"MessagePartIdentifier" using "Reference" described by XML Digital Signature
				Specification. Each part of the request message will have a corresponding
				"MessagePartNRInformation". If necessary, digital signature can be computed for this
				signal message and included using "Signature" element from XML Digital Signature
				namespace. </xsd:documentation>
		</xsd:annotation>
		<xsd:complexType>
			<xsd:complexContent>
				<xsd:extension base="bpssignal:SignalIdentificationInformation">
					<xsd:sequence>
						<xsd:element ref="bpssignal:NonRepudiationInformation" minOccurs="0"/>
						<xsd:element ref="ds:Signature" minOccurs="0"/>
					</xsd:sequence>
				</xsd:extension>
			</xsd:complexContent>
		</xsd:complexType>
	</xsd:element>
	<xsd:element name="NonRepudiationInformation">
		<xsd:complexType>
			<xsd:sequence>
				<xsd:element ref="bpssignal:MessagePartNRInformation" maxOccurs="unbounded"/>
			</xsd:sequence>
		</xsd:complexType>
	</xsd:element>
	<xsd:element name="MessagePartNRInformation">
		<xsd:complexType>
			<xsd:choice>
				<xsd:element name="MessagePartIdentifier" type="bpssignal:non-empty-string"/>
				<xsd:element ref="ds:Reference"/>
			</xsd:choice>
		</xsd:complexType>
	</xsd:element>
	<xsd:element name="AcceptanceAcknowledgement">
		<xsd:annotation>
			<xsd:documentation> This defines the content structure for messages that need to send an
				AcceptanceAcknowledgement signals as a business message to a trading partner. Please
				refer to the ebBP technical specification for detailed description of
				AcceptanceAcknowledgement. For description of first nine elements, refer to
				documentation on SignalIdentificationInformation. If necessary, digital signature
				can be computed for this signal message and included using "Signature" element from
				XML Digital Signature namespace. </xsd:documentation>
		</xsd:annotation>
		<xsd:complexType>
			<xsd:complexContent>
				<xsd:extension base="bpssignal:SignalIdentificationInformation">
					<xsd:sequence>
						<xsd:element ref="ds:Signature" minOccurs="0"/>
					</xsd:sequence>
				</xsd:extension>
			</xsd:complexContent>
		</xsd:complexType>
	</xsd:element>
</xsd:schema>
