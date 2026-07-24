# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Converts VS Code color theme files into our theme css files.
#
# Sources live in themes/sources/: each <slug>.json is a theme in the
# VS Code color theme format (JSONC, a colors map keyed by workbench color
# ids), and each sources/overrides/<slug>.json carries the theme's origin
# and license metadata plus optional pins of our tokens, applied last. Our
# own palette, Zato Default, is just another such source file - one kind
# of source for everything.
#
# For every theme the converter emits static/webapp/css/themes/<slug>.css
# with the full token set scoped by html[data-theme="<slug>"], plus
# static/webapp/js/themes-index.js (the list the settings panel shows) and
# templates/webapp/themes.html (the link tags base.html includes).
#
# Everything is resolved at conversion time: mapping chains first, then
# per-type defaults, then derived values (surface mixes and alpha tints),
# then the overrides. The pages never compute a color at runtime.
#
# Run as: python -m zato.common.webapp.ui.themes.convert

# stdlib
import argparse
import json
import os

# Zato
from zato.common.webapp.ui.themes.colors import composite, mix, parse_hex, to_hex
from zato.common.webapp.ui.themes.tokens import Defaults, Mapping, Min_Surface_Distance, Mixes, Shadows, \
    Surface_Wash_Ratio, Tints, Token_Order
from zato.common.webapp.ui.themes.jsonc import load_theme

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdictlist, strlist, strstrdict
    strdictlist = strdictlist
    strlist     = strlist
    strstrdict  = strstrdict

    from zato.common.webapp.ui.themes.colors import rgbtuple
    rgbtuple = rgbtuple

# ################################################################################################################################
# ################################################################################################################################

sortkey = tuple[bool, str]

# ################################################################################################################################
# ################################################################################################################################

def convert_one(theme_path:'str', overrides_dir:'str') -> 'strstrdict':

    base_name = os.path.basename(theme_path)
    slug = os.path.splitext(base_name)[0]
    theme = load_theme(theme_path)

    # Every theme carries an overrides file, even one pinning nothing:
    # that is where its origin and license are recorded.
    overrides_path = os.path.join(overrides_dir, slug + '.json')
    if not os.path.exists(overrides_path):
        message = f'{slug}: missing {overrides_path}, every theme needs an overrides file ' + \
            'with its origin and license metadata, even when it pins no tokens'
        raise SystemExit(message)

    with open(overrides_path) as file_object:
        overrides = json.load(file_object)

    meta = overrides['meta']
    for required in ('origin', 'license'):
        if required not in meta:
            raise SystemExit(f'{slug}: overrides meta lacks {required!r}')

    theme_type = theme['type']
    if theme_type is None:

        # Some sources, VS Code's own high contrast files among them,
        # carry no type at all: the overrides meta must say it then.
        theme_type = meta.get('type')

    if theme_type not in ('dark', 'light'):
        raise SystemExit(f'{slug}: theme type must be dark or light, got {theme_type!r}')

    theme_name = theme['name']
    if theme_name is None:

        # Some sources carry no name either, VS Code reads it from the
        # extension manifest then: the overrides meta must say it.
        theme_name = meta.get('name')

    if theme_name is None:
        raise SystemExit(f'{slug}: neither the theme file nor the overrides meta has a name')

    colors = theme['colors']
    type_defaults = Defaults[theme_type]

    # The background is resolved first: translucent colors anywhere else
    # are flattened over it, and it itself flattens over pure black or
    # pure white if a theme should ever make it translucent.
    base = (0, 0, 0) if theme_type == 'dark' else (255, 255, 255)

    def resolve(token:'str') -> 'rgbtuple':

        # The first key of the chain the theme defines wins ..
        for key in Mapping[token]:
            if key in colors:
                value = colors[key]
                break

        # .. and the per-type default catches themes defining none of them.
        else:
            value = type_defaults[token]

        red, green, blue, alpha = parse_hex(value, slug)

        # A translucent source color flattens over the base surface.
        if alpha < 1:
            out = composite((red, green, blue), alpha, base)
        else:
            out = (red, green, blue)

        return out

    # Resolve the mapped tokens, the background first as everything
    # translucent flattens over it ..
    resolved = {'--background': resolve('--background')}
    base = resolved['--background']

    for token in Mapping:
        if token not in resolved:
            resolved[token] = resolve(token)

    tokens = {}
    for token, rgb in resolved.items():
        tokens[token] = to_hex(rgb)

    # .. surfaces without a VS Code id come from mixes of resolved tokens ..
    for token, (from_token, to_token, ratio) in Mixes.items():
        mixed = mix(resolved[from_token], resolved[to_token], ratio)
        tokens[token] = to_hex(mixed)

    # .. the problems panel must always be a different color: themes that
    # paint their panels with the very background color (Gruvbox does)
    # make the mix land on the background itself, so it gets a wash of
    # the text color over the background instead ..
    problems_mix = Mixes['--problems-background']
    problems_ratio = problems_mix[2]
    background = resolved['--background']
    problems = mix(background, resolved['--panel'], problems_ratio)

    distance = 0
    for problems_channel, background_channel in zip(problems, background):
        distance += abs(problems_channel - background_channel)

    if distance < Min_Surface_Distance:
        washed = mix(background, resolved['--text'], Surface_Wash_Ratio)
        tokens['--problems-background'] = to_hex(washed)

    # .. the translucent washes, same alphas for every theme ..
    for token, (source, alpha) in Tints.items():
        red, green, blue = resolved[source]
        tokens[token] = f'rgba({red},{green},{blue},{alpha})'

    tokens.update(Shadows[theme_type])

    # .. and the overrides land last, the room for our own customizations
    # on top of any imported scheme.
    for token, value in overrides['tokens'].items():
        if token not in tokens:
            raise SystemExit(f'{slug}: overrides pin unknown token {token!r}')
        tokens[token] = value

    lines = [
        f'/* {theme_name} - generated by zato.common.webapp.ui.themes.convert, do not edit.',
        f'   Source: themes/sources/{slug}.json',
        f'   Origin: {meta["origin"]}',
        f'   License: {meta["license"]} */',
        f'html[data-theme="{slug}"]{{',
    ]
    for token in Token_Order:
        lines.append(f'  {token}:{tokens[token]};')
    lines.append('}')
    lines.append('')

    out = {'slug': slug, 'name': theme_name, 'type': theme_type, 'css': '\n'.join(lines)}
    return out

