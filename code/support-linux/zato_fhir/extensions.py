from __future__ import annotations

from typing import Any

from zato_fhir_r4_0_1_core import (
    get_extension as _get_extension,
    get_extensions_by_url as _get_extensions_by_url,
    has_extension as _has_extension,
    add_extension as _add_extension,
    set_extension as _set_extension,
    remove_extension as _remove_extension,
    get_extension_text as _get_extension_text,
    set_extension_text as _set_extension_text,
    get_nested_extension as _get_nested_extension,
)


def get_extension(resource: 'Any', url: 'str') -> 'Any | None':
    return _get_extension(resource, url)


def get_extensions(resource: 'Any', url: 'str') -> 'list[Any]':
    return _get_extensions_by_url(resource, url)


def has_extension(resource: 'Any', url: 'str') -> 'bool':
    return _has_extension(resource, url)


def get_extension_text(resource: 'Any', url: 'str') -> 'str | None':
    return _get_extension_text(resource, url)


def set_extension_text(resource: 'Any', url: 'str', value: 'str') -> 'None':
    _set_extension_text(resource, url, value)


def set_extension(resource: 'Any', url: 'str', value: 'Any') -> 'None':
    _set_extension(resource, url, value)


def add_extension(
    resource: 'Any',
    url: 'str',
    value: 'Any',
    value_type: 'str' = 'string',
) -> 'None':
    _add_extension(resource, url, value, value_type)


def remove_extension(resource: 'Any', url: 'str') -> 'bool':
    return _remove_extension(resource, url)


def get_nested_extension(resource: 'Any', *urls: 'str') -> 'Any | None':
    return _get_nested_extension(resource, list(urls))
