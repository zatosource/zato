from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_csuc09() -> str:
    return fake_msh("CSU", "C09", "CSU_C09") + fake_pid()
