// Destinations tab - reusable editor for a channel's destination list.
//
// A destination is an outgoing connection the platform delivers each message to
// after the channel's service runs. This module renders the rows of the
// destinations table, keeps the "Respond from" select in sync with the rows,
// and serializes everything to the form's hidden JSON fields before submit.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// 1. Include this file and its CSS in the page:
//
//      <link rel="stylesheet" href="/static/css/shared/destinations.css">
//      <script src="/static/js/shared/destinations.js"></script>
//
// 2. Include the shared tab panel markup inside a create or edit form,
//    passing the form and the action:
//
//      {% include "zato/include/destinations-tab.html" with form=create_form action="create" %}
//
//    The form must have two hidden fields, "destinations" and "respond_from".
//
// 3. In the page's create and edit functions, after the dialog is open:
//
//      $.fn.zato.destinations.init('create');
//
// The hidden "destinations" field holds a JSON list of rows:
//
//      [{"name":"...", "type":"rest", "connection":"...", "is_active":true, "options":{"method":"POST"}}]
//
// and "respond_from" holds either "service" or the name of one destination.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations.config = {
    connectionListUrl: '/zato/destinations/get-connection-list/',
    respondFromService: 'service',
    respondFromServiceLabel: 'The service',
    defaultType: 'rest',
    typeList: [
        {id: 'rest',     label: 'REST'},
        {id: 'hl7-mllp', label: 'HL7 MLLP'},
        {id: 'hl7-fhir', label: 'FHIR'},
        {id: 'smtp',     label: 'Email'}
    ],
    optionList: {
        'rest': [
            {id: 'method', label: 'Method', kind: 'select', values: ['POST', 'PUT', 'PATCH', 'GET', 'DELETE']}
        ],
        'hl7-mllp': [],
        'hl7-fhir': [
            {id: 'method', label: 'Method', kind: 'select', values: ['POST', 'PUT', 'PATCH', 'GET', 'DELETE']},
            {id: 'path',   label: 'Path',   kind: 'text',   placeholder: '/Patient'}
        ],
        'smtp': [
            {id: 'to',      label: 'To',      kind: 'text', placeholder: 'name@example.com'},
            {id: 'subject', label: 'Subject', kind: 'text', placeholder: 'Subject line'}
        ]
    }
};

// Connections grouped by destination type, loaded once per page
$.fn.zato.destinations._connectionData = null;

