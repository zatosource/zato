from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orlo22() -> str:
    return fake_msh("ORL", "O22", "ORL_O22") + fake_pid()

def fake_orlo34() -> str:
    return fake_msh("ORL", "O34", "ORL_O34") + fake_pid()

def fake_orlo36() -> str:
    return fake_msh("ORL", "O36", "ORL_O36") + fake_pid()

def fake_orlo40() -> str:
    return fake_msh("ORL", "O40", "ORL_O40") + fake_pid()

def fake_orlo53() -> str:
    return fake_msh("ORL", "O53", "ORL_O53") + fake_pid()

def fake_orlo54() -> str:
    return fake_msh("ORL", "O54", "ORL_O54") + fake_pid()

def fake_orlo55() -> str:
    return fake_msh("ORL", "O55", "ORL_O55") + fake_pid()

def fake_orlo56() -> str:
    return fake_msh("ORL", "O56", "ORL_O56") + fake_pid()
