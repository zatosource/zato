// HL7 MLLP channel wizard - popover micro-forms and the step 1 cards.
//
// Each micro-form is described by a descriptor - a list of pages, each page
// a list of fields. A field points at one of the hidden Django form inputs
// by name, so opening a micro-form seeds its inputs from the form and
// pressing Done writes the answers back. Selects clone their choices from
// the underlying Django select, which keeps the wizard and the full-page
// editor on the same single list of options.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.forms.config = {

    // The tippy theme all the micro-forms share
    theme: 'mllp-wizard',

    // How wide a popover may grow
    maxWidth: 380,

    // Button labels inside the popovers
    backLabel: 'Back',
    nextLabel: 'Next',
    doneLabel: 'Done',

    // The label of the link that turns the REST bridge off again
    restOffLabel: 'Turn off REST'
};

// The currently open popover, if any
$.fn.zato.channel.hl7.mllp.wizard.forms._instance = null;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.forms.descriptors = {

    'transport': {
        title: 'Protocol options',
        pages: [[
            {field: 'start_seq',  label: 'Start separator', kind: 'text'},
            {field: 'end_seq',    label: 'End separator',   kind: 'text'},
            {field: 'recv_timeout', label: 'Receive timeout (ms)', kind: 'text'},
            {field: 'max_msg_size', label: 'Max message size', kind: 'text', unitField: 'max_msg_size_unit'},
            {field: 'default_character_encoding', label: 'Encoding', kind: 'select'},
            {field: 'use_msh18_encoding', label: 'Read encoding from MSH-18', kind: 'checkbox'}
        ]]
    },

    'rest': {
        title: 'REST bridge',
        hasRestOff: true,
        pages: [[
            {field: 'rest_url_path', label: 'URL path', kind: 'text', placeholder: 'e.g. /api/hl7/v2'},
            {field: 'rest_security_id', label: 'Security', kind: 'select'},
            {field: 'rest_only', label: 'REST only - no MLLP listener', kind: 'checkbox'},
            {kind: 'groupList', label: 'Security groups'}
        ]]
    },

    'routing': {
        title: 'Message matchers',
        pages: [
            [
                {field: 'msh3_sending_app',        label: 'Sending application (MSH-3)',  kind: 'text'},
                {field: 'msh4_sending_facility',   label: 'Sending facility (MSH-4)',     kind: 'text'},
                {field: 'msh5_receiving_app',      label: 'Receiving application (MSH-5)', kind: 'text'},
                {field: 'msh6_receiving_facility', label: 'Receiving facility (MSH-6)',   kind: 'text'}
            ],
            [
                {field: 'msh9_message_type',   label: 'Message type (MSH-9.1)',  kind: 'text', placeholder: 'e.g. ORU'},
                {field: 'msh9_trigger_event',  label: 'Trigger event (MSH-9.2)', kind: 'text', placeholder: 'e.g. R01'},
                {field: 'msh11_processing_id', label: 'Processing ID (MSH-11)',  kind: 'text', placeholder: 'e.g. P'},
                {field: 'msh12_version_id',    label: 'Version (MSH-12)',        kind: 'text', placeholder: 'e.g. 2.5'}
            ]
        ]
    },

    'dedup': {
        title: 'Deduplication',
        pages: [[
            {field: 'dedup_ttl_value', label: 'Remember control IDs for', kind: 'text', unitField: 'dedup_ttl_unit',
                hint: 'Zero turns deduplication off'}
        ]]
    },

    'logging': {
        title: 'Logging and errors',
        pages: [[
            {field: 'should_return_errors', label: 'Return error details in NAK responses', kind: 'checkbox'},
            {field: 'should_log_messages',  label: 'Log each message to the server log',    kind: 'checkbox'},
            {field: 'logging_level', label: 'Log level', kind: 'select'}
        ]]
    }
};

// ////////////////////////////////////////////////////////////////////////

