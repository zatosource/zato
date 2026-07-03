from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.master_file import fake_mfi
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_mfkm01() -> str:
    return fake_msh("MFK", "M01", "MFK_M01") + fake_msa() + fake_mfi()
