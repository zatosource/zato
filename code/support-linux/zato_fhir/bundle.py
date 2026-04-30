from __future__ import annotations

from typing import Any, Iterator

from zato_fhir.base import FHIRResource
from zato_fhir_r4_0_1_core import (
    rs_bundle_to_json as _to_json,
    rs_bundle_from_json as _from_json,
    rs_create_bundle as _create_bundle,
    rs_bundle_get_resource as _get_resource,
    rs_bundle_get_resources as _get_resources,
    rs_build_typed_bundle as _build_typed_bundle,
    rs_build_searchset as _build_searchset,
)


class FHIRBundle:

    def __init__(self, data: 'dict[str, Any] | None' = None):
        self._data = data or {}
        self._entries: 'list[dict[str, Any]]' = []

        if data:
            self._entries = data.get('entry', [])

    @property
    def id(self) -> 'str | None':
        return self._data.get('id')

    @property
    def type(self) -> 'str | None':
        return self._data.get('type')

    @property
    def total(self) -> 'int | None':
        return self._data.get('total')

    @property
    def timestamp(self) -> 'str | None':
        return self._data.get('timestamp')

    def __len__(self) -> 'int':
        return len(self._entries)

    def __iter__(self) -> 'Iterator[dict[str, Any]]':
        return iter(self._entries)

    def __getitem__(self, index: 'int') -> 'dict[str, Any]':
        return self._entries[index]

    def get_resource(self, index: 'int') -> 'FHIRResource | None':
        return _get_resource(self._entries, index)

    def get_resources(self) -> 'list[FHIRResource]':
        return _get_resources(self._entries)

    def to_dict(self) -> 'dict[str, Any]':
        return self._data

    def to_json(self, indent: 'int | None' = None) -> 'str':
        return _to_json(self._data, indent)

    @classmethod
    def from_dict(cls, data: 'dict[str, Any]') -> 'FHIRBundle':
        return cls(data)

    @classmethod
    def from_json(cls, raw: 'str') -> 'FHIRBundle':
        data = _from_json(raw)
        return cls.from_dict(data)


def parse_bundle(raw: 'str') -> 'FHIRBundle':
    return FHIRBundle.from_json(raw)


def create_bundle(
    resources: 'list[FHIRResource]',
    bundle_type: 'str' = 'collection',
    id_: 'str | None' = None,
) -> 'FHIRBundle':
    data = _create_bundle(resources, bundle_type, id_)
    return FHIRBundle(data)


class _BundleBuilder:
    """Base for TransactionBuilder and BatchBuilder."""

    _bundle_type: str = ''

    def __init__(self) -> None:
        self._entries: 'list[dict[str, Any]]' = []

    def create(
        self,
        resource: 'FHIRResource',
        *,
        full_url: 'str | None' = None,
        if_none_exist: 'str | None' = None,
    ) -> '_BundleBuilder':
        rt = getattr(resource, '_resource_type', '') or ''
        entry: dict[str, Any] = {
            'method': 'POST',
            'url': rt,
            'resource': resource,
        }
        if full_url:
            entry['fullUrl'] = full_url
        if if_none_exist:
            entry['ifNoneExist'] = if_none_exist
        self._entries.append(entry)
        return self

    def update(
        self,
        resource: 'FHIRResource',
        *,
        full_url: 'str | None' = None,
        if_match: 'str | None' = None,
    ) -> '_BundleBuilder':
        rt = getattr(resource, '_resource_type', '') or ''
        rid = getattr(resource, 'id', None) or ''
        entry: dict[str, Any] = {
            'method': 'PUT',
            'url': f'{rt}/{rid}' if rid else rt,
            'resource': resource,
        }
        if full_url:
            entry['fullUrl'] = full_url
        if if_match:
            entry['ifMatch'] = if_match
        self._entries.append(entry)
        return self

    def delete(
        self,
        resource_type: 'str',
        resource_id: 'str',
    ) -> '_BundleBuilder':
        self._entries.append({
            'method': 'DELETE',
            'url': f'{resource_type}/{resource_id}',
        })
        return self

    def read(
        self,
        resource_type: 'str',
        resource_id: 'str',
    ) -> '_BundleBuilder':
        self._entries.append({
            'method': 'GET',
            'url': f'{resource_type}/{resource_id}',
        })
        return self

    def build(self) -> 'FHIRResource':
        from zato_fhir.r4_0_1.resources import Bundle
        return _build_typed_bundle(self._entries, self._bundle_type)


class TransactionBuilder(_BundleBuilder):
    """Build a Bundle of type ``transaction``.

    Usage::

        txn = TransactionBuilder()
        txn.create(patient)
        txn.update(observation, if_match='W/"1"')
        txn.delete('Patient', 'old-1')
        bundle = txn.build()
    """
    _bundle_type = 'transaction'


class BatchBuilder(_BundleBuilder):
    """Build a Bundle of type ``batch``.

    Same API as TransactionBuilder but produces ``type_ == "batch"``.
    """
    _bundle_type = 'batch'


def build_searchset(
    resources: 'list[FHIRResource]',
    *,
    total: 'int | None' = None,
) -> 'FHIRResource':
    """Wrap *resources* into a typed ``searchset`` Bundle.

    Each resource becomes an ``entry`` with ``search.mode = "match"``
    and (when possible) a ``fullUrl`` derived from ``resourceType/id``.

    Parameters
    ----------
    resources:
        FHIR resource instances (e.g. ``Patient``, ``Observation``).
    total:
        Explicit total; defaults to ``len(resources)``.

    Returns
    -------
    Bundle
        A typed ``Bundle`` with ``type_ == "searchset"`` and fully
        typed entries, ready for ``to_dict()`` / ``to_json()``
        serialization.
    """
    return _build_searchset(resources, total)
