from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.staff import fake_stf
from zato.hl7v2.tests.fakers.visit import fake_evn


def fake_pmub01() -> str:
    return fake_msh("PMU", "B01", "PMU_B01") + fake_evn("B01") + fake_stf()

def fake_pmub03() -> str:
    return fake_msh("PMU", "B03", "PMU_B03") + fake_evn("B03") + fake_stf()

def fake_pmub04() -> str:
    return fake_msh("PMU", "B04", "PMU_B04") + fake_evn("B04") + fake_stf()

def fake_pmub07() -> str:
    return fake_msh("PMU", "B07", "PMU_B07") + fake_evn("B07") + fake_stf()

def fake_pmub08() -> str:
    return fake_msh("PMU", "B08", "PMU_B08") + fake_evn("B08") + fake_stf()
