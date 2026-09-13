
// /////////////////////////////////////////////////////////////////////////////
//
// Alerts tab - the per-object alert settings panel of a create or edit form.
//
// The Django side (zato.admin.web.alerts_tab) renders the lines and writes the
// tab's configuration into a json_script element. This file reads it and hosts
// the decision lines of common/decision-lines.js and the popover micro-forms of
// common/micro-forms/core.js on the dialog's own form. A popover line with a time
// slots field opens the time slots kit of shared/time-slots.js instead.
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
    popupClass: 'alerts-tab-micro-form',

    // The lines of the tab are covered by the dialog's own How does it work? badge
    showHowItWorks: false,

    offClass: 'alerts-tab-off',
    lineOffClass: 'alerts-tab-line-off',
    idPrefixDjango: 'id_',

    // The kinds of line the Django side lists
    kindPopover: 'popover',
    kindToggle: 'toggle',
    kindPick: 'pick',

    // The kinds of field spec a popover is built of
    specCheckbox: 'checkbox',
    specNumber: 'number',
    specText: 'text',

    // The summary of a popover line - `{field}` is a value, `{field|singular|plural}` a
    // value with the right noun after it, `{unit_field@count_field}` a count with the
    // unit select's noun after it and `{slots_field#singular|plural}` the number of time
    // slots with the right noun after it, left out when there are none
    summaryToken: /\{([a-z_]+)(?:@([a-z_]+))?(?:#([^|}]+)\|([^}]+))?(?:\|([^|}]+)\|([^}]+))?\}/g,
    slotsSummarySeparator: ', ',

    // The class a slots field carries so the popover leaves the kit's controls to the kit's own styles
    slotsFieldClass: 'micro-form-field-own',

    // A slots popover is this wide from the start, so adding and removing ranges never changes its width
    slotsPopoverWidth: '560px',

    // A range's length comes from the kit in minutes, its units are compared in seconds
    secondsPerMinute: 60,

    // The keys of one time slot in the hidden slots field, shared with the Python side
    slotTimeFrom: 'time_from',
    slotTimeTo: 'time_to',
    slotIsOn: 'is_on',
    slotSeconds: 'silence_seconds',

    // What a hidden cell says of a checkbox, which is what the edit form reads a boolean back from
    cellTrue: 'True',
    cellFalse: 'False',
    cellEmpty: ''
};

// What the Django side told us about the page's alert fields
$.fn.zato.alerts_tab.settings = null;

// Which form's panel is bound at the moment, and the slots kits of the open popovers by line
$.fn.zato.alerts_tab.state = {
    panelId: null,
    fieldPrefix: '',
    slotsKits: {}
};

// The micro-forms kit installs the popover engine here
$.fn.zato.alerts_tab.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.alerts_tab.init = function(options) {

    var tab = $.fn.zato.alerts_tab;
    var configElement = document.getElementById(options.config_id);

    tab.settings = JSON.parse(configElement.textContent);

    // The seconds of each duration unit, by name
    var unitSeconds = {};

    tab.settings.duration_units.forEach(function(unit) {
        unitSeconds[unit.name] = unit.seconds;
    });

    tab.settings.unit_seconds = unitSeconds;

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: tab.config.popupClass,
        showHowItWorks: tab.config.showHowItWorks,
        showCancel: true,
        onDone: tab.render
    });

    tab.registerSlotsKind();
}

// /////////////////////////////////////////////////////////////////////////////

