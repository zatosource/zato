
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
//     opens a micro-form on the hidden number fields behind it - a threshold on
//     one row and the window it is measured over on the next,
//   - a popover line with a time slots field opens the time slots kit of
//     shared/time-slots.js instead - the All day slot holding the line's own
//     switch and duration, every range of the day added under it holding its
//     own, the ranges kept as one JSON list in the hidden slots field,
//   - a toggle line is a switch answered on the spot,
//   - a pick line is a select listing connections flat - the SMTP and Microsoft
//     365 connections for the email line, the LLM connections for the LLM line -
//     and a select with nothing to list is swapped for a sentence with the links
//     to the pages a connection is created on, the live form updates poll
//     swapping the two back as connections come and go,
//   - the Active switch, the first line of the core settings, dims and freezes
//     every other line when off, and a line depending on another toggle, the
//     LLM line on Use LLM, is dimmed while that toggle is off.
//
// The popovers are appended to document.body, so each wears a class of its
// own - alerts-tab-micro-form - under which shared/alerts-tab.css tunes the
// micro-form tokens.
//
// How to use, in a page's JS:
//
//     // With common/alerts-tab-slots.js loaded before this file
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
//     // Next to the page's own live form updates configs
//     $.fn.zato.live_form_updates.register('create', $.fn.zato.alerts_tab.live_configs(''));
//     $.fn.zato.live_form_updates.register('edit', $.fn.zato.alerts_tab.live_configs('edit-'));
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

    // The summary of a popover line - `{field}` is a value, `{field|singular|plural}` a
    // value with the right noun after it, `{unit_field@count_field}` a count with the
    // unit select's noun after it, the option's value being the singular and its label the
    // plural, and `{slots_field#singular|plural}` the number of time slots with the right
    // noun after it, set off with a comma and left out when there are none
    summary_token: /\{([a-z_]+)(?:@([a-z_]+))?(?:#([^|}]+)\|([^}]+))?(?:\|([^|}]+)\|([^}]+))?\}/g,
    slots_summary_separator: ', ',

    // How wide a popover carrying time slots is - the slots need the room the numbers alone do not
    // The class a slots field carries so the popover leaves the kit's controls to the kit's own styles
    slots_field_class: 'micro-form-field-own',

    // A slots popover is this wide from the start - room for a range with its Delete link -
    // so adding and removing ranges never changes its width
    slots_popover_width: '560px',

    // The keys of one time slot in the hidden slots field, shared with the Python side
    slot_time_from: 'time_from',
    slot_time_to: 'time_to',
    slot_is_on: 'is_on',
    slot_seconds: 'silence_seconds',

    // What a hidden cell says of a checkbox, which is what the edit form reads a boolean back from
    cell_true: 'True',
    cell_false: 'False',
    cell_empty: ''
};

// What the Django side told us about the page's alert fields
$.fn.zato.alerts_tab.settings = null;

// Which form's panel is bound at the moment, and the slots kits of the open popovers by line
$.fn.zato.alerts_tab.state = {
    panel_id: null,
    field_prefix: '',
    slots_kits: {}
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

    tab.register_slots_kind();
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

// One micro-form per popover line - the fields of a line share one row unless the
// line says which fields go on which row, a line with a unit select has it right
// after the last of its numbers, and a line with a time slots field is the slots
// kit alone, the All day slot carrying the line's own switch and duration
$.fn.zato.alerts_tab.build_descriptors = function() {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        if(line.kind !== 'popover') {
            return;
        }

        if(line.slots_field) {
            out[line.name] = {
                title: line.title,
                width: tab.config.slots_popover_width,
                pages: [[{kind: settings.slots_kind, field: line.slots_field, line: line}]]
            };
            return;
        }

        var rows = line.rows ? line.rows : [line.fields];
        var last_spec = null;

        var page = rows.map(function(row) {

            var specs = row.map(function(field_name) {
                var spec = {
                    field: field_name,
                    label: settings.field_labels[field_name],
                    kind: settings.toggle_kinds.indexOf(settings.field_kinds[field_name]) !== -1 ? 'checkbox' : 'number'
                };

                // A switch sharing a row with numbers stands under a label like they do
                if(spec.kind === 'checkbox' && row.length > 1) {
                    spec.labelAbove = true;
                }

                last_spec = spec;
                return spec;
            });

            var entry = specs.length === 1 ? specs[0] : specs;
            return entry;
        });

        if(line.unit_field) {
            last_spec.unitField = line.unit_field;
        }

        out[line.name] = {
            title: line.title,
            fitContent: true,
            pages: [page]
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
// id each line's label points at - the switch, the select or the edit link
$.fn.zato.alerts_tab.descriptions = function() {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        var target_id;

        if(line.kind === 'popover') {
            target_id = tab.element_id('edit', line.name);
        }
        else {
            target_id = tab.field_id(line.fields[0]);
        }

        out[target_id] = line.how_it_works;
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes a line's summary from its fields - `{field}` is the field's value,
// `{field|singular|plural}` the value with the right one of the two nouns after it
// and `{unit_field@count_field}` the count with the unit select's noun after it.
// A line with a switch among its fields reads as its off text while the switch is off.
$.fn.zato.alerts_tab.format_summary = function(line) {

    var tab = $.fn.zato.alerts_tab;

    if(line.off_field && !tab.field(line.off_field).is(':checked')) {
        return line.summary_off;
    }

    var out = line.summary.replace(tab.config.summary_token, function(ignored, field_name, count_field_name, slots_singular, slots_plural, singular, plural) {

        var field = tab.field(field_name);
        var value = field.val();

        // The ranges of the day a slots field holds, said only when there are any
        if(slots_singular !== undefined) {
            var slots_count = JSON.parse(value).length;

            if(slots_count === 0) {
                return '';
            }

            var slots_text = tab.config.slots_summary_separator + $.fn.zato.count_text(slots_count, slots_singular, slots_plural);
            return slots_text;
        }

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

// A pick line shows its select while there is anything to list and the sentence
// with the create links otherwise
$.fn.zato.alerts_tab.apply_pick_state = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var has_options = tab.field(line.field).find('option').length > 1;

    document.getElementById(tab.element_id('pick', line.name)).hidden = !has_options;
    document.getElementById(tab.element_id('empty', line.name)).hidden = has_options;
}

// /////////////////////////////////////////////////////////////////////////////

// The live form updates configs of the pick lines of one form - the poll keeps
// each select in step with the connections there are and the tab swaps the
// select and the empty sentence as they come and go. The field prefix is the
// form's, the empty string for the create form and 'edit-' for the edit form.
$.fn.zato.alerts_tab.live_configs = function(field_prefix) {

    var tab = $.fn.zato.alerts_tab;
    var out = [];

    tab.settings.lines.forEach(function(line) {

        if(line.kind !== 'pick') {
            return;
        }

        var select_id = tab.config.id_prefix + field_prefix + tab.settings.field_prefix + line.field;

        out.push({
            object_type: line.live_type,
            handler: 'callback',
            snapshot_func: function() {
                var items = $.fn.zato.live_form_updates._snapshot_select('#' + select_id);
                return items;
            },
            on_diff: function(diff, skip_puff) {
                tab.apply_pick_diff(line, select_id, diff, skip_puff);
            }
        });
    });

    return out;
}

// Applies one poll's differences to a pick select - options gone, renamed and new - and shows
// the select or the empty sentence as the count of options says
$.fn.zato.alerts_tab.apply_pick_diff = function(line, select_id, diff, skip_puff) {

    var tab = $.fn.zato.alerts_tab;
    var select = $('#' + select_id);

    diff.deleted.forEach(function(deleted_id) {
        select.find('option').filter(function() {
            var matches = this.value === deleted_id;
            return matches;
        }).remove();
    });

    diff.renamed.forEach(function(renamed) {
        var option = select.find('option').filter(function() {
            var matches = this.value === renamed._id;
            return matches;
        });
        option.text(renamed.item._label);
    });

    diff.created.forEach(function(item) {
        var option = $('<option/>').val(item._id).text(item._label);
        select.append(option);

        if(!skip_puff) {
            $.fn.zato.live_form_updates._puff(option);
        }
    });

    // The bound form's own select is the one on show, the other form's is not on screen
    if(select_id === tab.field_id(line.field)) {
        tab.apply_pick_state(line);
    }
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
// popover lines and the dimmed states
$.fn.zato.alerts_tab.render = function() {

    var tab = $.fn.zato.alerts_tab;

    tab.settings.lines.forEach(function(line) {

        if(line.kind === 'popover') {
            var summary = document.getElementById(tab.element_id('summary', line.name));
            summary.textContent = tab.format_summary(line);
        }

        if(line.depends_on) {
            tab.apply_dependent_state(line);
        }

        if(line.kind === 'pick') {
            tab.apply_pick_state(line);
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
