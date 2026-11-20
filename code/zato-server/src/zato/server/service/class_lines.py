# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import linecache
from ast import NodeVisitor, parse
from inspect import getmodule, getsourcefile

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ast import AsyncFunctionDef, ClassDef, FunctionDef
    from zato.common.typing_ import any_, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class _ClassLineVisitor(NodeVisitor):
    """ Collects the zero-based line number of each class of a module under its qualified name,
    by the rules of inspect.findsource.
    """

    def __init__(self) -> 'None':
        self.stack:'strlist' = []
        self.lines:'strintdict' = {}

    def visit_FunctionDef(self, node:'FunctionDef | AsyncFunctionDef') -> 'None':

        # A class defined in a function is qualified with the name of the function and with <locals> ..
        self.stack.append(node.name)
        self.stack.append('<locals>')

        # .. which applies to every class in its body.
        self.generic_visit(node)

        _ = self.stack.pop()
        _ = self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node:'ClassDef') -> 'None':
        self.stack.append(node.name)
        qualname = '.'.join(self.stack)

        # The first definition under a qualified name is the one that inspect.findsource returns ..
        if qualname not in self.lines:

            # .. and a decorated class begins on the line of its first decorator.
            if node.decorator_list:
                line_number = node.decorator_list[0].lineno
            else:
                line_number = node.lineno

            self.lines[qualname] = line_number - 1

        self.generic_visit(node)
        _ = self.stack.pop()

# ################################################################################################################################
# ################################################################################################################################

class ClassLines:
    """ Returns the line numbers of classes, parsing each source file once for all the classes it defines.
    """

    def __init__(self) -> 'None':
        self.file_name = ''
        self.source = ''
        self.lines:'strintdict' = {}

    def get_line_number(self, class_:'any_') -> 'int':
        """ Returns the zero-based line number of the definition of a class, as inspect.findsource does.
        """

        # The source is read the way inspect.findsource reads it ..
        file_name = getsourcefile(class_)
        if not file_name:
            raise OSError(f'Source file not found for {class_}')

        linecache.checkcache(file_name)
        module = getmodule(class_, file_name)

        if module:
            lines = linecache.getlines(file_name, module.__dict__)
        else:
            lines = linecache.getlines(file_name)

        if not lines:
            raise OSError(f'Source not available for {class_} in {file_name}')

        source = ''.join(lines)

        # .. a file is parsed again only when it is a different one or when its source has changed ..
        if file_name != self.file_name or source != self.source:
            visitor = _ClassLineVisitor()
            visitor.visit(parse(source))

            self.file_name = file_name
            self.source = source
            self.lines = visitor.lines

        # .. and a class that is not found in the source is reported as inspect.findsource reports it.
        qualname = class_.__qualname__
        if qualname not in self.lines:
            raise OSError(f'Class definition not found for {qualname} in {file_name}')

        out = self.lines[qualname]
        return out

# ################################################################################################################################
# ################################################################################################################################
