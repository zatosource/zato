# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake, fake_msh, fake_segment
from zato.hl7v2.tests.fakers.blood_bank import fake_bpo
from zato.hl7v2.tests.fakers.clinical import fake_gol, fake_prb, fake_pth, fake_rf1
from zato.hl7v2.tests.fakers.documents import fake_txa
from zato.hl7v2.tests.fakers.lab import fake_equ, fake_inv, fake_spm
from zato.hl7v2.tests.fakers.master_file import fake_mfe, fake_mfi
from zato.hl7v2.tests.fakers.order import fake_obr, fake_obx, fake_orc
from zato.hl7v2.tests.fakers.patient import fake_mrg, fake_nk1, fake_pid, fake_rel
from zato.hl7v2.tests.fakers.pharmacy import fake_rxa, fake_rxd, fake_rxe, fake_rxg
from zato.hl7v2.tests.fakers.query import fake_dsc, fake_msa, fake_qak, fake_qpd, fake_qrd, fake_rcp
from zato.hl7v2.tests.fakers.scheduling import fake_arq, fake_rgs, fake_sch
from zato.hl7v2.tests.fakers.software import fake_sft
from zato.hl7v2.tests.fakers.staff import fake_prd, fake_stf
from zato.hl7v2.tests.fakers.visit import fake_evn, fake_npu, fake_pv1

# ################################################################################################################################
# ################################################################################################################################

__all__ = [
    'fake',
    'fake_arq',
    'fake_bpo',
    'fake_dsc',
    'fake_equ',
    'fake_evn',
    'fake_gol',
    'fake_inv',
    'fake_mfe',
    'fake_mfi',
    'fake_mrg',
    'fake_msa',
    'fake_msh',
    'fake_nk1',
    'fake_npu',
    'fake_obr',
    'fake_obx',
    'fake_orc',
    'fake_pid',
    'fake_prb',
    'fake_prd',
    'fake_pth',
    'fake_pv1',
    'fake_qak',
    'fake_qpd',
    'fake_qrd',
    'fake_rcp',
    'fake_rel',
    'fake_rf1',
    'fake_rgs',
    'fake_rxa',
    'fake_rxd',
    'fake_rxe',
    'fake_rxg',
    'fake_sch',
    'fake_segment',
    'fake_sft',
    'fake_spm',
    'fake_stf',
    'fake_txa',
]

# ################################################################################################################################
# ################################################################################################################################