# ################################################################################################################################

def _theme_sort_key(theme:'strstrdict') -> 'sortkey':
    """ Zato Default leads the list, the rest stay alphabetical.
    """
    is_not_default = theme['slug'] != 'zato-default'

    out = (is_not_default, theme['name'])
    return out

# ################################################################################################################################

def _write_index(themes:'strdictlist', out_index:'str') -> 'None':
    """ The index the settings panel shows.
    """
    index_lines = [
        "'use strict';",
        '',
        '// Generated by zato.common.webapp.ui.themes.convert, do not edit.',
        'window.themesIndex = [',
    ]
    for theme in themes:
        index_lines.append(
            "    {{slug: '{slug}', name: '{name}', type: '{type}'}},".format(**theme))
    index_lines.append('];')
    index_lines.append('')

    with open(out_index, 'w') as file_object:
        _ = file_object.write('\n'.join(index_lines))
    print(f'wrote {out_index}')

# ################################################################################################################################

def _write_template(themes:'strdictlist', out_template:'str') -> 'None':
    """ The link tags webapp/base.html includes.
    """
    template_lines = ['{% load static %}{# Generated by zato.common.webapp.ui.themes.convert, do not edit. #}']
    for theme in themes:
        template_lines.append(
            '<link rel="stylesheet" href="{{% static \'webapp/css/themes/{slug}.css\' %}}">'.format(**theme))
    template_lines.append('')

    with open(out_template, 'w') as file_object:
        _ = file_object.write('\n'.join(template_lines))
    print(f'wrote {out_template}')

# ################################################################################################################################

def main() -> 'None':

    module_path = os.path.abspath(__file__)
    themes_package_dir = os.path.dirname(module_path)
    ui_dir = os.path.dirname(themes_package_dir)

    default_themes_dir = os.path.join(themes_package_dir, 'sources')
    default_css_dir    = os.path.join(ui_dir, 'static', 'webapp', 'css', 'themes')
    default_index      = os.path.join(ui_dir, 'static', 'webapp', 'js', 'themes-index.js')
    default_template   = os.path.join(ui_dir, 'templates', 'webapp', 'themes.html')

    parser = argparse.ArgumentParser(description='VS Code themes to our theme css')
    _ = parser.add_argument('--themes-dir', default=default_themes_dir)
    _ = parser.add_argument('--out-css-dir', default=default_css_dir)
    _ = parser.add_argument('--out-index', default=default_index)
    _ = parser.add_argument('--out-template', default=default_template)
    args = parser.parse_args()

    overrides_dir = os.path.join(args.themes_dir, 'overrides')

    # Collect the theme sources, one .json file per theme ..
    theme_files:'strlist' = []
    for entry in sorted(os.listdir(args.themes_dir)):
        if not entry.endswith('.json'):
            continue
        entry_path = os.path.join(args.themes_dir, entry)
        if os.path.isfile(entry_path):
            theme_files.append(entry)

    if not theme_files:
        raise SystemExit(f'no theme files in {args.themes_dir}')

    # .. convert everything first, so a broken theme stops the run before
    # any file is written ..
    themes:'strdictlist' = []
    for entry in theme_files:
        entry_path = os.path.join(args.themes_dir, entry)
        converted = convert_one(entry_path, overrides_dir)
        themes.append(converted)

    # .. Zato Default leads the list, the rest stay alphabetical ..
    themes.sort(key=_theme_sort_key)

    # .. one css file per theme ..
    os.makedirs(args.out_css_dir, exist_ok=True)
    for theme in themes:
        css_path = os.path.join(args.out_css_dir, theme['slug'] + '.css')
        with open(css_path, 'w') as file_object:
            _ = file_object.write(theme['css'])
        print(f'wrote {css_path}')

    # .. the index the settings panel shows ..
    _write_index(themes, args.out_index)

    # .. and the link tags base.html includes.
    _write_template(themes, args.out_template)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
