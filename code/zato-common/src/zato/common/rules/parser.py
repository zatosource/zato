# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# rule-engine
import rule_engine

# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################

def parse_rules_file(file_path: str) -> 'strdict':
    with open(file_path, 'r') as f:
        content = f.read()

    return parse_rules_content(content)

# ################################################################################################################################

def parse_rule_assignments(text:'str') -> 'strdict':

    # Remove multi-line comments (both """ and ''')
    text = re.sub(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')', '', text, flags=re.DOTALL)

    # Split the text into lines and strip whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Dictionary to store parsed assignments
    parsed = {}

    for line in lines:
        # Remove inline comments
        line = line.split('#')[0].strip()

        # Split on first '=' to separate key and value
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Handle comma-separated values
            if ',' in value:
                # Check if it's a dictionary first
                try:
                    # Attempt to parse the entire value as a dictionary
                    parsed_dict = ast.literal_eval(value)
                    if isinstance(parsed_dict, dict):
                        parsed[key] = parsed_dict
                        continue
                except (SyntaxError, ValueError):
                    # If not a dictionary, proceed with previous comma-handling logic
                    parts = re.findall(r"('[^']*'|[^,]+)", value)

                    # Process each part
                    parsed_values = []
                    for part in parts:
                        part = part.strip()

                        # If part is a quoted string, keep it as is
                        if part.startswith("'") and part.endswith("'"):
                            parsed_values.append(part[1:-1])
                        # If part is not a quoted string, wrap in {}
                        else:
                            parsed_values.append(f'{{{part}}}')

                    parsed[key] = parsed_values
            else:
                # Single value case
                try:
                    parsed[key] = ast.literal_eval(value)
                except (SyntaxError, ValueError):
                    parsed[key] = value

    return parsed

# ################################################################################################################################

def parse_rules_content(content: str) -> 'strdict':

    rules_dict = {}

    # Regular expression to find rule blocks
    rule_pattern = r'\[(rule_[^\]]+)\](.*?)(?=\[rule_|\Z)'
    rule_matches = re.findall(rule_pattern, content, re.DOTALL)

    for rule_name, rule_content in rule_matches:
        rule_dict = {}

        # First find all section headers (docs, when, then)
        section_headers = re.finditer(r'\b(rule|docs|when|then|defaults)\b', rule_content)
        section_positions = [(m.group(1), m.start()) for m in section_headers]

        # Add the end position of the rule content
        section_positions.append(('end', len(rule_content)))

        # Process each section ..
        for idx in range(len(section_positions) - 1):
            section_name = section_positions[idx][0]
            start_pos = section_positions[idx][1] + len(section_name)  # Skip the section name
            end_pos = section_positions[idx + 1][1]

            # .. extract the section content ..
            section_content = rule_content[start_pos:end_pos].strip()

            # .. remove comments ..
            cleaned_section = remove_comments(section_content)

            # .. post process the sections ..
            if section_name == 'when':
                cleaned_section = ' and '.join(elem.strip() for elem in cleaned_section.splitlines())
                cleaned_section = cleaned_section.replace('and and', 'and')

            elif section_name in {'defaults', 'then'}:
                cleaned_section = parse_rule_assignments(cleaned_section)

            # .. add it to rule dictionary ..
            rule_dict[section_name] = cleaned_section

        # .. add the rule to the rules dictionary ..
        rules_dict[rule_name] = rule_dict

    # .. and return everything to our caller.
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

    demo = rules['rule_4']
    request = {'abc':123}

    rule = rule_engine.Rule(demo['when'])
    result = rule.matches(request)

    print(111, json.dumps(demo, indent=2))
    print(222, result)
    print(333, demo['then'])

# ################################################################################################################################
# ################################################################################################################################
