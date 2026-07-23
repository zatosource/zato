# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from pathlib import Path

# Zato
from zato.common.rules.parser import parse_data_details
from zato.common.rules.render import render_document, render_documents

# ################################################################################################################################
# ################################################################################################################################

path_list = list[Path]

# ################################################################################################################################
# ################################################################################################################################

class TestRoundTrip(unittest.TestCase):
    """ The round-trip law - parse(render(document)) == document and rendering is idempotent.
    """

    def _get_fixture_files(self) -> 'path_list':
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        zrules_dir = current_dir / 'zrules'

        out = []
        for item in sorted(zrules_dir.rglob('*.zrules')):
            out.append(item)

        return out

# ################################################################################################################################

    def test_round_trip_all_fixtures(self) -> 'None':
        """ Every document from every fixture file survives render and reparse unchanged.
        """
        fixture_files = self._get_fixture_files()
        self.assertTrue(fixture_files, 'No fixture files found')

        checked = 0

        for path in fixture_files:
            container_name = path.stem

            # Parse the original text ..
            text = path.read_text()
            documents, errors = parse_data_details(text, container_name)
            self.assertListEqual(errors, [], f'Parse errors in {path}')

            for full_name, document in documents.items():

                # .. render each document back to text ..
                rendered = render_document(document)

                # .. reparse the rendered text ..
                reparsed_documents, reparse_errors = parse_data_details(rendered, container_name)
                self.assertListEqual(reparse_errors, [], f'Reparse errors for {full_name} in {path}')

                # .. and the reparsed document has to be identical.
                reparsed = reparsed_documents[full_name]
                self.assertDictEqual(reparsed, document, f'Round trip mismatch for {full_name} in {path}')

                checked += 1

        self.assertTrue(checked > 0, 'No documents were checked')

# ################################################################################################################################

    def test_render_is_idempotent(self) -> 'None':
        """ Rendering a reparsed document produces the same text again.
        """
        fixture_files = self._get_fixture_files()

        for path in fixture_files:

            # Perf fixtures are numerous and structurally identical, the plain ones suffice here.
            if path.name.startswith('perf_'):
                continue

            container_name = path.stem
            text = path.read_text()

            # The first render establishes the canonical text ..
            documents, _ = parse_data_details(text, container_name)
            canonical = render_documents(documents)

            # .. and rendering what that text parses into changes nothing.
            reparsed_documents, _ = parse_data_details(canonical, container_name)
            rendered_again = render_documents(reparsed_documents)

            self.assertEqual(rendered_again, canonical, f'Rendering is not idempotent for {path}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
