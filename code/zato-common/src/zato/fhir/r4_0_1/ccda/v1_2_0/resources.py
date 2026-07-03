from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.ccda.v1_2_0.extensions import (
    DATA_ENTERER_EXTENSION_URL,
    ORDER_EXTENSION_URL,
    INFORMATION_RECIPIENT_EXTENSION_URL,
    VERSION_NUMBER_URL,
    PERFORMER_EXTENSION_URL,
    PARTICIPANT_EXTENSION_URL,
    INFORMANT_EXTENSION_URL,
    AUTHORIZATION_EXTENSION_URL,
)

class Composition(base.Composition):

    @property
    def data_enterer_extension(self) -> Any:
        return get_extension(self, DATA_ENTERER_EXTENSION_URL)

    @data_enterer_extension.setter
    def data_enterer_extension(self, value: Any) -> None:
        set_extension(self, DATA_ENTERER_EXTENSION_URL, value)

    @property
    def order_extension(self) -> Any:
        return get_extension(self, ORDER_EXTENSION_URL)

    @order_extension.setter
    def order_extension(self, value: Any) -> None:
        set_extension(self, ORDER_EXTENSION_URL, value)

    @property
    def information_recipient_extension(self) -> Any:
        return get_extension(self, INFORMATION_RECIPIENT_EXTENSION_URL)

    @information_recipient_extension.setter
    def information_recipient_extension(self, value: Any) -> None:
        set_extension(self, INFORMATION_RECIPIENT_EXTENSION_URL, value)

    @property
    def version_number(self) -> Any:
        return get_extension(self, VERSION_NUMBER_URL)

    @version_number.setter
    def version_number(self, value: Any) -> None:
        set_extension(self, VERSION_NUMBER_URL, value)

    @property
    def performer_extension(self) -> Any:
        return get_extension(self, PERFORMER_EXTENSION_URL)

    @performer_extension.setter
    def performer_extension(self, value: Any) -> None:
        set_extension(self, PERFORMER_EXTENSION_URL, value)

    @property
    def participant_extension(self) -> Any:
        return get_extension(self, PARTICIPANT_EXTENSION_URL)

    @participant_extension.setter
    def participant_extension(self, value: Any) -> None:
        set_extension(self, PARTICIPANT_EXTENSION_URL, value)

    @property
    def informant_extension(self) -> Any:
        return get_extension(self, INFORMANT_EXTENSION_URL)

    @informant_extension.setter
    def informant_extension(self, value: Any) -> None:
        set_extension(self, INFORMANT_EXTENSION_URL, value)

    @property
    def authorization_extension(self) -> Any:
        return get_extension(self, AUTHORIZATION_EXTENSION_URL)

    @authorization_extension.setter
    def authorization_extension(self, value: Any) -> None:
        set_extension(self, AUTHORIZATION_EXTENSION_URL, value)
