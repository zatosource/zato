from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rpai08() -> str:
    return fake_msh("RPA", "I08", "RPA_I08") + fake_msa() + fake_pid()
