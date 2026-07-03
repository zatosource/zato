from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_orno08() -> str:
    return fake_msh("ORN", "O08", "ORN_O08") + fake_msa()
