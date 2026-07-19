// HL7 MLLP channel wizard - popover micro-forms and the step 1 cards.
//
// Each micro-form is described by a descriptor - a list of pages, each page
// a list of fields. A field points at one of the hidden Django form inputs
// by name, so opening a micro-form seeds its inputs from the form and
// pressing OK writes the answers back. Selects clone their choices from
// the underlying Django select, which keeps the wizard and the full-page
// editor on the same single list of options.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.forms.config = {

    // The tippy theme all the micro-forms share
    theme: 'mllp-wizard',

    // How wide a popover may grow
    maxWidth: 480,

    // Button labels inside the popovers
    backLabel: 'Back',
    nextLabel: 'Next',
    doneLabel: 'OK',

    // The per-field help of the popovers - the badge is rebuilt with every
    // page render, so one id can serve every micro-form
    helpBadgeId: 'mllp-wizard-popup-how-it-works',
    helpBadgeLabel: 'How does it work?',
    popupId: 'mllp-wizard-popup',

    // The list of security rows in the REST popover
    securityListId: 'mllp-wizard-security-list',

    // The value a security select carries when nothing is picked
    noSecurityValue: 'ZATO_NONE'
};

// The currently open popover, if any
$.fn.zato.channel.hl7.mllp.wizard.forms._instance = null;

// ////////////////////////////////////////////////////////////////////////

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
// A spec's optional width pins a field down to that many pixels.
$.fn.zato.channel.hl7.mllp.wizard.forms.descriptors = {

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
        arrow: false,
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

            // The title is the drag handle - the whole popover follows it
            forms._makeDraggable(tippyInstance);

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

        // Help mode dies with the popover it explains - otherwise its
        // state would keep pointing at elements about to leave the page
        var helpState = $.fn.zato.how_it_works._state;
        if(helpState && instance.popper.contains(helpState.container)) {
            $.fn.zato.how_it_works._deactivate();
        }

        instance.destroy();
    }
};

// ////////////////////////////////////////////////////////////////////////

