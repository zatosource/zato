# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from io import BytesIO
from xml.etree.ElementTree import iterparse, ParseError

# Zato
from zato.common.api import HL7
from zato.common.hl7.ccda.exception import CCDAError

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

# The root element of every CDA document
_Root_Element_Name = 'ClinicalDocument'

# The elements that precede a document's template IDs in its header - any other direct child of the root
# comes after the last template ID, which is where the reading stops
_Header_Preamble_Names = ('realmCode', 'typeId', 'templateId')

_Template_ID_Name = 'templateId'
_Root_Attribute   = 'root'

# The C-CDA document templates and the converter's root template for each
_Document_Template_Prefix = '2.16.840.1.113883.10.20.22.1.'

Root_Template_By_OID = {
    _Document_Template_Prefix + '2':  'CCD',
    _Document_Template_Prefix + '3':  'HistoryandPhysical',
    _Document_Template_Prefix + '4':  'ConsultationNote',
    _Document_Template_Prefix + '6':  'ProcedureNote',
    _Document_Template_Prefix + '7':  'OperativeNote',
    _Document_Template_Prefix + '8':  'DischargeSummary',
    _Document_Template_Prefix + '9':  'ProgressNote',
    _Document_Template_Prefix + '13': 'TransferSummary',
    _Document_Template_Prefix + '14': 'ReferralNote',
}

# ################################################################################################################################
# ################################################################################################################################

def _local_name(tag:'str') -> 'str':
    """ Returns an element's name without its namespace.
    """
    out = tag.rsplit('}', 1)[-1]
    return out

# ################################################################################################################################

def get_root_template(document:'bytes', cid:'str') -> 'str':
    """ Returns the name of the converter's root template for a document, read off the template IDs
    in the document's header. Only the header is read - the reading stops at the first element after it.
    Entity references are not substituted and nothing a document names is fetched.
    """
    out = _ccda.Default_Root_Template
    depth = 0

    try:

        # Walk the tags as they open and close - a start event carries the element's attributes,
        # which is all the header needs, and the end events keep the depth right ..
        for event, element in iterparse(BytesIO(document), events=('start', 'end')):

            if event == 'end':
                depth -= 1
                continue

            name = _local_name(element.tag)

            # .. the first element is the root and it must be a CDA document ..
            if depth == 0:
                if name != _Root_Element_Name:
                    raise CCDAError(cid, _ccda.Reason.Not_CDA, f'Root element is `{name}`, not `{_Root_Element_Name}`')

            # .. a direct child of the root is either part of the preamble or the end of it ..
            elif depth == 1:

                if name not in _Header_Preamble_Names:
                    break

                # .. the first template ID the converter knows decides the root template ..
                if name == _Template_ID_Name:
                    oid = element.attrib.get(_Root_Attribute, '')
                    if oid in Root_Template_By_OID:
                        out = Root_Template_By_OID[oid]
                        break

            # .. deeper elements belong to the preamble's children and carry nothing of interest.
            depth += 1

    except ParseError as e:
        raise CCDAError(cid, _ccda.Reason.Not_CDA, f'Not well-formed XML -> {e}')

    return out

# ################################################################################################################################
# ################################################################################################################################
