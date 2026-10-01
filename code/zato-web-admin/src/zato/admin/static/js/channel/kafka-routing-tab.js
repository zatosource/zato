
// The Routing tab of a Kafka channel's create and edit forms.

$.fn.zato.channel.kafka.routing_tab = {};

$.fn.zato.channel.kafka.routing_tab.config = {

    idPrefix: 'kafka-routing-tab',
    idPrefixDjango: 'id_',

    popoverClass: 'delivery-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    showHowItWorks: false,

    doneButtonClass: '',
    otherButtonClass: '',

    // The hidden field the rules travel in, as JSON
    fieldRouting: 'routing',

    // The scratch fields a rule is edited through
    fieldTopic: 'routing_topic',
    fieldHeaderName: 'routing_header_name',
    fieldHeaderValue: 'routing_header_value',
    fieldService: 'routing_service',

    // The keys of a stored rule
    keyTopic: 'topic',
    keyHeaderName: 'header_name',
    keyHeaderValue: 'header_value',
    keyService: 'service',

    ruleLine: 'rule',
    ruleTitle: 'Routing rule',

    labelTopic: 'Topic',
    labelHeaderName: 'Header',
    labelHeaderValue: 'Header value',
    labelService: 'Service',

    summaryAnyTopic: 'Any topic',
    summaryTopic: 'Topic {topic}',
    summaryHeaderAnyValue: 'header {name} present',
    summaryHeader: 'header {name} is {value}',
    summaryParts: ', ',

    emptyText: 'No rules',
    deleteLabel: 'Delete',

    helpRouting: 'Which service a message invokes. The first rule a message matches, from the top down, names its service. ' +
        'A message no rule matches invokes the channel\'s own service.',
    helpTopic: 'The topic the message has to come from, any topic when empty.',
    helpHeaderName: 'The name of a header the message has to carry, any header when empty.',
    helpHeaderValue: 'The value the header has to carry, any value when empty.',
    helpService: 'The service a matching message invokes.'
};

// A rule with no values
$.fn.zato.channel.kafka.routing_tab.config.emptyRule = {
    topic: '',
    header_name: '',
    header_value: '',
    service: ''
};

$.fn.zato.channel.kafka.routing_tab.state = {
    panelId: null,
    fieldPrefix: '',

    // The rules of the bound form
    rules: [],

    // The index of the rule being edited, or -1 for a rule being added
    editIndex: -1
};

$.fn.zato.channel.kafka.routing_tab.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.routing_tab.init = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popoverClass + ' ' + config.popupClass,
        showHowItWorks: config.showHowItWorks,
        doneButtonClass: config.doneButtonClass,
        otherButtonClass: config.otherButtonClass,
        showCancel: true,
        onDone: tab.onRuleDone
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The descriptor of the one micro-form, editing a rule through the scratch fields
$.fn.zato.channel.kafka.routing_tab.buildDescriptors = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;
    var out = {};

    out[config.ruleLine] = {
        title: config.ruleTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldTopic, label: config.labelTopic, kind: 'text'},
            [
                {field: config.fieldHeaderName, label: config.labelHeaderName, kind: 'text'},
                {field: config.fieldHeaderValue, label: config.labelHeaderValue, kind: 'text'}
            ],
            {field: config.fieldService, label: config.labelService, kind: 'select'}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields
$.fn.zato.channel.kafka.routing_tab.fieldId = function(fieldName) {
    var tab = $.fn.zato.channel.kafka.routing_tab;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// One of the tab's fields
$.fn.zato.channel.kafka.routing_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.channel.kafka.routing_tab.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel
$.fn.zato.channel.kafka.routing_tab.elementId = function(part) {
    var out = $.fn.zato.channel.kafka.routing_tab.state.panelId + '-' + part;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popover's inputs
$.fn.zato.channel.kafka.routing_tab.helpDescriptions = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;
    var out = {};

    out[tab.forms.inputId(config.fieldTopic)] = config.helpTopic;
    out[tab.forms.inputId(config.fieldHeaderName)] = config.helpHeaderName;
    out[tab.forms.inputId(config.fieldHeaderValue)] = config.helpHeaderValue;
    out[tab.forms.inputId(config.fieldService)] = config.helpService;

    return out;
}

// The how-it-works text of the tab, under the id of its add link
$.fn.zato.channel.kafka.routing_tab.descriptions = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var out = {};

    out[tab.elementId('add')] = tab.config.helpRouting;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The rules as the hidden field holds them
$.fn.zato.channel.kafka.routing_tab.readRules = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var text = tab.field(tab.config.fieldRouting).val();

    var out = JSON.parse(text);
    return out;
}

// Writes the rules back into the hidden field
$.fn.zato.channel.kafka.routing_tab.writeRules = function() {
    var tab = $.fn.zato.channel.kafka.routing_tab;
    tab.field(tab.config.fieldRouting).val(JSON.stringify(tab.state.rules));
}

// /////////////////////////////////////////////////////////////////////////////

