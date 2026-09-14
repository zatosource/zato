// HL7 MLLP channel wizard - the Alerts line of step 2 and the popover it opens.
//
// The popover is one of the wizard's own micro-forms - the same chrome, the
// same OK - and inside it stand the lines of the Alerts tab the dialogs have,
// one per alert setting, its label on the left and on the right the switch,
// the pick or a summary of its numbers, which opens the setting's own popover
// when clicked. Which lines there are, what they say and what they explain
// comes from alerts-tab.js, the same source the dialogs read, and the lines'
// popovers are the tab's own, wearing the wizard's class.
//
// The panel of lines is built once and kept in a hidden holder of the form,
// with the switches and the picks of the alert settings standing in its lines,
// the way they stand in the tab of a dialog. Opening the popover moves the
// panel into it, closing puts it back, so the tab always finds its elements
// on the page, whether the popover is open or not.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;

wizard.alerts = {};
var alerts = wizard.alerts;

// ////////////////////////////////////////////////////////////////////////

alerts.config = {

    // The config alerts-tab.js reads the lines and the fields from
    configId: 'mllp-wizard-alerts-tab-config',

    // The line on step 2
    editLinkId: 'mllp-wizard-edit-alerts',
    summaryId: 'mllp-wizard-summary-alerts',

    // The popover - exactly as wide as its lines, the longest summary standing
    // on one line beside its label
    descriptorName: 'alerts',
    title: 'Alerts',

    // The panel of lines, what the tab names its elements under, and where
    // it waits while the popover is closed
    panelId: 'mllp-wizard-alerts',
    holderId: 'mllp-wizard-alerts-holder',
    linesKind: 'alertsLines',

    // The classes of the panel and its parts, under which mllp-wizard-controls.css lays them out
    panelClass: 'mllp-wizard-alerts',
    headingClass: 'mllp-wizard-alerts-heading',
    lineClass: 'mllp-wizard-alerts-line',
    activeLineClass: 'mllp-wizard-alerts-active-line',
    labelClass: 'mllp-wizard-alerts-label',
    slotClass: 'mllp-wizard-alerts-slot',
    emptyClass: 'mllp-wizard-alerts-empty',

    // What the line and the review say
    offLabel: 'Off',
    onLabel: 'On',
    separator: ', ',
    notPickedLabel: 'Not picked',

    // How a picked connection reads on the line, by the name of its pick line,
    // and what the line says while none is picked
    pickPhrases: {
        email: 'email to {0}',
        llm: 'explained by {0}'
    },
    pickEmpty: {
        email: 'no email connection',
        llm: 'no LLM connection'
    }
};

// The panel of lines, once built
alerts._panel = null;

// ////////////////////////////////////////////////////////////////////////

alerts.init = function() {

    var config = alerts.config;
    var tab = $.fn.zato.alerts_tab;

    // The lines' popovers are the tab's, wearing the wizard's class so they look like its own
    tab.init({config_id: config.configId, popup_class: wizard.forms.config.popupClass});

    // The popover is one row of the wizard's micro-forms, the panel of lines,
    // which goes back to its holder once the popover is gone
    wizard.forms.registerKind(config.linesKind, {
        build: alerts._buildLinesRow,
        save: function() {}
    });

    wizard.forms.descriptors[config.descriptorName] = {
        title: config.title,
        fitContent: true,
        pages: [[{kind: config.linesKind}]],
        onClose: alerts._putAway
    };

    // The panel's elements are named under the tab's panel id and its fields are
    // found under the wizard's prefix, so the tab knows both before the panel is built ..
    tab.state.panelId = config.panelId;
    tab.state.fieldPrefix = wizard.config.fieldPrefix;

    alerts._panel = alerts._buildPanel();
    document.getElementById(config.holderId).appendChild(alerts._panel);

    // .. and then wires the lines - the summaries, the dimming and the popovers
    // of the numbers - against the wizard's form
    tab.bind({panel_id: config.panelId, field_prefix: wizard.config.fieldPrefix});

    // The step 2 line follows the switches and the picks as they change
    tab.settings.lines.forEach(function(line) {
        if(line.kind !== tab.settings.line_kinds.popover) {
            tab.field(line.fields[0]).on('change', alerts.refreshSummary);
        }
    });

    $('#' + config.editLinkId).on('click', function() {
        alerts.open(this);
    });
};

// ////////////////////////////////////////////////////////////////////////

alerts.open = function(anchor) {
    wizard.forms.open(alerts.config.descriptorName, anchor);
};

// ////////////////////////////////////////////////////////////////////////

alerts.refreshSummary = function() {
    wizard.review.setSummary(alerts.config.summaryId, alerts.summary());
};

// ////////////////////////////////////////////////////////////////////////

// The popover's one row takes the panel of lines
alerts._buildLinesRow = function(fieldSpec, row) {
    row.classList.add('micro-form-field-own');
    row.appendChild(alerts._panel);
};

// ////////////////////////////////////////////////////////////////////////

// The popover is gone - the panel goes back to the form, and a line's popover
// still open over it goes too
alerts._putAway = function() {
    $.fn.zato.alerts_tab.forms.close();
    document.getElementById(alerts.config.holderId).appendChild(alerts._panel);
};

// ////////////////////////////////////////////////////////////////////////

