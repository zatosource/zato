// The Bulk export tab of an outgoing FHIR connection - its sections of lines and the popovers
// the lines open. The destinations popover is in fhir-bulk-export-destinations.js, loaded after this file.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.namespace('zato.outgoing.hl7.fhir.bulk_export_tab');

var tab = $.fn.zato.outgoing.hl7.fhir.bulk_export_tab;

// ////////////////////////////////////////////////////////////////////////

tab.config = {

    // Every element the popovers make is named after this
    idPrefix: 'fhir-bulk-export',
    idPrefixDjango: 'id_',

    // The popovers open inside a dialog, so they wear the look of the dialog's other tabs and its plain buttons
    popupClass: 'fhir-bulk-export-popover alerts-tab-micro-form',
    showHowItWorks: false,
    doneButtonClass: '',
    otherButtonClass: '',

    fieldClass: 'micro-form-field',

    levelGroup: 'group',
    levelPatient: 'patient',

    // The form fields the tab reads and writes
    fieldLevel: 'bulk_export_level',
    fieldGroupID: 'bulk_export_group_id',
    fieldPatientIDs: 'bulk_export_patient_ids',
    fieldTypes: 'bulk_export_types',
    fieldSince: 'bulk_export_since',
    fieldTypeFilter: 'bulk_export_type_filter',
    fieldRunEvery: 'bulk_export_run_every',
    fieldRunUnit: 'bulk_export_run_unit',
    fieldStartDate: 'bulk_export_start_date',
    fieldDestinations: 'bulk_export_destinations',

    // The lines that open a popover - the level line opens the one of the level picked, if that level takes anything,
    // and the destinations line is bound by fhir-bulk-export-destinations.js
    levelLine: 'level',
    resourcesLine: 'resources',
    scheduleLine: 'schedule',

    groupPopover: 'level_group',
    patientPopover: 'level_patient',

    groupTitle: 'Group',
    patientTitle: 'Patients',
    resourcesTitle: 'Resources',
    scheduleTitle: 'Schedule',

    labelGroupID: 'Group ID',
    labelPatientIDs: 'Patient IDs',
    labelTypes: 'Resource types',
    labelTypeFilter: 'Type filters',
    labelSince: 'Since',
    labelRunEvery: 'Run every',
    labelRunUnit: 'Unit',

    // A popover with chips is this wide, room for a handful of names on one line and for the chips to wrap,
    // and one with a single short field is this wide
    chipsPopoverWidth: '420px',
    narrowPopoverWidth: '320px',

    // A system-level export takes nothing, so its summary is empty, which hides the link,
    // and a patient-level one says how many patients there are rather than naming them
    summaryNoGroup: 'No group ID',
    summaryNoPatients: 'No patient IDs',
    summarySystem: '',
    patientSingular: 'patient',
    patientPlural: 'patients',
    summaryAllTypes: 'All resource types',
    summarySince: '{summary}, since {since}',
    summaryFilters: '{summary}, {filters}',
    summaryNotScheduled: 'Not scheduled',
    summaryEvery: 'Every {count} {unit}',

    filterSingular: 'type filter',
    filterPlural: 'type filters',

    // The scheduler names its units in the plural, a count of one reads with the singular
    unitSingular: {
        seconds: 'second',
        minutes: 'minute',
        hours: 'hour',
        days: 'day'
    },
    countOne: 1,

    // What a list of names in a summary is joined with
    namesJoinText: ', ',

    // The element the page renders the tab's field names into
    fieldNamesId: 'fhir-bulk-export-field-names'
};

// What the tab holds - the connections grouped by type, loaded once per page, the destinations
// of the open dialog and the badge whose options popover is open
tab.state = {
    connectionData: null,
    fieldNames: [],
    panelId: '',
    fieldPrefix: '',
    destinationList: [],
    optionsBadge: null
};

// The micro-forms kit installs the popover engine here
tab.forms = {};

// ////////////////////////////////////////////////////////////////////////

tab.init = function() {

    var config = tab.config;

    var fieldNamesElement = document.getElementById(config.fieldNamesId);
    tab.state.fieldNames = JSON.parse(fieldNamesElement.textContent);

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popupClass,
        showHowItWorks: config.showHowItWorks,
        doneButtonClass: config.doneButtonClass,
        otherButtonClass: config.otherButtonClass,
        showCancel: true,
        onDone: tab.render
    });

    $.fn.zato.micro_forms.registerChipsKind(tab);

    tab.initDestinations();
    tab.loadConnectionData();
};

// ////////////////////////////////////////////////////////////////////////

