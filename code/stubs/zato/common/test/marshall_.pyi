from typing import Any

from zato.common.ext.dataclasses import dataclass, field
from zato.common.marshal_.api import Model
from zato.common.typing_ import anynone, anydictnone, anylistnone, dict_field, list_, list_field, optional

def get_default_address_details() -> None: ...

def get_default_address_characteristics() -> None: ...

class LineDetails(Model):
    name: str

class LineParent(Model):
    name: str
    details: LineDetails

class Address(Model):
    locality: str
    post_code: optional[str]
    details: optional[dict]
    characteristics: optional[list]

class AddressWithDefaults(Model):
    locality: str
    post_code: optional[str]
    details: optional[dict]
    characteristics: optional[list]

class User(Model):
    user_name: str
    address: Address

class Role(Model):
    type: str
    name: str

class CreateUserRequest(Model):
    request_id: int
    user: User
    role_list: list_[Role]

class Attr(Model):
    type: str
    name: str

class Phone(Model):
    attr_list: list_[Attr]

class Modem(Model):
    attr_list: list_[Attr]

class CreatePhoneListRequest(Model):
    phone_list: list_[Phone]

class CreateAttrListRequest(Model):
    attr_list: list_[Attr]

class WithAny(Model):
    str1: anynone
    list1: anylistnone
    dict1: anydictnone

class TestService:
    ...
