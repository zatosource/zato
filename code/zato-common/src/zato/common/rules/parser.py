# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################

def parse_rules_file(file_path: str) -> 'strdict':
    with open(file_path, 'r') as f:
        content = f.read()

    return parse_rules_content(content)

# ################################################################################################################################

def parse_rules_content(content: str) -> 'strdict':

    rules_dict = {}

    # Regular expression to find rule blocks
    rule_pattern = r'\[(rule_[^\]]+)\](.*?)(?=\[rule_|\Z)'
    rule_matches = re.findall(rule_pattern, content, re.DOTALL)

    for rule_name, rule_content in rule_matches:
        rule_dict = {}

        # First find all section headers (docs, when, then)
        section_headers = re.finditer(r'\b(rule|docs|when|then)\b', rule_content)
        section_positions = [(m.group(1), m.start()) for m in section_headers]

        # Add the end position of the rule content
        section_positions.append(('end', len(rule_content)))

        # Process each section
        for idx in range(len(section_positions) - 1):
            section_name = section_positions[idx][0]
            start_pos = section_positions[idx][1] + len(section_name)  # Skip the section name
            end_pos = section_positions[idx + 1][1]

            # Extract the section content
            section_content = rule_content[start_pos:end_pos].strip()

            # Remove comments
            cleaned_section = remove_comments(section_content)

            # Add to rule dictionary
            rule_dict[section_name] = cleaned_section

        # Add the rule to the rules dictionary
        rules_dict[rule_name] = rule_dict

    return rules_dict

# ################################################################################################################################

def remove_comments(text: str) -> str:

    lines = []

    for line in text.split('\n'):
        line = re.sub(r'#.*$', '', line)
        lines.append(line)

    cleaned_text = '\n'.join(lines).strip()

    return cleaned_text

# ################################################################################################################################
# ################################################################################################################################

if __name__ == "__main__":

    # stdlib
    import json
    import sys

    file_name = sys.argv[1]
    rules = parse_rules_file(file_name)

    print(json.dumps(rules, indent=2))

# ################################################################################################################################
# ################################################################################################################################
