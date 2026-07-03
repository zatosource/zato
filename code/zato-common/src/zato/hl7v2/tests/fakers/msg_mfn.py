from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_mfnm02() -> str:
    return fake_msh("MFN", "M02", "MFN_M02") + fake_pid()

def fake_mfnm04() -> str:
    return fake_msh("MFN", "M04", "MFN_M04") + fake_pid()

def fake_mfnm05() -> str:
    return fake_msh("MFN", "M05", "MFN_M05") + fake_pid()

def fake_mfnm06() -> str:
    return fake_msh("MFN", "M06", "MFN_M06") + fake_pid()

def fake_mfnm07() -> str:
    return fake_msh("MFN", "M07", "MFN_M07") + fake_pid()

def fake_mfnm08() -> str:
    return fake_msh("MFN", "M08", "MFN_M08") + fake_pid()

def fake_mfnm09() -> str:
    return fake_msh("MFN", "M09", "MFN_M09") + fake_pid()

def fake_mfnm10() -> str:
    return fake_msh("MFN", "M10", "MFN_M10") + fake_pid()

def fake_mfnm11() -> str:
    return fake_msh("MFN", "M11", "MFN_M11") + fake_pid()

def fake_mfnm12() -> str:
    return fake_msh("MFN", "M12", "MFN_M12") + fake_pid()

def fake_mfnm13() -> str:
    return fake_msh("MFN", "M13", "MFN_M13") + fake_pid()

def fake_mfnm15() -> str:
    return fake_msh("MFN", "M15", "MFN_M15") + fake_pid()

def fake_mfnm16() -> str:
    return fake_msh("MFN", "M16", "MFN_M16") + fake_pid()

def fake_mfnm17() -> str:
    return fake_msh("MFN", "M17", "MFN_M17") + fake_pid()

def fake_mfnm18() -> str:
    return fake_msh("MFN", "M18", "MFN_M18") + fake_pid()

def fake_mfnm19() -> str:
    return fake_msh("MFN", "M19", "MFN_M19") + fake_pid()

def fake_mfnznn() -> str:
    return fake_msh("MFN", "Znn", "MFN_Znn") + fake_pid()
