// HL7 MLLP channel wizard - the destination rows on step 2.
//
// Destinations show as compact one-line rows, each opening a popover
// micro-form for its details, the same interaction the step 1 cards use.
// The rows serialize into the form's hidden "destinations" and
// "respond_from" fields in the very shape the full-page editor produces,
// reusing the type and option definitions of the shared destinations module.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.destinations.config = {

    // What the caller's response defaults to
    respondFromService: 'service',
    respondFromServiceLabel: 'The service',

    // The label of rows whose destination is inactive
    inactiveLabel: 'inactive',

    // The label of the popover's confirm button
    doneLabel: 'OK'
};

// Connections grouped by destination type, loaded once per page
$.fn.zato.channel.hl7.mllp.wizard.destinations._connectionData = null;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.destinations.init = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var destinations = wizard.destinations;

    // Adding a row waits until the connection list has arrived ..
    $('#mllp-wizard-destination-add').on('click', function() {
        var addLink = this;

        destinations._withConnectionData(function() {
            destinations.add(addLink);
        });
    });

    // .. and picking the response source updates the hidden field right away.
    $('#mllp-wizard-respond-from').on('change', function() {
        wizard.field('respond_from').val($(this).val());
    });

    destinations.refreshRespondFrom();
};

// ////////////////////////////////////////////////////////////////////////

// Runs the callback once the connection list is available,
// loading it on the first call and caching it for the rest of the page.
$.fn.zato.channel.hl7.mllp.wizard.destinations._withConnectionData = function(callback) {

    var destinations = $.fn.zato.channel.hl7.mllp.wizard.destinations;

    if(destinations._connectionData) {
        callback();
        return;
    }

    var onLoaded = function(data, status) {
        if(status === 'success') {
            destinations._connectionData = JSON.parse(data.responseText);
            callback();
        }
    };
    $.fn.zato.post($.fn.zato.destinations.config.connectionListUrl, onLoaded, '', '', true);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.destinations.add = function(anchorElement) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var destinations = wizard.destinations;

    var destination = {
        type: $.fn.zato.destinations.config.defaultType,
        connection: '',
        isActive: true,
        options: {}
    };
    wizard.state.destinationList.push(destination);

    var newIndex = wizard.state.destinationList.length - 1;
    destinations.openEditor(newIndex, anchorElement);
};

// ////////////////////////////////////////////////////////////////////////

