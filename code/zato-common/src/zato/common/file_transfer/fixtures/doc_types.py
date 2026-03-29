# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.const import (
    AttributeType,
    ExtractionQueryType,
    FileType,
    PreprocessSavePolicy,
    RecognitionRuleType,
)
from zato.common.file_transfer.model import DocumentType, ExtractionRule, RecognitionRule

# ################################################################################################################################
# ################################################################################################################################

def get_sample_doc_types() -> 'list[DocumentType]':

    return [

        DocumentType(
            id='dt-001',
            name='Purchase order',
            description='XML purchase orders with PurchaseOrder root element',
            is_enabled=True,
            file_type=FileType.Xml,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Xml_Root_Tag,
                    tag='PurchaseOrder',
                    priority=1,
                ),
            ],
            extraction_rules=[
                ExtractionRule(
                    attribute='sender',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/PurchaseOrder/Header/SenderID',
                ),
                ExtractionRule(
                    attribute='receiver',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/PurchaseOrder/Header/ReceiverID',
                ),
                ExtractionRule(
                    attribute='document_id',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/PurchaseOrder/Header/OrderNumber',
                ),
                ExtractionRule(
                    attribute='order_amount',
                    attr_type=AttributeType.Custom,
                    query_type=ExtractionQueryType.Xpath,
                    query='/PurchaseOrder/Header/TotalAmount',
                ),
            ],
            preprocess_validate=True,
            preprocess_dedup=True,
            preprocess_dedup_window_days=30,
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-002',
            name='Financial report',
            description='CSV financial reports with invoice_*.csv filename pattern',
            is_enabled=True,
            file_type=FileType.Flat_File,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Filename_Glob,
                    pattern='invoice_*.csv',
                    priority=1,
                ),
                RecognitionRule(
                    type=RecognitionRuleType.Content_Regex,
                    pattern='^date,amount,currency',
                    bytes_limit=100,
                    priority=2,
                ),
            ],
            extraction_rules=[
                ExtractionRule(
                    attribute='sender',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Fixed,
                    value='sftp_username_mapping',
                ),
            ],
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-003',
            name='Shipping notice',
            description='EDI 856 shipping notices',
            is_enabled=True,
            file_type=FileType.Edi,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Edi_Segment,
                    segment='ISA',
                    transaction_set='856',
                    priority=1,
                ),
            ],
            extraction_rules=[
                ExtractionRule(
                    attribute='sender',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Regex,
                    query=r'ISA\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*([^*]*)',
                ),
                ExtractionRule(
                    attribute='receiver',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Regex,
                    query=r'ISA\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*[^*]*\*([^*]*)',
                ),
            ],
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-004',
            name='Product catalog',
            description='JSON product catalog updates',
            is_enabled=True,
            file_type=FileType.Json,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Json_Path,
                    path='$.catalog_version',
                    priority=1,
                ),
            ],
            extraction_rules=[
                ExtractionRule(
                    attribute='document_id',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Jsonpath,
                    query='$.catalog_version',
                ),
                ExtractionRule(
                    attribute='sender',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Jsonpath,
                    query='$.supplier.id',
                ),
            ],
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-005',
            name='HR export',
            description='PGP-encrypted HR data exports',
            is_enabled=True,
            file_type=FileType.Binary,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Pgp_Header,
                    priority=1,
                ),
            ],
            extraction_rules=[],
            preprocess_pgp_verify=True,
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-006',
            name='Price update',
            description='Excel price list updates',
            is_enabled=True,
            file_type=FileType.Flat_File,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Filename_Glob,
                    pattern='price_list_*.xlsx',
                    priority=1,
                ),
            ],
            extraction_rules=[],
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-007',
            name='Order acknowledgment',
            description='XML order acknowledgments',
            is_enabled=True,
            file_type=FileType.Xml,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Xml_Root_Tag,
                    tag='OrderAcknowledgment',
                    priority=1,
                ),
            ],
            extraction_rules=[
                ExtractionRule(
                    attribute='sender',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/OrderAcknowledgment/Header/SenderID',
                ),
                ExtractionRule(
                    attribute='receiver',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/OrderAcknowledgment/Header/ReceiverID',
                ),
                ExtractionRule(
                    attribute='document_id',
                    attr_type=AttributeType.System,
                    query_type=ExtractionQueryType.Xpath,
                    query='/OrderAcknowledgment/Header/AckNumber',
                ),
            ],
            preprocess_save=PreprocessSavePolicy.All,
        ),

        DocumentType(
            id='dt-008',
            name='Regulatory filing',
            description='PDF compliance and regulatory filings',
            is_enabled=True,
            file_type=FileType.Binary,
            recognition_rules=[
                RecognitionRule(
                    type=RecognitionRuleType.Filename_Glob,
                    pattern='compliance_*.pdf',
                    priority=1,
                ),
            ],
            extraction_rules=[],
            preprocess_checksum=True,
            preprocess_save=PreprocessSavePolicy.All,
        ),

    ]

# ################################################################################################################################
# ################################################################################################################################
