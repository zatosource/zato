// The destinations of the Bulk export tab and the hidden field they are serialised into. The Deliver to
// line opens the zones popover of fhir-bulk-export-destinations-zones.js, where every connection of
// every type is a badge and the ones assigned are the destinations. A destination of a type that takes
// options - a path for SFTP, a method and a path for FHIR - edits them in a popover of its own, which
// opens over the zones from its own micro-forms host, so it is a form of ordinary fields and not a row
// of little inputs. This file holds the config, the two hosts, the option forms and the hidden field.
// Loaded after fhir-bulk-export-tab.js, whose config it extends, and before the zones.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tab = $.fn.zato.outgoing.hl7.fhir.bulk_export_tab;

// ////////////////////////////////////////////////////////////////////////

$.extend(tab.config, {

    destinationLine: 'destination',
    destinationField: 'destinations',
    destinationKind: 'fhirBulkExportZones',
    destinationTitle: 'Destinations',

    // Wide enough for the two zones to each hold a tag, a name and the options next to it
    destinationPopoverWidth: '680px',

    // The options popover is a host of its own, so it opens over the zones popover
    optionsIdPrefix: 'fhir-bulk-export-options',
    optionsTitle: '{type} - {connection}',
    optionsPopoverWidth: '360px',

    // What tells a type and an option apart in the name of an options field
    optionsFieldSeparator: '__',

    // The destination types a bulk export delivers to, in the order the zones name them,
    // and the tint each type's tag wears
    typeOrder: ['sftp', 'kafka', 'hl7-fhir', 'service'],
    typeTagClass: {
        'sftp': 'zato-badge-amber',
        'kafka': 'zato-badge-green',
        'hl7-fhir': 'zato-badge-blue',
        'service': 'fhir-bulk-export-type-tag-service'
    },
    tagClass: 'zato-badge fhir-bulk-export-type-tag',

    // The row a kind builds into dresses its own controls
    ownFieldClass: 'micro-form-field-own',

    summaryNoDestinations: 'None',

    // The summary counts the destinations by type, in the order of the types, with a middle dot between the types
    summaryCountText: '{count}x {type}',
    summarySeparator: ' \u00b7 ',

    // What the options of a destination read as on its badge, and what they read as while there are none
    optionsJoinText: ' ',
    optionsEmptyLabel: 'Options'
});

// The host of the options popover - the micro-forms kit installs its engine here. Its fields are not
// on any Django form, so it keeps them in a store of its own, one element per option of every type.
tab.optionsHost = {
    config: {idPrefix: tab.config.optionsIdPrefix},
    forms: {},
    store: {},

    field: function(fieldName) {
        var out = $(tab.optionsHost.store[fieldName]);
        return out;
    }
};

// ////////////////////////////////////////////////////////////////////////

tab.initDestinations = function() {

    var config = tab.config;

    tab.forms.registerKind(config.destinationKind, tab.zones);

    tab.buildOptionsStore();

    $.fn.zato.micro_forms.setup(tab.optionsHost, {
        descriptors: tab.buildOptionsDescriptors(),
        popupClass: config.popupClass,
        showHowItWorks: config.showHowItWorks,
        doneButtonClass: config.doneButtonClass,
        otherButtonClass: config.otherButtonClass,
        showCancel: true,
        onDone: tab.zones.takeOptions
    });
};

// ////////////////////////////////////////////////////////////////////////