// Builds a popover header - the shared grip glyph plus the text, acting
// as the drag handle every micro-form shares. Both the look and the grip
// come from the shared popup chrome the IDE menus use as well.
$.fn.zato.channel.hl7.mllp.wizard.forms.buildTitle = function(text) {

    var title = document.createElement('div');
    title.className = 'zato-popup-header';
    title.appendChild($.fn.zato.popup.build_grip());
    title.appendChild(document.createTextNode(text));

    var out = title;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The "How does it work?" badge every popover shows next to its buttons.
// Only one popover is open at a time, so a single id serves them all.
$.fn.zato.channel.hl7.mllp.wizard.forms.buildHelpBadge = function() {

    var config = $.fn.zato.channel.hl7.mllp.wizard.forms.config;

    var badge = document.createElement('span');
    badge.className = 'how-it-works-badge';
    badge.id = config.helpBadgeId;
    badge.textContent = config.helpBadgeLabel;

    var out = badge;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Wires up the help badge of one popover. Tippy attaches the popover to
// the document only when it shows, so this runs after showTippy and again
// whenever an open popover re-renders its fields.
$.fn.zato.channel.hl7.mllp.wizard.forms.initHelp = function(container) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.forms.config;

    if(!container.isConnected) {
        return;
    }

    // A help session left over from the page or from an earlier render
    // of this popover points at elements that just went away
    if($.fn.zato.how_it_works._state) {
        $.fn.zato.how_it_works._deactivate();
    }

    $.fn.zato.how_it_works.init({
        badgeId: config.helpBadgeId,
        divId: '#' + config.popupId,
        containerSelector: '.mllp-wizard-tippy-form',
        fieldSelector: '.mllp-wizard-tippy-field',

        // Several fields share one row, so a tooltip on the left would
        // cover the neighbor - above the field nothing is in the way
        placement: 'top',
        descriptions: wizard.helpDescriptions()
    });
};

// ////////////////////////////////////////////////////////////////////////

// Lets the popover be dragged around by its header, through the shared
// popup drag machinery. The offset is applied to the tippy box itself,
// so tippy's own positioning stays untouched.
$.fn.zato.channel.hl7.mllp.wizard.forms._makeDraggable = function(tippyInstance) {

    var handle = tippyInstance.popper.querySelector('.zato-popup-header');
    if(!handle) {
        return;
    }

    var box = tippyInstance.popper.querySelector('.tippy-box');
    var offsetX = 0;
    var offsetY = 0;

    $.fn.zato.popup.install_drag(handle, {

        dragging_elem: tippyInstance.popper.querySelector('.zato-popup'),

        on_start: function() {

            // The stock tippy CSS animates transform changes - the box must
            // follow the pointer instantly instead
            box.style.transitionProperty = 'visibility, opacity';

            return {'x': offsetX, 'y': offsetY};
        },

        on_move: function(x, y) {
            offsetX = x;
            offsetY = y;
            box.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// Clones the options of the Django security select into the given select,
// leaving out the values picked by the other rows so no definition can be
// assigned twice. The requested value stays picked if it still exists -
// when it does not, e.g. after a broadcast said the definition is gone,
// the select falls to its default choice instead.
$.fn.zato.channel.hl7.mllp.wizard.forms._fillSecuritySelect = function(select, value, excludeValues) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.forms.config;
    excludeValues = excludeValues || [];

    select.textContent = '';

    wizard.field('rest_security_id').find('option').each(function() {

        // Turning security off altogether is what the slider above
        // the rows is for - the rows only ever pick real definitions
        if(this.value === config.noSecurityValue) {
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
$.fn.zato.channel.hl7.mllp.wizard.forms._refreshSecurityRows = function(list) {

    var forms = $.fn.zato.channel.hl7.mllp.wizard.forms;
    var config = forms.config;

    var selects = list.querySelectorAll('select');

    var pickedValues = [];
    selects.forEach(function(select) {
        pickedValues.push(select.value);
    });

    selects.forEach(function(select, selectIdx) {

        var excludeValues = [];

        pickedValues.forEach(function(value, valueIdx) {
            var isMeaningful = value && value !== config.noSecurityValue;
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
$.fn.zato.channel.hl7.mllp.wizard.forms._addSecurityRow = function(list, value) {

    var forms = $.fn.zato.channel.hl7.mllp.wizard.forms;

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
$.fn.zato.channel.hl7.mllp.wizard.forms._renumberSecurityRows = function(list) {

    var selects = list.querySelectorAll('select');

    for(var selectIdx = 0; selectIdx < selects.length; selectIdx++) {
        selects[selectIdx].removeAttribute('id');
    }

    if(selects.length) {
        selects[0].id = 'mllp-wizard-tippy-rest_security_id';
    }
};

// ////////////////////////////////////////////////////////////////////////

// Refreshes every security row of an open REST popover from the Django
// form select after a live update changed the latter's options. A row
// whose pick was deleted elsewhere falls to the default choice - the row
// itself stays where it is.
$.fn.zato.channel.hl7.mllp.wizard.forms.refreshSecuritySelect = function() {

    var forms = $.fn.zato.channel.hl7.mllp.wizard.forms;

    var list = document.getElementById(forms.config.securityListId);
    if(!list) {
        return;
    }

    forms._refreshSecurityRows(list);
};

// ////////////////////////////////////////////////////////////////////////

// Builds one input row of a micro-form page, seeded from the Django form.
$.fn.zato.channel.hl7.mllp.wizard.forms._buildFieldRow = function(fieldSpec) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;

    var row = document.createElement('div');
    row.className = 'mllp-wizard-tippy-field';

    // The security rows of the REST popover - one select per definition,
    // with as many rows as needed, behind an on/off slider ..
    if(fieldSpec.kind === 'securityList') {
        var forms = wizard.forms;

        // .. the head is the label plus the tiny slider next to it ..
        var head = document.createElement('div');
        head.className = 'mllp-wizard-security-head';

        var listLabel = document.createElement('label');
        listLabel.className = 'mllp-wizard-tippy-label';
        listLabel.setAttribute('for', 'mllp-wizard-tippy-rest_security_id');
        listLabel.setAttribute('data-help-placement', 'left');
        listLabel.textContent = fieldSpec.label;
        head.appendChild(listLabel);

        var enabledToggle = document.createElement('input');
        enabledToggle.type = 'checkbox';
        enabledToggle.id = 'mllp-wizard-tippy-rest_security_enabled';
        enabledToggle.checked = wizard.state.isSecurityEnabled;
        head.appendChild(enabledToggle);

        row.appendChild(head);

        var list = document.createElement('div');
        list.className = 'mllp-wizard-security-list';
        list.id = forms.config.securityListId;
        row.appendChild(list);

        // .. sliding the slider off swaps the rows for this badge - the rows
        // themselves stay as they are, in case the slide was an accident ..
        var disabledBadge = document.createElement('span');
        disabledBadge.className = 'mllp-wizard-badge mllp-wizard-badge-alert mllp-wizard-badge-blink mllp-wizard-security-disabled';
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
                return disabledBadge.closest('.mllp-wizard-tippy-form') || document.body;
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

        var out = row;
        return out;
    }

    var formField = wizard.field(fieldSpec.field);
    var inputId = 'mllp-wizard-tippy-' + fieldSpec.field;

    // A checkbox carries its slider after the label it acts on ..
    if(fieldSpec.kind === 'checkbox') {
        var checkboxLabel = document.createElement('label');
        checkboxLabel.className = 'mllp-wizard-tippy-checkbox';
        checkboxLabel.setAttribute('for', inputId);

        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = inputId;
        checkbox.checked = formField.prop('checked');

        checkboxLabel.appendChild(document.createTextNode(fieldSpec.label + ' '));
        checkboxLabel.appendChild(checkbox);
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

// The flat list of field specs on a page - row entries contribute
// each of their fields.
$.fn.zato.channel.hl7.mllp.wizard.forms._pageFieldList = function(page) {

    var out = [];

    for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {
        var entry = page[entryIdx];

        if(Array.isArray(entry)) {
            out = out.concat(entry);
        }
        else {
            out.push(entry);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes the answers of one rendered page back into the Django form.
$.fn.zato.channel.hl7.mllp.wizard.forms._savePage = function(popper, page) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var pageFields = $.fn.zato.channel.hl7.mllp.wizard.forms._pageFieldList(page);

    for(var fieldIdx = 0; fieldIdx < pageFields.length; fieldIdx++) {
        var fieldSpec = pageFields[fieldIdx];

        // The security rows write into the wizard state, with the first
        // pick also landing in the Django select - a single security posts
        // exactly the way the full-page editor posts it. The rows survive
        // even with the slider off - only the Django select and the submit
        // treat the channel as having no security then ..
        if(fieldSpec.kind === 'securityList') {
            var config = $.fn.zato.channel.hl7.mllp.wizard.forms.config;
            var keyList = [];

            $(popper).find('.mllp-wizard-security-row select').each(function() {
                var value = this.value;
                var isEmpty = !value || value === config.noSecurityValue;

                if(!isEmpty && keyList.indexOf(value) === -1) {
                    keyList.push(value);
                }
            });

            var enabledToggle = popper.querySelector('#mllp-wizard-tippy-rest_security_enabled');
            var isEnabled = enabledToggle ? enabledToggle.checked : true;

            wizard.state.isSecurityEnabled = isEnabled;
            wizard.state.securityKeyList = keyList;

            var securityField = wizard.field('rest_security_id');
            if(isEnabled && keyList.length) {
                securityField.val(keyList[0]);
            }
            else {
                securityField.val(config.noSecurityValue);
            }
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
    container.className = 'mllp-wizard-tippy-form zato-popup';
    container.id = config.popupId;

    if(descriptor.width) {
        container.style.width = descriptor.width;
    }

    container.appendChild(forms.buildTitle(descriptor.title));

    var pageContainer = document.createElement('div');
    pageContainer.className = 'mllp-wizard-tippy-body';
    container.appendChild(pageContainer);

    var pageIndex = 0;

    var renderPage = function() {

        pageContainer.innerHTML = '';
        var page = descriptor.pages[pageIndex];

        for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {
            var entry = page[entryIdx];

            // A list entry is several fields sharing one row ..
            if(Array.isArray(entry)) {
                var rowContainer = document.createElement('div');
                rowContainer.className = 'mllp-wizard-tippy-row';

                for(var fieldIdx = 0; fieldIdx < entry.length; fieldIdx++) {
                    var rowField = forms._buildFieldRow(entry[fieldIdx]);
                    if(entry[fieldIdx].width) {
                        rowField.style.flex = '0 0 ' + entry[fieldIdx].width;
                    }
                    rowContainer.appendChild(rowField);
                }
                pageContainer.appendChild(rowContainer);
            }

            // .. everything else takes a line of its own.
            else {
                var fieldRow = forms._buildFieldRow(entry);
                if(entry.width) {
                    fieldRow.style.width = entry.width;
                }
                pageContainer.appendChild(fieldRow);
            }
        }

        var buttons = document.createElement('div');
        buttons.className = 'mllp-wizard-tippy-buttons';

        // The per-field help sits to the left of the buttons ..
        buttons.appendChild(forms.buildHelpBadge());

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

            // .. and OK writes everything back and closes the popover.
            else {
                forms.close();
                wizard.review.refreshSummaries();
            }
        });
        buttons.appendChild(forwardButton);

        pageContainer.appendChild(buttons);

        // Each render brings a fresh badge, so its help needs rewiring -
        // before the first show the popover is not attached yet and the
        // wiring happens right after showTippy instead
        forms.initHelp(container);
    };

    renderPage();

    forms.showTippy(targetElement, container);
    forms.initHelp(container);
};

// ////////////////////////////////////////////////////////////////////////

// Wires up the step 1 controls - the transport toggles and the routing cards.
$.fn.zato.channel.hl7.mllp.wizard.forms.initCards = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var forms = wizard.forms;

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
