from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_ehce01() -> str:
    return fake_msh("EHC", "E01", "EHC_E01")

def fake_ehce02() -> str:
    return fake_msh("EHC", "E02", "EHC_E02")

def fake_ehce04() -> str:
    return fake_msh("EHC", "E04", "EHC_E04")

def fake_ehce10() -> str:
    return fake_msh("EHC", "E10", "EHC_E10") + fake_msa()

def fake_ehce12() -> str:
    return fake_msh("EHC", "E12", "EHC_E12") + fake_segment("RFI") + fake_segment("IVC") + fake_segment("PSS") + fake_segment("PSG")

def fake_ehce13() -> str:
    return fake_msh("EHC", "E13", "EHC_E13") + fake_msa() + fake_segment("RFI") + fake_segment("IVC") + fake_segment("PSS") + fake_segment("PSG")

def fake_ehce15() -> str:
    return fake_msh("EHC", "E15", "EHC_E15")

def fake_ehce20() -> str:
    return fake_msh("EHC", "E20", "EHC_E20")

def fake_ehce21() -> str:
    return fake_msh("EHC", "E21", "EHC_E21")

def fake_ehce24() -> str:
    return fake_msh("EHC", "E24", "EHC_E24") + fake_msa()
