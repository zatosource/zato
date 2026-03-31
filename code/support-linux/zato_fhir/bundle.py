from __future__ import annotations

import json
from typing import Any, Iterator

from zato_fhir.base import FHIRResource


class FHIRBundle:
    
    def __init__(self, data: dict[str, Any] | None = None):
        self._data = data or {}
        self._entries: list[dict[str, Any]] = []
        self._resources: list[FHIRResource] = []
        
        if data:
            self._entries = data.get('entry', [])
    
    @property
    def id(self) -> str | None:
        return self._data.get('id')
    
    @property
    def type(self) -> str | None:
        return self._data.get('type')
    
    @property
    def total(self) -> int | None:
        return self._data.get('total')
    
    @property
    def timestamp(self) -> str | None:
        return self._data.get('timestamp')
    
    def __len__(self) -> int:
        return len(self._entries)
    
    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self._entries)
    
    def __getitem__(self, index: int) -> dict[str, Any]:
        return self._entries[index]
    
    def get_resource(self, index: int) -> FHIRResource | None:
        if index >= len(self._entries):
            return None
        
        entry = self._entries[index]
        resource_data = entry.get('resource')
        if not resource_data:
            return None
        
        resource_type = resource_data.get('resourceType')
        if not resource_type:
            return None
        
        import zato_fhir.r4_0_1 as r4
        cls = getattr(r4, resource_type, None)
        if cls:
            return cls.from_dict(resource_data)
        return None
    
    def get_resources(self) -> list[FHIRResource]:
        resources = []
        for i in range(len(self._entries)):
            r = self.get_resource(i)
            if r:
                resources.append(r)
        return resources
    
    def to_dict(self) -> dict[str, Any]:
        return self._data
    
    def to_json(self, indent: int | None = None) -> str:
        return json.dumps(self._data, indent=indent)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FHIRBundle:
        return cls(data)
    
    @classmethod
    def from_json(cls, raw: str) -> FHIRBundle:
        data = json.loads(raw)
        return cls.from_dict(data)


def parse_bundle(raw: str) -> FHIRBundle:
    return FHIRBundle.from_json(raw)


def create_bundle(
    resources: list[FHIRResource],
    bundle_type: str = 'collection',
    id_: str | None = None,
) -> FHIRBundle:
    entries = []
    for r in resources:
        entry = {
            'resource': r.to_dict()
        }
        if hasattr(r, 'id') and r.id:
            entry['fullUrl'] = f'urn:uuid:{r.id}'
        entries.append(entry)
    
    data = {
        'resourceType': 'Bundle',
        'type': bundle_type,
        'entry': entries,
    }
    
    if id_:
        data['id'] = id_
    
    return FHIRBundle(data)
