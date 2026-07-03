from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.visit import fake_evn


def fake_dftp03() -> str:
    return fake_msh("DFT", "P03", "DFT_P03") + fake_evn("P03") + fake_pid()

def fake_dftp11() -> str:
    return fake_msh("DFT", "P11", "DFT_P11") + fake_evn("P11") + fake_pid()
