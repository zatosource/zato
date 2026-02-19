# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import logging
import os
import sys
from pathlib import Path

# Zato
from zato.common.api import IDE_Ignore_Modules

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class StubGenerator:
    """ Generates .pyi stub files for Zato modules.
    """

    def __init__(self, source_dirs:'list[str]', stubs_dir:'Path') -> 'None':
        self.source_dirs = source_dirs
        self.stubs_dir = stubs_dir
        self.generated_count = 0
        self.skipped_count = 0
        self.error_count = 0

# ################################################################################################################################

    def run(self) -> 'None':
        """ Main entry point - generates stubs for all source directories.
        """
        for source_dir in self.source_dirs:
            self._process_directory(source_dir)

        logger.info(f'Stub generation complete: {self.generated_count} generated, {self.skipped_count} skipped, {self.error_count} errors')

# ################################################################################################################################

    def _process_directory(self, source_dir:'str') -> 'None':
        """ Processes a single source directory recursively.
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f'Source directory does not exist: {source_dir}')
            return

        for py_file in source_path.rglob('*.py'):
            self._process_file(py_file, source_path)

# ################################################################################################################################

    def _process_file(self, py_file:'Path', source_dir:'Path') -> 'None':
        """ Processes a single Python file and generates its stub.
        """
        # .. compute relative path from source dir and create stub path ..
        rel_path = py_file.relative_to(source_dir.parent)
        pyi_file = self.stubs_dir / rel_path.with_suffix('.pyi')

        # .. ensure parent directory exists ..
        pyi_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            stub_content = self._generate_stub(py_file)
            if stub_content:
                with open(pyi_file, 'w', encoding='utf-8') as f:
                    _ = f.write(stub_content)
                self.generated_count += 1
                logger.info(f'Generated stub: {pyi_file}')
            else:
                self.skipped_count += 1

        except SyntaxError as e:
            logger.warning(f'Syntax error in {py_file}: {e}')
            self.error_count += 1

        except Exception as e:
            logger.warning(f'Error processing {py_file}: {e}')
            self.error_count += 1

# ################################################################################################################################

    def _generate_stub(self, py_file:'Path') -> 'str':
        """ Generates stub content for a single Python file.
        """
        with open(py_file, 'r', encoding='utf-8') as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise SyntaxError(f'Line {e.lineno}: {e.msg}') from e

        out = []
        out.append('from typing import Any')
        out.append('')

        # .. collect imports including those inside if 0: blocks ..
        self._collect_imports(tree, out)

        out.append('')

        # .. collect class and function definitions ..
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_stub = self._generate_class_stub(node)
                out.append(class_stub)
                out.append('')

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_stub = self._generate_function_stub(node)
                out.append(func_stub)
                out.append('')

        return '\n'.join(out)

# ################################################################################################################################

    def _collect_imports(self, tree:'ast.Module', out:'list[str]') -> 'None':
        """ Collects imports from the AST tree, including those inside if 0: blocks.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # .. skip ignored modules ..
                    should_skip = False
                    for ignore_module in IDE_Ignore_Modules:
                        if ignore_module in alias.name:
                            should_skip = True
                            break
                    if should_skip:
                        continue
                    import_line = f'import {alias.name}' + (f' as {alias.asname}' if alias.asname else '')
                    if import_line not in out:
                        out.append(import_line)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # .. skip ignored modules ..
                    should_skip = False
                    for ignore_module in IDE_Ignore_Modules:
                        if ignore_module in node.module:
                            should_skip = True
                            break
                    if should_skip:
                        continue
                    names = ', '.join(
                        (f'{alias.name} as {alias.asname}' if alias.asname else alias.name)
                        for alias in node.names
                    )
                    import_line = f'from {node.module} import {names}'
                    if import_line not in out:
                        out.append(import_line)

