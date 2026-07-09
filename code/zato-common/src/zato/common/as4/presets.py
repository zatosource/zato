# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.as4.common import AS4Exception

# ################################################################################################################################
# ################################################################################################################################

class DocumentTypePreset(NamedTuple):
    """ Everything a named document type stands for - the raw identifiers
    that the document standards define and that users never have to know.
    """
    document_type: str
    process_id: str
    process_scheme: str
    document_standard: str
    document_type_version: str

# ################################################################################################################################
# ################################################################################################################################

# The UBL namespaces the presets below build on.
_ubl_invoice         = 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
_ubl_credit_note     = 'urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2'
_ubl_order           = 'urn:oasis:names:specification:ubl:schema:xsd:Order-2'
_ubl_despatch_advice = 'urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2'

# The customization identifier of Peppol BIS Billing 3.0.
_billing_3_customization = 'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0'

# The customization identifiers of the PINT billing specializations.
_pint_anz_customization = 'urn:peppol:pint:billing-1@aunz-1'
_pint_jp_customization  = 'urn:peppol:pint:billing-1@jp-1'

# The process identifier every PINT billing exchange uses.
_pint_billing_process = 'urn:peppol:bis:billing'

# The identifier scheme every Peppol process identifier uses.
_process_scheme = 'cenbii-procid-ubl'

# ################################################################################################################################
# ################################################################################################################################

document_type_presets = {

    'peppol-bis-billing-3-invoice': DocumentTypePreset(
        document_type = f'{_ubl_invoice}::Invoice##{_billing_3_customization}::2.1',
        process_id = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
        process_scheme = _process_scheme,
        document_standard = _ubl_invoice,
        document_type_version = '2.1',
    ),

    'peppol-bis-billing-3-credit-note': DocumentTypePreset(
        document_type = f'{_ubl_credit_note}::CreditNote##{_billing_3_customization}::2.1',
        process_id = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
        process_scheme = _process_scheme,
        document_standard = _ubl_credit_note,
        document_type_version = '2.1',
    ),

    'peppol-bis-order-3': DocumentTypePreset(
        document_type = f'{_ubl_order}::Order##urn:fdc:peppol.eu:poacc:trns:order:3::2.1',
        process_id = 'urn:fdc:peppol.eu:poacc:bis:ordering:3',
        process_scheme = _process_scheme,
        document_standard = _ubl_order,
        document_type_version = '2.1',
    ),

    'peppol-bis-despatch-advice-3': DocumentTypePreset(
        document_type = f'{_ubl_despatch_advice}::DespatchAdvice##urn:fdc:peppol.eu:poacc:trns:despatch_advice:3::2.1',
        process_id = 'urn:fdc:peppol.eu:poacc:bis:despatch_advice:3',
        process_scheme = _process_scheme,
        document_standard = _ubl_despatch_advice,
        document_type_version = '2.1',
    ),

    'peppol-pint-anz-invoice': DocumentTypePreset(
        document_type = f'{_ubl_invoice}::Invoice##{_pint_anz_customization}::2.1',
        process_id = _pint_billing_process,
        process_scheme = _process_scheme,
        document_standard = _ubl_invoice,
        document_type_version = '2.1',
    ),

    'peppol-pint-anz-credit-note': DocumentTypePreset(
        document_type = f'{_ubl_credit_note}::CreditNote##{_pint_anz_customization}::2.1',
        process_id = _pint_billing_process,
        process_scheme = _process_scheme,
        document_standard = _ubl_credit_note,
        document_type_version = '2.1',
    ),

    'peppol-pint-jp-invoice': DocumentTypePreset(
        document_type = f'{_ubl_invoice}::Invoice##{_pint_jp_customization}::2.1',
        process_id = _pint_billing_process,
        process_scheme = _process_scheme,
        document_standard = _ubl_invoice,
        document_type_version = '2.1',
    ),

    'peppol-pint-jp-credit-note': DocumentTypePreset(
        document_type = f'{_ubl_credit_note}::CreditNote##{_pint_jp_customization}::2.1',
        process_id = _pint_billing_process,
        process_scheme = _process_scheme,
        document_standard = _ubl_credit_note,
        document_type_version = '2.1',
    ),
}

# ################################################################################################################################
# ################################################################################################################################

def get_document_type_preset(name:'str') -> 'DocumentTypePreset':
    """ Resolves a document type name to its preset, with a clear error when the name is unknown.
    """
    if name not in document_type_presets:
        known = ', '.join(sorted(document_type_presets))
        raise AS4Exception(f'Unknown document type `{name}` - known types are: {known}')

    out = document_type_presets[name]
    return out

# ################################################################################################################################
# ################################################################################################################################
