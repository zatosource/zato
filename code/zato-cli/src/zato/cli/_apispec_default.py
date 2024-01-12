# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# All APISpec-related files that will be created for each server
apispec_files = {}

# Custom CSS styles
apispec_files['_static/custom.css'] = """
* {
    font-size:0.99em;
}

body, html {
    background-color:#111 !important;
}

code {
    font-size:1.2em
}

div.body {
    max-width:900px !important
}

html {
    position: relative !important;
    min-height: 100% !important;
}

h1 {
    color:#67beff !important;
    background-color:#282f33 !important;
    border-bottom:2px solid #57aeff !important;
    font-size: 30px !important;
    padding:12px !important;
    text-shadow: 3px 3px 1px #111;
}

h2 {
    color:#eee !important;
    background-color:#332f2f !important;
    border-bottom:none !important;
    text-shadow: 3px 3px 1px #222;
}

span.doc{
    color:#eee !important;
}

a.reference {
    text-decoration:none;
    padding:3px !important;
    margin:9px !important;
    margin-left:0px !important;
    color: #red !important;
}

a.reference:hover {
    background-color:#48751d;
}

a.headerlink {
    color: red !important;
}

h4, p.topless a, .nav-item, .nav-item a, li.right a {
    color:#e6e6e6 !important;
     text-shadow: 1px 1px 1px #222;
}

table.align-default {
    width:100% !important;
    margin:none !important;
}

table.docutils td {
    padding-top:2px;
    padding-bottom:2px;
    padding-left:0px;
    padding-right:0px;
    border-bottom:1px solid #f3f3e3;
}

table.docutils th.head {
    background-color:#eec;
    text-align:left;
    padding-left:0px;
}

div.documentwrapper {
    min-height: 300px;
    background-color:#222;
}

div.related {
    background-color:#000;
    border-top:1px solid #111;
    border-bottom:1px solid #111;
}

.footer {
    position: absolute !important;
    height: 18px !important;
    width: 100% !important;
    overflow: hidden !important;
    padding-top:8px !important;
    padding-bottom:18px !important;
    background-color:#111;
}

table.docutils thead tr th {
    background-color:#332f2f !important;
    border-bottom:1px solid #3a3a3f !important;
    padding-top:7px;
    padding-bottom:7px;
    font-weight: 500 !important;
}

table.docutils thead tr th:first-child {
    padding-left: 3px !important;
}

table.docutils tbody tr td {
    vertical-align:middle;
    border-bottom:2px dotted #333 !important;
}

table.docutils tbody tr td:first-child {
    padding:2px;
    padding-right:7px;
    padding-left: 7px !important;
    color: #97eeff !important;
    text-shadow: 2px 2px 1px #000;
}

li table.docutils tbody tr td:first-child {
    color: #fff !important;
}

div.body {
    background-color: #232221;
    color:#fff;
}

#services table.docutils thead tr th:first-child {
    color:transparent;
}

#services table.docutils tbody tr td:first-child {
    font-size:12px;
    text-align: center;
    color:#331;
}

table.docutils tbody tr td {
    vertical-align:top;
}

div.last_updated {
    font-size:smaller;
    color:#eee;
    padding-top:10px;
    text-shadow: 2px 2px 1px #222;
}

span.zato-tag-name-highlight {
    color: white;
    background-color: #885606;
    padding: 8px;
    font-weight: 600;
    border-radius: 8px;
    text-shadow: 2px 1px 1px #333;
}
""".lstrip()

