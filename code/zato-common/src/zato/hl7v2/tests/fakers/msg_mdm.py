from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.documents import fake_txa
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.visit import fake_evn, fake_pv1


def fake_mdmt01() -> str:
    return fake_msh("MDM", "T01", "MDM_T01") + fake_evn("T01") + fake_pid() + fake_pv1() + fake_txa()

def fake_mdmt02() -> str:
    return fake_msh("MDM", "T02", "MDM_T02") + fake_evn("T02") + fake_pid() + fake_pv1() + fake_txa()
