# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The dynamic, dot-accessed message builder - the channel-free core that both JSON
payloads and the XML message tree build upon.

Its whole contract:

1. Dot access creates and reads child elements, auto-vivifying: message.foo.bar.baz = value
2. Assignment order is preserved
3. Assigning a list means repeated elements, for scalars and message nodes alike
4. Reading gives the same shape back
5. Nodes that were vivified by reads alone carry no content and are pruned at serialization time

Subclasses vivify children of their own type, so a tree built through a subclass
consists of that subclass throughout.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class Message:
    """ A dynamic, dot-accessed message node - a tree of named children built through plain attribute access.
    """

    def __init__(self) -> 'None':
        object.__setattr__(self, '_children', {})

# ################################################################################################################################

    def __setattr__(self, name:'str', value:'any_') -> 'None':

        # Every name is a child element - a dict preserves the order of first assignment,
        # which is what keeps the output in the order the fields were assigned in.
        self._children[name] = value

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':

        # This method only runs when normal lookup failed, so internal fields are never seen here -
        # underscore names are protocol probes (deepcopy, pickle, pytest) and must fail normally.
        if name.startswith('_'):
            raise AttributeError(name)

        # Auto-vivify - reading a child that does not exist yet creates an empty node
        # of our own type, which is what lets message.foo.bar.baz = value build the whole
        # path in one go. Nodes that never receive any content are pruned at serialization time.
        if name in self._children:
            out = self._children[name]
        else:
            out = type(self)()
            self._children[name] = out

        return out

# ################################################################################################################################

    def __bool__(self) -> 'bool':
        out = has_content(self)
        return out

# ################################################################################################################################

    def __len__(self) -> 'int':

        # Only children that actually carry content count - nodes vivified
        # by reads alone are as good as absent.
        out = 0

        for value in self._children.values():
            if _value_has_content(value):
                out += 1

        return out

# ################################################################################################################################

    def __repr__(self) -> 'str':
        child_names = list(self._children)
        out = f'<{type(self).__name__} children={child_names}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

def has_content(message:'Message') -> 'bool':
    """ Returns True if a node carries anything worth serializing - at least one child
    with content. Nodes vivified by reads alone have none.
    """
    for value in message._children.values():
        if _value_has_content(value):
            return True

    return False

# ################################################################################################################################

def _value_has_content(value:'any_') -> 'bool':
    """ Returns True if a child value carries content - scalars always do because
    only an assignment can have put them there, nodes are checked recursively.
    """
    if isinstance(value, Message):
        out = has_content(value)
    elif isinstance(value, list):
        out = False
        for item in value:
            if _value_has_content(item):
                out = True
                break
    else:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################
