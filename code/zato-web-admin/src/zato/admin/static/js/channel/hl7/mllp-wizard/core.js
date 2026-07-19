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
    selectedGroups: {}
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.field = function(name) {
    var out = $('#id_' + name);
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

    // .. live uniqueness indicators for the name and the REST URL path ..
    $.fn.zato.validate_unique('#id_name', 'generic_connection', 'name');
    $.fn.zato.validate_unique('#id_rest_url_path', 'channel_rest', 'url_path');

    // .. keep the service select fresh while the page is open ..
    $.fn.zato.live_form_updates.register('create', [
        {object_type: 'service', target_select: '#id_service'}
    ]);
    $.fn.zato.live_form_updates.start('create');

    // .. security groups for the REST bridge arrive asynchronously ..
    $.fn.zato.post(config.securityGroupsUrl, wizard._onSecurityGroupsLoaded, '', '', true);

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

    // .. the Next button follows the current step's validity as the user types ..
    $('#id_name').on('input', wizard.updateNextState);
    $('#id_service').on('change', wizard.updateNextState);

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

// Whether the given step's own answers are complete - step 1 needs a name,
// step 2 needs a service, the review step is always complete.
$.fn.zato.channel.hl7.mllp.wizard.isStepComplete = function(stepIndex) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var out = true;

    if(stepIndex === 0) {
        var name = wizard.field('name').val().trim();
        out = name !== '';
    }
    else if(stepIndex === 1) {
        var service = wizard.field('service').val();
        out = service !== '';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.updateNextState = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var isComplete = wizard.isStepComplete(wizard.state.currentStep);

    $('#mllp-wizard-next').prop('disabled', !isComplete);
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

        step.removeClass('mllp-wizard-step-active mllp-wizard-step-done');

        if(stepNumber === stepIndex) {
            step.addClass('mllp-wizard-step-active');
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

    // .. and the footer follows the position.
    // Hide Back on the first step so Next sits where Back would be
    $('#mllp-wizard-back').toggle(stepIndex !== 0);
    $('#mllp-wizard-next').text(isLastStep ? config.finishLabel : config.nextLabel);

    wizard.updateNextState();
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
