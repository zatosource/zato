from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rpli02() -> str:
    return fake_msh("RPL", "I02", "RPL_I02") + fake_msa()