// Shows the given content element in a popover anchored to the target.
// This is the one place all the wizard's popovers come from, so they all
// close on Escape and on clicks outside, and only one is open at a time.
$.fn.zato.channel.hl7.mllp.wizard.forms.showTippy = function(targetElement, contentElement, onHidden) {

    var forms = $.fn.zato.channel.hl7.mllp.wizard.forms;
    var config = forms.config;

    forms.close();

    var instance = tippy(targetElement, {
        content: contentElement,
        allowHTML: true,
        trigger: 'manual',
        interactive: true,
        arrow: true,
        animation: 'fade',
        duration: [150, 150],
        placement: 'bottom-start',
        appendTo: document.body,
        theme: config.theme,
        maxWidth: config.maxWidth,
        zIndex: 100001,

        onShow: function(tippyInstance) {

            // Escape closes the popover ..
            var handleEscape = function(event) {
                if(event.key === 'Escape') {
                    forms.close();
                }
            };
            tippyInstance.handleEscape = handleEscape;
            document.addEventListener('keydown', handleEscape);

            // .. and so does a click anywhere outside of it.
            var handleOutsideMousedown = function(event) {
                var isInPopper = tippyInstance.popper.contains(event.target);
                var isOnTarget = targetElement.contains(event.target);
                if(!isInPopper && !isOnTarget) {
                    forms.close();
                }
            };
            tippyInstance.handleOutsideMousedown = handleOutsideMousedown;
            document.addEventListener('mousedown', handleOutsideMousedown);
        },

        onHide: function(tippyInstance) {
            document.removeEventListener('keydown', tippyInstance.handleEscape);
            document.removeEventListener('mousedown', tippyInstance.handleOutsideMousedown);

            if(onHidden) {
                onHidden();
            }
        },

        onShown: function(tippyInstance) {

            // The first input is ready for typing right away
            var firstInput = tippyInstance.popper.querySelector('input[type="text"], select');
            if(firstInput) {
                firstInput.focus();
            }
        }
    });

    forms._instance = instance;
    instance.show();

    var out = instance;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.forms.close = function() {

    var forms = $.fn.zato.channel.hl7.mllp.wizard.forms;

    if(forms._instance) {
        var instance = forms._instance;
        forms._instance = null;
        instance.destroy();
    }
};

// ////////////////////////////////////////////////////////////////////////

// Builds one input row of a micro-form page, seeded from the Django form.
$.fn.zato.channel.hl7.mllp.wizard.forms._buildFieldRow = function(fieldSpec) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;

    var row = document.createElement('div');
    row.className = 'mllp-wizard-tippy-field';

    // A list of security group checkboxes rather than a single input ..
    if(fieldSpec.kind === 'groupList') {
        var listLabel = document.createElement('label');
        listLabel.className = 'mllp-wizard-tippy-label';
        listLabel.textContent = fieldSpec.label;
        row.appendChild(listLabel);

        var groupList = wizard.state.securityGroupList;

        if(!groupList.length) {
            var emptyNote = document.createElement('div');
            emptyNote.className = 'mllp-wizard-tippy-hint';
            emptyNote.textContent = 'No security groups exist yet';
            row.appendChild(emptyNote);
        }

        for(var groupIdx = 0; groupIdx < groupList.length; groupIdx++) {
            var group = groupList[groupIdx];

            var groupLabel = document.createElement('label');
            groupLabel.className = 'mllp-wizard-tippy-checkbox';

            var groupInput = document.createElement('input');
            groupInput.type = 'checkbox';
            groupInput.className = 'mllp-wizard-tippy-group';
            groupInput.setAttribute('data-group-id', group.id);
            groupInput.checked = Boolean(wizard.state.selectedGroups[group.id]);

            groupLabel.appendChild(groupInput);
            groupLabel.appendChild(document.createTextNode(' ' + group.name));
            row.appendChild(groupLabel);
        }

        var out = row;
        return out;
    }

    var formField = wizard.field(fieldSpec.field);
    var inputId = 'mllp-wizard-tippy-' + fieldSpec.field;

    // A checkbox carries its label to the right of the box ..
    if(fieldSpec.kind === 'checkbox') {
        var checkboxLabel = document.createElement('label');
        checkboxLabel.className = 'mllp-wizard-tippy-checkbox';

        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = inputId;
        checkbox.checked = formField.prop('checked');

        checkboxLabel.appendChild(checkbox);
        checkboxLabel.appendChild(document.createTextNode(' ' + fieldSpec.label));
        row.appendChild(checkboxLabel);

        var out = row;
        return out;
    }

    // .. everything else has the label above the input.
    var label = document.createElement('label');
    label.className = 'mllp-wizard-tippy-label';
    label.setAttribute('for', inputId);
    label.textContent = fieldSpec.label;
    row.appendChild(label);

    var input;

    if(fieldSpec.kind === 'select') {

        // The choices are cloned from the Django select, the single source of options
        input = document.createElement('select');
        input.id = inputId;

        formField.find('option').each(function() {
            var option = document.createElement('option');
            option.value = this.value;
            option.textContent = this.textContent;
            input.appendChild(option);
        });
        input.value = formField.val();
    }
    else {
        input = document.createElement('input');
        input.type = 'text';
        input.id = inputId;
        input.value = formField.val();

        if(fieldSpec.placeholder) {
            input.placeholder = fieldSpec.placeholder;
        }
    }

    // Fields like max message size keep their unit select right next to the value
    if(fieldSpec.unitField) {
        var inputRow = document.createElement('div');
        inputRow.className = 'mllp-wizard-tippy-input-row';
        inputRow.appendChild(input);

        var unitFormField = wizard.field(fieldSpec.unitField);
        var unitSelect = document.createElement('select');
        unitSelect.id = 'mllp-wizard-tippy-' + fieldSpec.unitField;
        unitSelect.className = 'mllp-wizard-tippy-unit';

        unitFormField.find('option').each(function() {
            var unitOption = document.createElement('option');
            unitOption.value = this.value;
            unitOption.textContent = this.textContent;
            unitSelect.appendChild(unitOption);
        });
        unitSelect.value = unitFormField.val();

        inputRow.appendChild(unitSelect);
        row.appendChild(inputRow);
    }
    else {
        row.appendChild(input);
    }

    if(fieldSpec.hint) {
        var hint = document.createElement('div');
        hint.className = 'mllp-wizard-tippy-hint';
        hint.textContent = fieldSpec.hint;
        row.appendChild(hint);
    }

    var out = row;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes the answers of one rendered page back into the Django form.
$.fn.zato.channel.hl7.mllp.wizard.forms._savePage = function(popper, pageFields) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;

    for(var fieldIdx = 0; fieldIdx < pageFields.length; fieldIdx++) {
        var fieldSpec = pageFields[fieldIdx];

        // The group list writes into the wizard state instead of the form ..
        if(fieldSpec.kind === 'groupList') {
            var selectedGroups = {};

            $(popper).find('.mllp-wizard-tippy-group').each(function() {
                if(this.checked) {
                    selectedGroups[this.getAttribute('data-group-id')] = true;
                }
            });
            wizard.state.selectedGroups = selectedGroups;
            continue;
        }

        // .. everything else maps straight onto a form field.
        var input = popper.querySelector('#mllp-wizard-tippy-' + fieldSpec.field);
        var formField = wizard.field(fieldSpec.field);

        if(fieldSpec.kind === 'checkbox') {
            formField.prop('checked', input.checked);
        }
        else {
            formField.val(input.value);
        }

        if(fieldSpec.unitField) {
            var unitInput = popper.querySelector('#mllp-wizard-tippy-' + fieldSpec.unitField);
            wizard.field(fieldSpec.unitField).val(unitInput.value);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

// Opens the named micro-form anchored to the given element.
$.fn.zato.channel.hl7.mllp.wizard.forms.open = function(descriptorName, targetElement) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var forms = wizard.forms;
    var config = forms.config;
    var descriptor = forms.descriptors[descriptorName];

    var container = document.createElement('div');
    container.className = 'mllp-wizard-tippy-form';

    var title = document.createElement('div');
    title.className = 'mllp-wizard-tippy-title';
    title.textContent = descriptor.title;
    container.appendChild(title);

    var pageContainer = document.createElement('div');
    container.appendChild(pageContainer);

    var pageIndex = 0;

    var renderPage = function() {

        pageContainer.innerHTML = '';
        var pageFields = descriptor.pages[pageIndex];

        for(var fieldIdx = 0; fieldIdx < pageFields.length; fieldIdx++) {
            var fieldRow = forms._buildFieldRow(pageFields[fieldIdx]);
            pageContainer.appendChild(fieldRow);
        }

        var buttons = document.createElement('div');
        buttons.className = 'mllp-wizard-tippy-buttons';

        // The REST micro-form can switch the whole bridge off again ..
        if(descriptor.hasRestOff) {
            var offLink = document.createElement('span');
            offLink.className = 'mllp-wizard-tippy-off';
            offLink.textContent = config.restOffLabel;

            offLink.addEventListener('click', function() {
                wizard.field('use_rest').prop('checked', false);
                forms.close();
                wizard.review.refreshSummaries();
            });
            buttons.appendChild(offLink);
        }

        // .. multi-page micro-forms navigate with Back and Next ..
        if(pageIndex > 0) {
            var backButton = document.createElement('button');
            backButton.type = 'button';
            backButton.className = 'secondary-button';
            backButton.textContent = config.backLabel;

            backButton.addEventListener('click', function() {
                forms._savePage(pageContainer, descriptor.pages[pageIndex]);
                pageIndex--;
                renderPage();
            });
            buttons.appendChild(backButton);
        }

        var hasMorePages = pageIndex < descriptor.pages.length - 1;

        var forwardButton = document.createElement('button');
        forwardButton.type = 'button';
        forwardButton.className = 'action-button';
        forwardButton.textContent = hasMorePages ? config.nextLabel : config.doneLabel;

        forwardButton.addEventListener('click', function() {
            forms._savePage(pageContainer, descriptor.pages[pageIndex]);

            if(hasMorePages) {
                pageIndex++;
                renderPage();
            }

            // .. and Done writes everything back and closes the popover.
            else {
                forms.close();
                wizard.review.refreshSummaries();
            }
        });
        buttons.appendChild(forwardButton);

        pageContainer.appendChild(buttons);
    };

    renderPage();

    forms.showTippy(targetElement, container);
};

// ////////////////////////////////////////////////////////////////////////

// Wires up the step 1 cards - transport, the REST bridge and routing.
$.fn.zato.channel.hl7.mllp.wizard.forms.initCards = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var forms = wizard.forms;

    // The MLLP transport card opens the protocol options ..
    $('#mllp-wizard-card-transport').on('click', function() {
        forms.open('transport', this);
    });

    // .. the REST card switches the bridge on and opens its options ..
    $('#mllp-wizard-card-rest').on('click', function() {
        wizard.field('use_rest').prop('checked', true);
        wizard.review.refreshSummaries();
        forms.open('rest', this);
    });

    // .. the matching card switches the default flag off and opens the matchers ..
    $('#mllp-wizard-card-routing-match').on('click', function() {
        wizard.field('is_default').prop('checked', false);
        wizard.review.refreshSummaries();
        forms.open('routing', this);
    });

    // .. and the default card claims everything, so there is nothing to configure.
    $('#mllp-wizard-card-routing-default').on('click', function() {
        wizard.field('is_default').prop('checked', true);
        forms.close();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
