// MCP gateway wizard - the wizard kit instance.
//
// The page is rendered by zato/gateway/mcp-wizard.html. The generic
// machinery - the step strip, the name badge, the footer and the save -
// comes from the wizard kit, configured here. This file holds only what
// is MCP's own: the required fields, the help texts, the wizard-wide
// overview and the badge picker inputs written on save. The micro-forms
// live in forms.js and the summaries plus the review step in review.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;

// ////////////////////////////////////////////////////////////////////////

wizard.config_own = {

    // What the button ending either of the two actions says
    saveLabel: 'Save',

    // The sections the review is read in, each group of answers under its own -
    // the missing targets below name them too, which is why they are here rather
    // than in the review module, loaded after this one
    groups: {
        basics: 'Basics',
        services: 'Services',
        security: 'Security',
        shaping: 'Response shaping',
        gatewayOptions: 'Gateway options',
        compaction: 'Compaction',
        pii: 'PII removal',
        contentSafety: 'Content safety'
    },

    // The connection type the name has to be unique within - generic
    // connection names are unique per type rather than across all of them
    connectionType: 'gateway-mcp',

    // The action the two badge pickers on step 1 are registered under - it is
    // what their element ids are derived from, with the security picker
    // additionally carrying the sec- prefix its loader adds on its own
    pickerAction: 'wizard',
    securityPickerAction: 'sec-wizard',

    // What the edit endpoint reads its input under - the edit page's Django
    // form is built with the same prefix and the kit's fieldPrefix follows it
    editFieldPrefix: 'edit-'
};

// ////////////////////////////////////////////////////////////////////////

// The instance's own state - the kit adds its keys on top
wizard.state = {

    // Which of the two actions the page is serving
    isEdit: false,

    // The gateway being edited - the badge pickers load with it so the
    // assigned zones open on what the gateway already exposes
    itemId: ''
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.core.setup(wizard, {

    idPrefix: 'mcp-wizard',
    formSelector: '#create-form',

    // How many steps the wizard has
    stepCount: 3,

    // What the create page is - the edit page says so in its init options
    // and the key is switched to the edit prefix before the kit's own init runs
    fieldPrefix: '',
    finishLabel: wizard.config_own.saveLabel,

    // The rows the "How does it work?" badge walks through - the card
    // header with the wizard-wide overview, then anything on a step
    // body holding a labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-field-row, ' +
        '.wizard-section-title, .wizard-line, .mcp-wizard-field-grid, .mcp-wizard-pii-selects',

    // Fields that must not be empty on submit
    requiredFields: [
        'name',
        'url_path',
        'characters_per_token'
    ],

    // Where each of them is read on the review and answered on its step - the
    // name and the path stand on rows of their own, the token estimate is
    // edited in the size caps popover, so the line opening it is what a
    // refused save points at
    missingTargets: {
        name:                 {group: wizard.config_own.groups.basics, label: 'Name'},
        url_path:             {group: wizard.config_own.groups.basics, label: 'URL path',
                               anchorSelector: '#mcp-wizard-row-url-path'},
        characters_per_token: {group: wizard.config_own.groups.shaping, label: 'Characters per token',
                               anchorSelector: '#mcp-wizard-line-size-caps'}
    },

    // The name check is scoped to MCP gateways because generic
    // connection names are unique per connection type
    nameUnique: {
        source: 'generic_connection',
        field: 'name',
        filterName: 'type_',
        filterValue: wizard.config_own.connectionType
    },

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        var ownConfig = wizard.config_own;

        // The shared control wiring reads its fields under action-derived ids,
        // and on edit the pickers load with the gateway so their assigned
        // zones open on what it already exposes
        var action = wizard.state.isEdit ? 'edit' : 'create';
        var itemId = wizard.state.isEdit ? wizard.state.itemId : null;

        // The size caps line and the option cards of step 2 ..
        wizard.forms.initRows();
        wizard.review.initOptionCards();

        // .. the PII multi-selects and the master toggles enabling the
        // safeguard fields under them - the same wiring both actions share ..
        $.fn.zato.gateway.mcp._init_pii_selects(action);
        $.fn.zato.gateway.mcp._init_safeguard_toggles(action);

        // .. the services and the security definitions the gateway exposes
        // and authenticates with, each in a badge picker of its own ..
        $.fn.zato.gateway.mcp.badge_picker.load(ownConfig.pickerAction, itemId);
        $.fn.zato.gateway.mcp.security_badge_picker.load(ownConfig.pickerAction, itemId);

        // .. and a live uniqueness indicator for the URL path - the name
        // has its own check through the kit config above.
        $.fn.zato.validate_unique(wizard.fieldSelector('url_path'), 'http_soap', 'url_path');
    },

// ////////////////////////////////////////////////////////////////////////

    beforeSave: function(form) {

        // The badge picks travel as the repeated hidden inputs the create
        // endpoint reads its services and security definitions from
        wizard._writeBadgeInputs(form);
    }
});