# Custom HTML layout
apispec_files['_templates/layout.html'] = """
{#
    basic/layout.html
    ~~~~~~~~~~~~~~~~~

    Master layout template for Sphinx themes.

    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
#}
{%- block doctype -%}{%- if html5_doctype %}
<!DOCTYPE html>
{%- else %}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
{%- endif %}{%- endblock %}
{%- set reldelim1 = reldelim1 is not defined and ' &#187;' or reldelim1 %}
{%- set reldelim2 = reldelim2 is not defined and ' |' or reldelim2 %}
{%- set render_sidebar = (not embedded) and (not theme_nosidebar|tobool) and
                         (sidebars != []) %}
{%- set url_root = pathto('', 1) %}
{# XXX necessary? #}
{%- if url_root == '#' %}{% set url_root = '' %}{% endif %}
{%- if not embedded and docstitle %}
  {%- set titlesuffix = " &#8212; "|safe + docstitle|e %}
{%- else %}
  {%- set titlesuffix = "" %}
{%- endif %}

{%- macro relbar() %}
    <div class="related" role="navigation" aria-label="related navigation">
      <h3>{{ _('Navigation') }}</h3>
      <ul>
        {%- for rellink in rellinks %}
        <li class="right" {% if loop.first %}style="margin-right: 10px"{% endif %}>
          <a href="{{ pathto(rellink[0]) }}" title="{{ rellink[1]|striptags|e }}"
             {{ accesskey(rellink[2]) }}>{{ rellink[3] }}</a>
          {%- if not loop.first %}{{ reldelim2 }}{% endif %}</li>
        {%- endfor %}
        {%- block rootrellink %}
        <li class="nav-item nav-item-0"><a href="{{ pathto(master_doc) }}">{{ shorttitle|e }}</a>{{ reldelim1 }}</li>
        {%- endblock %}
        {%- for parent in parents %}
          <li class="nav-item nav-item-{{ loop.index }}"><a href="{{ parent.link|e }}" {% if loop.last %}{{ accesskey("U") }}{% endif %}>{{ parent.title }}</a>{{ reldelim1 }}</li>
        {%- endfor %}
        {%- block relbaritems %} {% endblock %}
      </ul>
    </div>
{%- endmacro %}

{%- macro sidebar() %}
      {%- if render_sidebar %}
      <div class="sphinxsidebar" role="navigation" aria-label="main navigation">
        <div class="sphinxsidebarwrapper">
          {%- block sidebarlogo %}
          {%- if logo %}
            <p class="logo"><a href="{{ pathto(master_doc) }}">
              <img class="logo" src="{{ pathto('_static/' + logo, 1) }}" alt="Logo"/>
            </a></p>
          {%- endif %}
          {%- endblock %}
          {%- if sidebars != None %}
            {#- new style sidebar: explicitly include/exclude templates #}
            {%- for sidebartemplate in sidebars %}
            {%- include sidebartemplate %}
            {%- endfor %}
          {%- else %}
            {#- old style sidebars: using blocks -- should be deprecated #}
            {%- block sidebartoc %}
            {%- include "localtoc.html" %}
            {%- endblock %}
            {%- block sidebarrel %}
            {%- include "relations.html" %}
            {%- endblock %}
            {%- block sidebarsourcelink %}
            {%- include "sourcelink.html" %}
            {%- endblock %}
            {%- if customsidebar %}
            {%- include customsidebar %}
            {%- endif %}
            {%- block sidebarsearch %}
            {%- include "searchbox.html" %}
            {%- endblock %}
          {%- endif %}
        </div>
      </div>
      {%- endif %}
{%- endmacro %}

{%- macro script() %}
    <script type="text/javascript" id="documentation_options" data-url_root="{{ pathto('', 1) }}" src="{{ pathto('_static/documentation_options.js', 1) }}"></script>
    {%- for scriptfile in script_files %}
    <script type="text/javascript" src="{{ pathto(scriptfile, 1) }}"></script>
    {%- endfor %}
{%- endmacro %}

{%- macro css() %}
    <link rel="stylesheet" href="{{ pathto('_static/' + style, 1) }}" type="text/css" />
    <link rel="stylesheet" href="{{ pathto('_static/pygments.css', 1) }}" type="text/css" />
    {%- for css in css_files %}
      {%- if css|attr("rel") %}
    <link rel="{{ css.rel }}" href="{{ pathto(css.filename, 1) }}" type="text/css"{% if css.title is not none %} title="{{ css.title }}"{% endif %} />
      {%- else %}
    <link rel="stylesheet" href="{{ pathto(css, 1) }}" type="text/css" />
      {%- endif %}
    {%- endfor %}
{%- endmacro %}

{%- if html_tag %}
{{ html_tag }}
{%- else %}
<html xmlns="http://www.w3.org/1999/xhtml"{% if language is not none %} lang="{{ language }}"{% endif %}>
{%- endif %}
  <head>
    {%- if not html5_doctype and not skip_ua_compatible %}
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    {%- endif %}
    {%- if use_meta_charset or html5_doctype %}
    <meta charset="{{ encoding }}" />
    {%- else %}
    <meta http-equiv="Content-Type" content="text/html; charset={{ encoding }}" />
    {%- endif %}
    {{- metatags }}
    {%- block htmltitle %}
    <title>{{ title|striptags|e }}{{ titlesuffix }}</title>
    {%- endblock %}
    {%- block css %}
    {{- css() }}
    {%- endblock %}
    {%- if not embedded %}
    {%- block scripts %}
    {{- script() }}
    {%- endblock %}
    {%- if use_opensearch %}
    <link rel="search" type="application/opensearchdescription+xml"
          title="{% trans docstitle=docstitle|e %}Search within {{ docstitle }}{% endtrans %}"
          href="{{ pathto('_static/opensearch.xml', 1) }}"/>
    {%- endif %}
    {%- if favicon %}
    <link rel="shortcut icon" href="{{ pathto('_static/' + favicon, 1) }}"/>
    {%- endif %}
    {%- endif %}
{%- block linktags %}
    {%- if hasdoc('about') %}
    <link rel="author" title="{{ _('About these documents') }}" href="{{ pathto('about') }}" />
    {%- endif %}
    {%- if hasdoc('genindex') %}
    <link rel="index" title="{{ _('Index') }}" href="{{ pathto('genindex') }}" />
    {%- endif %}
    {%- if hasdoc('search') %}
    <link rel="search" title="{{ _('Search') }}" href="{{ pathto('search') }}" />
    {%- endif %}
    {%- if hasdoc('copyright') %}
    <link rel="copyright" title="{{ _('Copyright') }}" href="{{ pathto('copyright') }}" />
    {%- endif %}
    {%- if next %}
    <link rel="next" title="{{ next.title|striptags|e }}" href="{{ next.link|e }}" />
    {%- endif %}
    {%- if prev %}
    <link rel="prev" title="{{ prev.title|striptags|e }}" href="{{ prev.link|e }}" />
    {%- endif %}
{%- endblock %}
{%- block extrahead %} {% endblock %}
  </head>
  {%- block body_tag %}<body>{% endblock %}
{%- block header %}{% endblock %}

{%- block relbar1 %}{{ relbar() }}{% endblock %}

{%- block content %}
  {%- block sidebar1 %} {# possible location for sidebar #} {% endblock %}

    <div class="document">
  {%- block document %}
      <div class="documentwrapper">
      {%- if render_sidebar %}
        <div class="bodywrapper">
      {%- endif %}
          <div class="body" role="main">
            {% block body %} {% endblock %}
          </div>
      {%- if render_sidebar %}
        </div>
      {%- endif %}
      </div>
  {%- endblock %}

  {%- block sidebar2 %}{{ sidebar() }}{% endblock %}
      <div class="clearer"></div>
    </div>
{%- endblock %}

{%- block relbar2 %}{{ relbar() }}{% endblock %}

{%- block footer %}
    <div class="footer" role="contentinfo">
      <div style="padding-bottom:1px">
        Generated by <a href="https://zato.io?apidocs">Zato</a>
      </div>
      <div>
        ESB, APIs, AI and Cloud Integrations in Python
      </div>
    </div>
{%- endblock %}
  </body>
</html>
""".lstrip() # noqa: E501


