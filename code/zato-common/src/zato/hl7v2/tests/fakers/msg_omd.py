from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omdo03() -> str:
    return fake_msh("OMD", "O03", "OMD_O03") + fake_pid()
