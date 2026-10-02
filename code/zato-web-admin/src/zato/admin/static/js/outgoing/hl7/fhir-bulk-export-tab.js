// The Bulk export tab of an outgoing FHIR connection - the rows that follow the level select
// and the destinations picker that serialises its badges into the form's hidden field.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.namespace('zato.outgoing.hl7.fhir.bulk_export_tab');

var tab = $.fn.zato.outgoing.hl7.fhir.bulk_export_tab;

// ////////////////////////////////////////////////////////////////////////

tab.config = {

    // The levels the Group ID and Patient IDs rows follow
    levelGroup: 'group',
    levelPatient: 'patient',

    rowGroupClass: 'fhir-bulk-export-row-group',
    rowPatientClass: 'fhir-bulk-export-row-patient',

    // The form fields the tab reads and writes
    fieldLevel: 'bulk_export_level',
    fieldDestinations: 'bulk_export_destinations',

    // The parts of the picker, each under the panel's id
    badgesSuffix: '-destination-badges',
    optionsSuffix: '-destination-options',
    addSuffix: '-destination-add',
    typeSelectSuffix: 'fhir-bulk-export-destination-type',
    connectionSelectSuffix: 'fhir-bulk-export-destination-connection',

    badgeClass: 'zato-badge zato-badge-blue fhir-bulk-export-badge',
    badgeRemoveClass: 'fhir-bulk-export-badge-remove',
    optionInputClass: 'fhir-bulk-export-destination-option',
    badgeSeparator: ' - ',

    // The destination types a bulk export delivers to, in the order the picker offers them
    typeOrder: ['sftp', 'kafka', 'hl7-fhir', 'service'],

    noConnectionsLabel: 'No connections',

    // The element the page renders the tab's field names into
    fieldNamesId: 'fhir-bulk-export-field-names'
};

// What the picker holds - the connections grouped by type, loaded once per page, and the badges of the open dialog
tab.state = {
    connectionData: null,
    fieldNames: [],
    panelId: '',
    fieldPrefix: '',
    destinationList: []
};

// ////////////////////////////////////////////////////////////////////////

tab.init = function() {
    var fieldNamesElement = document.getElementById(tab.config.fieldNamesId);
    tab.state.fieldNames = JSON.parse(fieldNamesElement.textContent);
    tab.loadConnectionData();
};

// ////////////////////////////////////////////////////////////////////////