// What the tab is called in a dialog's tab strip
$.fn.zato.alerts_tab.tab_label = function() {
    var out = $.fn.zato.alerts_tab.settings.tab_label;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden columns of a row the tab's fields travel in, in the order the Django side lists them
$.fn.zato.alerts_tab.columns = function() {
    var out = $.fn.zato.alerts_tab.settings.storage_field_names.slice();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden cells of a new row, one per column above
$.fn.zato.alerts_tab.hidden_cells = function(item) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = '';

    settings.storage_field_names.forEach(function(fieldName) {

        var value = item[fieldName];
        var text;

        if(settings.checkbox_field_names.indexOf(fieldName) !== -1) {
            if(value == true) {
                text = tab.config.cellTrue;
            }
            else {
                text = tab.config.cellFalse;
            }
        }
        else if(value === undefined) {
            text = tab.config.cellEmpty;
        }
        else {
            text = value;
        }

        out += String.format("<td class='ignore'>{0}</td>", text);
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields on the form bound at the moment - a field
// of the page's own form goes by its own name, an alert setting by its alert name
$.fn.zato.alerts_tab.fieldId = function(fieldName) {

    var tab = $.fn.zato.alerts_tab;
    var alertPrefix = tab.settings.field_prefix;

    if(tab.settings.page_fields.indexOf(fieldName) !== -1) {
        alertPrefix = '';
    }

    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + alertPrefix + fieldName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The one way into the rendered Django form, which is what the kit's popovers read and write
$.fn.zato.alerts_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.alerts_tab.fieldId(fieldName));
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The id of one element of the bound panel - a line, a summary, an edit link or a slot
$.fn.zato.alerts_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.alerts_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// One field spec of a popover page
$.fn.zato.alerts_tab.buildSpec = function(fieldName, row, line) {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;

    var fieldKind = settings.field_kinds[fieldName];
    var isToggle = settings.toggle_kinds.indexOf(fieldKind) !== -1;
    var kind;

    if(isToggle) {
        kind = tab.config.specCheckbox;
    }
    else if(fieldKind === settings.text_kind) {
        kind = tab.config.specText;
    }
    else {
        kind = tab.config.specNumber;
    }

    var out = {
        field: fieldName,
        label: settings.field_labels[fieldName],
        kind: kind
    };

    // A switch sharing a row with numbers stands under a label like they do
    if(kind === tab.config.specCheckbox) {
        if(row.length > 1) {
            out.labelAbove = true;
        }
    }

    // A text shows what a value looks like while it is empty
    if(kind === tab.config.specText) {
        out.placeholder = line.text_fields[fieldName];
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// One micro-form per popover line
$.fn.zato.alerts_tab.buildDescriptors = function() {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        if(line.kind !== tab.config.kindPopover) {
            return;
        }

        // A line with a time slots field is the slots kit alone
        if(line.slots_field) {
            out[line.name] = {
                title: line.title,
                width: tab.config.slotsPopoverWidth,
                pages: [[{kind: settings.slots_kind, field: line.slots_field, line: line}]]
            };
            return;
        }

        var page = line.rows.map(function(row) {

            var specs = row.map(function(fieldName) {
                var spec = tab.buildSpec(fieldName, row, line);
                return spec;
            });

            var entry;

            if(specs.length === 1) {
                entry = specs[0];
            }
            else {
                entry = specs;
            }

            return entry;
        });

        // A line with a unit select has it right after the last of its numbers
        if(line.unit_field) {
            var lastEntry = page[page.length - 1];
            var lastSpec;

            if(Array.isArray(lastEntry)) {
                lastSpec = lastEntry[lastEntry.length - 1];
            }
            else {
                lastSpec = lastEntry;
            }

            lastSpec.unitField = line.unit_field;
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

    for(var fieldName in tab.settings.field_how_it_works) {
        out[tab.forms.inputId(fieldName)] = tab.settings.field_how_it_works[fieldName];
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

        var targetId;

        if(line.kind === tab.config.kindPopover) {
            targetId = tab.elementId('edit', line.name);
        }
        else {
            targetId = tab.fieldId(line.fields[0]);
        }

        out[targetId] = line.how_it_works;
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// One token of a summary as text
$.fn.zato.alerts_tab.formatToken = function(fieldName, countFieldName, slotsSingular, slotsPlural, singular, plural) {

    var tab = $.fn.zato.alerts_tab;
    var field = tab.field(fieldName);
    var value = field.val();
    var out;

    // The ranges of the day a slots field holds, said only when there are any
    if(slotsSingular !== undefined) {
        var slotsCount = JSON.parse(value).length;

        if(slotsCount === 0) {
            out = '';
        }
        else {
            out = tab.config.slotsSummarySeparator + $.fn.zato.count_text(slotsCount, slotsSingular, slotsPlural);
        }
    }

    // A unit select spells its noun both ways - the value is the singular, the label the plural
    else if(countFieldName !== undefined) {
        var count = parseInt(tab.field(countFieldName).val());
        var option = field.find('option:selected');
        out = $.fn.zato.count_text(count, option.val(), option.text());
    }

    else if(singular === undefined) {
        out = value;
    }

    else {
        out = $.fn.zato.count_text(parseInt(value), singular, plural);
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes a line's summary from its fields
$.fn.zato.alerts_tab.formatSummary = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var isOff = false;
    var isEmpty = false;

    // A line with a switch among its fields reads as its off text while the switch is off ..
    if(line.off_field) {
        if(!tab.field(line.off_field).is(':checked')) {
            isOff = true;
        }
    }

    // .. and a line that may be left empty reads as its empty text while its first field is
    if(line.summary_empty !== undefined) {
        if(tab.field(line.fields[0]).val() === '') {
            isEmpty = true;
        }
    }

    var out;

    if(isOff) {
        out = line.summary_off;
    }
    else if(isEmpty) {
        out = line.summary_empty;
    }
    else {
        out = line.summary.replace(tab.config.summaryToken, function(ignored, fieldName, countFieldName, slotsSingular, slotsPlural, singular, plural) {
            var text = tab.formatToken(fieldName, countFieldName, slotsSingular, slotsPlural, singular, plural);
            return text;
        });
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// A pick line shows its select while there is anything to list and the sentence
// with the create links otherwise
$.fn.zato.alerts_tab.applyPickState = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var hasOptions = tab.field(line.field).find('option').length > 1;

    var pickElement = document.getElementById(tab.elementId('pick', line.name));
    var emptyElement = document.getElementById(tab.elementId('empty', line.name));

    pickElement.hidden = !hasOptions;
    emptyElement.hidden = hasOptions;
}

// /////////////////////////////////////////////////////////////////////////////

// The live form updates configs of the pick lines of one form. The field prefix is the
// form's, the empty string for the create form and 'edit-' for the edit form.
$.fn.zato.alerts_tab.live_configs = function(fieldPrefix) {

    var tab = $.fn.zato.alerts_tab;
    var out = [];

    tab.settings.lines.forEach(function(line) {

        if(line.kind !== tab.config.kindPick) {
            return;
        }

        var selectId = tab.config.idPrefixDjango + fieldPrefix + tab.settings.field_prefix + line.field;

        out.push({
            object_type: line.live_type,
            handler: 'callback',
            snapshot_func: function() {
                var items = $.fn.zato.live_form_updates.snapshot_select('#' + selectId);
                return items;
            },
            on_diff: function(diff, skipPuff) {
                tab.applyPickDiff(line, selectId, diff, skipPuff);
            }
        });
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Applies one poll's differences to a pick select - options gone, renamed and new
$.fn.zato.alerts_tab.applyPickDiff = function(line, selectId, diff, skipPuff) {

    var tab = $.fn.zato.alerts_tab;
    var select = $('#' + selectId);

    diff.deleted.forEach(function(deletedId) {
        select.find('option').filter(function() {
            var matches = this.value === deletedId;
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

        if(!skipPuff) {
            $.fn.zato.live_form_updates.puff(option);
        }
    });

    // The bound form's own select is the one on show
    if(selectId === tab.fieldId(line.field)) {
        tab.applyPickState(line);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Dims the other lines when Active is off and lights them up again when it is on
$.fn.zato.alerts_tab.applyActiveState = function() {

    var tab = $.fn.zato.alerts_tab;
    var panel = $('#' + tab.state.panelId);
    var isActive = tab.field(tab.settings.is_active_field).is(':checked');

    if(isActive) {
        panel.removeClass(tab.config.offClass);
    }
    else {
        panel.addClass(tab.config.offClass);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Dims a line while the toggle it depends on is off
$.fn.zato.alerts_tab.applyDependentState = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var element = $('#' + tab.elementId('line', line.name));
    var isOn = tab.field(line.depends_on).is(':checked');

    if(isOn) {
        element.removeClass(tab.config.lineOffClass);
    }
    else {
        element.addClass(tab.config.lineOffClass);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Writes every line of the bound panel from the form
$.fn.zato.alerts_tab.render = function() {

    var tab = $.fn.zato.alerts_tab;

    tab.settings.lines.forEach(function(line) {

        if(line.kind === tab.config.kindPopover) {
            var summary = document.getElementById(tab.elementId('summary', line.name));
            summary.textContent = tab.formatSummary(line);
        }

        if(line.depends_on) {
            tab.applyDependentState(line);
        }

        if(line.kind === tab.config.kindPick) {
            tab.applyPickState(line);
        }
    });

    tab.applyActiveState();
}

// /////////////////////////////////////////////////////////////////////////////

// Wires one form's panel - call it each time before the dialog opens
$.fn.zato.alerts_tab.bind = function(options) {

    var tab = $.fn.zato.alerts_tab;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    tab.field(tab.settings.is_active_field).off('change.alerts_tab').on('change.alerts_tab', function() {
        tab.applyActiveState();
    });

    tab.settings.lines.forEach(function(line) {

        if(line.depends_on) {
            tab.field(line.depends_on).off('change.alerts_tab_' + line.name).on('change.alerts_tab_' + line.name, function() {
                tab.applyDependentState(line);
            });
        }

        if(line.kind !== tab.config.kindPopover) {
            return;
        }

        // The cursor lands in the first field of the line, its value left as it stands
        $('#' + tab.elementId('edit', line.name)).off('click.alerts_tab').on('click.alerts_tab', function() {
            tab.forms.open(line.name, this, line.fields[0]);
        });
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
