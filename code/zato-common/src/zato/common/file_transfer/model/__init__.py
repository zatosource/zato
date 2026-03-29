# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.common.file_transfer.model.core import (
    ActivityLogEntry,
    CriteriaSpec,
    DocumentType,
    ExtendedCriteria,
    ExtractionRule,
    PGPKey,
    PickupChannel,
    PreprocessOverrides,
    ProcessingRule,
    RecognitionRule,
    RuleAction,
    Settings,
    Task,
    Transaction,
)

from zato.common.file_transfer.model.result import (
    ActionResult,
    ChecksumResult,
    DedupResult,
    DeliveryResult,
    ExtractionResult,
    KeyInfo,
    KeyPairResult,
    PreprocessResult,
    SearchResult,
    VerifyResult,
)
