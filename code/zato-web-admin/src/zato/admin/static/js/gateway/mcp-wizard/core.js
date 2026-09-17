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

// The Alerts line of step 2 and its popover - the kit's, named under the page's prefix
wizard.alerts = $.fn.zato.wizard_alerts.create({wizard: wizard, idPrefix: 'mcp-wizard'});

// ////////////////////////////////////////////////////////////////////////

wizard.config_own = {

    // What the button ending either of the two actions says
    saveLabel: 'Save',

    // The sections the review is read in, each group of answers under its own -
    // the missing targets below name them too, which is why they are here rather
    // than in the review module, loaded after this one
    groups: {
        basics: 'Basics',
        tools: 'Tools',
        skills: 'Skills',
        security: 'Security',
        shaping: 'Response shaping',
        alerts: 'Alerts',
        gatewayOptions: 'Gateway options',
        compaction: 'Compaction',
        pii: 'PII removal',
        contentSafety: 'Content safety'
    },

    // The connection type the name has to be unique within - generic
    // connection names are unique per type rather than across all of them
    connectionType: 'gateway-mcp',

    // The action the badge pickers on step 1 are registered under - it is
    // what their element ids are derived from, with the security and skills
    // pickers additionally carrying the prefix their loaders add on their own
    pickerAction: 'wizard',
    securityPickerAction: 'sec-wizard',
    skillsPickerAction: 'skills-wizard',

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
        '.wizard-option-header, .decision-line, .mcp-wizard-field-grid, .mcp-wizard-pii-selects',

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

        // The size caps line, the Alerts line and the option cards of step 2 ..
        wizard.forms.initRows();
        wizard.alerts.init();
        wizard.review.initOptionCards();

        // .. the PII multi-selects, the URL allow list chips and the master
        // toggles enabling the safeguard fields under them - the same wiring
        // both actions share ..
        $.fn.zato.gateway.mcp._init_pii_selects(action);
        $.fn.zato.gateway.mcp._init_host_list(action);
        $.fn.zato.gateway.mcp._init_safeguard_toggles(action);

        // .. the tools the gateway exposes - the services and the outgoing
        // connections, each source of the one Tools card holding its own
        // picks - plus the security definitions it authenticates with and
        // the skills it serves as prompts ..
        wizard.toolSources.init();
        $.fn.zato.gateway.mcp.security_badge_picker.load(ownConfig.pickerAction, itemId);
        $.fn.zato.gateway.mcp.skills_badge_picker.load(ownConfig.pickerAction, itemId);

        // .. a live uniqueness indicator for the URL path - the name
        // has its own check through the kit config above ..
        $.fn.zato.validate_unique(wizard.fieldSelector('url_path'), 'http_soap', 'url_path');

        // .. and the email and LLM connections the Alerts popup picks from stay fresh
        // while the page is open - no reloading to pick up new ones.
        var liveConfigs = $.fn.zato.alerts_tab.live_configs(wizard.config.fieldPrefix);

        $.fn.zato.live_form_updates.register(action, liveConfigs);
        $.fn.zato.live_form_updates.start(action);
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

    // The name and the path a gateway already has are its own, so keeping them
    // is not the same as taking someone else's - this is what the uniqueness
    // checks compare each edit against
    if(options.is_edit) {
        wizard._rememberOwnValue(wizard.config.nameField);
        wizard._rememberOwnValue('url_path');
    }
};

// ////////////////////////////////////////////////////////////////////////

wizard._rememberOwnValue = function(fieldName) {

    var field = wizard.field(fieldName);
    field.data('zato-original-value', field.val());
};

// ////////////////////////////////////////////////////////////////////////

// The assigned zone of one badge picker - where the picks are read from,
// both on save and on the review step.
wizard.assignedBadges = function(pickerAction) {

    var out = $('#badge-zone-assigned-' + pickerAction + ' .badge-zone-body .security-badge');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every pick becomes one hidden input, in the very shape the create
// endpoint reads - mcp_service_* for the services, mcp_<source>_* for the
// connection sources and mcp_security_* for the security definitions.
wizard._writeBadgeInputs = function(form) {

    var ownConfig = wizard.config_own;

    form.find('input.badge-member-input').remove();

    var toolPicks = wizard.toolSources.allAssigned();

    for(var pickIndex = 0; pickIndex < toolPicks.length; pickIndex++) {

        var pick = toolPicks[pickIndex];
        var inputName;

        if(pick.key === 'services') {
            inputName = 'mcp_service_' + pick.name;
        } else {
            inputName = 'mcp_' + pick.key + '_' + pick.name;
        }

        form.append($('<input/>', {
            type: 'hidden',
            name: inputName,
            value: pick.name,
            'class': 'badge-member-input'
        }));
    }

    wizard.assignedBadges(ownConfig.securityPickerAction).each(function() {
        $.fn.zato.gateway.mcp.security_badge_picker_config.inject_hidden_input(form, $(this));
    });

    wizard.assignedBadges(ownConfig.skillsPickerAction).each(function() {
        $.fn.zato.gateway.mcp.skills_badge_picker_config.inject_hidden_input(form, $(this));
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

    // The badge pickers of step 1 ..
    out['badge-filter-text-wizard'] = 'What this gateway exposes as MCP tools - services and outgoing connections, ' +
        'each source on the list holding its own picks. Every assigned item becomes one tool ' +
        'an agent can discover and invoke. ' +
        'Click a badge to move it between the two zones, or drag a whole selection.';
    out['badge-filter-text-skills-wizard'] = 'The skills this gateway serves as MCP prompts. ' +
        'Each assigned skill becomes one prompt an agent can discover and read. ' +
        'Skills are authored on the AI - Skills screen. With none assigned, ' +
        'the gateway serves tools only.';
    out['badge-filter-text-sec-wizard'] = 'Security definitions used to authenticate incoming MCP requests. ' +
        'More than one can be assigned. With none assigned, the gateway accepts ' +
        'requests from anyone who knows its address.';

    // .. the size caps line of step 2 ..
    out['mcp-wizard-edit-size-caps'] = 'How large a tool response may grow and what happens to one over the cap. ' +
        'The line says what is currently set.';

    // .. the Alerts line and the inputs of its popover ..
    out['mcp-wizard-edit-alerts'] = 'Whether the gateway raises alerts and which ones - tool calls failing in a row, ' +
        'the share of them in the recent traffic, invalid tool calls, rejected responses, rejected and throttled callers, ' +
        'one session calling one tool over and over, slow tool calls, truncated responses, the volume of responses, ' +
        'a gateway that receives no tool calls at all and one that exposes too many tools. ' +
        'All but the last read the gateway\'s audit log, so the audit log option under More options has to be on ' +
        'for anything to be measured.';

    $.extend(out, wizard.alerts.descriptions());

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

        '<p>On <span class="wizard-title-help-step">01</span> you choose how agents connect - ' +
        'the address they call, the services they may invoke and the credentials they ' +
        'authenticate with. ' +
        'On <span class="wizard-title-help-step">02</span> you shape what they receive back - ' +
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
        'checked for unsafe content. Name the gateway, assign a ' +
        'service and keep the defaults.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
