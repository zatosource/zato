# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The segment mappers are kept in per-domain modules, re-exported here as one flat namespace.

from zato.hl7.mappings.segments.admin import apply_pra as apply_pra
from zato.hl7.mappings.segments.admin import apply_prt as apply_prt
from zato.hl7.mappings.segments.admin import map_segment_to_basic as map_segment_to_basic
from zato.hl7.mappings.segments.admin import map_stf as map_stf
from zato.hl7.mappings.segments.blood import apply_bpo as apply_bpo
from zato.hl7.mappings.segments.clinical import map_al1 as map_al1
from zato.hl7.mappings.segments.clinical import map_dg1 as map_dg1
from zato.hl7.mappings.segments.clinical import map_iam as map_iam
from zato.hl7.mappings.segments.clinical import map_pr1 as map_pr1
from zato.hl7.mappings.segments.common import Encapsulated_Value_Type as Encapsulated_Value_Type
from zato.hl7.mappings.segments.common import No_Consumed_Fields as No_Consumed_Fields
from zato.hl7.mappings.segments.common import Text_Value_Types as Text_Value_Types
from zato.hl7.mappings.segments.common import append_to_list_field as append_to_list_field
from zato.hl7.mappings.segments.common import preserve_unmapped as preserve_unmapped
from zato.hl7.mappings.segments.common import preserve_value as preserve_value
from zato.hl7.mappings.segments.documents import add_document_attachment as add_document_attachment
from zato.hl7.mappings.segments.documents import map_txa as map_txa
from zato.hl7.mappings.segments.documents import set_document_text as set_document_text
from zato.hl7.mappings.segments.encounter import apply_evn as apply_evn
from zato.hl7.mappings.segments.encounter import apply_rol as apply_rol
from zato.hl7.mappings.segments.encounter import apply_zbe as apply_zbe
from zato.hl7.mappings.segments.encounter import enrich_pv2 as enrich_pv2
from zato.hl7.mappings.segments.encounter import map_pv1 as map_pv1
from zato.hl7.mappings.segments.financial import apply_in2 as apply_in2
from zato.hl7.mappings.segments.financial import map_ft1 as map_ft1
from zato.hl7.mappings.segments.financial import map_in1 as map_in1
from zato.hl7.mappings.segments.header import apply_msa as apply_msa
from zato.hl7.mappings.segments.header import enrich_sft as enrich_sft
from zato.hl7.mappings.segments.header import map_err as map_err
from zato.hl7.mappings.segments.header import map_msh as map_msh
from zato.hl7.mappings.segments.imaging import apply_ipc as apply_ipc
from zato.hl7.mappings.segments.imaging import apply_zds as apply_zds
from zato.hl7.mappings.segments.medication import enrich_rxr as enrich_rxr
from zato.hl7.mappings.segments.medication import map_rxa as map_rxa
from zato.hl7.mappings.segments.medication import map_rxa_to_administration as map_rxa_to_administration
from zato.hl7.mappings.segments.medication import map_rxd as map_rxd
from zato.hl7.mappings.segments.medication import map_rxe as map_rxe
from zato.hl7.mappings.segments.medication import map_rxg as map_rxg
from zato.hl7.mappings.segments.medication import map_rxo as map_rxo
from zato.hl7.mappings.segments.observations import apply_sac as apply_sac
from zato.hl7.mappings.segments.observations import gather_obx_text as gather_obx_text
from zato.hl7.mappings.segments.observations import map_obx as map_obx
from zato.hl7.mappings.segments.observations import map_spm as map_spm
from zato.hl7.mappings.segments.observations import nte_text as nte_text
from zato.hl7.mappings.segments.observations import obx_attachment as obx_attachment
from zato.hl7.mappings.segments.orders import OBR_Handled_Order_Only as OBR_Handled_Order_Only
from zato.hl7.mappings.segments.orders import OBR_Handled_With_Report as OBR_Handled_With_Report
from zato.hl7.mappings.segments.orders import apply_tq1 as apply_tq1
from zato.hl7.mappings.segments.orders import enrich_service_request_with_orc as enrich_service_request_with_orc
from zato.hl7.mappings.segments.orders import map_obr_to_diagnostic_report as map_obr_to_diagnostic_report
from zato.hl7.mappings.segments.orders import map_orc_obr_to_service_request as map_orc_obr_to_service_request
from zato.hl7.mappings.segments.orders import obr_matches_orc as obr_matches_orc
from zato.hl7.mappings.segments.orders import orc_matches_service_request as orc_matches_service_request
from zato.hl7.mappings.segments.patient import apply_mrg as apply_mrg
from zato.hl7.mappings.segments.patient import apply_pda as apply_pda
from zato.hl7.mappings.segments.patient import enrich_pd1 as enrich_pd1
from zato.hl7.mappings.segments.patient import map_gt1 as map_gt1
from zato.hl7.mappings.segments.patient import map_nk1 as map_nk1
from zato.hl7.mappings.segments.patient import map_pid as map_pid
from zato.hl7.mappings.segments.referral import apply_prd as apply_prd
from zato.hl7.mappings.segments.referral import map_rf1 as map_rf1
from zato.hl7.mappings.segments.scheduling import aig_participant as aig_participant
from zato.hl7.mappings.segments.scheduling import ail_participant as ail_participant
from zato.hl7.mappings.segments.scheduling import aip_participant as aip_participant
from zato.hl7.mappings.segments.scheduling import enrich_ais as enrich_ais
from zato.hl7.mappings.segments.scheduling import map_arq as map_arq
from zato.hl7.mappings.segments.scheduling import map_sch as map_sch

# ################################################################################################################################
# ################################################################################################################################
