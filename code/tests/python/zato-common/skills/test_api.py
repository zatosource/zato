# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import TemporaryDirectory
from unittest import main, TestCase

# Zato
from zato.common.skills.api import example_skill_contents, get_skill_name_list, load_skill, parse_skill_document, \
    skill_file_name, skills_directory_name

# ################################################################################################################################
# ################################################################################################################################

_invoice_skill = """---
name: invoice-mapping
description: How invoices map between systems
---

# Invoice mapping

Map the invoice number to the reference field.
"""

# ################################################################################################################################
# ################################################################################################################################

def _write_skill(repo_location:'str', name:'str', contents:'str') -> 'None':
    """ Puts one skill on disk the way the Skills screen lays it out - a directory
    of the skill's name with a SKILL.md file in it.
    """
    skill_directory = os.path.join(repo_location, skills_directory_name, name)
    os.makedirs(skill_directory)

    skill_path = os.path.join(skill_directory, skill_file_name)

    with open(skill_path, 'w') as skill_file:
        _ = skill_file.write(contents)

# ################################################################################################################################
# ################################################################################################################################

class ParseSkillDocument(TestCase):

    def test_frontmatter_and_instructions(self) -> 'None':
        """ The frontmatter carries the name and description, everything after it is the instructions.
        """
        document = parse_skill_document(_invoice_skill)

        self.assertEqual(document.name, 'invoice-mapping')
        self.assertEqual(document.description, 'How invoices map between systems')
        self.assertTrue(document.instructions.startswith('# Invoice mapping'))
        self.assertIn('Map the invoice number', document.instructions)

    def test_example_skill_parses(self) -> 'None':
        """ The starter skill every new environment comes with parses into a full document.
        """
        document = parse_skill_document(example_skill_contents)

        self.assertEqual(document.name, 'example')
        self.assertTrue(document.description)
        self.assertIn('# Example skill', document.instructions)

    def test_document_without_frontmatter(self) -> 'None':
        """ A document with no frontmatter at all is all instructions.
        """
        document = parse_skill_document('# Just markdown\n\nNo frontmatter here.')

        self.assertEqual(document.name, '')
        self.assertEqual(document.description, '')
        self.assertEqual(document.instructions, '# Just markdown\n\nNo frontmatter here.')

# ################################################################################################################################
# ################################################################################################################################

class GetSkillNameList(TestCase):

    def test_missing_directory_is_empty(self) -> 'None':
        """ A server without a skills directory has no skills.
        """
        with TemporaryDirectory() as repo_location:
            name_list = get_skill_name_list(repo_location)
            self.assertEqual(name_list, [])

    def test_lists_only_directories_with_skill_files(self) -> 'None':
        """ Only subdirectories holding a SKILL.md file are skills, sorted by name.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'zulu', _invoice_skill)
            _write_skill(repo_location, 'alpha', _invoice_skill)

            # A directory without a SKILL.md file is not a skill
            empty_directory = os.path.join(repo_location, skills_directory_name, 'not-a-skill')
            os.makedirs(empty_directory)

            name_list = get_skill_name_list(repo_location)
            self.assertEqual(name_list, ['alpha', 'zulu'])

# ################################################################################################################################
# ################################################################################################################################

class LoadSkill(TestCase):

    def test_loads_from_disk(self) -> 'None':
        """ A skill is read from disk by its directory name.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping', _invoice_skill)

            document = load_skill(repo_location, 'invoice-mapping')

            assert document is not None
            self.assertEqual(document.name, 'invoice-mapping')
            self.assertIn('Map the invoice number', document.instructions)

    def test_missing_skill_is_none(self) -> 'None':
        """ A name without a skill returns None.
        """
        with TemporaryDirectory() as repo_location:
            document = load_skill(repo_location, 'no-such-skill')
            self.assertIsNone(document)

    def test_path_traversal_is_none(self) -> 'None':
        """ A name reaching outside the skills directory returns None instead of following the path.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping', _invoice_skill)

            traversal_document = load_skill(repo_location, '../skills/invoice-mapping')
            self.assertIsNone(traversal_document)

            nested_document = load_skill(repo_location, 'a/b')
            self.assertIsNone(nested_document)

    def test_save_is_what_the_next_call_gets(self) -> 'None':
        """ There is no cache - a file changed on disk is what the next call reads.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping', _invoice_skill)

            changed = _invoice_skill.replace('Map the invoice number', 'Map the order number')
            skill_path = os.path.join(repo_location, skills_directory_name, 'invoice-mapping', skill_file_name)

            with open(skill_path, 'w') as skill_file:
                _ = skill_file.write(changed)

            document = load_skill(repo_location, 'invoice-mapping')

            assert document is not None
            self.assertIn('Map the order number', document.instructions)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
