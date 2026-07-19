// HL7 MLLP channel wizard - state, step navigation and submit.
//
// The page is rendered by zato/channel/hl7/mllp-wizard.html. The rendered
// Django form is the single source of every field's value - its inputs carry
// all the defaults and the popover micro-forms read from and write back into
// them, so the payload posted on Finish is exactly what the full-page editor
// would post. This file holds the wizard-wide config and state, the step
// strip, the footer buttons and the actual save. The micro-forms live in
// forms.js, the destination rows in destinations.js and the summaries plus
// the review step in review.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.config = {

    // Messages shown next to the Finish button after a save attempt
    savedMessage: 'OK, saved',
    saveErrorMessage: 'Could not save',

    // How long the success message stays on screen before the redirect
    redirectDelayMs: 750,

    // How many steps the wizard has
    stepCount: 3,

    // The footer button label on the last step
    finishLabel: 'Finish',
    nextLabel: 'Next',

    // Where the security groups for the REST bridge come from
    securityGroupsUrl: '/zato/http-soap/get-security-groups/zato-api-creds/',

    // The rows the "How does it work?" badge walks through - anything
    // on a step body holding a labeled field
    helpRowSelector: '.mllp-wizard-name-row, .mllp-wizard-toggle-row, .mllp-wizard-section-title, .mllp-wizard-respond-from-row, .mllp-wizard-tolerance-grid',

    // Fields that must not be empty on submit - the same list the editor uses
    requiredFields: [
        'name',
        'service',
        'logging_level',
        'max_msg_size',
        'max_msg_size_unit',
        'recv_timeout',
        'start_seq',
        'end_seq',
        'default_character_encoding'
    ]
};

// ////////////////////////////////////////////////////////////////////////

