from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.visit import fake_evn, fake_pv1


def fake_barp01() -> str:
    return fake_msh("BAR", "P01", "BAR_P01") + fake_evn("P01") + fake_pid()

def fake_barp02() -> str:
    return fake_msh("BAR", "P02", "BAR_P02") + fake_evn("P02")

def fake_barp05() -> str:
    return fake_msh("BAR", "P05", "BAR_P05") + fake_evn("P05") + fake_pid()

def fake_barp06() -> str:
    return fake_msh("BAR", "P06", "BAR_P06") + fake_evn("P06")

def fake_barp10() -> str:
    return fake_msh("BAR", "P10", "BAR_P10") + fake_evn("P10") + fake_pid() + fake_pv1() + fake_segment("GP1")

def fake_barp12() -> str:
    return fake_msh("BAR", "P12", "BAR_P12") + fake_evn("P12") + fake_pid() + fake_pv1()
