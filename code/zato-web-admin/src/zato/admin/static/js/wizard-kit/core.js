// Wizard kit - the step engine and page state machine every multi-step
// wizard shares.
//
// A wizard page is one dashboard card holding a step strip, one body per
// step, a review on the last step and a footer with Back, Next and Cancel.
// The rendered Django form is the single source of every field's value -
// whatever a wizard shows on its steps reads from and writes back into the
// form, so the payload posted on Finish is exactly what the matching
// full-page editor would post.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// An instance module hands its own namespace over to setup, together with
// a config object - setup installs the generic machinery onto the
// namespace and the instance adds its specifics around it:
//
//      var wizard = $.fn.zato.channel.hl7.mllp.wizard;
//
//      $.fn.zato.wizard_kit.core.setup(wizard, {
//          idPrefix: 'mllp-wizard',
//          formSelector: '#create-form',
//          stepCount: 3,
//          requiredFields: ['name', 'service'],
//          helpRowSelector: '.dashboard-card-header, .wizard-name-row',
//          nameUnique: {source: 'generic_connection', field: 'name',
//              filterName: 'type_', filterValue: 'channel-hl7-mllp'},
//          onInit: function() { /* wire instance controls */ },
//          beforeSave: function(form) { /* write hidden fields */ }
//      });
//
// The config keys:
//
//      idPrefix       - every element id on the page starts with it, see
//                       the element contract below
//      formSelector   - the form that Finish posts
//      stepCount      - how many steps the wizard has
//      fieldPrefix    - optional, in front of Django field ids, e.g. 'edit-'
//      nameField      - the field the header badge mirrors, 'name' by default
//      requiredFields - fields that must not be empty on submit
//      helpRowSelector- optional, the rows the page-wide "How does it work?"
//                       badge walks through
//      nameUnique     - optional, a live uniqueness check for the name -
//                       {source, field, filterName, filterValue}
//      onInit         - optional, instance wiring run during init
//      beforeSave     - optional, runs before validation on Finish, e.g. to
//                       serialize rows into hidden fields
//      savedMessage, saveErrorMessage, redirectDelayMs, finishLabel,
//      nextLabel      - optional, the defaults below cover them
//
// The element contract - ids derived from idPrefix, all required:
//
//      #<idPrefix>              - the card, also the help badge's div
//      #<idPrefix>-steps        - the step strip, tabs carry .wizard-step
//                                 and a data-step attribute
//      #<idPrefix>-step-body-N  - one body per step, N counted from 0
//      #<idPrefix>-name-badge   - the header badge mirroring the name
//      #<idPrefix>-back, -next, -cancel, -status - the footer
//      #<idPrefix>-how-it-works - the page-wide help badge
//      #<idPrefix>-review       - where the review step renders
//
// The instance contract - the namespace must provide:
//
//      wizard.helpDescriptions()       - the help texts for every badge
//      wizard.review.render()          - renders the review step
//      wizard.review.refreshSummaries()- recomputes the card summaries
//
// setup(wizard, config) installs on the namespace: config, state, field,
// init, goToStep, save, updateNameBadge, initNameBadge, onNameCheckResult.
// The page then calls wizard.init({list_url: ...}) when the DOM is ready.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.core = {};

// ////////////////////////////////////////////////////////////////////////

// The defaults every wizard shares - the instance config overrides them
kit.core.defaults = {

    // Messages shown next to the Finish button after a save attempt
    savedMessage: 'OK, saved',
    saveErrorMessage: 'Could not save',

    // How long the success message stays on screen before the redirect
    redirectDelayMs: 750,

    // The footer button labels
    finishLabel: 'Finish',
    nextLabel: 'Next',

    // The field the header badge mirrors
    nameField: 'name'
};

// ////////////////////////////////////////////////////////////////////////

