from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import RelatedArtifact


class TestRelatedArtifact:

    def test_create(self):
        obj = RelatedArtifact()
        assert obj is not None

    def test_to_dict(self):
        obj = RelatedArtifact()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = RelatedArtifact()
        j = obj.to_json()
        assert isinstance(j, str)
