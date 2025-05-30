# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shlex
import subprocess
import sys

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

def _run_command_in_root(command_parts: 'strlist') -> 'str':
    script_dir: 'str' = os.path.dirname(os.path.abspath(__file__))
    project_root: 'str' = os.path.dirname(os.path.dirname(script_dir)) # ../../

    try:
        process: 'subprocess.CompletedProcess[str]' = subprocess.run(
            command_parts, capture_output=True, text=True, check=True, cwd=project_root
            )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f'Error running command: {' '.join(shlex.quote(str(arg)) for arg in command_parts)}', file=sys.stderr)
        if e.stdout:
            print(f'Stdout: {e.stdout}', file=sys.stderr)
        if e.stderr:
            print(f'Stderr: {e.stderr}', file=sys.stderr)
        raise

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """
    Main function to find modified/untracked Python files and run 'unify' on them.
    """
    git_command: 'strlist' = [
        'git', 'ls-files', '--modified', '--others', '--exclude-standard', '--', '*.py'
    ]

    try:
        files_to_process_str: 'str' = _run_command_in_root(git_command)
    except Exception:
        print('Failed to get list of files from git. Exiting.', file=sys.stderr)
        sys.exit(1)

    if not files_to_process_str:
        print('No Python files found to process.')
        sys.exit(0)

    files_to_process: 'strlist' = files_to_process_str.splitlines()

    processed_count: 'int' = 0
    failed_count: 'int' = 0

    for filename_relative_to_root in files_to_process:
        filename_relative_to_root = filename_relative_to_root.strip()
        if not filename_relative_to_root:
            continue

        unify_command: 'strlist' = [
            'unify',
            '-i',  # in-place
            '--quote',
            "'",   # The actual single quote character as the argument for --quote
            filename_relative_to_root
        ]

        print(f'Processing: {filename_relative_to_root}')
        try:
            _ = _run_command_in_root(unify_command)
            processed_count += 1
        except Exception:
            print(f'Failed to unify: {filename_relative_to_root}', file=sys.stderr)
            failed_count += 1

    print(f'Unify process complete. Processed: {processed_count}, Failed: {failed_count}.')
    if failed_count > 0:
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
