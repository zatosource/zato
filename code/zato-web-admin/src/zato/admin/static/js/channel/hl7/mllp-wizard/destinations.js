// HL7 MLLP channel wizard - the destination rows on step 2.
//
// A destination is an outgoing connection every message is delivered to
// after the channel's service ran. Each destination is one row - the kind
// of connection, the connection itself, whatever options that kind has and
// the switch deciding whether the destination receives messages at all.
// The rows are the wizard kit's shared select rows, the same ones the REST
// security picks wear on step 1. They serialize into the form's hidden
// "destinations" and "respond_from" fields in the very shape the full-page
// editor produces, reusing the type and option definitions of the shared
// destinations module.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;
var destinations = wizard.destinations;

// ////////////////////////////////////////////////////////////////////////

destinations.config = {

    // What the caller's response defaults to
    respondFromService: 'service',
    respondFromServiceLabel: 'The service',

    // Where the rows are appended
    rowsId: 'mllp-wizard-destination-rows',

    // The rows are too tight for labels, so their controls name
    // themselves on hover
    typeTitle: 'Destination type',
    connectionTitle: 'Connection',
    activeTitle: 'Whether this destination receives messages'
};

// Connections grouped by destination type, loaded once per page
destinations._connectionData = null;

// ////////////////////////////////////////////////////////////////////////

