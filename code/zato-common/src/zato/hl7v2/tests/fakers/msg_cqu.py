from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.clinical import fake_rf1
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_cqui19() -> str:
    return fake_msh("CQU", "I19", "CQU_I19") + fake_msa() + fake_rf1()
