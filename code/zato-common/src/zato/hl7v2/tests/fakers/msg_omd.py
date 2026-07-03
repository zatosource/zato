from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omdo03() -> str:
    return fake_msh("OMD", "O03", "OMD_O03")
