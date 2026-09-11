
// /////////////////////////////////////////////////////////////////////////////
//
// Alerts tab - the per-object alert settings panel of a create or edit form,
// read as one page of settings inside a dialog.
//
// The Django side (zato.admin.web.alerts_tab) renders the lines and writes the
// tab's configuration into a json_script element. This file reads it and hosts
// the shared kits on the dialog's own form - the decision lines of
// common/decision-lines.js and the popover micro-forms of common/micro-forms.js:
//
//   - a popover line carries a summary link reading as a sentence, and the link
//     opens a micro-form on the hidden number fields behind it,
//   - a toggle line is a switch answered on the spot,
//   - a pick line is a chip opening a pick panel that lists connections in
//     groups - the SMTP and Microsoft 365 connections for the email line, the
//     LLM connections for the LLM line - each group with the link to the page
//     a new one is made on, and picking a row writes the hidden select,
//   - the Active switch, the first line of the core settings, dims and freezes
//     every other line when off, and a line depending on another toggle, the
//     LLM line on Use LLM, is dimmed while that toggle is off.
//
// The popovers and the panel are appended to document.body, so each wears a
// class of its own - alerts-tab-micro-form and alerts-tab-pick-panel - under
// which shared/alerts-tab.css tunes the kits' tokens.
//
// How to use, in a page's JS:
//
//     $.fn.zato.alerts_tab.init({config_id: 'out-sftp-alerts-tab-config'});
//
//     // Before opening the create dialog
//     $.fn.zato.alerts_tab.bind({
//         panel_id: 'out-sftp-create-tab-panel-alerts',
//         field_prefix: ''
//     });
//
//     // When building the how-it-works descriptions
//     var descriptions = $.extend({}, own_descriptions, $.fn.zato.alerts_tab.descriptions());
//
//     // The hidden columns of a row the edit form is populated from
//     get_columns: [..., ...$.fn.zato.alerts_tab.columns()]
//     new_row: row += $.fn.zato.alerts_tab.hidden_cells(item);
//
// The field_prefix is the Django form prefix with its trailing dash, the empty
// string for the create form and 'edit-' for the edit form.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.alerts_tab');

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.alerts_tab.config = {

    // Every element the popovers make is named after this
    idPrefix: 'alerts-tab',

    // The class the popovers wear, under which alerts-tab.css tunes the micro-form tokens
    popup_class: 'alerts-tab-micro-form',

    // Whether a popover carries a How does it work? badge of its own - the lines
    // of the tab are covered by the dialog's own badge, so the popovers carry none
    show_how_it_works: false,

    off_class: 'alerts-tab-off',
    line_off_class: 'alerts-tab-line-off',
    id_prefix: 'id_',
    window_target: '_blank',

    // The panel a connection is picked in, and the class it wears,
    // under which alerts-tab.css tunes the pick panel tokens
    pick_panel_width: 340,
    pick_panel_min_width: 280,
    pick_panel_class: 'alerts-tab-pick-panel',

    // The link under a group's list opening the page a new connection is made on
    add_link_class: 'alerts-tab-add-link',

    // The summary of a popover line - `{field}` is a value, `{field|singular|plural}` a
    // value with the right noun after it and `{unit_field@count_field}` a count with the
    // unit select's noun after it, the option's value being the singular and its label the plural
    summary_token: /\{([a-z_]+)(?:@([a-z_]+))?(?:\|([^|}]+)\|([^}]+))?\}/g,

    // What a hidden cell says of a checkbox, which is what the edit form reads a boolean back from
    cell_true: 'True',
    cell_false: 'False',
    cell_empty: ''
};

// What the Django side told us about the page's alert fields
$.fn.zato.alerts_tab.settings = null;

// Which form's panel is bound at the moment
$.fn.zato.alerts_tab.state = {
    panel_id: null,
    field_prefix: ''
};

// The micro-forms kit installs the popover engine here
$.fn.zato.alerts_tab.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.alerts_tab.init = function(options) {

    var tab = $.fn.zato.alerts_tab;
    var config_element = document.getElementById(options.config_id);

    tab.settings = JSON.parse(config_element.textContent);

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.build_descriptors(),
        popupClass: tab.config.popup_class,
        showHowItWorks: tab.config.show_how_it_works,
        onDone: tab.render
    });
}

