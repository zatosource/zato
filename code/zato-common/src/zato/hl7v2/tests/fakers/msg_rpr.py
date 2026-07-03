from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rpri03() -> str:
    return fake_msh("RPR", "I03", "RPR_I03") + fake_msa()
