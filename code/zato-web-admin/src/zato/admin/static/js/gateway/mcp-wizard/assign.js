// MCP gateway wizard - the popover the Tools, Skills and Security sections of step 1 open in.
//
// On the step, each of the three sections is a row with its summary. A click
// on a row opens this popover - a strip of three tabs, each naming its section
// and how many items it has assigned, and under it the pane with the section
// picked in the strip. The pane holds the section's own body, moved out of its card
// and back into it once another section is picked or the popover closes, so
// the pickers, the tool sources and the OAuth fields keep their state and
// the form keeps its inputs. The pickers edit the form directly, which is
// why OK only closes the popover.
//
// The layout is gateway/mcp-wizard-assign.css.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var forms = wizard.forms;
var assign = wizard.assign;

// ////////////////////////////////////////////////////////////////////////

assign.config = {

    descriptorName: 'assignments',
    kindName: 'assignSections',
    title: 'Tools, skills and security',

    // The size the popover first opens at
    width: 1000,
    height: 560,

    layoutClass: 'mcp-assign wizard-surface-pickers',
    indexClass: 'mcp-assign-index',
    entryClass: 'mcp-assign-entry mcp-masking-plain',
    entryCurrentClass: 'mcp-assign-entry-current',
    entryEmptyClass: 'mcp-assign-entry-empty',
    entryLabelClass: 'mcp-assign-entry-label',
    entryCountClass: 'mcp-assign-entry-count',
    countOpen: '(',
    countClose: ')',
    paneClass: 'mcp-assign-pane',
    growsClass: 'micro-form-grows',
    bodyOpenClass: 'wizard-option-body-open',

    // What the Security summary says while OAuth sign-in is active, e.g. OAuth sign-in (2 scopes)
    oauthLabel: 'OAuth sign-in',
    oauthCountOpen: ' (',
    scopeLabel: ' scope',
    scopesLabel: ' scopes',
    noScopesLabel: 'no scopes'
};

// The section in the pane, and the pane and the index entries while the popover is open
assign.state = {
    current: null,
    pane: null,
    entries: null
};

// ////////////////////////////////////////////////////////////////////////

assign.open = function(name, anchor) {

    // The popover already open returns its section to the card before the
    // new one is built, or closing it afterwards would take the section away
    forms.close();

    assign.state.current = name;
    forms.open(assign.config.descriptorName, anchor);
};

// ////////////////////////////////////////////////////////////////////////

assign._bodyOf = function(name) {
    var out = document.getElementById('mcp-wizard-' + name + '-body');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

assign._putBack = function(name) {

    var body = assign._bodyOf(name);

    body.classList.remove(assign.config.bodyOpenClass);
    document.getElementById('mcp-wizard-picker-' + name).appendChild(body);
};

// ////////////////////////////////////////////////////////////////////////

// ////////////////////////////////////////////////////////////////////////

assign._build = function(fieldSpec, row) {

    var config = assign.config;
    var state = assign.state;

    row.classList.add('micro-form-field-own');
    row.classList.add(config.growsClass);

    var layout = document.createElement('div');
    layout.className = config.layoutClass;

    var index = document.createElement('div');
    index.className = config.indexClass;
    index.setAttribute('role', 'tablist');

    var pane = document.createElement('div');
    pane.className = config.paneClass;

    state.pane = pane;
    state.entries = {};

    wizard.review.pickerCards().forEach(function(card) {
        var entry = assign._buildEntry(card);
        state.entries[card.name] = entry;
        index.appendChild(entry.element);
    });

    layout.appendChild(index);
    layout.appendChild(pane);
    row.appendChild(layout);

    assign._show(state.current);
    assign.refreshIndex();
};

// ////////////////////////////////////////////////////////////////////////

assign._buildEntry = function(card) {

    var config = assign.config;

    var element = document.createElement('button');
    element.type = 'button';
    element.className = config.entryClass;
    element.setAttribute('role', 'tab');

    var label = document.createElement('span');
    label.className = config.entryLabelClass;
    label.textContent = $('#mcp-wizard-' + card.name + '-header .wizard-option-label label').text();

    var count = document.createElement('span');
    count.className = config.entryCountClass;

    element.appendChild(label);
    element.appendChild(count);

    element.addEventListener('click', function() {
        assign._show(card.name);
        assign._bodyOf(card.name).querySelector('input[type="text"]').focus();
    });

    var out = {
        element: element,
        count: count
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

assign._show = function(name) {

    var config = assign.config;
    var state = assign.state;

    // The section in the pane returns to its card before the next one takes its place
    if(state.pane.firstChild !== null) {
        assign._putBack(state.current);
    }

    var body = assign._bodyOf(name);

    state.current = name;
    body.classList.add(config.bodyOpenClass);
    state.pane.appendChild(body);

    wizard.review.pickerCards().forEach(function(card) {
        var isCurrent = card.name === name;
        var element = state.entries[card.name].element;

        element.classList.toggle(config.entryCurrentClass, isCurrent);
        element.setAttribute('aria-selected', isCurrent ? 'true' : 'false');
    });
};

// ////////////////////////////////////////////////////////////////////////

// OAuth sign-in and how many scopes the clients ask the identity provider for.
assign.oauthSummary = function() {

    var config = assign.config;
    var mcp = $.fn.zato.gateway.mcp;

    var scopes = mcp._chip_list_split(wizard.field('oauth_scopes').val(), mcp.scope_list_config);

    var countText = config.noScopesLabel;

    if(scopes.length) {
        countText = scopes.length + (scopes.length === 1 ? config.scopeLabel : config.scopesLabel);
    }

    var out = config.oauthLabel + config.oauthCountOpen + countText + config.countClose;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The counts in the strip follow the assigned zones the way the summaries on the step do
assign.refreshIndex = function() {

    var config = assign.config;
    var state = assign.state;
    var review = wizard.review;

    // A closed popover has no strip
    if(state.entries === null) {
        return;
    }

    review.pickerCards().forEach(function(card) {
        var entry = state.entries[card.name];
        var assignedCount = review._cardCount(card);

        entry.count.textContent = config.countOpen + assignedCount + config.countClose;
        entry.element.classList.toggle(config.entryEmptyClass, assignedCount === 0);
    });
};

// ////////////////////////////////////////////////////////////////////////

assign._putAway = function() {

    var state = assign.state;

    assign._putBack(state.current);

    state.pane = null;
    state.entries = null;
};

// ////////////////////////////////////////////////////////////////////////

forms.registerKind(assign.config.kindName, {
    build: assign._build,
    save: function() {}
});

forms.descriptors[assign.config.descriptorName] = {
    title: assign.config.title,
    floating: true,
    openAt: forms.openUnderSteps(assign.config.width),
    size: {width: assign.config.width, height: assign.config.height},
    pages: [[{kind: assign.config.kindName}]],
    onClose: assign._putAway
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