// The one-line summary of what a rule matches
$.fn.zato.channel.kafka.routing_tab.formatMatch = function(rule) {

    var config = $.fn.zato.channel.kafka.routing_tab.config;
    var parts = [];

    var topic = rule[config.keyTopic];
    var headerName = rule[config.keyHeaderName];
    var headerValue = rule[config.keyHeaderValue];

    if(topic) {
        parts.push(config.summaryTopic.replace('{topic}', topic));
    }
    else {
        parts.push(config.summaryAnyTopic);
    }

    if(headerName) {
        if(headerValue) {
            parts.push(config.summaryHeader.replace('{name}', headerName).replace('{value}', headerValue));
        }
        else {
            parts.push(config.summaryHeaderAnyValue.replace('{name}', headerName));
        }
    }

    var out = parts.join(config.summaryParts);
    return out;
}

// The arrow between what a rule matches and the service it invokes
$.fn.zato.channel.kafka.routing_tab.arrow = function() {
    var out = $(
        '<svg class="kafka-routing-tab-arrow" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" ' +
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    );
    return out;
}

// The summary of a rule, as the elements of its line
$.fn.zato.channel.kafka.routing_tab.formatRule = function(rule) {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;

    var match = $('<span class="kafka-routing-tab-match"></span>');
    match.text(tab.formatMatch(rule));

    var service = $('<span class="kafka-routing-tab-service"></span>');
    service.text(rule[config.keyService]);

    var out = $('<span class="zato-link-face summary-link-text"></span>');
    out.append(match);
    out.append(tab.arrow());
    out.append(service);

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Renders the rule lines of the bound panel from the form
$.fn.zato.channel.kafka.routing_tab.render = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;
    var rules = tab.state.rules;

    var container = $('#' + tab.elementId('rules'));
    container.empty();

    if(rules.length === 0) {
        var empty = $('<div class="decision-line alerts-tab-line alerts-tab-always-on-line kafka-routing-tab-empty"></div>');
        var emptyText = $('<span class="zato-soft-hint"></span>');
        emptyText.text(config.emptyText);
        empty.append(emptyText);
        container.append(empty);
        return;
    }

    rules.forEach(function(rule, idx) {

        var line = $('<div class="decision-line alerts-tab-line alerts-tab-line-popover alerts-tab-always-on-line kafka-routing-tab-rule"></div>');
        line.attr('id', tab.elementId('rule-' + idx));

        var label = $('<span class="decision-line-label kafka-routing-tab-rule-number"></span>');
        label.text(String(idx + 1));

        var edit = $('<a href="javascript:void(0)" class="summary-link"></a>');
        edit.attr('id', tab.elementId('edit-rule-' + idx));
        edit.append(tab.formatRule(rule));
        edit.append('<span class="zato-soft-hint">Click to edit</span>');
        edit.on('click', function() {
            tab.openRule(idx, this);
        });

        var remove = $('<a href="javascript:void(0)" class="kafka-routing-tab-delete"></a>');
        remove.text(config.deleteLabel);
        remove.on('click', function() {
            tab.state.rules.splice(idx, 1);
            tab.writeRules();
            tab.render();
        });

        var slot = $('<span class="decision-line-slot"></span>');
        slot.append(edit);
        slot.append(remove);

        line.append(label);
        line.append(slot);
        container.append(line);
    });
}

// /////////////////////////////////////////////////////////////////////////////

// Seeds the scratch fields from a rule and opens the popover
$.fn.zato.channel.kafka.routing_tab.openRule = function(idx, anchor) {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;

    var rule;

    if(idx >= 0) {
        rule = tab.state.rules[idx];
    }
    else {
        rule = config.emptyRule;
    }

    tab.state.editIndex = idx;

    tab.field(config.fieldTopic).val(rule[config.keyTopic]);
    tab.field(config.fieldHeaderName).val(rule[config.keyHeaderName]);
    tab.field(config.fieldHeaderValue).val(rule[config.keyHeaderValue]);

    // A new rule invokes the first service listed.
    var serviceField = tab.field(config.fieldService);
    var service = rule[config.keyService];

    if(!service) {
        service = serviceField.find('option').first().val();
    }

    serviceField.val(service);

    tab.forms.open(config.ruleLine, anchor, config.fieldTopic);
}

// Reads the scratch fields back into the rule once its popover is accepted
$.fn.zato.channel.kafka.routing_tab.onRuleDone = function() {

    var tab = $.fn.zato.channel.kafka.routing_tab;
    var config = tab.config;

    var rule = {};
    rule[config.keyTopic] = tab.field(config.fieldTopic).val().trim();
    rule[config.keyHeaderName] = tab.field(config.fieldHeaderName).val().trim();
    rule[config.keyHeaderValue] = tab.field(config.fieldHeaderValue).val().trim();
    rule[config.keyService] = tab.field(config.fieldService).val();

    if(tab.state.editIndex >= 0) {
        tab.state.rules[tab.state.editIndex] = rule;
    }
    else {
        tab.state.rules.push(rule);
    }

    tab.state.editIndex = -1;
    tab.writeRules();
    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////

// Binds one form's panel, before the dialog opens
$.fn.zato.channel.kafka.routing_tab.bind = function(options) {

    var tab = $.fn.zato.channel.kafka.routing_tab;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;
    tab.state.rules = tab.readRules();
    tab.state.editIndex = -1;

    $('#' + tab.elementId('add')).off('click.routing_tab').on('click.routing_tab', function() {
        tab.openRule(-1, this);
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
