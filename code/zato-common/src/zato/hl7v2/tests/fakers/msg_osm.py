from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_osmr26() -> str:
    return fake_msh("OSM", "R26", "OSM_R26") + fake_pid()
