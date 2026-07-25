# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as4.common import NS
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

# Fixed element ids used in signature references.
Messaging_Element_ID = '_zato-as4-messaging'
Body_Element_ID      = '_zato-as4-body'

Nsmap = {
    's12':  NS.SOAP,
    'eb':   NS.EBMS,
    'wsu':  NS.WSU,
    'ebbp': NS.EBBP,
    'ds':   NS.DS,
}

WSU_ID = f'{{{NS.WSU}}}Id'
XML_Lang = '{http://www.w3.org/XML/1998/namespace}lang'

# ################################################################################################################################
# ################################################################################################################################

# The fully qualified names of the SOAP elements built and read here.
Envelope_Name        = qname(NS.SOAP, 'Envelope')
Header_Name          = qname(NS.SOAP, 'Header')
Body_Name            = qname(NS.SOAP, 'Body')
Must_Understand_Name = qname(NS.SOAP, 'mustUnderstand')

# The fully qualified names of the ebMS elements built and read here.
Messaging_Name                 = qname(NS.EBMS, 'Messaging')
User_Message_Name              = qname(NS.EBMS, 'UserMessage')
Signal_Message_Name            = qname(NS.EBMS, 'SignalMessage')
Message_Information_Name       = qname(NS.EBMS, 'MessageInfo')
Timestamp_Name                 = qname(NS.EBMS, 'Timestamp')
Message_Id_Name                = qname(NS.EBMS, 'MessageId')
Ref_To_Message_Id_Name         = qname(NS.EBMS, 'RefToMessageId')
Property_Name                  = qname(NS.EBMS, 'Property')
Party_Information_Name         = qname(NS.EBMS, 'PartyInfo')
From_Name                      = qname(NS.EBMS, 'From')
To_Name                        = qname(NS.EBMS, 'To')
Party_Id_Name                  = qname(NS.EBMS, 'PartyId')
Role_Name                      = qname(NS.EBMS, 'Role')
Collaboration_Information_Name = qname(NS.EBMS, 'CollaborationInfo')
Agreement_Ref_Name             = qname(NS.EBMS, 'AgreementRef')
Service_Name                   = qname(NS.EBMS, 'Service')
Action_Name                    = qname(NS.EBMS, 'Action')
Conversation_Id_Name           = qname(NS.EBMS, 'ConversationId')
Message_Properties_Name        = qname(NS.EBMS, 'MessageProperties')
Payload_Information_Name       = qname(NS.EBMS, 'PayloadInfo')
Part_Information_Name          = qname(NS.EBMS, 'PartInfo')
Part_Properties_Name           = qname(NS.EBMS, 'PartProperties')
Receipt_Name                   = qname(NS.EBMS, 'Receipt')
Error_Name                     = qname(NS.EBMS, 'Error')
Description_Name               = qname(NS.EBMS, 'Description')
Error_Detail_Name              = qname(NS.EBMS, 'ErrorDetail')
Pull_Request_Name              = qname(NS.EBMS, 'PullRequest')

# The fully qualified names of the non-repudiation and signature elements.
Non_Repudiation_Name      = qname(NS.EBBP, 'NonRepudiationInformation')
Part_NR_Information_Name  = qname(NS.EBBP, 'MessagePartNRInformation')
Reference_Name            = qname(NS.DS, 'Reference')

# ################################################################################################################################
# ################################################################################################################################
