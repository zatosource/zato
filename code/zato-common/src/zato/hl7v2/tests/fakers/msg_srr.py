from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_srrs01() -> str:
    return fake_msh("SRR", "S01", "SRR_S01") + fake_msa()
