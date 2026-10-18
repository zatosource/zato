// MCP gateway wizard - data masking, at the head of the PII and data masking section.
//
// The answers name the fields masked in every tool response regardless of
// what the detectors find - the industry sets picked, the fields of those
// sets left out one by one, and the custom fields, which can be switched off
// as a whole while still kept. The data masking line opens the popover of
// masking-popover.js, which edits the state kept here, and the line-numbered
// editor of the custom fields is built here.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var dataMasking = wizard.dataMasking;
var maskingSets = wizard.maskingSets;

// ////////////////////////////////////////////////////////////////////////

dataMasking.config = {

    // Where the page embeds the stored answers, the defaults on create
    stateScriptId: 'mcp-wizard-masking-state',

    // The line in the PII and data masking section
    editLinkId: 'mcp-wizard-edit-data-masking',
    summaryId: 'mcp-wizard-summary-data-masking',

    // How many names the review shows before it counts the rest
    reviewNameLimit: 12,

    labels: {
        and: ' and ',
        more: ' more',
        field: ' field',
        fields: ' fields',
        custom: 'Custom',
        noFields: 'No fields',
        countOpen: ' (',
        countClose: ')',
        separator: ', '
    }
};

// ////////////////////////////////////////////////////////////////////////

// The sets picked in the order they were picked, the fields of picked sets
// left out, the custom fields in the order they were given and whether
// they are masked at all.
dataMasking.state = {
    sets: [],
    excluded: [],
    customFields: [],
    isCustomEnabled: true
};

// ////////////////////////////////////////////////////////////////////////

dataMasking.init = function() {

    var config = dataMasking.config;
    var state = dataMasking.state;

    var stateScript = document.getElementById(config.stateScriptId);
    var stored = JSON.parse(stateScript.textContent);

    state.sets = stored.sets;
    state.excluded = stored.excluded;
    state.customFields = stored.customFields;
    state.isCustomEnabled = stored.isCustomEnabled;

    $('#' + config.editLinkId).on('click', function() {
        wizard.maskingPopover.open(this);
    });
};

// ////////////////////////////////////////////////////////////////////////

dataMasking.refreshSummaries = function() {
    wizard.review.setSummary(dataMasking.config.summaryId, dataMasking.summary());
};

// ////////////////////////////////////////////////////////////////////////

// Every field a state masks - the fields of its sets less the ones left out,
// then its custom fields unless they are switched off, each field once.
dataMasking.maskedFields = function(state) {

    var setFields = maskingSets.union(state.sets);
    var kept = maskingSets.subtract(setFields, state.excluded);

    if(!state.isCustomEnabled) {
        return kept;
    }

    var out = maskingSets.merge(kept, state.customFields);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The names an editor holds - one per line, trimmed, blank lines left out
// and a name given twice kept once, where it first appears.
dataMasking.parse = function(text) {

    var out = [];
    var lineList = text.split('\n');

    for(var lineIdx = 0; lineIdx < lineList.length; lineIdx++) {

        var name = lineList[lineIdx].trim();

        if(name === '') {
            continue;
        }

        if(out.indexOf(name) === -1) {
            out.push(name);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many fields a list holds, with the noun agreeing with the count.
dataMasking.countLabel = function(fieldCount) {

    var labels = dataMasking.config.labels;

    if(fieldCount === 0) {
        return labels.noFields;
    }

    var noun = fieldCount === 1 ? labels.field : labels.fields;

    var out = fieldCount + noun;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the data masking line says - each set by name with how many of its
// fields are masked, then Custom with its own count when its fields are masked.
dataMasking.summary = function() {

    var state = dataMasking.state;
    var labels = dataMasking.config.labels;
    var masked = dataMasking.maskedFields(state);

    if(masked.length === 0) {
        return labels.noFields;
    }

    var parts = [];

    for(var setIdx = 0; setIdx < state.sets.length; setIdx++) {

        var setName = state.sets[setIdx];
        var setMasked = maskingSets.subtract(maskingSets.allFieldsOf(setName), state.excluded);

        parts.push(maskingSets.get(setName).label + labels.countOpen + setMasked.length + labels.countClose);
    }

    if(state.isCustomEnabled && state.customFields.length > 0) {
        parts.push(labels.custom + labels.countOpen + state.customFields.length + labels.countClose);
    }

    var out = parts.join(labels.separator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The value the review shows - the first of the masked fields and how many follow them.
dataMasking.reviewValue = function() {

    var config = dataMasking.config;
    var masked = dataMasking.maskedFields(dataMasking.state);

    if(masked.length === 0) {
        return config.labels.noFields;
    }

    var shown = masked.slice(0, config.reviewNameLimit);
    var out = shown.join(', ');

    var restCount = masked.length - shown.length;

    if(restCount > 0) {
        out += config.labels.and + restCount + config.labels.more;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Brings the gutter to one number per line of the editor.
dataMasking._syncGutter = function(gutter, textarea) {

    var lineCount = textarea.value.split('\n').length;

    if(gutter.childElementCount !== lineCount) {

        gutter.textContent = '';

        for(var lineIdx = 1; lineIdx <= lineCount; lineIdx++) {
            var number = document.createElement('div');
            number.className = 'mcp-field-list-gutter-line';
            number.textContent = lineIdx;
            gutter.appendChild(number);
        }
    }

    gutter.scrollTop = textarea.scrollTop;
};

// ////////////////////////////////////////////////////////////////////////

// Builds a line-numbered editor of field names into a host element. onChange
// receives the parsed names after every edit, typed or set through the
// returned setFields, and once right away.
dataMasking.buildEditor = function(host, inputId, fieldList, placeholder, onChange) {

    var editor = document.createElement('div');
    editor.className = 'mcp-field-list-editor';

    var gutter = document.createElement('div');
    gutter.className = 'mcp-field-list-gutter';

    var textarea = document.createElement('textarea');
    textarea.className = 'mcp-field-list-input';
    textarea.id = inputId;
    textarea.wrap = 'off';
    textarea.spellcheck = false;
    textarea.autocomplete = 'off';
    textarea.placeholder = placeholder;
    textarea.value = fieldList.join('\n');

    editor.appendChild(gutter);
    editor.appendChild(textarea);
    host.appendChild(editor);

    var refresh = function() {
        dataMasking._syncGutter(gutter, textarea);
        onChange(dataMasking.parse(textarea.value));
    };

    textarea.addEventListener('input', refresh);

    textarea.addEventListener('scroll', function() {
        gutter.scrollTop = textarea.scrollTop;
    });

    var setFields = function(fields) {
        textarea.value = fields.join('\n');
        refresh();
    };

    refresh();

    var out = {editor: editor, textarea: textarea, refresh: refresh, setFields: setFields};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
