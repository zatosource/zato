from __future__ import annotations

import json
from pathlib import Path

import pytest
import zato.fhir.r4_0_1 as r4

_SPEC_DIR = Path(__file__).resolve().parent / 'examples' / 'spec'


def _json_paths():
    return sorted(_SPEC_DIR.glob('*.json'))


@pytest.mark.parametrize('path', _json_paths(), ids=lambda p: p.name)
def test_spec_example_roundtrip(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    resource_type = data.get('resourceType')
    if resource_type is None:
        pytest.skip('missing resourceType')
    cls = getattr(r4, resource_type, None)
    if cls is None:
        pytest.skip('unsupported resourceType')
    if not isinstance(cls, type):
        pytest.skip('unsupported resourceType')
    obj = cls.from_dict(data)
    out = obj.to_dict()
    assert out.get('resourceType') == resource_type
