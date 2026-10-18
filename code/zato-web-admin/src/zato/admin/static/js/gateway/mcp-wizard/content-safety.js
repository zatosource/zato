// MCP gateway wizard - the content safety popover of step 2.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var forms = wizard.forms;
var safety = wizard.contentSafety;

// ////////////////////////////////////////////////////////////////////////

safety.config = {

    descriptorName: 'contentSafety',
    kindName: 'contentSafetyGrid',
    title: 'Content safety',
    width: 520,
    editLinkId: 'mcp-wizard-edit-safety',
    summaryId: 'mcp-wizard-summary-safety',
    holderId: 'mcp-wizard-safety-holder',
    hostsId: 'mcp-wizard-safety-hosts',

    columnCheck: 'Check',
    columnOn: 'On',
    columnMode: 'When found',

    allOffLabel: 'Off',
    removeLabel: 'Remove',
    countOpen: ' (',
    countClose: ')',
    separator: ', ',

    checks: [
        {label: 'Secrets', toggle: 'safeguards_secrets_enabled', mode: null},
        {label: 'Hidden control characters', toggle: 'safeguards_normalize_unicode', mode: 'safeguards_unicode_mode'},
        {label: 'Active HTML and Markdown', toggle: 'safeguards_sanitize_markup', mode: 'safeguards_markup_mode'},
        {label: 'URLs', toggle: 'safeguards_url_policy_enabled', mode: 'safeguards_url_mode'}
    ]
};

safety.state = {
    openUpdate: null
};

// ////////////////////////////////////////////////////////////////////////

safety._el = function(tagName, className, text) {

    var out = document.createElement(tagName);
    out.className = className;

    if(text !== null) {
        out.textContent = text;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

safety._modeText = function(check) {

    if(check.mode === null) {
        return safety.config.removeLabel;
    }

    var out = wizard.field(check.mode).find('option:selected').text();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

safety.summary = function() {

    var config = safety.config;
    var parts = [];

    config.checks.forEach(function(check) {
        if(wizard.field(check.toggle).prop('checked')) {
            parts.push(check.label + config.countOpen + safety._modeText(check).toLowerCase() + config.countClose);
        }
    });

    if(parts.length === 0) {
        return config.allOffLabel;
    }

    var out = parts.join(config.separator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

safety._switch = function(check) {

    var input = safety._el('input', '', null);
    input.type = 'checkbox';
    input.id = forms.inputId(check.toggle);

    input.addEventListener('change', function() {
        wizard.field(check.toggle).prop('checked', input.checked).trigger('change');
    });

    return input;
};

// ////////////////////////////////////////////////////////////////////////

// The help anchors a description to a label wrapping its control
safety._select = function(check) {

    var label = safety._el('label', '', null);
    var select = safety._el('select', 'micro-form-select', null);

    select.id = forms.inputId(check.mode);
    label.setAttribute('for', select.id);

    wizard.field(check.mode).find('option').each(function() {
        var option = safety._el('option', '', this.textContent);
        option.value = this.value;
        select.appendChild(option);
    });

    select.addEventListener('change', function() {
        wizard.field(check.mode).val(select.value).trigger('change');
    });

    label.appendChild(select);

    return label;
};

// ////////////////////////////////////////////////////////////////////////

safety._row = function(check) {

    var row = safety._el('tr', '', null);

    var nameCell = safety._el('td', 'mcp-safety-grid-name', null);
    var name = safety._el('label', '', check.label);
    name.setAttribute('for', forms.inputId(check.toggle));
    nameCell.appendChild(name);
    row.appendChild(nameCell);

    var switchCell = safety._el('td', 'mcp-safety-grid-switch', null);
    var input = safety._switch(check);
    switchCell.appendChild(input);
    row.appendChild(switchCell);

    var modeCell = safety._el('td', '', null);
    var select = null;

    if(check.mode === null) {
        modeCell.textContent = safety.config.removeLabel;
    }
    else {
        var modeLabel = safety._select(check);
        select = modeLabel.querySelector('select');
        modeCell.appendChild(modeLabel);
    }

    row.appendChild(modeCell);

    var update = function() {

        input.checked = wizard.field(check.toggle).prop('checked');

        if(select !== null) {
            select.value = wizard.field(check.mode).val();
        }
    };

    var out = {row: row, update: update};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

safety._build = function(fieldSpec, row) {

    var config = safety.config;
    var updates = [];

    row.classList.add('micro-form-field-own');

    var table = safety._el('table', 'mcp-safety-grid', null);
    var head = safety._el('tr', '', null);

    [config.columnCheck, config.columnOn, config.columnMode].forEach(function(title) {
        head.appendChild(safety._el('th', '', title));
    });
    table.appendChild(head);

    config.checks.forEach(function(check) {
        var built = safety._row(check);
        updates.push(built.update);
        table.appendChild(built.row);
    });

    var hostsRow = safety._el('tr', 'mcp-safety-grid-hosts', null);
    var hostsCell = safety._el('td', '', null);
    hostsCell.colSpan = 3;
    hostsCell.appendChild(document.getElementById(config.hostsId));
    hostsRow.appendChild(hostsCell);
    table.appendChild(hostsRow);

    row.appendChild(table);

    safety.state.openUpdate = function() {
        updates.forEach(function(update) {
            update();
        });
    };

    safety.state.openUpdate();
};

// ////////////////////////////////////////////////////////////////////////

safety._putAway = function() {

    var config = safety.config;

    safety.state.openUpdate = null;
    document.getElementById(config.holderId).appendChild(document.getElementById(config.hostsId));
};

// ////////////////////////////////////////////////////////////////////////

safety.open = function() {
    forms.open(safety.config.descriptorName, document.getElementById(safety.config.editLinkId));
};

// ////////////////////////////////////////////////////////////////////////

safety.edit = function() {
    safety.open();
};

// ////////////////////////////////////////////////////////////////////////

safety.refresh = function() {

    wizard.review.refreshSummaries();

    if(safety.state.openUpdate !== null) {
        safety.state.openUpdate();
    }
};

// ////////////////////////////////////////////////////////////////////////

safety.init = function() {

    safety.config.checks.forEach(function(check) {

        wizard.field(check.toggle).on('change', safety.refresh);

        if(check.mode !== null) {
            wizard.field(check.mode).on('change', safety.refresh);
        }
    });

    $('#' + safety.config.editLinkId).on('click', safety.open);
};

// ////////////////////////////////////////////////////////////////////////

// The controls write the fields directly, so OK only closes the popover
forms.registerKind(safety.config.kindName, {
    build: safety._build,
    save: function() {}
});

forms.descriptors[safety.config.descriptorName] = {
    title: safety.config.title,
    width: safety.config.width + 'px',
    floating: true,
    openAt: forms.openUnderSteps(safety.config.width),
    pages: [[{kind: safety.config.kindName}]],
    onClose: safety._putAway
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