# Custom HTML sidebar
apispec_files['_templates/zato_sidebar.html'] = """
<h4>Downloads</h4>

<p class="topless">
  <a href="_downloads/openapi.yaml" title="Download OpenAPI specification">OpenAPI</a>
</p>

<div class="last_updated">
Last update: {{ last_updated }}
</div>

"""

# Default download files
apispec_files['download/api.raml'] = '' # RAML
apispec_files['download/api.wsdl'] = '' # WSDL
apispec_files['download/api.yaml'] = '' # OpenAPI

# Make for Linux
apispec_files['Makefile'] = """
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = APISpec
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
    @$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
    @$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
    mkdir -p ./$(BUILDDIR)/html/_downloads
    cp -p ./download/* ./$(BUILDDIR)/html/_downloads

""".lstrip().replace('    ', '\t')

# Make for Windows
apispec_files['make.bat'] = """
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
    set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXPROJ=APISpec

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
    echo.
    echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
    echo.installed, then set the SPHINXBUILD environment variable to point
    echo.to the full path of the 'sphinx-build' executable. Alternatively you
    echo.may add the Sphinx directory to PATH.
    echo.
    echo.If you don't have Sphinx installed, grab it from
    echo.http://sphinx-doc.org/
    exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
""".lstrip()


# Main Sphinx documentation
apispec_files['conf.py'] = """
# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = u'API documentation'
copyright = u''
author = u'Zato Source s.r.o. (https://zato.io)'

rst_epilog = '.. |index_title| replace:: {}'.format(project)

# The short X.Y version
version = u''
# The full version, including alpha/beta/rc tags
release = u''


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.ifconfig',
    'sphinx.ext.githubpages',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

html_title = project

html_last_updated_fmt = '%b %d, %Y'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'classic'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
html_sidebars = {'**':['relations.html', 'zato_sidebar.html']}

html_use_index = False

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'APIdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'api.tex', u'API documentation',
     u'Zato', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'apispec', u'API documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'API', u'API documentation',
     author, 'API', 'API documentation.',
     'Miscellaneous'),
]


# -- Extension configuration -------------------------------------------------

def setup(app):
    app.add_css_file('custom.css')
""".lstrip()

# Main file
apispec_files['index.rst'] = """
|index_title|
=================

.. toctree::
   :hidden:
   :titlesonly:
   :glob:

   ./*

.. include:: ./services.rst
""".lstrip()
