from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_orgo20() -> str:
    return fake_msh("ORG", "O20", "ORG_O20") + fake_msa()
