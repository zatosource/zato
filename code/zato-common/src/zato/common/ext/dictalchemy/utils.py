# vim: set fileencoding=utf-8 :
# flake8: noqa
"""
~~~~~~~~~
Utilities
~~~~~~~~~
"""
from __future__ import absolute_import, division

import copy
from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import _AssociationList

from sqlalchemy.orm.dynamic import AppenderMixin
from sqlalchemy.orm.query import Query

from zato.common.ext.dictalchemy import constants
from zato.common.ext.dictalchemy import errors


def arg_to_dict(arg):
    """Convert an argument that can be None, list/tuple or dict to dict

    Example::

        >>> arg_to_dict(None)
        []
        >>> arg_to_dict(['a', 'b'])
        {'a':{},'b':{}}
        >>> arg_to_dict({'a':{'only': 'id'}, 'b':{'only': 'id'}})
        {'a':{'only':'id'},'b':{'only':'id'}}

    :return: dict with keys and dict arguments as value
    """
    if arg is None:
        arg = []
    try:
        arg = dict(arg)
    except ValueError:
        arg = dict.fromkeys(list(arg), {})

    return arg


def asdict(model, exclude=None, exclude_underscore=None, exclude_pk=None,
           follow=None, include=None, only=None, method='asdict', **kwargs):
    """Get a dict from a model

    Using the `method` parameter makes it possible to have multiple methods
    that formats the result.

    Additional keyword arguments will be passed to all relationships that are
    followed. This can be used to pass on things like request or context.

    :param follow: List or dict of relationships that should be followed.
            If the parameter is a dict the value should be a dict of \
            keyword arguments. Currently it follows InstrumentedList, \
            MappedCollection and regular 1:1, 1:m, m:m relationships. Follow \
            takes an extra argument, 'method', which is the method that \
            should be used on the relation. It also takes the extra argument \
            'parent' which determines where the relationships data should be \
            added in the response dict. If 'parent' is set the relationship \
            will be added with it's own key as a child to `parent`.
    :param exclude: List of properties that should be excluded, will be \
            merged with `model.dictalchemy_exclude`
    :param exclude_pk: If True any column that refers to the primary key will \
            be excluded.
    :param exclude_underscore: Overides `model.dictalchemy_exclude_underscore`\
            if set
    :param include: List of properties that should be included. Use this to \
            allow python properties to be called. This list will be merged \
            with `model.dictalchemy_asdict_include` or \
            `model.dictalchemy_include`.
    :param only: List of properties that should be included. This will \
            override everything else except `follow`.
    :param method: Name of the method that is currently called. This will be \
            the default method used in 'follow' unless another method is\
            set.

    :raises: :class:`dictalchemy.errors.MissingRelationError` \
            if `follow` contains a non-existent relationship.
    :raises: :class:`dictalchemy.errors.UnsupportedRelationError` If `follow` \
            contains an existing relationship that currently isn't supported.

    :returns: dict

    """

    follow = arg_to_dict(follow)

    info = inspect(model)

    columns = [c.key for c in info.mapper.column_attrs]
    synonyms = [c.key for c in info.mapper.synonyms]

    if only:
        attrs = only
    else:
        exclude = exclude or []
        exclude += getattr(model, 'dictalchemy_exclude',
                           constants.default_exclude) or []
        if exclude_underscore is None:
            exclude_underscore = getattr(model,
                                         'dictalchemy_exclude_underscore',
                                         constants.default_exclude_underscore)
        if exclude_underscore:
            # Exclude all properties starting with underscore
            exclude += [k.key for k in info.mapper.attrs if k.key[0] == '_']
        if exclude_pk is True:
            exclude += [c.key for c in info.mapper.primary_key]

        include = (include or []) + (getattr(model,
                                             'dictalchemy_asdict_include',
                                             getattr(model,
                                                     'dictalchemy_include',
                                                     None)) or [])
        attrs = [k for k in columns + synonyms + include if k not in exclude]

    data = dict([(k, getattr(model, k)) for k in attrs])

    for (rel_key, orig_args) in follow.items():

        try:
            rel = getattr(model, rel_key)
        except AttributeError:
            raise errors.MissingRelationError(rel_key)

        args = copy.deepcopy(orig_args)
        method = args.pop('method', method)
        args['method'] = method
        args.update(copy.copy(kwargs))

        if hasattr(rel, method):
            rel_data = getattr(rel, method)(**args)
        elif isinstance(rel, (list, _AssociationList)):
            rel_data = []

            for child in rel:
                if hasattr(child, method):
                    rel_data.append(getattr(child, method)(**args))
                else:
                    try:
                        rel_data.append(dict(child))
                        # TypeError is for non-dictable children
                    except TypeError:
                        rel_data.append(copy.copy(child))

        elif isinstance(rel, dict):
            rel_data = {}

            for (child_key, child) in rel.items():
                if hasattr(child, method):
                    rel_data[child_key] = getattr(child, method)(**args)
                else:
                    try:
                        rel_data[child_key] = dict(child)
                    except ValueError:
                        rel_data[child_key] = copy.copy(child)

        elif isinstance(rel, (AppenderMixin, Query)):
            rel_data = []

            for child in rel.all():
                if hasattr(child, method):
                    rel_data.append(getattr(child, method)(**args))
                else:
                    rel_data.append(dict(child))

        elif rel is None:
            rel_data = None
        else:
            raise errors.UnsupportedRelationError(rel_key)

        ins_key = args.pop('parent', None)

        if ins_key is None:
            data[rel_key] = rel_data
        else:
            if ins_key not in data:
                data[ins_key] = {}

            data[ins_key][rel_key] = rel_data

    return data