// The panel - the lines of the tab under their section headings, save for the
// heading of the first section, which the popover's title covers
alerts._buildPanel = function() {

    var config = alerts.config;
    var tab = $.fn.zato.alerts_tab;

    var out = document.createElement('div');
    out.id = config.panelId;
    out.className = config.panelClass;

    var section = null;

    tab.settings.lines.forEach(function(line) {

        if(section !== null) {
            if(line.section !== section) {
                out.appendChild(alerts._buildHeading(line.section));
            }
        }

        section = line.section;

        out.appendChild(alerts._buildLine(line));
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

alerts._buildHeading = function(text) {

    var out = document.createElement('div');
    out.className = alerts.config.headingClass;
    out.textContent = text;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One line - its label on the left and, on the right, the switch, the pick or the
// summary link of the setting, under the ids the tab wires and writes them by
alerts._buildLine = function(line) {

    var config = alerts.config;
    var tab = $.fn.zato.alerts_tab;
    var lineKinds = tab.settings.line_kinds;

    var out = document.createElement('div');
    out.id = tab.elementId('line', line.name);
    out.className = config.lineClass;

    if(line.fields[0] === tab.settings.is_active_field) {
        out.classList.add(config.activeLineClass);
    }

    var label = document.createElement('label');
    label.className = config.labelClass;
    label.textContent = line.label;
    out.appendChild(label);

    var slot = document.createElement('span');
    slot.className = config.slotClass;
    out.appendChild(slot);

    // A switch is the alert setting's own checkbox, moved here from the form's hidden fields ..
    if(line.kind === lineKinds.toggle) {
        var toggle = tab.field(line.fields[0])[0];
        label.htmlFor = toggle.id;
        slot.appendChild(toggle);
    }

    // .. a pick is the setting's own select, with the sentence standing in for it while
    // there is nothing to pick from ..
    else if(line.kind === lineKinds.pick) {

        var select = tab.field(line.field)[0];
        label.htmlFor = select.id;

        var pick = document.createElement('span');
        pick.id = tab.elementId('pick', line.name);
        pick.appendChild(select);
        slot.appendChild(pick);

        var empty = document.createElement('span');
        empty.id = tab.elementId('empty', line.name);
        empty.className = config.emptyClass;
        empty.innerHTML = line.empty_html;
        slot.appendChild(empty);
    }

    // .. and the numbers of a setting read as a sentence that opens their popover -
    // without the hint the tab puts after it, whose room would stand empty at the
    // popover's right edge, the popover being exactly as wide as its longest line.
    else {

        var editId = tab.elementId('edit', line.name);
        label.htmlFor = editId;

        var link = document.createElement('a');
        link.href = 'javascript:void(0)';
        link.className = 'summary-link';
        link.id = editId;

        var summary = document.createElement('span');
        summary.className = 'zato-link-face summary-link-text';
        summary.id = tab.elementId('summary', line.name);
        link.appendChild(summary);

        slot.appendChild(link);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the lines, keyed by what each line's label points at -
// the switch, the select or the edit link. A field's id is its create form id, the
// help looks an edit form's field up under that one.
alerts.descriptions = function() {

    var tab = $.fn.zato.alerts_tab;
    var settings = tab.settings;
    var out = {};

    settings.lines.forEach(function(line) {

        var targetId;

        if(line.kind === settings.line_kinds.popover) {
            targetId = tab.elementId('edit', line.name);
        }
        else {
            var alertPrefix = settings.field_prefix;

            if(settings.page_fields.indexOf(line.fields[0]) !== -1) {
                alertPrefix = '';
            }

            targetId = tab.config.idPrefixDjango + alertPrefix + line.fields[0];
        }

        out[targetId] = line.how_it_works;
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether a line stands - one that depends on a switch stands only while the switch is on
alerts._isLineOn = function(line) {

    var tab = $.fn.zato.alerts_tab;

    if(!line.depends_on) {
        return true;
    }

    var out = tab.field(line.depends_on).is(':checked');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a pick line has picked, as its option's label, or an empty string
alerts._pickText = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var field = tab.field(line.field);

    if(!field.val()) {
        return '';
    }

    var out = field.find('option:selected').text();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the line says - Off, or On with where the alerts go and who explains them
alerts.summary = function() {

    var config = alerts.config;
    var tab = $.fn.zato.alerts_tab;
    var lineKinds = tab.settings.line_kinds;

    if(!tab.field(tab.settings.is_active_field).is(':checked')) {
        return config.offLabel;
    }

    var parts = [config.onLabel];

    tab.settings.lines.forEach(function(line) {

        if(line.kind !== lineKinds.pick) {
            return;
        }

        if(!alerts._isLineOn(line)) {
            return;
        }

        var text = alerts._pickText(line);

        if(text) {
            parts.push(String.format(config.pickPhrases[line.name], text));
        }
        else {
            parts.push(config.pickEmpty[line.name]);
        }
    });

    var out = parts.join(config.separator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The rows of the Alerts group of the review - every line of the tab with its answer
alerts.reviewRows = function() {

    var config = alerts.config;
    var tab = $.fn.zato.alerts_tab;
    var lineKinds = tab.settings.line_kinds;
    var out = [];

    tab.settings.lines.forEach(function(line) {

        if(!alerts._isLineOn(line)) {
            return;
        }

        var value;

        if(line.kind === lineKinds.popover) {
            value = tab.formatSummary(line);
        }
        else if(line.kind === lineKinds.toggle) {
            value = tab.field(line.fields[0]).is(':checked') ? config.onLabel : config.offLabel;
        }
        else {
            value = alerts._pickText(line);

            if(!value) {
                value = config.notPickedLabel;
            }
        }

        out.push([line.label, value]);
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
