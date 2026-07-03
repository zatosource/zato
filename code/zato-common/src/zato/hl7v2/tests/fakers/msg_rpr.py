from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rpri03() -> str:
    return fake_msh("RPR", "I03", "RPR_I03") + fake_pid()