def fromdict(model, data, exclude=None, exclude_underscore=None,
             allow_pk=None, follow=None, include=None, only=None):
    """Update a model from a dict

    Works almost identically as :meth:`dictalchemy.utils.asdict`. However, it
    will not create missing instances or update collections.

    This method updates the following properties on a model:

    * Simple columns
    * Synonyms
    * Simple 1-m relationships

    :param data: dict of data
    :param exclude: list of properties that should be excluded
    :param exclude_underscore: If True underscore properties will be excluded,\
            if set to None model.dictalchemy_exclude_underscore will be used.
    :param allow_pk: If True any column that refers to the primary key will \
            be excluded. Defaults model.dictalchemy_fromdict_allow_pk or \
            dictable.constants.fromdict_allow_pk. If set to True a primary \
            key can still be excluded with the `exclude` parameter.
    :param follow: Dict of relations that should be followed, the key is the \
            arguments passed to the relation. Relations only works on simple \
            relations, not on lists.
    :param include: List of properties that should be included. This list \
            will override anything in the exclude list. It will not override \
            allow_pk.
    :param only: List of the only properties that should be set. This \
            will not override `allow_pk` or `follow`.

    :raises: :class:`dictalchemy.errors.DictalchemyError` If a primary key is \
            in data and allow_pk is False

    :returns: The model

    """

    follow = arg_to_dict(follow)

    info = inspect(model)
    columns = [c.key for c in info.mapper.column_attrs]
    synonyms = [c.key for c in info.mapper.synonyms]
    relations = [c.key for c in info.mapper.relationships]
    primary_keys = [c.key for c in info.mapper.primary_key]

    if allow_pk is None:
        allow_pk = getattr(model, 'dictalchemy_fromdict_allow_pk',
                           constants.default_fromdict_allow_pk)

    if only:
        valid_keys = only
    else:
        exclude = exclude or []
        exclude += getattr(model, 'dictalchemy_exclude',
                           constants.default_exclude) or []
        if exclude_underscore is None:
            exclude_underscore = getattr(model,
                                         'dictalchemy_exclude_underscore',
                                         constants.default_exclude_underscore)

        if exclude_underscore:
            # Exclude all properties starting with underscore
            exclude += [k.key for k in info.mapper.attrs if k.key[0] == '_']

        include = (include or []) + (getattr(model,
                                             'dictalchemy_fromdict_include',
                                             getattr(model,
                                                     'dictalchemy_include',
                                                     None)) or [])
        valid_keys = [k for k in columns + synonyms
                      if k not in exclude] + include

    # Keys that will be updated
    update_keys = set(valid_keys) & set(data.keys())

    # Check for primary keys
    data_primary_key= update_keys & set(primary_keys)
    if len(data_primary_key) and not allow_pk:
        msg = ("Primary keys({0}) cannot be updated by fromdict."
               "Set 'dictalchemy_fromdict_allow_pk' to True in your Model"
               " or pass 'allow_pk=True'.").format(','.join(data_primary_key))
        raise errors.DictalchemyError(msg)

    # Update columns and synonyms
    for k in update_keys:
        setattr(model, k, data[k])

    # Update simple relations
    for (k, args) in follow.items():
        if k not in data:
            continue
        if k not in relations:
            raise errors.MissingRelationError(k)
        rel = getattr(model, k)
        if hasattr(rel, 'fromdict'):
            rel.fromdict(data[k], **args)

    return model


def iter(model):
    """iter method for models

    Yields everything returned by `asdict`.
    """
    for i in model.asdict().items():
        yield i


def make_class_dictable(
        cls,
        exclude=constants.default_exclude,
        exclude_underscore=constants.default_exclude_underscore,
        fromdict_allow_pk=constants.default_fromdict_allow_pk,
        include=None,
        asdict_include=None,
        fromdict_include=None):
    """Make a class dictable

    Useful for when the Base class is already defined, for example when using
    Flask-SQLAlchemy.

    Warning: This method will overwrite existing attributes if they exists.

    :param exclude: Will be set as dictalchemy_exclude on the class
    :param exclude_underscore: Will be set as dictalchemy_exclude_underscore \
            on the class
    :param fromdict_allow_pk: Will be set as dictalchemy_fromdict_allow_pk\
            on the class
    :param include: Will be set as dictalchemy_include on the class.
    :param asdict_include: Will be set as `dictalchemy_asdict_include` on the \
            class. If not None it will override `dictalchemy_include`.
    :param fromdict_include: Will be set as `dictalchemy_fromdict_include` on \
            the class. If not None it will override `dictalchemy_include`.

    :returns: The class
    """

    setattr(cls, 'dictalchemy_exclude', exclude)
    setattr(cls, 'dictalchemy_exclude_underscore', exclude_underscore)
    setattr(cls, 'dictalchemy_fromdict_allow_pk', fromdict_allow_pk)
    setattr(cls, 'asdict', asdict)
    setattr(cls, 'fromdict', fromdict)
    setattr(cls, '__iter__', iter)
    setattr(cls, 'dictalchemy_include', include)
    setattr(cls, 'dictalchemy_asdict_include', asdict_include)
    setattr(cls, 'dictalchemy_fromdict_include', fromdict_include)
    return cls
