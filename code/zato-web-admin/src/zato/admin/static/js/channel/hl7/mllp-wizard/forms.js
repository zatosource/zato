// HL7 MLLP channel wizard - the micro-form descriptors and the step 1 cards.
//
// The popover engine itself comes from the wizard kit - this file declares
// which micro-forms the MLLP wizard has, registers the securityList field
// kind the REST popover uses and wires the step 1 transport toggles.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;
var forms = wizard.forms;

// ////////////////////////////////////////////////////////////////////////

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
// A spec's optional width pins a field down to that many pixels.
$.fn.zato.wizard_kit.forms.setup(wizard, {

    descriptors: {

        'transport': {
            title: 'Protocol options',
            width: '430px',
            pages: [[
                [
                    {field: 'start_seq',  label: 'Start separator', kind: 'text'},
                    {field: 'end_seq',    label: 'End separator',   kind: 'text'},
                    {field: 'recv_timeout', label: 'Receive timeout (ms)', kind: 'text'}
                ],
                [
                    {field: 'max_msg_size', label: 'Max message size', kind: 'text', unitField: 'max_msg_size_unit', width: '110px'},
                    {field: 'default_character_encoding', label: 'Encoding', kind: 'select'},
                    {field: 'use_msh18_encoding', label: 'Use MSH-18 too', kind: 'checkbox'}
                ]
            ]]
        },

        'rest': {
            title: 'REST options',
            width: '430px',
            pages: [[
                {field: 'rest_url_path', label: 'Path', kind: 'text', placeholder: 'e.g. /api/hl7/v2'},
                {kind: 'securityList', label: 'Security'}
            ]]
        },

        'routing': {
            title: 'Message matchers',
            width: '430px',
            pages: [[
                [
                    {field: 'msh3_sending_app',        label: 'Sending application (MSH-3)',  kind: 'text'},
                    {field: 'msh4_sending_facility',   label: 'Sending facility (MSH-4)',     kind: 'text'}
                ],
                [
                    {field: 'msh5_receiving_app',      label: 'Receiving application (MSH-5)', kind: 'text'},
                    {field: 'msh6_receiving_facility', label: 'Receiving facility (MSH-6)',   kind: 'text'}
                ],
                [
                    {field: 'msh9_message_type',   label: 'Message type (MSH-9.1)',  kind: 'text', placeholder: 'e.g. ORU'},
                    {field: 'msh9_trigger_event',  label: 'Trigger event (MSH-9.2)', kind: 'text', placeholder: 'e.g. R01'}
                ],
                [
                    {field: 'msh11_processing_id', label: 'Processing ID (MSH-11)',  kind: 'text', placeholder: 'e.g. P'},
                    {field: 'msh12_version_id',    label: 'Version (MSH-12)',        kind: 'text', placeholder: 'e.g. 2.5'}
                ]
            ]]
        },

        'dedup': {
            title: 'Deduplication',
            pages: [[
                {field: 'dedup_ttl_value', label: 'Remember control IDs for', kind: 'text', unitField: 'dedup_ttl_unit',
                    width: '210px'}
            ]]
        },

        'logging': {
            title: 'Logging and errors',
            pages: [[
                {field: 'should_return_errors', label: 'Return error details in NAK responses', kind: 'checkbox'},
                {field: 'should_log_messages',  label: 'Log each message to the server log',    kind: 'checkbox'},
                {field: 'logging_level', label: 'Log level', kind: 'select', width: '150px'}
            ]]
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

// The REST security rows - what only the MLLP wizard has on top of the
// kit's field kinds
forms.securityConfig = {

    // The list of security rows in the REST popover
    securityListId: 'mllp-wizard-security-list',

    // The value a security select carries when nothing is picked
    noSecurityValue: 'ZATO_NONE'
};

// ////////////////////////////////////////////////////////////////////////

// Clones the options of the Django security select into the given select,
// leaving out the values picked by the other rows so no definition can be
// assigned twice. The requested value stays picked if it still exists -
// when it does not, e.g. after a broadcast said the definition is gone,
// the select falls to its default choice instead.
forms._fillSecuritySelect = function(select, value, excludeValues) {

    var securityConfig = forms.securityConfig;
    excludeValues = excludeValues || [];

    select.textContent = '';

    wizard.field('rest_security_id').find('option').each(function() {

        // Turning security off altogether is what the slider above
        // the rows is for - the rows only ever pick real definitions
        if(this.value === securityConfig.noSecurityValue) {
            return;
        }

        if(excludeValues.indexOf(this.value) !== -1) {
            return;
        }

        var option = document.createElement('option');
        option.value = this.value;
        option.textContent = this.textContent;
        select.appendChild(option);
    });

    select.value = value;
    if(select.value !== value) {
        select.selectedIndex = 0;
    }
};

// ////////////////////////////////////////////////////////////////////////

// Rebuilds the options of every security row so each select offers only
// what the other rows have not taken. This runs after any change to the
// rows - a pick, a new row, a deleted row - and after a broadcast changed
// the underlying Django select.
forms._refreshSecurityRows = function(list) {

    var securityConfig = forms.securityConfig;

    var selects = list.querySelectorAll('select');

    var pickedValues = [];
    selects.forEach(function(select) {
        pickedValues.push(select.value);
    });

    selects.forEach(function(select, selectIdx) {

        var excludeValues = [];

        pickedValues.forEach(function(value, valueIdx) {
            var isMeaningful = value && value !== securityConfig.noSecurityValue;
            if(valueIdx !== selectIdx && isMeaningful) {
                excludeValues.push(value);
            }
        });

        forms._fillSecuritySelect(select, pickedValues[selectIdx], excludeValues);
    });
};

// ////////////////////////////////////////////////////////////////////////

// Appends one security row - a select plus the delete link to its right -
// to the list of security rows in the REST popover.
forms._addSecurityRow = function(list, value) {

    var row = document.createElement('div');
    row.className = 'mllp-wizard-security-row';

    var select = document.createElement('select');
    forms._fillSecuritySelect(select, value);
    row.appendChild(select);

    // A new pick here frees the old value for the other rows
    // and takes the new one away from them
    select.addEventListener('change', function() {
        forms._refreshSecurityRows(list);
    });

    // The icon itself is drawn by the stylesheet, from the shared close.svg
    var deleteLink = document.createElement('a');
    deleteLink.href = 'javascript:void(0)';
    deleteLink.className = 'mllp-wizard-security-delete';
    deleteLink.title = 'Remove';
    deleteLink.setAttribute('aria-label', 'Remove');

    deleteLink.addEventListener('click', function() {
        list.removeChild(row);

        // The list never goes fully empty - a blank row takes over
        if(!list.children.length) {
            forms._addSecurityRow(list, '');
        }
        forms._renumberSecurityRows(list);

        // The removed pick is up for grabs again in the remaining rows
        forms._refreshSecurityRows(list);
    });

    row.appendChild(deleteLink);
    list.appendChild(row);
};

// ////////////////////////////////////////////////////////////////////////

// The first select in the list carries the id that the Security label and
// its help tooltip point at - after every add or delete it moves as needed.
forms._renumberSecurityRows = function(list) {

    var selects = list.querySelectorAll('select');

    for(var selectIdx = 0; selectIdx < selects.length; selectIdx++) {
        selects[selectIdx].removeAttribute('id');
    }

    if(selects.length) {
        selects[0].id = forms.inputId('rest_security_id');
    }
};

// ////////////////////////////////////////////////////////////////////////

// Refreshes every security row of an open REST popover from the Django
// form select after a live update changed the latter's options. A row
// whose pick was deleted elsewhere falls to the default choice - the row
// itself stays where it is.
forms.refreshSecuritySelect = function() {

    var list = document.getElementById(forms.securityConfig.securityListId);
    if(!list) {
        return;
    }

    forms._refreshSecurityRows(list);
};

// ////////////////////////////////////////////////////////////////////////

// The securityList field kind - one select per definition, with as many
// rows as needed, behind an on/off slider.
forms.registerKind('securityList', {

    build: function(fieldSpec, row) {

        // The head is the label plus the tiny slider next to it ..
        var head = document.createElement('div');
        head.className = 'mllp-wizard-security-head';

        var listLabel = document.createElement('label');
        listLabel.className = 'wizard-tippy-label';
        listLabel.setAttribute('for', forms.inputId('rest_security_id'));
        listLabel.setAttribute('data-help-placement', 'left');
        listLabel.textContent = fieldSpec.label;
        head.appendChild(listLabel);

        var enabledToggle = document.createElement('input');
        enabledToggle.type = 'checkbox';
        enabledToggle.id = forms.inputId('rest_security_enabled');
        enabledToggle.checked = wizard.state.isSecurityEnabled;
        head.appendChild(enabledToggle);

        row.appendChild(head);

        var list = document.createElement('div');
        list.className = 'mllp-wizard-security-list';
        list.id = forms.securityConfig.securityListId;
        row.appendChild(list);

        // .. sliding the slider off swaps the rows for this badge - the rows
        // themselves stay as they are, in case the slide was an accident ..
        var disabledBadge = document.createElement('span');
        disabledBadge.className = 'wizard-badge wizard-badge-alert wizard-badge-blink mllp-wizard-security-disabled';
        disabledBadge.textContent = 'SECURITY DISABLED';
        row.appendChild(disabledBadge);

        // .. clicking the badge explains the situation - and any tooltip
        // already open in this popover leaves first, one at a time is enough ..
        tippy(disabledBadge, {
            content: 'Security is disabled - the channel will accept requests<br>' +
                'from anyone who knows its address.<br>' +
                'Slide security back on to require authentication.',
            allowHTML: true,
            theme: 'dark',
            arrow: true,
            trigger: 'click',
            placement: 'left',
            zIndex: 100002,
            appendTo: function() {
                return disabledBadge.closest('.wizard-tippy-form') || document.body;
            },
            onShow: function() {
                var helpState = $.fn.zato.how_it_works._state;
                if(helpState && helpState.container.contains(disabledBadge)) {
                    $.fn.zato.how_it_works._deactivate();
                }
            }
        });

        // .. the rows come from the wizard state, seeded from the Django
        // select the first time around ..
        var keyList = wizard.state.securityKeyList.slice();
        if(!keyList.length) {
            keyList = [wizard.field('rest_security_id').val() || ''];
        }

        for(var keyIdx = 0; keyIdx < keyList.length; keyIdx++) {
            forms._addSecurityRow(list, keyList[keyIdx]);
        }
        forms._renumberSecurityRows(list);
        forms._refreshSecurityRows(list);

        // .. the add link under the list grows it one row at a time ..
        var addLink = document.createElement('a');
        addLink.href = 'javascript:void(0)';
        addLink.className = 'mllp-wizard-security-add';
        addLink.textContent = 'Add security';

        addLink.addEventListener('click', function() {
            forms._addSecurityRow(list, '');
            forms._renumberSecurityRows(list);
            forms._refreshSecurityRows(list);
        });

        row.appendChild(addLink);

        // .. and the slider decides which of the two faces is on screen.
        var applyEnabledState = function() {
            var isOn = enabledToggle.checked;
            list.hidden = !isOn;
            addLink.hidden = !isOn;
            disabledBadge.hidden = isOn;

            // A tooltip must not outlive the badge it explains
            if(isOn && disabledBadge._tippy) {
                disabledBadge._tippy.hide();
            }
        };

        enabledToggle.addEventListener('change', applyEnabledState);
        applyEnabledState();
    },

// ////////////////////////////////////////////////////////////////////////

    // The security rows write into the wizard state, with the first pick
    // also landing in the Django select - a single security posts exactly
    // the way the full-page editor posts it. The rows survive even with
    // the slider off - only the Django select and the submit treat the
    // channel as having no security then.
    save: function(popper, fieldSpec) {

        var securityConfig = forms.securityConfig;
        var keyList = [];

        $(popper).find('.mllp-wizard-security-row select').each(function() {
            var value = this.value;
            var isEmpty = !value || value === securityConfig.noSecurityValue;

            if(!isEmpty && keyList.indexOf(value) === -1) {
                keyList.push(value);
            }
        });

        var enabledToggle = popper.querySelector('#' + forms.inputId('rest_security_enabled'));
        var isEnabled = enabledToggle ? enabledToggle.checked : true;

        wizard.state.isSecurityEnabled = isEnabled;
        wizard.state.securityKeyList = keyList;

        var securityField = wizard.field('rest_security_id');
        if(isEnabled && keyList.length) {
            securityField.val(keyList[0]);
        }
        else {
            securityField.val(securityConfig.noSecurityValue);
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

// Wires up the step 1 controls - the transport toggles and the routing cards.
forms.initCards = function() {

    // The MLLP toggle is the inverse of the REST-only flag ..
    $('#mllp-wizard-toggle-mllp').on('change', function() {
        var isMllpOn = this.checked;
        wizard.field('rest_only').prop('checked', !isMllpOn);

        // .. without the MLLP listener the messages have to arrive over REST.
        if(!isMllpOn) {
            wizard.field('use_rest').prop('checked', true);
        }
        wizard.review.refreshSummaries();
    });

    // .. the REST toggle drives the bridge flag ..
    $('#mllp-wizard-toggle-rest').on('change', function() {
        var isRestOn = this.checked;
        wizard.field('use_rest').prop('checked', isRestOn);

        // .. and with REST gone the MLLP listener has to stay on.
        if(!isRestOn) {
            wizard.field('rest_only').prop('checked', false);
        }
        wizard.review.refreshSummaries();
    });

    // .. clicking a summary link opens the matching options popover ..
    $('#mllp-wizard-edit-transport').on('click', function() {
        forms.open('transport', this);
    });

    $('#mllp-wizard-edit-rest').on('click', function() {
        forms.open('rest', this);
    });

    // .. and the routing summary link opens the MSH matchers.
    $('#mllp-wizard-edit-routing').on('click', function() {
        forms.open('routing', this);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