// The hidden cells a freshly saved row carries, one per field, in the order the page declares them
tab.rowCells = function(item) {

    var out = '';
    var fieldNames = tab.state.fieldNames;

    for(var fieldIdx = 0; fieldIdx < fieldNames.length; fieldIdx++) {
        var value = item[fieldNames[fieldIdx]];
        if(value === undefined) {
            value = '';
        }
        out += String.format("<td class='ignore'>{0}</td>", value);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.loadConnectionData = function() {

    var onLoaded = function(data, status) {
        if(status === 'success') {
            tab.state.connectionData = JSON.parse(data.responseText);
            tab.renderConnectionSelect();
        }
    };

    $.fn.zato.post($.fn.zato.destinations.config.connectionListUrl, onLoaded, '', '', true);
};

// ////////////////////////////////////////////////////////////////////////

tab.fieldId = function(fieldName) {
    var out = 'id_' + tab.state.fieldPrefix + fieldName;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.field = function(fieldName) {
    var out = document.getElementById(tab.fieldId(fieldName));
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.panelElement = function(suffix) {
    var out = document.getElementById(tab.state.panelId + suffix);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Binds the tab to one dialog - the create or the edit one - and reads what its form already holds.
tab.bind = function(options) {

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    var levelSelect = tab.field(tab.config.fieldLevel);
    levelSelect.onchange = tab.renderLevelRows;
    tab.renderLevelRows();

    tab.renderTypeSelect();
    tab.renderConnectionSelect();

    var typeSelect = tab.field(tab.config.typeSelectSuffix);
    typeSelect.onchange = tab.renderConnectionSelect;

    var addButton = tab.panelElement(tab.config.addSuffix);
    addButton.onclick = tab.addDestination;

    tab.deserialize();
    tab.renderBadges();
};

// ////////////////////////////////////////////////////////////////////////

// The Group ID row shows for a group export, the Patient IDs row for a patient-level one.
tab.renderLevelRows = function() {

    var level = tab.field(tab.config.fieldLevel).value;
    var panel = document.getElementById(tab.state.panelId);

    var groupRows = panel.getElementsByClassName(tab.config.rowGroupClass);
    var patientRows = panel.getElementsByClassName(tab.config.rowPatientClass);

    groupRows[0].hidden = level !== tab.config.levelGroup;
    patientRows[0].hidden = level !== tab.config.levelPatient;
};

// ////////////////////////////////////////////////////////////////////////

tab.typeLabelMap = function() {

    var typeList = $.fn.zato.destinations.config.typeList;
    var out = {};

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        out[typeList[typeIdx].id] = typeList[typeIdx].label;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.renderTypeSelect = function() {

    var typeSelect = tab.field(tab.config.typeSelectSuffix);
    var typeLabelMap = tab.typeLabelMap();
    var typeOrder = tab.config.typeOrder;

    typeSelect.innerHTML = '';

    for(var typeIdx = 0; typeIdx < typeOrder.length; typeIdx++) {
        var option = document.createElement('option');
        option.value = typeOrder[typeIdx];
        option.textContent = typeLabelMap[typeOrder[typeIdx]];
        typeSelect.appendChild(option);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The connections of the type picked, and the options that type carries.
tab.renderConnectionSelect = function() {

    // Nothing is bound yet when the connections arrive before a dialog opens
    if(!tab.state.panelId) {
        return;
    }

    var typeSelect = tab.field(tab.config.typeSelectSuffix);
    var connectionSelect = tab.field(tab.config.connectionSelectSuffix);
    var type = typeSelect.value;

    connectionSelect.innerHTML = '';

    var rows = [];
    if(tab.state.connectionData) {
        rows = tab.state.connectionData[type];
    }

    if(rows.length === 0) {
        var emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = tab.config.noConnectionsLabel;
        connectionSelect.appendChild(emptyOption);
    }

    for(var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
        var option = document.createElement('option');
        option.value = rows[rowIdx].name;
        option.textContent = rows[rowIdx].name;
        connectionSelect.appendChild(option);
    }

    tab.renderOptionInputs(type);
};

// ////////////////////////////////////////////////////////////////////////

tab.renderOptionInputs = function(type) {

    var container = tab.panelElement(tab.config.optionsSuffix);
    var optionList = $.fn.zato.destinations.config.optionList[type];

    container.innerHTML = '';

    for(var optionIdx = 0; optionIdx < optionList.length; optionIdx++) {

        var optionConfig = optionList[optionIdx];

        if(optionConfig.kind === 'select') {
            var select = document.createElement('select');
            select.className = tab.config.optionInputClass;
            select.setAttribute('data-option', optionConfig.id);

            for(var valueIdx = 0; valueIdx < optionConfig.values.length; valueIdx++) {
                var valueOption = document.createElement('option');
                valueOption.value = optionConfig.values[valueIdx];
                valueOption.textContent = optionConfig.values[valueIdx];
                select.appendChild(valueOption);
            }

            container.appendChild(select);
        }
        else {
            var input = document.createElement('input');
            input.type = 'text';
            input.className = tab.config.optionInputClass;
            input.setAttribute('data-option', optionConfig.id);
            input.placeholder = optionConfig.placeholder;
            container.appendChild(input);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

tab.readOptions = function() {

    var container = tab.panelElement(tab.config.optionsSuffix);
    var inputs = container.getElementsByClassName(tab.config.optionInputClass);
    var out = {};

    for(var inputIdx = 0; inputIdx < inputs.length; inputIdx++) {
        var input = inputs[inputIdx];
        if(input.value) {
            out[input.getAttribute('data-option')] = input.value;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.addDestination = function() {

    var type = tab.field(tab.config.typeSelectSuffix).value;
    var connection = tab.field(tab.config.connectionSelectSuffix).value;

    // There is nothing to add without a connection to deliver through
    if(!connection) {
        return;
    }

    tab.state.destinationList.push({
        type: type,
        connection: connection,
        isActive: true,
        options: tab.readOptions()
    });

    tab.serialize();
    tab.renderBadges();
};

// ////////////////////////////////////////////////////////////////////////

tab.removeDestination = function(destinationIdx) {

    tab.state.destinationList.splice(destinationIdx, 1);

    tab.serialize();
    tab.renderBadges();
};

// ////////////////////////////////////////////////////////////////////////

tab.badgeLabel = function(destination, typeLabelMap) {

    var parts = [typeLabelMap[destination.type], destination.connection];

    for(var optionName in destination.options) {
        parts.push(destination.options[optionName]);
    }

    var out = parts.join(tab.config.badgeSeparator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.buildBadge = function(destination, destinationIdx, typeLabelMap) {

    var badge = document.createElement('span');
    badge.className = tab.config.badgeClass;

    var text = document.createElement('span');
    text.textContent = tab.badgeLabel(destination, typeLabelMap);
    badge.appendChild(text);

    var remove = document.createElement('a');
    remove.href = 'javascript:void(0)';
    remove.className = tab.config.badgeRemoveClass;
    remove.appendChild($.fn.zato.new_remove_icon());
    remove.onclick = function() {
        tab.removeDestination(destinationIdx);
    };
    badge.appendChild(remove);

    return badge;
};

// ////////////////////////////////////////////////////////////////////////

tab.renderBadges = function() {

    var container = tab.panelElement(tab.config.badgesSuffix);
    var typeLabelMap = tab.typeLabelMap();
    var destinationList = tab.state.destinationList;

    container.innerHTML = '';

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {
        var badge = tab.buildBadge(destinationList[destinationIdx], destinationIdx, typeLabelMap);
        container.appendChild(badge);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Writes the badges into the hidden field in the shape a connection stores them.
tab.serialize = function() {

    var serialized = [];
    var destinationList = tab.state.destinationList;

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {

        var destination = destinationList[destinationIdx];

        serialized.push({
            'name': destination.connection,
            'type': destination.type,
            'connection': destination.connection,
            'is_active': destination.isActive,
            'options': destination.options
        });
    }

    tab.field(tab.config.fieldDestinations).value = serialized.length ? JSON.stringify(serialized) : '';
};

// ////////////////////////////////////////////////////////////////////////

// Reads the hidden field back into badges - what a connection opened for editing starts out with.
tab.deserialize = function() {

    var stored = tab.field(tab.config.fieldDestinations).value;
    var destinationList = [];

    if(stored) {
        var storedList = JSON.parse(stored);

        for(var storedIdx = 0; storedIdx < storedList.length; storedIdx++) {

            var entry = storedList[storedIdx];

            destinationList.push({
                type: entry.type,
                connection: entry.connection,
                isActive: entry.is_active,
                options: entry.options
            });
        }
    }

    tab.state.destinationList = destinationList;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
