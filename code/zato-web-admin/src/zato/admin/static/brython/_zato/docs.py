# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Brython
from browser import document as doc, window
from browser.html import A as a, DIV as div, TABLE as table, TR as tr, TD as td

# ################################################################################################################################

_anon_ns = 'zato_anonymous'

# ################################################################################################################################

# Taken from https://docs.python.org/3.3/library/itertools.html#itertools.zip_longest

class ZipExhausted(Exception):
    pass

def chain(*iterables):
    """ chain('ABC', 'DEF') --> A B C D E F
    """
    for it in iterables:
        for element in it:
            yield element

def repeat(object, times=None):
    """ repeat(10, 3) --> 10 10 10
    """
    if times is None:
        while True:
            yield object
    else:
        for i in range(times):
            yield object

def zip_longest(*args, **kwds):
    """ zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    """
    fillvalue = kwds.get('fillvalue')
    counter = len(args) - 1

    def sentinel():
        nonlocal counter
        if not counter:
            raise ZipExhausted
        counter -= 1
        yield fillvalue
    fillers = repeat(fillvalue)
    iterators = [chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass

# ################################################################################################################################

tr_ns_html_contents_template = """
<td id="td-ns-{name}" class="td-ns">
  <div id="ns-name-{name}" class="ns-name"><span class="header">{ns_name_human}</span> <span class="docs">{ns_docs_md}</span></div>
  <div id="ns-options-{name}" class="ns-options">
    <a href="#" id="a-ns-options-toggle-services-{name}">Toggle services</a>
    |
    <a href="#" id="a-ns-options-toggle-all-details-{name}">Toggle all details</a>
  </div>
</td>
"""

tr_service_html_contents_template = """
<td id="td-service-{ns_name}-{name}" class="td-service">
  <div id="service-name-{ns_name}-{name}" class="service-name"><span class="header">{service_no}. {display_name}</span>
  <span class="service-desc" id="service-desc-{ns_name}-{name}"></span></div>
  <div id="service-options-{ns_name}-{name}" class="service-options"><a href="#" id="a-toggle-details-{ns_name}-{name}">Toggle details</a></div>
  <div id="service-details-header-{ns_name}-{name}" class="hidden service-details service-details-toggle-{ns_name}-{name}">
    <span class="header">
      <a href="#" id="service-header-docs-{ns_name}-{name}">Docs</a>
      |
      <a href="#" id="service-header-deps-{ns_name}-{name}">Dependencies</a>
      |
      <a href="#" id="service-header-io-{ns_name}-{name}">I/O</a>
    </span>
  </div>
  <div id="service-details-deps-{ns_name}-{name}" class="hidden header-details service-details-toggle-{ns_name}-{name}">Dependencies</div>
  <div id="service-details-io-{ns_name}-{name}" class="hidden header-details service-details-toggle-{ns_name}-{name}">I/O</div>
  <div id="service-details-docs-{ns_name}-{name}" class="hidden visible current-item header-details service-details-toggle-{ns_name}-{name}"/>
</td>
"""

deps_template = """
<p>Invokes: {invokes}</p>
<p>Invoked by: {invoked_by}</p>
"""

io_template = """
<table class="service-io">
  <thead>
    <tr>
      <th colspan="3" class="input">Input</th>
      <th colspan="3">Output</th>
    </tr>
  </thead>
  <tbody id="io-tbody-{name}">
    {rows}
  </tbody>
</table>
"""

io_row_template = """
    <tr class="{tr_class}">
      <td class="io-name-input">{input_name}</td>
      <td class="io-data-type">{input_data_type}</td>
      <td class="io-is-required req-opt">{input_is_required}</td>
      <td class="io-name">{output_name}</td>
      <td class="io-data-type">{output_data_type}</td>
      <td class="io-is-required req-opt">{output_is_required}</td>
    </tr>
"""

none_html = '<span class="form_hint">(None)</span>'
header_details = ('deps', 'io', 'docs')

# ################################################################################################################################

class APISpec(object):
    """ Main object responsible for representation of API specifications.
    """
    def __init__(self, data):
        self.data = data
        self.spec_table = table(id='spec-table')
        self.cluster_id = doc['cluster_id'].value

# ################################################################################################################################

    def toggle_visible_hidden(self, e, id, needs_visible, _attrs=('visible', 'hidden')):
        elem = doc[id]
        current = [_elem.strip() for _elem in elem.class_name.split(' ')]

        for name in _attrs:
            try:
                current.remove(name)
            except ValueError:
                pass

        current.append('visible' if needs_visible else 'hidden')
        elem.class_name = ' '.join(current)

        if e:
            e.preventDefault()

# ################################################################################################################################

    def _switch_css_class(self, id, class_name, needs_add=True):
        elem = doc[id]
        classes = set(elem.class_name.split(' '))

        if needs_add:
            classes.add(class_name)
        else:
            classes.remove(class_name)

        elem.class_name = ' '.join(classes)

# ################################################################################################################################

    def _toggle(self, e, selector, needs_visible=None):
        for elem in doc.get(selector=selector):
            if needs_visible is None:
                needs_visible = 'hidden' in elem.class_name
            self.toggle_visible_hidden(e, elem.id, needs_visible)

# ################################################################################################################################

    def toggle_simple(self, selector_prefix, ns_name):
        def _toggle(e):
            self._toggle(e, '.{}{}'.format(selector_prefix, ns_name))
        return _toggle

# ################################################################################################################################

    def toggle_details(self, selector_prefix, ns_name, service_name):
        def _toggle(e):
            selector = '.{}{}-{}'.format(selector_prefix, ns_name, service_name)
            elems = doc.get(selector=selector)
            for elem in elems:
                if 'service-details-header' in elem.id or 'current-item' in elem.class_name:
                    self._toggle(None, '#{}'.format(elem.id))
        return _toggle

# ################################################################################################################################

    def toggle_all_details(self, ns_name):
        def _toggle(e):

            self._toggle(e, '.tr-service-ns-{}'.format(ns_name), True)

            # Iterate as long as we don't hit upon another header
            for elem in doc.get(selector='#tr-ns-{} ~ tr'.format(ns_name)):
                if 'tr-ns' in elem.id:
                    break

                selector = '.service-details-toggle-{}-{}'.format(ns_name, elem.id.replace('tr-service-', ''))
                elems = doc.get(selector=selector)

                for elem in elems:
                    if 'service-details-header' in elem.id or 'current-item' in elem.class_name:
                        self._toggle(None, '#{}'.format(elem.id))

        return _toggle

# ################################################################################################################################

    def highlight(self, id_pattern, *pattern_args, needs_add=True):
        def _highlight(e):
            id = id_pattern.format(*pattern_args)
            self._switch_css_class(id, 'highlight', needs_add)
        return _highlight

# ################################################################################################################################

    def switch_detail(self, ns_name, service_name, current):
        def _switch(e):

            # Switch everything off ..
            for detail in header_details:
                id = '#service-details-{}-{}-{}'.format(detail, ns_name, service_name)
                elems = doc.get(selector=id)

                for elem in elems:

                    classes = elem.class_name.split(' ')
                    if 'current-item' in classes:
                        classes.remove('current-item')
                    elem.class_name = ' '.join(classes)

                self._toggle(None, id, False)

            # .. and switch on only the required one.
            current_id = 'service-details-{}-{}-{}'.format(current, ns_name, service_name)
            _current = doc[current_id]
            self._toggle(None, '#{}'.format(current_id), True)

            classes = _current.class_name.split(' ')
            classes.append('current-item')
            _current.class_name = ' '.join(classes)

            # Don't forget about cancelling the default handler
            e.preventDefault()

        return _switch

# ################################################################################################################################

    def get_tr_ns_html(self, ns_name, ns_name_human, ns_docs_md=''):
        return tr_ns_html_contents_template.format(name=ns_name, ns_name_human=ns_name_human, ns_docs_md=ns_docs_md)

# ################################################################################################################################

    def _get_deps(self, deps):
        out = []
        for name in deps:
            out.append('<a href="/zato/service/overview/{name}/?cluster={cluster_id}">{name}</a>'.format(
                name=name, cluster_id=self.cluster_id))

        return ', '.join(out) or none_html

# ################################################################################################################################

    def get_deps_html(self, invokes, invoked_by):
        return deps_template.format(invokes=self._get_deps(invokes), invoked_by=self._get_deps(invoked_by))

# ################################################################################################################################

    def get_io_html(self, name, io):
        if not io:
            return none_html

        _input = io['input_required'] + io['input_optional']
        _output = io['output_required'] + io['output_optional']

        rows = []

        _io = list(zip_longest(_input, _output))
        len_io = len(_io)
        for idx, elems in enumerate(_io, 1):
            _input_elem, _output_elem = elems

            if not _input_elem:
                input_name, input_data_type, input_is_required = '---', '---', '---'
            else:
                input_name = _input_elem['name']
                input_data_type = _input_elem['subtype']
                input_is_required = 'required' if _input_elem['is_required'] else 'optional'

            if not _output_elem:
                output_name, output_data_type, output_is_required = '---', '---', '---'
            else:
                output_name = _output_elem['name']
                output_data_type = _output_elem['subtype']
                output_is_required = 'required' if _output_elem['is_required'] else 'optional'

            rows.append(io_row_template.format(tr_class='tr-io-last' if idx == len_io else '',
                input_name=input_name, input_data_type=input_data_type, input_is_required=input_is_required,
                output_name=output_name, output_data_type=output_data_type, output_is_required=output_is_required))

        return io_template.format(name=name, rows='\n'.join(rows))

# ################################################################################################################################

    def get_tr_service_html(self, service_no, service):
        display_name = service['name']
        name = self.get_service_name(service['name'])
        ns_name = self.get_ns(service['namespace_name'])
        return tr_service_html_contents_template.format(
            display_name=display_name, name=name, ns_name=ns_name, service_no=service_no)

# ################################################################################################################################

    def get_ns(self, ns, orig_or_anon=False):
        if orig_or_anon:
            return ns if ns else _anon_ns
        else:
            return ns.replace('.', '-') if ns else _anon_ns

# ################################################################################################################################

    def get_service_name(self, name):
        return name.replace('.', '-')

# ################################################################################################################################

    def run(self):
        """ Creates a table with all the namespaces and services.
        """
        default_ns_name_human = """
            <span class="form_hint" style="font-size:100%;font-style:italic">(Services without a namespace)</span>
        """

        # Maps names of services to their summaries and descriptions
        service_details = {}

        # All namespaces
        namespaces = list(self.data.get('namespaces', {}).values())
        for values in namespaces:

            # Config
            services = values['services']

            if not services:
                continue

            ns_docs_md = values['docs_md']
            orig_ns_name = self.get_ns(values['name'], orig_or_anon=True)
            ns_name = self.get_ns(values['name'])

            # Create a new row for each namespace
            tr_ns = tr(id='tr-ns-{}'.format(ns_name))
            tr_ns.class_name='tr-ns'
            tr_ns.html = self.get_tr_ns_html(
                ns_name, (orig_ns_name if orig_ns_name != _anon_ns else default_ns_name_human), ns_docs_md)

            # Append namespaces to the main table
            self.spec_table <= tr_ns

            # Append a row for each service in a given namespace
            for idx, service in enumerate(services):
                service_name = self.get_service_name(service['name'])
                tr_service = tr(id='tr-service-{}'.format(service_name))
                tr_service.class_name='visible tr-service tr-service-ns-{}'.format(ns_name)
                tr_service.html = self.get_tr_service_html(idx+1, service)
                self.spec_table <= tr_service
                service_details[service_name] = {

                    'ns_name': ns_name,
                    'docs': {
                        'summary': service['docs']['summary_html'],
                        'full': service['docs']['full_html'],
                    },
                    'deps': {
                        'invokes': service['invokes'],
                        'invoked_by': service['invoked_by']
                    },
                    'io': service['simple_io'].get('zato', {})

                }

        # Don't display anything if there are no services in the only namespace
        if len(namespaces) == 1 and not namespaces[0]['services']:
            doc['main-div'].html = '<b>No results</b>'
            doc['main-div'].class_name = 'no-results'
            return

        # We can append the table with contents to the main div
        doc['main-div'] <= self.spec_table

        # Now we can set up details by their div IDs
        for name, details in service_details.items():

            ns_name = details['ns_name']
            name = self.get_service_name(name)

            docs = details['docs']
            doc['service-desc-{}-{}'.format(ns_name, name)].html = docs['summary']
            doc['service-details-docs-{}-{}'.format(ns_name, name)].html = docs['full'] or none_html

            deps = details['deps']
            doc['service-details-deps-{}-{}'.format(ns_name, name)].html = self.get_deps_html(deps['invokes'], deps['invoked_by'])

            io = details['io']
            doc['service-details-io-{}-{}'.format(ns_name, name)].html = self.get_io_html(name, io)

            elem = doc['a-toggle-details-{}-{}'.format(ns_name, name)]
            elem.bind('click', self.toggle_details('service-details-toggle-', details['ns_name'], name))

            elem.bind('mouseover', self.highlight('service-name-{}-{}', ns_name, name))
            elem.bind('mouseout', self.highlight('service-name-{}-{}', ns_name, name, needs_add=False))

            for detail in header_details:
                elem = doc['service-header-{}-{}-{}'.format(detail, ns_name, name)]
                elem.bind('click', self.switch_detail(ns_name, name, detail))

        for item in namespaces:
            ns_name = self.get_ns(item['name'])

            if not item['services']:
                continue

            elem = doc['a-ns-options-toggle-services-{}'.format(ns_name)]
            elem.bind('click', self.toggle_simple('tr-service-ns-', ns_name))
            elem.bind('mouseover', self.highlight('ns-name-{}', ns_name))
            elem.bind('mouseout', self.highlight('ns-name-{}', ns_name, needs_add=False))

            elem = doc['a-ns-options-toggle-all-details-{}'.format(ns_name)]
            elem.bind('click', self.toggle_all_details(ns_name))
            elem.bind('mouseover', self.highlight('ns-name-{}', ns_name))
            elem.bind('mouseout', self.highlight('ns-name-{}', ns_name, needs_add=False))

# ################################################################################################################################

apispec = APISpec(loads(doc['docs-data'].text))
apispec.run()

# ################################################################################################################################