# ################################################################################################################################

    def _generate_class_stub(self, node:'ast.ClassDef') -> 'str':
        """ Generates stub for a class definition.
        """
        lines = []

        # .. class declaration with bases ..
        bases = ', '.join(self._get_name(base) for base in node.bases)
        if bases:
            lines.append(f'class {node.name}({bases}):')
        else:
            lines.append(f'class {node.name}:')

        has_content = False

        # .. class attributes ..
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                annotation = self._get_annotation(item.annotation)
                lines.append(f'    {item.target.id}: {annotation}')
                has_content = True

            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        lines.append(f'    {target.id}: Any')
                        has_content = True

        # .. methods ..
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_stub = self._generate_function_stub(item, indent=4)
                lines.append(method_stub)
                has_content = True

        if not has_content:
            lines.append('    ...')

        return '\n'.join(lines)

# ################################################################################################################################

    def _generate_function_stub(self, node:'ast.FunctionDef | ast.AsyncFunctionDef', indent:'int'=0) -> 'str':
        """ Generates stub for a function or method definition.
        """
        prefix = ' ' * indent
        async_prefix = 'async ' if isinstance(node, ast.AsyncFunctionDef) else ''

        # .. build parameters ..
        params = []
        defaults_offset = len(node.args.args) - len(node.args.defaults)

        for idx, arg in enumerate(node.args.args):
            annotation = self._get_annotation(arg.annotation) if arg.annotation else 'Any'
            param = f'{arg.arg}: {annotation}'

            # .. add default value ..
            default_idx = idx - defaults_offset
            if default_idx >= 0:
                param += ' = ...'

            params.append(param)

        # .. handle *args ..
        if node.args.vararg:
            annotation = self._get_annotation(node.args.vararg.annotation) if node.args.vararg.annotation else 'Any'
            params.append(f'*{node.args.vararg.arg}: {annotation}')

        # .. handle **kwargs ..
        if node.args.kwarg:
            annotation = self._get_annotation(node.args.kwarg.annotation) if node.args.kwarg.annotation else 'Any'
            params.append(f'**{node.args.kwarg.arg}: {annotation}')

        params_str = ', '.join(params)

        # .. return type ..
        returns = self._get_annotation(node.returns) if node.returns else 'None'

        # .. check for decorators ..
        decorators = []
        for decorator in node.decorator_list:
            dec_name = self._get_name(decorator)
            if dec_name in ('staticmethod', 'classmethod', 'property'):
                decorators.append(f'{prefix}@{dec_name}')

        out = '\n'.join(decorators)
        if out:
            out += '\n'
        out += f'{prefix}{async_prefix}def {node.name}({params_str}) -> {returns}: ...'

        return out

# ################################################################################################################################

    def _get_annotation(self, node:'ast.expr | None') -> 'str':
        """ Extracts annotation string from an AST node.
        """
        if node is None:
            return 'Any'

        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                # .. check if the string annotation references an ignored module ..
                for ignore_module in IDE_Ignore_Modules:
                    if ignore_module in node.value.lower():
                        return 'Any'
                return node.value
            return str(node.value)

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            name = self._get_name(node)
            # .. check if the attribute references an ignored module ..
            for ignore_module in IDE_Ignore_Modules:
                if ignore_module in name.lower():
                    return 'Any'
            return name

        if isinstance(node, ast.Subscript):
            value = self._get_name(node.value)
            slice_val = self._get_annotation(node.slice)
            return f'{value}[{slice_val}]'

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            left = self._get_annotation(node.left)
            right = self._get_annotation(node.right)
            return f'{left} | {right}'

        if isinstance(node, ast.Tuple):
            elts = ', '.join(self._get_annotation(elt) for elt in node.elts)
            return elts

        return 'Any'

# ################################################################################################################################

    def _get_name(self, node:'ast.expr') -> 'str':
        """ Extracts name from an AST node.
        """
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f'{value}.{node.attr}'

        if isinstance(node, ast.Call):
            return self._get_name(node.func)

        return 'Any'

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point.
    """
    base_dir = Path(__file__).parent.parent
    stubs_dir = base_dir / 'stubs'

    # .. find all zato-* directories with src/zato subdirectory ..
    source_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.startswith('zato-'):
            zato_src = item / 'src' / 'zato'
            if zato_src.exists():
                source_dirs.append(str(zato_src))

    logger.info(f'Found {len(source_dirs)} zato source directories')

    generator = StubGenerator(source_dirs, stubs_dir)
    generator.run()

# ################################################################################################################################

if __name__ == '__main__':
    main()
