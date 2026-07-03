from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omqo57() -> str:
    return fake_msh("OMQ", "O57", "OMQ_O57")