destinations.init = function() {

    // Adding a row waits until the connection list has arrived ..
    $('#mllp-wizard-destination-add').on('click', function() {
        destinations._withConnectionData(function() {
            destinations.add();
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
destinations._withConnectionData = function(callback) {

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

destinations.add = function() {

    var destination = {
        type: $.fn.zato.destinations.config.defaultType,
        connection: '',
        isActive: true,
        options: {}
    };
    wizard.state.destinationList.push(destination);

    destinations._appendRow(destination);
    destinations.refreshRespondFrom();
};

// ////////////////////////////////////////////////////////////////////////

// What each destination type is called, keyed by the type itself, so that labelling a list
// of rows reads the type list once rather than searching it once per row.
destinations._getTypeLabelMap = function() {

    var typeList = $.fn.zato.destinations.config.typeList;
    var out = {};

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        out[typeList[typeIdx].id] = typeList[typeIdx].label;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The one-line label a destination gets in the review - type, connection
// and options.
destinations._rowLabel = function(destination, typeLabelMap) {

    // A single destination labelled on its own has no map read ahead of it
    if(typeLabelMap === undefined) {
        typeLabelMap = destinations._getTypeLabelMap();
    }

    var parts = [typeLabelMap[destination.type], destination.connection];

    for(var optionName in destination.options) {
        parts.push(destination.options[optionName]);
    }

    var out = parts.join(' - ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The kinds of connection a destination can be, in a select of their own.
destinations._buildTypeSelect = function(destination) {

    var select = document.createElement('select');
    select.className = 'mllp-wizard-destination-type';
    select.title = destinations.config.typeTitle;

    var typeList = $.fn.zato.destinations.config.typeList;

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        var option = document.createElement('option');
        option.value = typeList[typeIdx].id;
        option.textContent = typeList[typeIdx].label;
        select.appendChild(option);
    }
    select.value = destination.type;

    var out = select;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Fills a select with the connections of the destination's type.
destinations._fillConnectionSelect = function(select, destination) {

    select.textContent = '';

    var connectionList = destinations._connectionData[destination.type];

    for(var connectionIdx = 0; connectionIdx < connectionList.length; connectionIdx++) {
        var option = document.createElement('option');
        option.value = connectionList[connectionIdx].name;
        option.textContent = connectionList[connectionIdx].name;
        select.appendChild(option);
    }

    if(destination.connection) {
        select.value = destination.connection;
    }

    // A select always shows one of its options, so what it shows is what the
    // destination is - and an empty string when this type has no connections
    // to offer, which is what keeps such a row out of the serialized list
    destination.connection = select.value;
};

// ////////////////////////////////////////////////////////////////////////

// One input for an option of the destination's type, e.g. the HTTP method
// a REST destination is invoked with.
destinations._buildOptionInput = function(destination, optionDef) {

    var isSelect = optionDef.kind === 'select';
    var input;

    if(isSelect) {
        input = document.createElement('select');

        for(var valueIdx = 0; valueIdx < optionDef.values.length; valueIdx++) {
            var valueOption = document.createElement('option');
            valueOption.value = optionDef.values[valueIdx];
            valueOption.textContent = optionDef.values[valueIdx];
            input.appendChild(valueOption);
        }
    }
    else {
        input = document.createElement('input');
        input.type = 'text';
        input.placeholder = optionDef.placeholder;
    }

    input.className = 'mllp-wizard-destination-option';
    input.title = optionDef.label;

    if(destination.options[optionDef.id]) {
        input.value = destination.options[optionDef.id];
    }

    // A select shows a value from the start, so the destination carries it
    // right away - a text input starts out empty and only counts once typed in
    if(isSelect) {
        destination.options[optionDef.id] = input.value;
    }

    // A select settles on change, free text as it is typed
    input.addEventListener(isSelect ? 'change' : 'input', function() {
        if(input.value) {
            destination.options[optionDef.id] = input.value;
        }
        else {
            delete destination.options[optionDef.id];
        }
        destinations.refreshRespondFrom();
    });

    var out = input;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Rebuilds the inputs for the options the destination's type has - the
// type is what decides which ones there are, so a new type brings new ones.
destinations._fillOptions = function(optionBox, destination) {

    optionBox.textContent = '';

    var optionDefs = $.fn.zato.destinations.config.optionList[destination.type];

    for(var optionIdx = 0; optionIdx < optionDefs.length; optionIdx++) {
        optionBox.appendChild(destinations._buildOptionInput(destination, optionDefs[optionIdx]));
    }
};

// ////////////////////////////////////////////////////////////////////////

// The switch at the end of a row - an inactive destination is skipped
// when messages are delivered.
destinations._buildActiveToggle = function(destination) {

    var toggle = document.createElement('input');
    toggle.type = 'checkbox';
    toggle.className = 'mllp-wizard-destination-active';
    toggle.title = destinations.config.activeTitle;
    toggle.checked = destination.isActive;

    toggle.addEventListener('change', function() {
        destination.isActive = toggle.checked;
    });

    var out = toggle;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Appends the row of one destination to the list on step 2.
destinations._appendRow = function(destination) {

    var list = document.getElementById(destinations.config.rowsId);

    var buildContent = function(row) {

        var typeSelect = destinations._buildTypeSelect(destination);
        row.appendChild(typeSelect);

        var connectionSelect = document.createElement('select');
        connectionSelect.className = 'mllp-wizard-destination-connection';
        connectionSelect.title = destinations.config.connectionTitle;
        destinations._fillConnectionSelect(connectionSelect, destination);
        row.appendChild(connectionSelect);

        var optionBox = document.createElement('div');
        optionBox.className = 'mllp-wizard-destination-options';
        destinations._fillOptions(optionBox, destination);
        row.appendChild(optionBox);

        // A new type comes with connections and options of its own,
        // so neither the old connection nor the old options survive it
        typeSelect.addEventListener('change', function() {
            destination.type = typeSelect.value;
            destination.connection = '';
            destination.options = {};

            destinations._fillConnectionSelect(connectionSelect, destination);
            destinations._fillOptions(optionBox, destination);
            destinations.refreshRespondFrom();
        });

        connectionSelect.addEventListener('change', function() {
            destination.connection = connectionSelect.value;
            destinations.refreshRespondFrom();
        });

        row.appendChild(destinations._buildActiveToggle(destination));
    };

    var onRemove = function() {
        var destinationIndex = wizard.state.destinationList.indexOf(destination);
        wizard.state.destinationList.splice(destinationIndex, 1);
        destinations.refreshRespondFrom();
    };

    $.fn.zato.wizard_kit.selectRows.appendRow(list, buildContent, onRemove);
};

// ////////////////////////////////////////////////////////////////////////

// Rebuilds the "Respond from" select - the service plus one entry per row.
destinations.refreshRespondFrom = function() {

    var config = destinations.config;

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
destinations.serialize = function() {

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