// Filled in by init() and updated as the user moves through the steps
$.fn.zato.channel.hl7.mllp.wizard.state = {

    // Which step is on screen
    currentStep: 0,

    // Where the channel list page is
    listUrl: '',

    // Destination rows - {type, connection, isActive, options}
    destinationList: [],

    // Security groups for the REST bridge - [{id, name}]
    securityGroupList: [],

    // Which group IDs are selected - id -> true
    selectedGroups: {},

    // Whether the last uniqueness check found the name already taken
    isNameTaken: false
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.field = function(name) {
    var out = $('#id_' + name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page -
// the map the full-page editor uses, re-keyed for the popover inputs,
// plus entries for the controls only the wizard has.
$.fn.zato.channel.hl7.mllp.wizard.helpDescriptions = function() {

    var shared = $.fn.zato.channel.hl7.mllp.field_descriptions;
    var out = $.extend({}, shared);

    // The popover micro-forms name their inputs mllp-wizard-tippy-<field>
    for(var key in shared) {
        if(key.indexOf('id_') === 0) {
            out['mllp-wizard-tippy-' + key.substring(3)] = shared[key];
        }
    }

    // The step 1 transport toggles and the routing link ..
    out['mllp-wizard-toggle-mllp'] = 'When on, HL7 v2 messages framed with MLLP<br>are received over plain TCP.<br>When off, messages arrive over REST only.';
    out['mllp-wizard-toggle-rest'] = shared['id_use_rest'];
    out['mllp-wizard-edit-routing'] = 'Which incoming messages this channel accepts.<br>With no matchers, every message is accepted -<br>matchers filter by MSH header fields,<br>e.g. sending application or message type.';

    // .. and the step 2 destination controls.
    out['mllp-wizard-respond-from'] = shared['destinations-respond-from-create'];
    out['mllp-wizard-destination-type'] = 'The kind of the outgoing connection<br>this destination delivers to.';
    out['mllp-wizard-destination-connection'] = 'The connection each message is delivered to<br>after the service runs.';
    out['mllp-wizard-destination-active'] = 'Whether this destination receives messages.<br>Inactive destinations are skipped.';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.init = function(options) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.config;

    wizard.state.listUrl = options.list_url;

    // Mark the fields that must not be empty ..
    for(var fieldIdx = 0; fieldIdx < config.requiredFields.length; fieldIdx++) {
        $.fn.zato.data_table.set_field_required('#id_' + config.requiredFields[fieldIdx]);
    }

    // .. the transport, REST and routing cards on step 1 ..
    wizard.forms.initCards();

    // .. the destination rows and the option cards on step 2 ..
    wizard.destinations.init();
    wizard.review.initOptionCards();

    // .. the searchable select for services ..
    $.fn.zato.turn_selects_into_chosen('#mllp-wizard-service-row');

    // .. live uniqueness indicators for the name and the REST URL path,
    // with the name badge in the header following the checks ..
    $.fn.zato.validate_unique('#id_name', 'generic_connection', 'name', null, wizard.onNameCheckResult);
    $.fn.zato.validate_unique('#id_rest_url_path', 'channel_rest', 'url_path');

    // .. the header badge mirrors the name and edits it in place ..
    wizard.initNameBadge();

    // .. the per-field help badge in the footer - each popover micro-form
    // additionally wires a badge of its own when it opens ..
    $.fn.zato.how_it_works.init({
        badgeId: 'mllp-wizard-how-it-works',
        divId: '#mllp-wizard',
        fieldSelector: config.helpRowSelector,

        // The card has empty margin on its left, so the tooltips go there
        // instead of covering the rows above the described field
        placement: 'left',
        descriptions: wizard.helpDescriptions()
    });

    // .. keep the service select fresh while the page is open ..
    $.fn.zato.live_form_updates.register('create', [
        {object_type: 'service', target_select: '#id_service'}
    ]);
    $.fn.zato.live_form_updates.start('create');

    // .. security groups for the REST bridge arrive asynchronously ..
    $.fn.zato.post(config.securityGroupsUrl, wizard._onSecurityGroupsLoaded, '', '', true);

    // .. the tabs jump straight to their step ..
    $('#mllp-wizard-steps .mllp-wizard-step').on('click', function() {
        wizard.goToStep(parseInt($(this).attr('data-step')));
    });

    // .. the footer buttons ..
    $('#mllp-wizard-back').on('click', function() {
        wizard.goToStep(wizard.state.currentStep - 1);
    });

    $('#mllp-wizard-next').on('click', function() {
        var isLastStep = wizard.state.currentStep === config.stepCount - 1;
        if(isLastStep) {
            wizard.save();
        }
        else {
            wizard.goToStep(wizard.state.currentStep + 1);
        }
    });

    $('#mllp-wizard-cancel').on('click', function() {
        window.location.href = wizard.state.listUrl;
    });

    // .. the name badge follows the name as the user types ..
    $('#id_name').on('input', function() {
        wizard.state.isNameTaken = false;
        wizard.updateNameBadge();
    });

    // .. show the first step ..
    wizard.review.refreshSummaries();
    wizard.goToStep(0);

    // .. and fade the page in.
    $.fn.zato.dashboard_kit.reveal();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard._onSecurityGroupsLoaded = function(data, status) {

    if(status != 'success') {
        return;
    }

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    wizard.state.securityGroupList = $.parseJSON(data.responseText);
};

// ////////////////////////////////////////////////////////////////////////

// The name badge in the header - it mirrors the name field on every step,
// turns red when the uniqueness check finds the name taken and opens
// the shared inline-edit form when clicked.
$.fn.zato.channel.hl7.mllp.wizard.updateNameBadge = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var badge = $('#mllp-wizard-name-badge');
    var name = wizard.field('name').val().trim();

    badge.prop('hidden', !name);
    badge.text(name);
    badge.toggleClass('mllp-wizard-name-badge-taken', wizard.state.isNameTaken);
};

// ////////////////////////////////////////////////////////////////////////

// Invoked by the shared uniqueness validator each time a check completes.
$.fn.zato.channel.hl7.mllp.wizard.onNameCheckResult = function(exists) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    wizard.state.isNameTaken = exists;
    wizard.updateNameBadge();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.initNameBadge = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.config;

    $('#mllp-wizard-name-badge').on('click', function() {
        var badge = this;

        $.fn.zato.inline_edit.form_tippy({
            link_elem: badge,
            title: 'Name',
            input_width: '18em',
            rows: [
                {name: 'name', label: 'Name', value: wizard.field('name').val()}
            ],
            validate: function(values) {
                if(!values.name) {
                    return 'This field is required: Name';
                }
                return '';
            },
            on_submit: function(values) {

                // Writing through the field runs everything the field's own
                // input event runs - the badge, the Next button and the
                // debounced uniqueness check.
                wizard.field('name').val(values.name);
                wizard.field('name').trigger('input');

                // The review step renders once, on entry - an edit made
                // while it is on screen has to re-render it by hand.
                if(wizard.state.currentStep === config.stepCount - 1) {
                    wizard.review.render();
                }
            }
        });
    });

    wizard.updateNameBadge();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.goToStep = function(stepIndex) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.config;

    if(stepIndex < 0) {
        return;
    }
    if(stepIndex >= config.stepCount) {
        return;
    }

    // Any open micro-form belongs to the step being left behind ..
    wizard.forms.close();

    wizard.state.currentStep = stepIndex;

    // .. show only the body of the current step ..
    for(var bodyIdx = 0; bodyIdx < config.stepCount; bodyIdx++) {
        var body = $('#mllp-wizard-step-body-' + bodyIdx);
        body.prop('hidden', bodyIdx !== stepIndex);
    }

    // .. the step strip marks where the user is and what is already done ..
    $('#mllp-wizard-steps .mllp-wizard-step').each(function() {
        var step = $(this);
        var stepNumber = parseInt(step.attr('data-step'));
        var isCurrent = stepNumber === stepIndex;

        step.removeClass('mllp-wizard-step-active mllp-wizard-step-done dashboard-tab-active');
        step.attr('aria-selected', isCurrent ? 'true' : 'false');

        if(isCurrent) {
            step.addClass('mllp-wizard-step-active dashboard-tab-active');
        }
        else if(stepNumber < stepIndex) {
            step.addClass('mllp-wizard-step-done');
        }
    });

    // .. the review step renders itself from the form each time it opens ..
    var isLastStep = stepIndex === config.stepCount - 1;
    if(isLastStep) {
        wizard.review.render();
    }

    // .. and the footer follows the position - there is nothing
    // to go back to from the first step.
    $('#mllp-wizard-back').prop('disabled', stepIndex === 0);
    $('#mllp-wizard-next').text(isLastStep ? config.finishLabel : config.nextLabel);
};

// ////////////////////////////////////////////////////////////////////////

// Security groups travel as one form input per selected group,
// named the way the create endpoint expects them.
$.fn.zato.channel.hl7.mllp.wizard._writeSecurityGroupInputs = function(form) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;

    form.find('.mllp-wizard-group-input').remove();

    for(var groupId in wizard.state.selectedGroups) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.className = 'mllp-wizard-group-input';
        input.name = 'mllp_security_group_checkbox_' + groupId;
        input.value = 'on';
        form.append(input);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.save = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.config;
    var form = $('#create-form');

    // The destination rows travel in hidden JSON fields the backend reads ..
    wizard.destinations.serialize();

    // .. so do the security groups selected for the REST bridge ..
    wizard._writeSecurityGroupInputs(form);

    // .. client-side validation first ..
    if(!$.fn.zato.is_form_valid(form)) {
        return;
    }

    // .. then the synchronous uniqueness checks ..
    if(!$.fn.zato.validate_unique_on_submit(form)) {
        return;
    }

    var statusElement = $('#mllp-wizard-status');
    statusElement.text('').removeClass('mllp-wizard-status-saved mllp-wizard-status-error');

    var callback = function(data, status) {

        if(status === 'success') {
            var response = JSON.parse(data.responseText);
            statusElement.text(config.savedMessage).addClass('mllp-wizard-status-saved');
            $('#user-message-div').hide();

            // Back to the list page, with the new channel highlighted
            setTimeout(function() {
                window.location.href = wizard.state.listUrl + '&highlight=' + response.id;
            }, config.redirectDelayMs);
        }
        else {
            statusElement.text(config.saveErrorMessage).addClass('mllp-wizard-status-error');
            $.fn.zato.user_message(false, data.responseText);
        }
    };

    // .. and the actual POST to the create endpoint.
    $.fn.zato.data_table._on_submit(form, callback);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