// ////////////////////////////////////////////////////////////////////////

// The page hands its resolved urls and which of the two actions it is over
// once the DOM is ready, and the kit's own init does the rest.
wizard._kitInit = wizard.init;

wizard.init = function(options) {

    wizard.state.isEdit = options.is_edit;
    wizard.state.itemId = options.item_id;

    // On edit the Django form carries the edit- prefix its endpoint reads its
    // input under, and every field lookup in the wizard follows it
    if(options.is_edit) {
        wizard.config.fieldPrefix = wizard.config_own.editFieldPrefix;
    }

    wizard._kitInit(options);
};

// ////////////////////////////////////////////////////////////////////////

// The assigned zone of one badge picker - where the picks are read from,
// both on save and on the review step.
wizard.assignedBadges = function(pickerAction) {

    var out = $('#badge-zone-assigned-' + pickerAction + ' .badge-zone-body .security-badge');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every badge assigned in either picker becomes one hidden input, in the
// very shape the create endpoint reads - mcp_service_* for the services
// and mcp_security_* for the security definitions.
wizard._writeBadgeInputs = function(form) {

    var ownConfig = wizard.config_own;

    form.find('input.badge-member-input').remove();

    wizard.assignedBadges(ownConfig.pickerAction).each(function() {
        $.fn.zato.gateway.mcp.badge_picker_config.inject_hidden_input(form, $(this));
    });

    wizard.assignedBadges(ownConfig.securityPickerAction).each(function() {
        $.fn.zato.gateway.mcp.security_badge_picker_config.inject_hidden_input(form, $(this));
    });
};

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page - the
// map keyed by field name, re-keyed for the popover inputs, plus entries
// for the controls that are not fields at all.
wizard.helpDescriptions = function() {

    var shared = $.fn.zato.gateway.mcp.field_descriptions;

    // The popover micro-forms name their inputs after the fields they mirror,
    // so the kit says each text again under the id its input takes
    var out = wizard.forms.helpDescriptions(shared);

    // The page title carries the wizard-wide overview
    out['mcp-wizard-title'] = wizard.titleHelp();

    // The two badge pickers of step 1 ..
    out['badge-filter-text-wizard'] = 'The services this gateway exposes as MCP tools. ' +
        'Each assigned service becomes one tool an agent can discover and invoke. ' +
        'Click a badge to move it between the two zones, or drag a whole selection.';
    out['badge-filter-text-sec-wizard'] = 'Security definitions used to authenticate incoming MCP requests. ' +
        'More than one can be assigned. With none assigned, the gateway will accept ' +
        'requests from anyone who knows its address.';

    // .. the size caps line of step 2 ..
    out['mcp-wizard-edit-size-caps'] = 'How large a tool response may grow and what happens to one over the cap. ' +
        'The line says what is currently set.';

    // .. and the options folded away under it.
    out['mcp-wizard-edit-options'] = 'Input validation and the audit log, the compaction of responses, ' +
        'PII removal and content safety. The line says what is currently set.';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The wizard-wide overview shown when the page title is clicked - one of
// the regular "How does it work?" stops. Everyone gets the short pitch,
// and the MCP primer waits folded inside for those who want the
// background - the help tooltips are interactive, so the fold can be
// clicked open in place.
wizard.titleHelp = function() {

    var out =
        '<div class="wizard-title-help">' +

        '<p>This wizard creates a gateway - the endpoint through which ' +
        'AI agents reach the services of the platform.</p>' +

        '<p><span class="wizard-title-help-step">01</span> decides how agents connect - ' +
        'the address they call, the services they may invoke and the credentials they ' +
        'authenticate with. ' +
        '<span class="wizard-title-help-step">02</span> shapes what they receive back - ' +
        'response size, compaction and safety. ' +
        '<span class="wizard-title-help-step">03</span> is a review before the gateway is created.</p>' +

        '<details class="wizard-title-help-details">' +
        '<summary>New to MCP? A 30-second primer</summary>' +
        '<div class="wizard-title-help-primer">' +

        '<p>MCP, the Model Context Protocol, is how AI agents and assistants ' +
        'discover and call tools offered by other systems.</p>' +

        '<p>A gateway is such an offer - it exposes a set of services under one ' +
        'URL path, each service appearing to the agent as one tool with its own ' +
        'input schema.</p>' +

        '<p>Everything an agent receives back flows through the gateway, which is ' +
        'where responses can be capped in size, compacted, cleared of PII and ' +
        'checked for unsafe content. If in doubt, name the gateway, assign a ' +
        'service and keep the defaults.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