// /////////////////////////////////////////////////////////////////////////////

// What the tab is called in a dialog's tab strip
$.fn.zato.alerts_tab.tab_label = function() {
    var out = $.fn.zato.alerts_tab.settings.tab_label;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden columns of a row the tab's fields travel in, in the order the Django
// side lists them - what a page appends to its get_columns
$.fn.zato.alerts_tab.columns = function() {
    var out = $.fn.zato.alerts_tab.settings.storage_field_names.slice();
    return out;
}

// The hidden cells of a new row, one per column above - a checkbox reads as True
// or False, anything else as the value the form holds, so that the edit form
// populated from the row reads the way the dialog that made it did
$.fn.zato.alerts_tab.hidden_cells = function(item) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = '';

    settings.storage_field_names.forEach(function(field_name) {

        var value = item[field_name];
        var text;

        if(settings.checkbox_field_names.indexOf(field_name) !== -1) {
            text = value == true ? tab.config.cell_true : tab.config.cell_false;
        }
        else if(value === undefined) {
            text = tab.config.cell_empty;
        }
        else {
            text = value;
        }

        out += String.format("<td class='ignore'>{0}</td>", text);
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields on the form bound at the moment
$.fn.zato.alerts_tab.field_id = function(field_name) {
    var tab = $.fn.zato.alerts_tab;
    var out = tab.config.id_prefix + tab.state.field_prefix + tab.settings.field_prefix + field_name;
    return out;
}

// The one way into the rendered Django form, which is what the kit's popovers read and write
$.fn.zato.alerts_tab.field = function(field_name) {
    var out = $('#' + $.fn.zato.alerts_tab.field_id(field_name));
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The id of one element of the bound panel - a line, a summary, an edit link or a slot
$.fn.zato.alerts_tab.element_id = function(part, line_name) {
    var out = $.fn.zato.alerts_tab.state.panel_id + '-' + part + '-' + line_name;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// One micro-form per popover line - the fields of a line share one row, so
// a warning and an error count are read side by side, and a line with a
// unit select has it right after the last of its numbers
$.fn.zato.alerts_tab.build_descriptors = function() {

    var settings = $.fn.zato.alerts_tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        if(line.kind !== 'popover') {
            return;
        }

        var specs = line.fields.map(function(field_name) {
            var spec = {
                field: field_name,
                label: settings.field_labels[field_name],
                kind: settings.toggle_kinds.indexOf(settings.field_kinds[field_name]) !== -1 ? 'checkbox' : 'number'
            };
            return spec;
        });

        if(line.unit_field) {
            specs[specs.length - 1].unitField = line.unit_field;
        }

        var entry = specs.length === 1 ? specs[0] : specs;

        out[line.name] = {
            title: line.title,
            fitContent: true,
            pages: [[entry]]
        };
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popover inputs, under the ids the micro-forms kit gives them
$.fn.zato.alerts_tab.helpDescriptions = function() {

    var tab = $.fn.zato.alerts_tab;
    var out = {};

    for(var field_name in tab.settings.field_how_it_works) {
        out[tab.forms.inputId(field_name)] = tab.settings.field_how_it_works[field_name];
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works descriptions of the lines of the bound panel, keyed by the
// id each line's label points at - the switch, the edit link or the chip
$.fn.zato.alerts_tab.descriptions = function() {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        var target_id;

        if(line.kind === 'toggle') {
            target_id = tab.field_id(line.fields[0]);
        }
        else if(line.kind === 'popover') {
            target_id = tab.element_id('edit', line.name);
        }
        else {
            target_id = tab.element_id('slot', line.name) + '-chip';
        }

        out[target_id] = line.how_it_works;
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes a line's summary from its fields - `{field}` is the field's value,
// `{field|singular|plural}` the value with the right one of the two nouns after it
// and `{unit_field@count_field}` the count with the unit select's noun after it
$.fn.zato.alerts_tab.format_summary = function(template) {

    var tab = $.fn.zato.alerts_tab;

    var out = template.replace(tab.config.summary_token, function(ignored, field_name, count_field_name, singular, plural) {

        var field = tab.field(field_name);
        var value = field.val();

        // A unit select spells its noun both ways - the value is the singular, the label the plural
        if(count_field_name !== undefined) {
            var count = parseInt(tab.field(count_field_name).val());
            var option = field.find('option:selected');
            var unit_text = $.fn.zato.count_text(count, option.val(), option.text());
            return unit_text;
        }

        if(singular === undefined) {
            return value;
        }

        var text = $.fn.zato.count_text(parseInt(value), singular, plural);
        return text;
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Splits a pick select value into the kind of connection and the connection's
// name - an email value carries the kind before the separator, an LLM value is
// the name alone and belongs to the line's one group
$.fn.zato.alerts_tab.split_pick_value = function(line, value) {

    var out;

    if(line.encode_kind) {
        var separator = $.fn.zato.alerts_tab.settings.pick_kind_separator;
        var separator_index = value.indexOf(separator);

        out = {
            kind: value.substring(0, separator_index),
            name: value.substring(separator_index + separator.length)
        };
    }
    else {
        out = {
            kind: line.groups[0].kind,
            name: value
        };
    }

    return out;
}

// The value one entry of a pick line's select carries for a connection of a kind
$.fn.zato.alerts_tab.pick_value = function(line, kind, name) {

    var out;

    if(line.encode_kind) {
        out = kind + $.fn.zato.alerts_tab.settings.pick_kind_separator + name;
    }
    else {
        out = name;
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The group of a pick line a kind of connection belongs to
$.fn.zato.alerts_tab.pick_group = function(line, kind) {

    var out = null;

    line.groups.forEach(function(group) {
        if(group.kind === kind) {
            out = group;
        }
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The connections of one kind, read off the hidden select's own group so the
// select stays the single source of what there is to pick from
$.fn.zato.alerts_tab.pick_connection_names = function(line, kind) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = [];

    tab.field(line.field).find('option').each(function() {

        if(!this.value) {
            return;
        }

        var parts = tab.split_pick_value(line, this.value);

        if(parts.kind !== kind) {
            return;
        }

        // The entries saying a group is empty or opening the create page are not connections
        if(parts.name === settings.pick_none_value || parts.name === settings.pick_create_new_value) {
            return;
        }

        out.push(parts.name);
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Fills a pick line's chip from the hidden select - solid with the picked
// connection and its group as the note, dashed while nothing is picked yet
$.fn.zato.alerts_tab.render_pick_chip = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var value = tab.field(line.field).val();

    var spec = {
        panel: {
            title: line.title,
            width: tab.config.pick_panel_width,
            minWidth: tab.config.pick_panel_min_width,
            panelClass: tab.config.pick_panel_class,
            build: function(body) {
                var out = tab.build_pick_panel(line, body);
                return out;
            }
        }
    };

    if(value === settings.pick_no_selection_value) {
        spec.text = settings.pick_no_selection_label;
        spec.isBlank = true;
    }
    else {
        var parts = tab.split_pick_value(line, value);
        spec.text = parts.name;
        spec.note = tab.pick_group(line, parts.kind).label;
    }

    $.fn.zato.decision_lines.setChip(tab.element_id('slot', line.name), spec);
}

// /////////////////////////////////////////////////////////////////////////////

// The panel a pick line's connection is picked in - one heading and one list
// per group, the list saying (None) when the group has no connections, and
// under each the link to the page a new one is made on
$.fn.zato.alerts_tab.build_pick_panel = function(line, body) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var lines = $.fn.zato.decision_lines;

    var current = tab.field(line.field).val();

    line.groups.forEach(function(group) {

        var heading = document.createElement('span');
        heading.className = 'micro-form-label';
        heading.textContent = group.label;
        body.appendChild(heading);

        var list = document.createElement('div');
        list.className = 'decision-pick-panel-list';

        var names = tab.pick_connection_names(line, group.kind);

        names.forEach(function(name) {

            var value = tab.pick_value(line, group.kind, name);
            var is_picked = value === current;
            var row = lines.buildPickRow(name, is_picked, tab.pick_connection(line, value));

            // Picking the connection already picked is how the object is left without one,
            // which the name says right after itself rather than through a control of its own
            if(is_picked) {
                var remove = document.createElement('span');
                remove.className = 'decision-pick-remove';
                remove.textContent = settings.pick_remove_label;
                row.querySelector('.decision-pick-name').appendChild(remove);
            }

            list.appendChild(row);
        });

        if(!names.length) {
            var empty = document.createElement('div');
            empty.className = 'decision-pick-panel-empty';
            empty.textContent = tab.pick_option_label(line, tab.pick_value(line, group.kind, settings.pick_none_value));
            list.appendChild(empty);
        }

        body.appendChild(list);

        var add_link = document.createElement('a');
        add_link.href = 'javascript:void(0)';
        add_link.className = tab.config.add_link_class;
        add_link.textContent = tab.pick_option_label(line, tab.pick_value(line, group.kind, settings.pick_create_new_value));

        add_link.addEventListener('click', function() {
            window.open(group.create_url, tab.config.window_target);
        });

        body.appendChild(add_link);
    });

    var out = null;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The label of one option of a pick line's hidden select
$.fn.zato.alerts_tab.pick_option_label = function(line, value) {
    var tab = $.fn.zato.alerts_tab;
    var option = tab.field(line.field).find('option').filter(function() {
        return this.value === value;
    });
    var out = option.text();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The row of one connection knows the value it stands for - picking the one
// already picked is how the object is left without a connection
$.fn.zato.alerts_tab.pick_connection = function(line, value) {

    var tab = $.fn.zato.alerts_tab;

    var out = function() {

        var field = tab.field(line.field);

        if(field.val() === value) {
            field.val(tab.settings.pick_no_selection_value);
        }
        else {
            field.val(value);
        }

        $.fn.zato.decision_lines.closePanel();
        tab.render();
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Dims the other lines when Active is off and lights them up again when it is on
$.fn.zato.alerts_tab.apply_active_state = function() {

    var tab = $.fn.zato.alerts_tab;
    var panel = $('#' + tab.state.panel_id);
    var is_active = tab.field(tab.settings.is_active_field).is(':checked');

    if(is_active) {
        panel.removeClass(tab.config.off_class);
    }
    else {
        panel.addClass(tab.config.off_class);
    }
}

// Dims a line while the toggle it depends on is off - the LLM line while Use LLM is off
$.fn.zato.alerts_tab.apply_dependent_state = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var element = $('#' + tab.element_id('line', line.name));
    var is_on = tab.field(line.depends_on).is(':checked');

    if(is_on) {
        element.removeClass(tab.config.line_off_class);
    }
    else {
        element.addClass(tab.config.line_off_class);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Writes every line of the bound panel from the form - the summaries of the
// popover lines, the chips of the pick lines and the dimmed states
$.fn.zato.alerts_tab.render = function() {

    var tab = $.fn.zato.alerts_tab;

    tab.settings.lines.forEach(function(line) {

        if(line.kind === 'popover') {
            var summary = document.getElementById(tab.element_id('summary', line.name));
            summary.textContent = tab.format_summary(line.summary);
        }
        else if(line.kind === 'pick') {
            tab.render_pick_chip(line);
        }

        if(line.depends_on) {
            tab.apply_dependent_state(line);
        }
    });

    tab.apply_active_state();
}

// /////////////////////////////////////////////////////////////////////////////

// Wires one form's panel - call it each time before the dialog opens so the
// panel starts from the state its fields are in
$.fn.zato.alerts_tab.bind = function(options) {

    var tab = $.fn.zato.alerts_tab;

    tab.state.panel_id = options.panel_id;
    tab.state.field_prefix = options.field_prefix;

    tab.field(tab.settings.is_active_field).off('change.alerts_tab').on('change.alerts_tab', function() {
        tab.apply_active_state();
    });

    tab.settings.lines.forEach(function(line) {

        // A line dimmed by another toggle follows that toggle as it is flipped
        if(line.depends_on) {
            tab.field(line.depends_on).off('change.alerts_tab_' + line.name).on('change.alerts_tab_' + line.name, function() {
                tab.apply_dependent_state(line);
            });
        }

        if(line.kind !== 'popover') {
            return;
        }

        // The cursor lands in the first field of the line, its value left as it stands
        $('#' + tab.element_id('edit', line.name)).off('click.alerts_tab').on('click.alerts_tab', function() {
            tab.forms.open(line.name, this, line.fields[0]);
        });
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
