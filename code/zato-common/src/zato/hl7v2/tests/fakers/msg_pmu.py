from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_pmub01() -> str:
    return fake_msh("PMU", "B01", "PMU_B01") + fake_pid()

def fake_pmub03() -> str:
    return fake_msh("PMU", "B03", "PMU_B03") + fake_pid()

def fake_pmub04() -> str:
    return fake_msh("PMU", "B04", "PMU_B04") + fake_pid()

def fake_pmub07() -> str:
    return fake_msh("PMU", "B07", "PMU_B07") + fake_pid()

def fake_pmub08() -> str:
    return fake_msh("PMU", "B08", "PMU_B08") + fake_pid()
