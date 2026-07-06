from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ormo01() -> str:
    return fake_msh("ORM", "O01", "ORM_O01") + fake_pid()
