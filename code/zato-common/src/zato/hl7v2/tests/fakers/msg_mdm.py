from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_mdmt01() -> str:
    return fake_msh("MDM", "T01", "MDM_T01") + fake_pid()

def fake_mdmt02() -> str:
    return fake_msh("MDM", "T02", "MDM_T02") + fake_pid()