// True once the serialize-on-submit hook has been installed on this page
$.fn.zato.destinations._hookInstalled = false;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._fieldId = function(action, name) {
    var prefix = action === 'edit' ? 'edit-' : '';
    return '#id_' + prefix + name;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._rowsContainer = function(action) {
    return $('#destinations-rows-' + action);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._respondFromSelect = function(action) {
    return $('#destinations-respond-from-' + action);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations.init = function(action) {

    // Load the connection list first, then build the rows ..
    if($.fn.zato.destinations._connectionData) {
        $.fn.zato.destinations._initRows(action);
    }

    // .. the list is cached so the round trip happens once per page.
    else {
        var callback = function(data, status) {
            if(status === 'success') {
                $.fn.zato.destinations._connectionData = JSON.parse(data.responseText);
                $.fn.zato.destinations._initRows(action);
            }
        };
        $.fn.zato.post($.fn.zato.destinations.config.connectionListUrl, callback, '', '', true);
    }

    $.fn.zato.destinations._installHook();
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._initRows = function(action) {

    var container = $.fn.zato.destinations._rowsContainer(action);
    container.empty();

    // Remember the saved "Respond from" answer before anything rewrites its hidden field ..
    var respondFrom = $($.fn.zato.destinations._fieldId(action, 'respond_from')).val();

    // .. rebuild the rows from the hidden field, e.g. when an edit form is populated ..
    var value = $($.fn.zato.destinations._fieldId(action, 'destinations')).val();

    if(value) {
        var items = JSON.parse(value);
        for(var itemIdx = 0; itemIdx < items.length; itemIdx++) {
            $.fn.zato.destinations._appendRow(action, items[itemIdx]);
        }
    }

    // .. sync the "Respond from" select with the rows ..
    $.fn.zato.destinations._refreshRespondFrom(action);

    // .. and select the previously saved answer, if any.
    var select = $.fn.zato.destinations._respondFromSelect(action);

    if(respondFrom) {
        select.val(respondFrom);
        $($.fn.zato.destinations._fieldId(action, 'respond_from')).val(select.val());
    }

    select.off('change.destinations').on('change.destinations', function() {
        $($.fn.zato.destinations._fieldId(action, 'respond_from')).val($(this).val());
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations.addRow = function(action) {

    var config = $.fn.zato.destinations.config;
    var destination = {
        'type': config.defaultType,
        'connection': '',
        'is_active': true,
        'options': {}
    };

    $.fn.zato.destinations._appendRow(action, destination);
    $.fn.zato.destinations._refreshRespondFrom(action);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._appendRow = function(action, destination) {

    var config = $.fn.zato.destinations.config;

    var row = document.createElement('tr');
    row.className = 'destinations-row';

    // Active checkbox
    var activeCell = document.createElement('td');
    activeCell.className = 'destinations-active-cell';

    var activeCheckbox = document.createElement('input');
    activeCheckbox.type = 'checkbox';
    activeCheckbox.className = 'destinations-active';
    activeCheckbox.title = 'Whether this destination receives messages';
    activeCheckbox.checked = destination.is_active;

    activeCell.appendChild(activeCheckbox);

    // Type select
    var typeCell = document.createElement('td');
    typeCell.className = 'destinations-type-cell';

    var typeSelect = document.createElement('select');
    typeSelect.className = 'destinations-type';

    for(var typeIdx = 0; typeIdx < config.typeList.length; typeIdx++) {
        var typeItem = config.typeList[typeIdx];
        var typeOption = document.createElement('option');
        typeOption.value = typeItem.id;
        typeOption.textContent = typeItem.label;
        typeSelect.appendChild(typeOption);
    }
    typeSelect.value = destination.type;

    typeCell.appendChild(typeSelect);

    // Connection select
    var connectionCell = document.createElement('td');
    connectionCell.className = 'destinations-connection-cell';

    var connectionSelect = document.createElement('select');
    connectionSelect.className = 'destinations-connection';

    connectionCell.appendChild(connectionSelect);

    // Per-type options
    var optionsCell = document.createElement('td');
    optionsCell.className = 'destinations-options-cell';

    // Remove link
    var removeCell = document.createElement('td');
    removeCell.className = 'destinations-remove-cell';

    var removeLink = document.createElement('a');
    removeLink.href = 'javascript:void(0)';
    removeLink.className = 'destinations-remove';
    removeLink.title = 'Remove';
    removeLink.textContent = 'x';

    removeCell.appendChild(removeLink);

    row.appendChild(activeCell);
    row.appendChild(typeCell);
    row.appendChild(connectionCell);
    row.appendChild(optionsCell);
    row.appendChild(removeCell);

    // Fill in the type-dependent cells for the initial type ..
    $.fn.zato.destinations._populateConnectionSelect(connectionSelect, destination.type, destination.connection);
    $.fn.zato.destinations._populateOptionsCell(optionsCell, destination.type, destination.options);

    // .. switching the type rebuilds them ..
    $(typeSelect).on('change', function() {
        var newType = this.value;
        $.fn.zato.destinations._populateConnectionSelect(connectionSelect, newType, '');
        $.fn.zato.destinations._populateOptionsCell(optionsCell, newType, {});
        $.fn.zato.destinations._refreshRespondFrom(action);
    });

    // .. picking a connection renames the destination in "Respond from" ..
    $(connectionSelect).on('change', function() {
        $.fn.zato.destinations._refreshRespondFrom(action);
    });

    // .. and removing the row updates "Respond from" too.
    $(removeLink).on('click', function() {
        $(row).remove();
        $.fn.zato.destinations._refreshRespondFrom(action);
    });

    $.fn.zato.destinations._rowsContainer(action).append(row);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._populateConnectionSelect = function(connectionSelect, type, selected) {

    $(connectionSelect).empty();

    var connectionList = $.fn.zato.destinations._connectionData[type];

    for(var connectionIdx = 0; connectionIdx < connectionList.length; connectionIdx++) {
        var connection = connectionList[connectionIdx];
        var option = document.createElement('option');
        option.value = connection.name;
        option.textContent = connection.name;
        connectionSelect.appendChild(option);
    }

    if(selected) {
        connectionSelect.value = selected;
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._populateOptionsCell = function(optionsCell, type, values) {

    $(optionsCell).empty();

    var optionDefs = $.fn.zato.destinations.config.optionList[type];

    for(var optionIdx = 0; optionIdx < optionDefs.length; optionIdx++) {
        var optionDef = optionDefs[optionIdx];

        var wrapper = document.createElement('span');
        wrapper.className = 'destinations-option';

        var label = document.createElement('label');
        label.className = 'destinations-option-label';
        label.textContent = optionDef.label;

        var input;

        if(optionDef.kind === 'select') {
            input = document.createElement('select');
            for(var valueIdx = 0; valueIdx < optionDef.values.length; valueIdx++) {
                var value = optionDef.values[valueIdx];
                var option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                input.appendChild(option);
            }
        }
        else {
            input = document.createElement('input');
            input.type = 'text';
            input.placeholder = optionDef.placeholder;
        }

        input.className = 'destinations-option-input';
        input.setAttribute('data-option-id', optionDef.id);

        if(values[optionDef.id]) {
            input.value = values[optionDef.id];
        }

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        optionsCell.appendChild(wrapper);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._rowNames = function(action) {

    var out = [];

    $.fn.zato.destinations._rowsContainer(action).find('.destinations-row').each(function() {
        var connection = $(this).find('.destinations-connection').val();
        if(connection) {
            out.push(connection);
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._refreshRespondFrom = function(action) {

    var config = $.fn.zato.destinations.config;
    var select = $.fn.zato.destinations._respondFromSelect(action);
    var current = select.val();

    select.empty();

    // The service is always the first answer ..
    var serviceOption = document.createElement('option');
    serviceOption.value = config.respondFromService;
    serviceOption.textContent = config.respondFromServiceLabel;
    select.append(serviceOption);

    // .. followed by one entry per destination.
    var names = $.fn.zato.destinations._rowNames(action);

    for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
        var nameOption = document.createElement('option');
        nameOption.value = names[nameIdx];
        nameOption.textContent = names[nameIdx];
        select.append(nameOption);
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

    $($.fn.zato.destinations._fieldId(action, 'respond_from')).val(select.val());
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._serialize = function(action) {

    var out = [];

    $.fn.zato.destinations._rowsContainer(action).find('.destinations-row').each(function() {

        var connection = $(this).find('.destinations-connection').val();
        if(!connection) {
            return;
        }

        var options = {};

        $(this).find('.destinations-option-input').each(function() {
            var optionValue = $(this).val();
            if(optionValue) {
                options[$(this).attr('data-option-id')] = optionValue;
            }
        });

        out.push({
            'name': connection,
            'type': $(this).find('.destinations-type').val(),
            'connection': connection,
            'is_active': $(this).find('.destinations-active').prop('checked'),
            'options': options
        });
    });

    $($.fn.zato.destinations._fieldId(action, 'destinations')).val(out.length ? JSON.stringify(out) : '');
    $($.fn.zato.destinations._fieldId(action, 'respond_from')).val($.fn.zato.destinations._respondFromSelect(action).val());
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations._installHook = function() {

    if($.fn.zato.destinations._hookInstalled) {
        return;
    }
    $.fn.zato.destinations._hookInstalled = true;

    // Chain with whatever hook the page may have installed already
    var previousHook = $.fn.zato.data_table.before_submit_hook;

    $.fn.zato.data_table.before_submit_hook = function(form) {

        var isEdit = $(form).attr('id') === 'edit-form';
        $.fn.zato.destinations._serialize(isEdit ? 'edit' : 'create');

        if(previousHook) {
            return previousHook(form);
        }
        return true;
    };
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
