from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.qicore.v7_0_0.extensions import (
    CODE_OPTIONS_URL,
    KEYELEMENT_URL,
)

class CodeableConcept(base.CodeableConcept):

    @property
    def code_options(self) -> Any:
        return get_extension(self, CODE_OPTIONS_URL)

    @code_options.setter
    def code_options(self, value: Any) -> None:
        set_extension(self, CODE_OPTIONS_URL, value)

class ElementDefinition(base.ElementDefinition):

    @property
    def keyelement(self) -> Any:
        return get_extension(self, KEYELEMENT_URL)

    @keyelement.setter
    def keyelement(self, value: Any) -> None:
        set_extension(self, KEYELEMENT_URL, value)