// The one-line label a destination row shows - type, connection and options.
$.fn.zato.channel.hl7.mllp.wizard.destinations._rowLabel = function(destination) {

    var typeList = $.fn.zato.destinations.config.typeList;

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        if(typeList[typeIdx].id === destination.type) {
            var typeLabel = typeList[typeIdx].label;
            break;
        }
    }

    var parts = [typeLabel, destination.connection];

    for(var optionName in destination.options) {
        parts.push(destination.options[optionName]);
    }

    var out = parts.join(' - ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.wizard.destinations.renderRows = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var destinations = wizard.destinations;
    var config = destinations.config;

    var container = $('#mllp-wizard-destination-rows');
    container.empty();

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {
        var destination = wizard.state.destinationList[destinationIdx];

        var row = document.createElement('div');
        row.className = 'mllp-wizard-conn-row';
        row.setAttribute('data-destination-index', destinationIdx);

        var text = document.createElement('span');
        text.className = 'mllp-wizard-conn-row-text';
        text.textContent = destinations._rowLabel(destination);
        row.appendChild(text);

        if(!destination.isActive) {
            var inactive = document.createElement('span');
            inactive.className = 'mllp-wizard-conn-row-inactive';
            inactive.textContent = config.inactiveLabel;
            row.appendChild(inactive);
        }

        var remove = document.createElement('span');
        remove.className = 'mllp-wizard-conn-row-remove';
        remove.textContent = 'x';
        remove.title = 'Remove';
        row.appendChild(remove);

        container.append(row);
    }

    // Clicking a row edits it, the little x at its end removes it ..
    container.find('.mllp-wizard-conn-row').on('click', function(event) {
        var row = this;
        var destinationIndex = parseInt(row.getAttribute('data-destination-index'));

        if($(event.target).hasClass('mllp-wizard-conn-row-remove')) {
            wizard.state.destinationList.splice(destinationIndex, 1);
            destinations.renderRows();
            destinations.refreshRespondFrom();
            return;
        }

        destinations._withConnectionData(function() {
            destinations.openEditor(destinationIndex, row);
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

// Builds the connection select and the per-type option inputs for one type.
$.fn.zato.channel.hl7.mllp.wizard.destinations._renderTypeFields = function(container, destination) {

    var destinations = $.fn.zato.channel.hl7.mllp.wizard.destinations;

    container.innerHTML = '';

    // The connections of this type ..
    var connectionRow = document.createElement('div');
    connectionRow.className = 'mllp-wizard-tippy-field';

    var connectionLabel = document.createElement('label');
    connectionLabel.className = 'mllp-wizard-tippy-label';
    connectionLabel.setAttribute('for', 'mllp-wizard-destination-connection');
    connectionLabel.textContent = 'Connection';
    connectionRow.appendChild(connectionLabel);

    var connectionSelect = document.createElement('select');
    connectionSelect.id = 'mllp-wizard-destination-connection';

    var connectionList = destinations._connectionData[destination.type];

    for(var connectionIdx = 0; connectionIdx < connectionList.length; connectionIdx++) {
        var option = document.createElement('option');
        option.value = connectionList[connectionIdx].name;
        option.textContent = connectionList[connectionIdx].name;
        connectionSelect.appendChild(option);
    }

    if(destination.connection) {
        connectionSelect.value = destination.connection;
    }

    connectionRow.appendChild(connectionSelect);
    container.appendChild(connectionRow);

    // .. and the options this type supports, e.g. the HTTP method.
    var optionDefs = $.fn.zato.destinations.config.optionList[destination.type];

    for(var optionIdx = 0; optionIdx < optionDefs.length; optionIdx++) {
        var optionDef = optionDefs[optionIdx];

        var optionRow = document.createElement('div');
        optionRow.className = 'mllp-wizard-tippy-field';

        var optionLabel = document.createElement('label');
        optionLabel.className = 'mllp-wizard-tippy-label';
        optionLabel.textContent = optionDef.label;
        optionRow.appendChild(optionLabel);

        var optionInput;

        if(optionDef.kind === 'select') {
            optionInput = document.createElement('select');
            for(var valueIdx = 0; valueIdx < optionDef.values.length; valueIdx++) {
                var valueOption = document.createElement('option');
                valueOption.value = optionDef.values[valueIdx];
                valueOption.textContent = optionDef.values[valueIdx];
                optionInput.appendChild(valueOption);
            }
        }
        else {
            optionInput = document.createElement('input');
            optionInput.type = 'text';
            optionInput.placeholder = optionDef.placeholder;
        }

        optionInput.className = 'mllp-wizard-destination-option';
        optionInput.setAttribute('data-option-id', optionDef.id);

        if(destination.options[optionDef.id]) {
            optionInput.value = destination.options[optionDef.id];
        }

        optionRow.appendChild(optionInput);
        container.appendChild(optionRow);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Opens the micro-form for one destination row.
$.fn.zato.channel.hl7.mllp.wizard.destinations.openEditor = function(destinationIndex, anchorElement) {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var destinations = wizard.destinations;
    var destination = wizard.state.destinationList[destinationIndex];

    var container = document.createElement('div');
    container.className = 'mllp-wizard-tippy-form zato-popup';
    container.id = wizard.forms.config.popupId;

    container.appendChild(wizard.forms.buildTitle('Destination'));

    // The fields live under the header, in the popup body
    var body = document.createElement('div');
    body.className = 'mllp-wizard-tippy-body';
    container.appendChild(body);

    // The type select drives what the rest of the form shows ..
    var typeRow = document.createElement('div');
    typeRow.className = 'mllp-wizard-tippy-field';

    var typeLabel = document.createElement('label');
    typeLabel.className = 'mllp-wizard-tippy-label';
    typeLabel.setAttribute('for', 'mllp-wizard-destination-type');
    typeLabel.textContent = 'Type';
    typeRow.appendChild(typeLabel);

    var typeSelect = document.createElement('select');
    typeSelect.id = 'mllp-wizard-destination-type';

    var typeList = $.fn.zato.destinations.config.typeList;

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        var typeOption = document.createElement('option');
        typeOption.value = typeList[typeIdx].id;
        typeOption.textContent = typeList[typeIdx].label;
        typeSelect.appendChild(typeOption);
    }
    typeSelect.value = destination.type;

    typeRow.appendChild(typeSelect);
    body.appendChild(typeRow);

    // .. the type-dependent fields live in their own block ..
    var typeFields = document.createElement('div');
    body.appendChild(typeFields);
    destinations._renderTypeFields(typeFields, destination);

    typeSelect.addEventListener('change', function() {
        destination.type = typeSelect.value;
        destination.connection = '';
        destination.options = {};
        destinations._renderTypeFields(typeFields, destination);

        // The re-rendered fields need their help hooked up again
        wizard.forms.initHelp(container);
    });

    // .. whether the destination receives messages at all ..
    var activeRow = document.createElement('div');
    activeRow.className = 'mllp-wizard-tippy-field';

    var activeLabel = document.createElement('label');
    activeLabel.className = 'mllp-wizard-tippy-checkbox';
    activeLabel.setAttribute('for', 'mllp-wizard-destination-active');

    var activeCheckbox = document.createElement('input');
    activeCheckbox.type = 'checkbox';
    activeCheckbox.id = 'mllp-wizard-destination-active';
    activeCheckbox.checked = destination.isActive;

    activeLabel.appendChild(document.createTextNode('Active '));
    activeLabel.appendChild(activeCheckbox);
    activeRow.appendChild(activeLabel);
    body.appendChild(activeRow);

    // .. and the confirm button, with the per-field help to its left.
    var buttons = document.createElement('div');
    buttons.className = 'mllp-wizard-tippy-buttons';
    buttons.appendChild(wizard.forms.buildHelpBadge());

    var doneButton = document.createElement('button');
    doneButton.type = 'button';
    doneButton.className = 'action-button';
    doneButton.textContent = destinations.config.doneLabel;

    doneButton.addEventListener('click', function() {

        var connectionSelect = container.querySelector('#mllp-wizard-destination-connection');
        destination.connection = connectionSelect.value;
        destination.isActive = activeCheckbox.checked;

        var options = {};
        $(container).find('.mllp-wizard-destination-option').each(function() {
            if(this.value) {
                options[this.getAttribute('data-option-id')] = this.value;
            }
        });
        destination.options = options;

        wizard.forms.close();
    });

    buttons.appendChild(doneButton);
    body.appendChild(buttons);

    // Closing without a connection means the row never really existed
    var onHidden = function() {
        if(!destination.connection) {
            var currentIndex = wizard.state.destinationList.indexOf(destination);
            if(currentIndex > -1) {
                wizard.state.destinationList.splice(currentIndex, 1);
            }
        }
        destinations.renderRows();
        destinations.refreshRespondFrom();
        wizard.review.refreshSummaries();
    };

    wizard.forms.showTippy(anchorElement, container, onHidden);
    wizard.forms.initHelp(container);
};

// ////////////////////////////////////////////////////////////////////////

// Rebuilds the "Respond from" select - the service plus one entry per row.
$.fn.zato.channel.hl7.mllp.wizard.destinations.refreshRespondFrom = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var config = wizard.destinations.config;

    var select = $('#mllp-wizard-respond-from');
    var current = select.val();

    select.empty();

    var serviceOption = document.createElement('option');
    serviceOption.value = config.respondFromService;
    serviceOption.textContent = config.respondFromServiceLabel;
    select.append(serviceOption);

    var names = [];

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {
        var destination = wizard.state.destinationList[destinationIdx];
        if(destination.connection) {
            names.push(destination.connection);

            var nameOption = document.createElement('option');
            nameOption.value = destination.connection;
            nameOption.textContent = destination.connection;
            select.append(nameOption);
        }
    }

    // Keep the previous answer if its destination still exists
    if(current) {
        if(names.indexOf(current) > -1) {
            select.val(current);
        }
        else {
            select.val(config.respondFromService);
        }
    }

    wizard.field('respond_from').val(select.val());

    // The question only makes sense once there is at least one destination
    $('#mllp-wizard-respond-from-row').prop('hidden', !names.length);
};

// ////////////////////////////////////////////////////////////////////////

// Writes the rows into the form's hidden JSON fields before submit.
$.fn.zato.channel.hl7.mllp.wizard.destinations.serialize = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;
    var serialized = [];

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {
        var destination = wizard.state.destinationList[destinationIdx];

        if(!destination.connection) {
            continue;
        }

        serialized.push({
            'name': destination.connection,
            'type': destination.type,
            'connection': destination.connection,
            'is_active': destination.isActive,
            'options': destination.options
        });
    }

    wizard.field('destinations').val(serialized.length ? JSON.stringify(serialized) : '');
    wizard.field('respond_from').val($('#mllp-wizard-respond-from').val());
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
