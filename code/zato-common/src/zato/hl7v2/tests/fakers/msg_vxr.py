from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid
from zato.hl7v2.tests.fakers.query import fake_msa, fake_qrd


def fake_vxrv03() -> str:
    return fake_msh("VXR", "V03", "VXR_V03") + fake_msa() + fake_qrd() + fake_pid()