// The descriptors of the popovers the tab's lines open
tab.buildDescriptors = function() {

    var config = tab.config;
    var chipsKind = $.fn.zato.micro_forms.chipsKind;
    var out = {};

    out[config.groupPopover] = {
        title: config.groupTitle,
        width: config.narrowPopoverWidth,
        pages: [[
            {field: config.fieldGroupID, label: config.labelGroupID, kind: 'text'}
        ]]
    };

    out[config.patientPopover] = {
        title: config.patientTitle,
        width: config.chipsPopoverWidth,
        pages: [[
            {field: config.fieldPatientIDs, label: config.labelPatientIDs, kind: chipsKind}
        ]]
    };

    out[config.resourcesLine] = {
        title: config.resourcesTitle,
        width: config.chipsPopoverWidth,
        pages: [[
            {field: config.fieldTypes, label: config.labelTypes, kind: chipsKind},
            {field: config.fieldTypeFilter, label: config.labelTypeFilter, kind: chipsKind},
            {field: config.fieldSince, label: config.labelSince, kind: 'text'}
        ]]
    };

    out[config.scheduleLine] = {
        title: config.scheduleTitle,
        fitContent: true,
        pages: [[
            [
                {field: config.fieldRunEvery, label: config.labelRunEvery, kind: 'number'},
                {field: config.fieldRunUnit, label: config.labelRunUnit, kind: 'select'}
            ]
        ]]
    };

    $.extend(out, tab.destinationDescriptors());

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The date picker of the start time, in the user's own date and time format, for both dialogs
tab.attachDatePickers = function() {

    var prefixes = ['', 'edit-'];

    for(var prefixIdx = 0; prefixIdx < prefixes.length; prefixIdx++) {
        var fieldId = '#id_' + prefixes[prefixIdx] + tab.config.fieldStartDate;
        $(fieldId).datetimepicker({
            'dateFormat': $('#js_date_format').val(),
            'timeFormat': $('#js_time_format').val(),
            'ampm': $.fn.zato.to_bool($('#js_ampm').val())
        });
    }
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
        }
    };

    $.fn.zato.post($.fn.zato.destinations.config.connectionListUrl, onLoaded, '', '', true);
};

// ////////////////////////////////////////////////////////////////////////

// One of the tab's fields on the form bound at the moment
tab.field = function(fieldName) {
    var out = $('#' + tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName);
    return out;
};

// The id of one element of the bound panel
tab.elementId = function(part, lineName) {
    var out = tab.state.panelId + '-' + part + '-' + lineName;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Binds the tab to one dialog - the create or the edit one - and reads what its form already holds.
tab.bind = function(options) {

    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    tab.field(config.fieldLevel).off('change.bulk_export_tab').on('change.bulk_export_tab', tab.render);

    $('#' + tab.elementId('edit', config.levelLine)).off('click.bulk_export_tab').on('click.bulk_export_tab', function() {
        tab.openLevel(this);
    });

    $('#' + tab.elementId('edit', config.resourcesLine)).off('click.bulk_export_tab').on('click.bulk_export_tab', function() {
        tab.forms.open(config.resourcesLine, this, config.fieldTypes);
    });

    $('#' + tab.elementId('edit', config.scheduleLine)).off('click.bulk_export_tab').on('click.bulk_export_tab', function() {
        tab.forms.open(config.scheduleLine, this, config.fieldRunEvery);
    });

    tab.bindDestinations();
    tab.deserialize();
    tab.render();
};

// ////////////////////////////////////////////////////////////////////////

// Renders the summaries of the bound panel from the form
tab.render = function() {

    var config = tab.config;

    document.getElementById(tab.elementId('summary', config.levelLine)).textContent = tab.formatLevelSummary();
    document.getElementById(tab.elementId('summary', config.resourcesLine)).textContent = tab.formatResourcesSummary();
    document.getElementById(tab.elementId('summary', config.scheduleLine)).textContent = tab.formatScheduleSummary();
    document.getElementById(tab.elementId('summary', config.destinationLine)).textContent = tab.formatDestinationsSummary();
};

// ////////////////////////////////////////////////////////////////////////

// The names a list field holds, joined the way a summary reads them
tab.namesText = function(fieldName) {
    var names = $.fn.zato.micro_forms.chipNames(tab.field(fieldName).val());
    var out = names.join(tab.config.namesJoinText);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.formatLevelSummary = function() {

    var config = tab.config;
    var level = tab.field(config.fieldLevel).val();
    var out;

    if(level === config.levelGroup) {
        out = tab.field(config.fieldGroupID).val().trim();

        if(out === '') {
            out = config.summaryNoGroup;
        }
    }
    else if(level === config.levelPatient) {
        var patientCount = $.fn.zato.micro_forms.chipNames(tab.field(config.fieldPatientIDs).val()).length;

        if(patientCount === 0) {
            out = config.summaryNoPatients;
        }
        else {
            out = $.fn.zato.count_text(patientCount, config.patientSingular, config.patientPlural);
        }
    }

    // .. anything else is a system-level export.
    else {
        out = config.summarySystem;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.formatResourcesSummary = function() {

    var config = tab.config;

    var out = tab.namesText(config.fieldTypes);
    if(out === '') {
        out = config.summaryAllTypes;
    }

    var since = tab.field(config.fieldSince).val().trim();
    if(since !== '') {
        out = config.summarySince.replace('{summary}', out).replace('{since}', since);
    }

    var filterCount = $.fn.zato.micro_forms.chipNames(tab.field(config.fieldTypeFilter).val()).length;
    if(filterCount > 0) {
        var filters = $.fn.zato.count_text(filterCount, config.filterSingular, config.filterPlural);
        out = config.summaryFilters.replace('{summary}', out).replace('{filters}', filters);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.formatScheduleSummary = function() {

    var config = tab.config;
    var runEvery = tab.field(config.fieldRunEvery).val();
    var out;

    if(runEvery === '') {
        out = config.summaryNotScheduled;
    }
    else {
        var count = parseInt(runEvery);
        var unit = tab.field(config.fieldRunUnit).val();

        if(count === config.countOne) {
            unit = config.unitSingular[unit];
        }

        out = config.summaryEvery.replace('{count}', count).replace('{unit}', unit);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the popover of the level picked - the link is only on show for a level that takes something
tab.openLevel = function(link) {

    var config = tab.config;
    var level = tab.field(config.fieldLevel).val();

    if(level === config.levelGroup) {
        tab.forms.open(config.groupPopover, link, config.fieldGroupID);
    }
    else {
        tab.forms.open(config.patientPopover, link, config.fieldPatientIDs);
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