kit.core.setup = function(wizard, config) {

    wizard.config = $.extend({}, kit.core.defaults, config);

    // The kit's own state keys join whatever the instance seeded
    wizard.state = $.extend({

        // Which step is on screen
        currentStep: 0,

        // Where the list page is
        listUrl: '',

        // Whether the last uniqueness check found the name already taken
        isNameTaken: false

    }, wizard.state);

    var idPrefix = wizard.config.idPrefix;

// ////////////////////////////////////////////////////////////////////////

    // The one accessor into the rendered Django form
    wizard.field = function(name) {
        var fieldPrefix = wizard.config.fieldPrefix ? wizard.config.fieldPrefix : '';
        var out = $('#id_' + fieldPrefix + name);
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    wizard.init = function(options) {

        var wizardConfig = wizard.config;

        wizard.state.listUrl = options.list_url;

        // Mark the fields that must not be empty ..
        for(var fieldIdx = 0; fieldIdx < wizardConfig.requiredFields.length; fieldIdx++) {
            $.fn.zato.data_table.set_field_required('#id_' + wizardConfig.requiredFields[fieldIdx]);
        }

        // .. the instance wires its own controls ..
        if(wizardConfig.onInit) {
            wizardConfig.onInit();
        }

        // .. a live uniqueness indicator for the name, with the name badge
        // in the header following the checks ..
        if(wizardConfig.nameUnique) {
            var unique = wizardConfig.nameUnique;
            $.fn.zato.validate_unique('#id_' + wizardConfig.nameField, unique.source, unique.field,
                {filter_name: unique.filterName, filter_value: unique.filterValue}, wizard.onNameCheckResult);
        }

        // .. the header badge mirrors the name and edits it in place ..
        wizard.initNameBadge();

        // .. the per-field help badge in the footer - each popover
        // micro-form additionally wires a badge of its own when it opens ..
        if(wizardConfig.helpRowSelector) {
            $.fn.zato.how_it_works.init({
                badgeId: idPrefix + '-how-it-works',
                divId: '#' + idPrefix,
                fieldSelector: wizardConfig.helpRowSelector,

                // The card has empty margin on its left, so the tooltips go
                // there instead of covering the rows above the described field
                placement: 'left',
                descriptions: wizard.helpDescriptions()
            });
        }

        // .. the tabs jump straight to their step ..
        $('#' + idPrefix + '-steps .wizard-step').on('click', function() {
            wizard.goToStep(parseInt($(this).attr('data-step')));
        });

        // .. the footer buttons ..
        $('#' + idPrefix + '-back').on('click', function() {
            wizard.goToStep(wizard.state.currentStep - 1);
        });

        $('#' + idPrefix + '-next').on('click', function() {
            var isLastStep = wizard.state.currentStep === wizardConfig.stepCount - 1;
            if(isLastStep) {
                wizard.save();
            }
            else {
                wizard.goToStep(wizard.state.currentStep + 1);
            }
        });

        $('#' + idPrefix + '-cancel').on('click', function() {
            window.location.href = wizard.state.listUrl;
        });

        // .. the name badge follows the name as the user types ..
        $('#id_' + wizardConfig.nameField).on('input', function() {
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

    // The badge and the inline-edit form take turns owning the badge's tippy
    // slot - the form destroys whatever tooltip it finds there when it opens.
    // This puts a fresh verdict tooltip back in the slot, unless the form is
    // on screen right now, in which case the slot is its.
    wizard._ensureNameBadgeTippy = function() {

        var badge = document.getElementById(idPrefix + '-name-badge');

        if(badge._tippy) {
            if(badge._tippy.isNameVerdict) {
                return badge._tippy;
            }
            if(badge._tippy.state.isVisible) {
                return null;
            }
            badge._tippy.destroy();
        }

        var instance = tippy(badge, {
            content: '',
            allowHTML: true,
            theme: 'dark',
            arrow: true,
            placement: 'bottom'
        });

        instance.isNameVerdict = true;

        var out = instance;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The name badge in the header - it mirrors the name field on every
    // step, turns red when the uniqueness check finds the name taken and
    // opens the shared inline-edit form when clicked.
    wizard.updateNameBadge = function() {

        var badge = $('#' + idPrefix + '-name-badge');
        var name = wizard.field(wizard.config.nameField).val().trim();
        var isTaken = wizard.state.isNameTaken;

        badge.prop('hidden', !name);
        badge.text(isTaken ? 'Already taken: ' + name : name);
        badge.toggleClass('wizard-badge-alert', isTaken);

        // The hover tooltip follows the check's verdict
        var verdictTippy = wizard._ensureNameBadgeTippy();
        if(verdictTippy) {
            verdictTippy.setContent(isTaken ? 'This name is already taken' : 'Name is available');
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // Invoked by the shared uniqueness validator each time a check completes.
    wizard.onNameCheckResult = function(exists) {
        wizard.state.isNameTaken = exists;
        wizard.updateNameBadge();
    };

// ////////////////////////////////////////////////////////////////////////

    wizard.initNameBadge = function() {

        var wizardConfig = wizard.config;

        $('#' + idPrefix + '-name-badge').on('click', function() {
            var badge = this;

            $.fn.zato.inline_edit.form_tippy({
                link_elem: badge,
                title: 'Name',
                input_width: '18em',
                rows: [
                    {name: 'name', label: 'Name', value: wizard.field(wizardConfig.nameField).val()}
                ],
                validate: function(values) {
                    if(!values.name) {
                        return 'This field is required: Name';
                    }
                    return '';
                },
                on_submit: function(values) {

                    // Writing through the field runs everything the field's
                    // own input event runs - the badge, the Next button and
                    // the debounced uniqueness check.
                    wizard.field(wizardConfig.nameField).val(values.name);
                    wizard.field(wizardConfig.nameField).trigger('input');

                    // The review step renders once, on entry - an edit made
                    // while it is on screen has to re-render it by hand.
                    if(wizard.state.currentStep === wizardConfig.stepCount - 1) {
                        wizard.review.render();
                    }
                }
            });

            // The edit form just took over the badge's tippy slot - once it
            // is fully gone, however it was dismissed, the verdict tooltip
            // is due back in, which updateNameBadge takes care of.
            var formInstance = badge._tippy;
            if(formInstance && !formInstance.isNameVerdict) {
                formInstance.setProps({
                    onHidden: function() {
                        wizard.updateNameBadge();
                    }
                });
            }
        });

        wizard.updateNameBadge();
    };

// ////////////////////////////////////////////////////////////////////////

    wizard.goToStep = function(stepIndex) {

        var wizardConfig = wizard.config;

        if(stepIndex < 0) {
            return;
        }
        if(stepIndex >= wizardConfig.stepCount) {
            return;
        }

        // Any open micro-form belongs to the step being left behind ..
        wizard.forms.close();

        wizard.state.currentStep = stepIndex;

        // .. show only the body of the current step ..
        for(var bodyIdx = 0; bodyIdx < wizardConfig.stepCount; bodyIdx++) {
            var body = $('#' + idPrefix + '-step-body-' + bodyIdx);
            body.prop('hidden', bodyIdx !== stepIndex);
        }

        // .. the step strip marks where the user is and what is already done ..
        $('#' + idPrefix + '-steps .wizard-step').each(function() {
            var step = $(this);
            var stepNumber = parseInt(step.attr('data-step'));
            var isCurrent = stepNumber === stepIndex;

            step.removeClass('wizard-step-active wizard-step-done dashboard-tab-active');
            step.attr('aria-selected', isCurrent ? 'true' : 'false');

            if(isCurrent) {
                step.addClass('wizard-step-active dashboard-tab-active');
            }
            else if(stepNumber < stepIndex) {
                step.addClass('wizard-step-done');
            }
        });

        // .. the review step renders itself from the form each time it opens ..
        var isLastStep = stepIndex === wizardConfig.stepCount - 1;
        if(isLastStep) {
            wizard.review.render();
        }

        // .. and the footer follows the position - there is nothing
        // to go back to from the first step.
        $('#' + idPrefix + '-back').prop('disabled', stepIndex === 0);
        $('#' + idPrefix + '-next').text(isLastStep ? wizardConfig.finishLabel : wizardConfig.nextLabel);
    };

// ////////////////////////////////////////////////////////////////////////

    wizard.save = function() {

        var wizardConfig = wizard.config;
        var form = $(wizardConfig.formSelector);

        // The instance writes its hidden fields first, e.g. serialized rows ..
        if(wizardConfig.beforeSave) {
            wizardConfig.beforeSave(form);
        }

        // .. client-side validation next ..
        if(!$.fn.zato.is_form_valid(form)) {
            return;
        }

        // .. then the synchronous uniqueness checks ..
        if(!$.fn.zato.validate_unique_on_submit(form)) {
            return;
        }

        var statusElement = $('#' + idPrefix + '-status');
        statusElement.text('').removeClass('wizard-status-saved wizard-status-error');

        var callback = function(data, status) {

            if(status === 'success') {
                var response = JSON.parse(data.responseText);
                statusElement.text(wizardConfig.savedMessage).addClass('wizard-status-saved');
                $('#user-message-div').hide();

                // Back to the list page, with the new item highlighted
                setTimeout(function() {
                    window.location.href = wizard.state.listUrl + '&highlight=' + response.id;
                }, wizardConfig.redirectDelayMs);
            }
            else {
                statusElement.text(wizardConfig.saveErrorMessage).addClass('wizard-status-error');
                $.fn.zato.user_message(false, data.responseText);
            }
        };

        // .. and the actual POST to the create endpoint.
        $.fn.zato.data_table._on_submit(form, callback);
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
