from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_dsc, fake_msa, fake_qak, fake_qpd, fake_rcp


def fake_rspe03() -> str:
    return fake_msh("RSP", "E03", "RSP_E03") + fake_msa()

def fake_rspe22() -> str:
    return fake_msh("RSP", "E22", "RSP_E22") + fake_msa()

def fake_rspk11() -> str:
    return fake_msh("RSP", "K11", "RSP_K11") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspk21() -> str:
    return fake_msh("RSP", "K21", "RSP_K21") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspk22() -> str:
    return fake_msh("RSP", "K22", "RSP_K22") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspk23() -> str:
    return fake_msh("RSP", "K23", "RSP_K23") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspk25() -> str:
    return fake_msh("RSP", "K25", "RSP_K25") + fake_msa() + fake_qak() + fake_qpd() + fake_rcp()

def fake_rspk31() -> str:
    return fake_msh("RSP", "K31", "RSP_K31") + fake_msa() + fake_qak() + fake_qpd() + fake_rcp()

def fake_rspk32() -> str:
    return fake_msh("RSP", "K32", "RSP_K32") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspo33() -> str:
    return fake_msh("RSP", "O33", "RSP_O33") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspo34() -> str:
    return fake_msh("RSP", "O34", "RSP_O34") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspz82() -> str:
    return fake_msh("RSP", "Z82", "RSP_Z82") + fake_msa() + fake_qak() + fake_qpd() + fake_rcp()

def fake_rspz84() -> str:
    return fake_msh("RSP", "Z84", "RSP_Z84") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspz86() -> str:
    return fake_msh("RSP", "Z86", "RSP_Z86") + fake_msa() + fake_qak() + fake_qpd()

def fake_rspz88() -> str:
    return fake_msh("RSP", "Z88", "RSP_Z88") + fake_msa() + fake_qak() + fake_qpd() + fake_rcp() + fake_dsc()

def fake_rspz90() -> str:
    return fake_msh("RSP", "Z90", "RSP_Z90") + fake_msa() + fake_qak() + fake_qpd() + fake_rcp() + fake_dsc()

def fake_rspznn() -> str:
    return fake_msh("RSP", "Znn", "RSP_Znn") + fake_msa() + fake_qak() + fake_qpd()
