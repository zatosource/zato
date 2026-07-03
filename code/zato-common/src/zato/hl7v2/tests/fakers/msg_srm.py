from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.scheduling import fake_arq


def fake_srms01() -> str:
    return fake_msh("SRM", "S01", "SRM_S01") + fake_arq()