tab.destinationDescriptors = function() {

    var config = tab.config;
    var out = {};

    out[config.destinationLine] = {
        title: config.destinationTitle,
        width: config.destinationPopoverWidth,
        pages: [[
            {field: config.destinationField, kind: config.destinationKind}
        ]]
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tab.bindDestinations = function() {

    var config = tab.config;

    $('#' + tab.elementId('edit', config.destinationLine)).off('click.bulk_export_tab').on('click.bulk_export_tab', function() {
        tab.forms.open(config.destinationLine, this);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The name an option of a type goes by in the options host
tab.optionsFieldName = function(type, optionId) {
    var out = type.replace(/-/g, '_') + tab.config.optionsFieldSeparator + optionId;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One element per option of every type, which the options popover reads its values off and writes them into
tab.buildOptionsStore = function() {

    var optionList = $.fn.zato.destinations.config.optionList;
    var store = tab.optionsHost.store;

    tab.config.typeOrder.forEach(function(type) {

        optionList[type].forEach(function(optionConfig) {

            var element;

            if(optionConfig.kind === 'select') {
                element = document.createElement('select');

                optionConfig.values.forEach(function(value) {
                    var option = document.createElement('option');
                    option.value = value;
                    option.textContent = value;
                    element.appendChild(option);
                });
            }
            else {
                element = document.createElement('input');
                element.type = 'text';
            }

            store[tab.optionsFieldName(type, optionConfig.id)] = element;
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

// One popover per type that takes options, of the kit's own text and select fields
tab.buildOptionsDescriptors = function() {

    var config = tab.config;
    var optionList = $.fn.zato.destinations.config.optionList;
    var out = {};

    config.typeOrder.forEach(function(type) {

        if(optionList[type].length === 0) {
            return;
        }

        var page = [];

        optionList[type].forEach(function(optionConfig) {

            var spec = {
                field: tab.optionsFieldName(type, optionConfig.id),
                label: optionConfig.label,
                kind: optionConfig.kind
            };

            if(optionConfig.kind !== 'select') {
                spec.placeholder = optionConfig.placeholder;
            }

            page.push(spec);
        });

        out[type] = {
            title: config.optionsTitle,
            width: config.optionsPopoverWidth,
            pages: [page]
        };
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether a type has anything to open an options popover for
tab.typeHasOptions = function(type) {
    var out = $.fn.zato.destinations.config.optionList[type].length > 0;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the options popover of one destination, its fields standing on the options the destination has
tab.openOptions = function(type, connection, options, anchor) {

    var config = tab.config;
    var optionList = $.fn.zato.destinations.config.optionList[type];
    var store = tab.optionsHost.store;

    optionList.forEach(function(optionConfig) {

        var element = store[tab.optionsFieldName(type, optionConfig.id)];
        var value = options[optionConfig.id];

        if(value === undefined) {
            value = '';
        }

        // A select with no value stands on its first choice, the way the popover will show it
        if(optionConfig.kind === 'select' && value === '') {
            value = optionConfig.values[0];
        }

        element.value = value;
    });

    var title = config.optionsTitle.replace('{type}', tab.typeLabelMap()[type]).replace('{connection}', connection);
    tab.optionsHost.forms.descriptors[type].title = title;

    tab.optionsHost.forms.open(type, anchor, tab.optionsFieldName(type, optionList[0].id));
};

// ////////////////////////////////////////////////////////////////////////

// The options of one type as the options popover left them, the ones left empty out
tab.readOptionsStore = function(type) {

    var optionList = $.fn.zato.destinations.config.optionList[type];
    var store = tab.optionsHost.store;
    var out = {};

    optionList.forEach(function(optionConfig) {
        var value = store[tab.optionsFieldName(type, optionConfig.id)].value;
        if(value) {
            out[optionConfig.id] = value;
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the options of a destination read as on its badge
tab.optionsText = function(type, options) {

    var config = tab.config;
    var optionList = $.fn.zato.destinations.config.optionList[type];
    var parts = [];

    optionList.forEach(function(optionConfig) {
        var value = options[optionConfig.id];
        if(value !== undefined) {
            parts.push(value);
        }
    });

    var out = parts.join(config.optionsJoinText);

    if(out === '') {
        out = config.optionsEmptyLabel;
    }

    return out;
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

// The connections of one type, none until the list has arrived from the server
tab.connectionRows = function(type) {

    var out = [];

    if(tab.state.connectionData) {
        out = tab.state.connectionData[type];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Runs the callback once the element is on the page - a kind builds its row before the popover is
// mounted, and a component that finds its elements by id through the document finds nothing until then
tab.whenOnScreen = function(element, callback) {

    if(element.isConnected) {
        callback();
        return;
    }

    window.requestAnimationFrame(function() {
        tab.whenOnScreen(element, callback);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The small tinted word saying what type a destination is
tab.buildTypeTag = function(type) {

    var config = tab.config;

    var tag = document.createElement('span');
    tag.className = config.tagClass + ' ' + config.typeTagClass[type];
    tag.textContent = tab.typeLabelMap()[type];

    var out = tag;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The destination of a given type and connection on the list, or null
tab.findDestination = function(type, connection) {

    var destinationList = tab.state.destinationList;
    var out = null;

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {
        var destination = destinationList[destinationIdx];
        if(destination.type === type && destination.connection === connection) {
            out = destination;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many destinations there are of each type, the types in their order
tab.formatDestinationsSummary = function() {

    var config = tab.config;
    var typeLabelMap = tab.typeLabelMap();
    var destinationList = tab.state.destinationList;

    var countByType = {};

    destinationList.forEach(function(destination) {
        if(countByType[destination.type] === undefined) {
            countByType[destination.type] = 0;
        }
        countByType[destination.type] += 1;
    });

    var parts = [];

    config.typeOrder.forEach(function(type) {
        if(countByType[type] !== undefined) {
            parts.push(config.summaryCountText.replace('{count}', countByType[type]).replace('{type}', typeLabelMap[type]));
        }
    });

    var out = parts.join(config.summarySeparator);

    if(out === '') {
        out = config.summaryNoDestinations;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes the destinations into the hidden field in the shape a connection stores them.
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

    tab.field(tab.config.fieldDestinations).val(serialized.length ? JSON.stringify(serialized) : '');
};

// ////////////////////////////////////////////////////////////////////////

// Reads the hidden field back into the list - what a connection opened for editing starts out with.
tab.deserialize = function() {

    var stored = tab.field(tab.config.fieldDestinations).val();
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
