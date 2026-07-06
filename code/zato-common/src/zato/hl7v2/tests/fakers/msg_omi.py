from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omio23() -> str:
    return fake_msh("OMI", "O23", "OMI_O23") + fake_pid()
