from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_sdrs31() -> str:
    return fake_msh("SDR", "S31", "SDR_S31") + fake_pid()

def fake_sdrs32() -> str:
    return fake_msh("SDR", "S32", "SDR_S32") + fake_pid()
