// HL7 MLLP channel wizard - the three panels step 2 opens from its lines.
//
// The destinations panel is the shared badge picker, the same two-zone
// control the security groups and the MCP gateways use - available on the
// left, the ones messages go to on the right, moved by a click or dragged
// across with the marquee and the ghost the picker draws. A destination
// badge carries the switch pausing it and the options its kind has.
//
// The service and the reply panels are lists of one pick each, filtered by
// typing, and both read their choices from the rendered Django form, which
// keeps the wizard and the full-page editor on one list of options.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;
var destinations = wizard.destinations;

destinations.panels = {};
var panels = destinations.panels;

// ////////////////////////////////////////////////////////////////////////

panels.config = {

    // The key the badge picker keys its elements and its events by
    pickerAction: 'mllp-wizard-destinations',

    titles: {
        destinations: 'destinations',
        service: 'service',
        reply: 'reply'
    },

    widths: {

        // Two zones side by side, and a row of the right one carries a name,
        // a kind and the options of that kind - this is what fits all three
        // without the name having to give way on the first connection
        destinations: 980,
        service: 480,
        reply: 470
    },

    // How narrow the corners may drag a panel - for the destinations that
    // is the width where a row still holds its options and its switch whole
    minWidths: {
        destinations: 700,
        service: 340,
        reply: 380
    },

    labels: {
        available: 'Available',
        assigned: 'Messages go to',
        anyType: '----------',
        filterDestinations: 'Filter destinations',
        filterServices: 'Filter services',
        filterLabel: 'Filter',
        clear: 'Clear',
        services: 'Services',
        replyService: 'The service',
        replyDestinations: 'The destinations',
        noneActive: 'Nothing is active',
        active: 'Active'
    }
};

// ////////////////////////////////////////////////////////////////////////

panels.destinationsPanel = function() {

    var panelsConfig = panels.config;

    var out = {
        title: panelsConfig.titles.destinations,
        width: panelsConfig.widths.destinations,
        minWidth: panelsConfig.minWidths.destinations,
        build: panels._buildDestinations
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildDestinations = function(body) {

    var panelsConfig = panels.config;
    var action = panelsConfig.pickerAction;

    body.appendChild(panels._buildPickerFilter(action));
    body.appendChild(panels._buildPickerZones(action));

    var itemList = panels._buildItemList();

    $.fn.zato.badge_picker.init(action, itemList, {
        make_badge: panels._makeBadge,
        sort_items: panels._sortItems,
        is_assigned: panels._isAssigned,
        filter_badge: panels._filterBadge
    });

    // What the zones hold when the panel closes is what the channel does
    var out = panels._readPicker;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The filter row above the zones - the kind of connection, free text and
// the clear button, all three the badge picker's own element ids.
panels._buildPickerFilter = function(action) {

    var labels = panels.config.labels;

    var filter = document.createElement('div');
    filter.className = 'badge-picker-filter';
    filter.id = 'badge-filter-' + action;

    var typeSelect = document.createElement('select');
    typeSelect.className = 'noChosen';
    typeSelect.id = 'badge-security-type-' + action;

    var anyOption = document.createElement('option');
    anyOption.value = '';
    anyOption.textContent = labels.anyType;
    typeSelect.appendChild(anyOption);

    var typeList = $.fn.zato.destinations.config.typeList;

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {

        var typeOption = document.createElement('option');
        typeOption.value = typeList[typeIdx].id;
        typeOption.textContent = typeList[typeIdx].label;
        typeSelect.appendChild(typeOption);
    }

    filter.appendChild(typeSelect);

    var text = document.createElement('input');
    text.type = 'text';
    text.className = 'wizard-panel-filter';
    text.id = 'badge-filter-text-' + action;
    text.autocomplete = 'off';
    text.placeholder = labels.filterDestinations;
    filter.appendChild(text);

    var clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'badge-filter-clear';
    clear.id = 'badge-filter-clear-' + action;
    clear.textContent = labels.clear;
    filter.appendChild(clear);

    var out = filter;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildPickerZones = function(action) {

    var labels = panels.config.labels;

    var picker = document.createElement('div');
    picker.className = 'badge-picker';
    picker.id = 'badge-picker-' + action;

    picker.appendChild(panels._buildZone('available-' + action, 'badge-zone-available', labels.available));

    var resizer = document.createElement('div');
    resizer.className = 'badge-picker-resizer';
    picker.appendChild(resizer);

    picker.appendChild(panels._buildZone('assigned-' + action, 'badge-zone-assigned', labels.assigned));

    var out = picker;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildZone = function(idSuffix, sideClass, headerText) {

    var zone = document.createElement('div');
    zone.className = 'badge-zone ' + sideClass;
    zone.id = 'badge-zone-' + idSuffix;

    var header = document.createElement('div');
    header.className = 'badge-zone-header';
    header.textContent = headerText + ' (';

    var count = document.createElement('span');
    count.className = 'badge-zone-count';
    count.textContent = '0';
    header.appendChild(count);
    header.appendChild(document.createTextNode(')'));

    zone.appendChild(header);

    var zoneBody = document.createElement('div');
    zoneBody.className = 'badge-zone-body';
    zone.appendChild(zoneBody);

    var out = zone;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every connection there is, each one knowing whether messages already go
// to it and, if so, in which position, with what options and paused or not.
panels._buildItemList = function() {

    var out = [];

    if(!destinations._connectionData) {
        return out;
    }

    var typeList = $.fn.zato.destinations.config.typeList;

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {

        var type = typeList[typeIdx];
        var connectionList = destinations._connectionData[type.id];

        for(var connectionIdx = 0; connectionIdx < connectionList.length; connectionIdx++) {
            out.push(panels._buildItem(type, connectionList[connectionIdx].name));
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildItem = function(type, connectionName) {

    var out = {
        id: type.id + ':' + connectionName,
        name: connectionName,
        type: type.id,
        typeLabel: type.label,
        is_member: false,
        isActive: true,
        options: {},
        order: -1
    };

    var destinationList = wizard.state.destinationList;

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {

        var destination = destinationList[destinationIdx];

        if(destination.type === type.id) {
            if(destination.connection === connectionName) {
                out.is_member = true;
                out.isActive = destination.isActive;
                out.options = destination.options;
                out.order = destinationIdx;
            }
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._isAssigned = function(item) {
    return item.is_member;
};

// ////////////////////////////////////////////////////////////////////////

// The ones already picked keep the order they were picked in, the rest read
// kind by kind - the picked order is the order of one-after-another delivery.
panels._sortItems = function(left, right) {

    if(left.order !== right.order) {
        return left.order - right.order;
    }

    if(left.typeLabel !== right.typeLabel) {
        return left.typeLabel.localeCompare(right.typeLabel);
    }

    var out = left.name.localeCompare(right.name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A badge is one connection, with the switch and the options of its kind
// riding along - the assigned zone is where they are shown.
panels._makeBadge = function(item, num) {

    var badge = document.createElement('div');
    badge.className = 'security-badge wizard-destination-badge';
    badge.setAttribute('data-id', item.id);
    badge.setAttribute('data-name', item.name.toLowerCase());
    badge.setAttribute('data-type', item.type);
    badge.setAttribute('data-connection', item.name);

    var indicator = document.createElement('span');
    indicator.className = 'security-badge-indicator';
    badge.appendChild(indicator);

    var number = document.createElement('span');
    number.className = 'security-badge-number';
    number.textContent = num + '.';
    badge.appendChild(number);

    // The kind comes first and always takes the same width, so every name
    // down the zone starts at the same place
    var kind = document.createElement('span');
    kind.className = 'wizard-destination-kind';
    kind.textContent = item.typeLabel;
    badge.appendChild(kind);

    var name = document.createElement('span');
    name.className = 'security-badge-name';
    name.textContent = item.name;
    badge.appendChild(name);

    badge.appendChild(panels._buildBadgeControls(item));

    var out = $(badge);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildBadgeControls = function(item) {

    var controls = document.createElement('span');
    controls.className = 'wizard-destination-controls';

    var optionDefList = $.fn.zato.destinations.config.optionList[item.type];

    for(var optionIdx = 0; optionIdx < optionDefList.length; optionIdx++) {
        controls.appendChild(panels._buildOptionInput(item, optionDefList[optionIdx]));
    }

    var active = document.createElement('input');
    active.type = 'checkbox';
    active.className = 'wizard-destination-active';
    active.title = panels.config.labels.active;
    active.checked = item.isActive;
    controls.appendChild(active);

    var out = controls;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One option of the destination's kind, e.g. the method a REST call is made
// with - the value travels on the input itself until the panel closes.
panels._buildOptionInput = function(item, optionDef) {

    if(optionDef.kind === 'select') {

        var input = document.createElement('select');

        for(var valueIdx = 0; valueIdx < optionDef.values.length; valueIdx++) {

            var option = document.createElement('option');
            option.value = optionDef.values[valueIdx];
            option.textContent = optionDef.values[valueIdx];
            input.appendChild(option);
        }
    }
    else {
        input = document.createElement('input');
        input.type = 'text';
        input.placeholder = optionDef.placeholder;
    }

    input.className = 'wizard-destination-option';
    input.title = optionDef.label;
    input.setAttribute('data-option', optionDef.id);

    if(item.options[optionDef.id]) {
        input.value = item.options[optionDef.id];
    }

    var out = input;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._filterBadge = function(badge, textWords, typeValue) {

    if(typeValue) {
        if(badge.attr('data-type') !== typeValue) {
            return false;
        }
    }

    var name = badge.attr('data-name');

    for(var wordIdx = 0; wordIdx < textWords.length; wordIdx++) {
        if(name.indexOf(textWords[wordIdx]) === -1) {
            return false;
        }
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

// The assigned zone read back into the state, in the order it holds.
panels._readPicker = function() {

    var assigned = $('#badge-zone-assigned-' + panels.config.pickerAction + ' .badge-zone-body .security-badge');
    var destinationList = [];

    assigned.each(function() {

        var badge = $(this);
        var options = {};

        badge.find('[data-option]').each(function() {
            if(this.value) {
                options[this.getAttribute('data-option')] = this.value;
            }
        });

        destinationList.push({
            type: badge.attr('data-type'),
            connection: badge.attr('data-connection'),
            isActive: badge.find('.wizard-destination-active').prop('checked'),
            options: options
        });
    });

    wizard.state.destinationList = destinationList;

    destinations.settle();
    destinations.render();
};

// ////////////////////////////////////////////////////////////////////////

panels.servicePanel = function() {

    var panelsConfig = panels.config;

    var out = {
        title: panelsConfig.titles.service,
        width: panelsConfig.widths.service,
        minWidth: panelsConfig.minWidths.service,
        build: panels._buildService
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._buildService = function(body) {

    var lines = $.fn.zato.wizard_kit.lines;
    var labels = panels.config.labels;

    var nameList = [];

    wizard.field('service').find('option').each(function() {
        if(this.value) {
            nameList.push(this.value);
        }
    });

    var list = document.createElement('div');
    list.className = 'wizard-panel-list';

    var fill = function(filterText) {
        panels._fillServiceList(list, nameList, filterText);
    };

    var filter = lines.buildFilter(labels.filterLabel, labels.filterServices, fill);
    body.appendChild(filter.field);

    var label = document.createElement('span');
    label.className = 'wizard-tippy-label';
    label.textContent = labels.services;
    body.appendChild(label);

    fill('');
    body.appendChild(list);

    var out = null;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._fillServiceList = function(list, nameList, filterText) {

    var lines = $.fn.zato.wizard_kit.lines;
    var current = wizard.field('service').val();

    list.textContent = '';

    for(var nameIdx = 0; nameIdx < nameList.length; nameIdx++) {

        var name = nameList[nameIdx];

        if(name.toLowerCase().indexOf(filterText) === -1) {
            continue;
        }

        list.appendChild(lines.buildPickRow(name, name === current, panels._pickService(name)));
    }
};

// ////////////////////////////////////////////////////////////////////////

// The row of one service knows the name it stands for. Picking the one
// already picked is how the channel is left without a service at all.
panels._pickService = function(name) {

    var out = function() {

        var field = wizard.field('service');

        if(field.val() === name) {
            field.val('');
        }
        else {
            field.val(name);
        }

        $.fn.zato.wizard_kit.lines.closePanel();
        destinations.render();
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels.replyPanel = function() {

    var panelsConfig = panels.config;

    var out = {
        title: panelsConfig.titles.reply,
        width: panelsConfig.widths.reply,
        minWidth: panelsConfig.minWidths.reply,
        build: panels._buildReply
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The reply comes from the service or from one of the destinations that are
// active, so the panel is those two groups side by side.
panels._buildReply = function(body) {

    var lines = $.fn.zato.wizard_kit.lines;
    var labels = panels.config.labels;
    var destinationsConfig = destinations.config;

    var columns = lines.buildColumns([labels.replyService, labels.replyDestinations]);
    body.appendChild(columns.row);

    var serviceList = document.createElement('div');
    serviceList.className = 'wizard-panel-list';

    var serviceName = wizard.field('service').val();
    var isService = wizard.state.respondFrom === destinationsConfig.respondFromService;

    serviceList.appendChild(lines.buildPickRow(serviceName, isService,
        panels._pickReply(destinationsConfig.respondFromService)));

    columns.columnList[0].appendChild(serviceList);

    var destinationList = document.createElement('div');
    destinationList.className = 'wizard-panel-list';

    var activeList = destinations.activeList();

    if(!activeList.length) {

        var empty = document.createElement('div');
        empty.className = 'wizard-panel-empty';
        empty.textContent = labels.noneActive;
        destinationList.appendChild(empty);
    }

    for(var activeIdx = 0; activeIdx < activeList.length; activeIdx++) {

        var connection = activeList[activeIdx].connection;
        var isPicked = wizard.state.respondFrom === connection;

        destinationList.appendChild(lines.buildPickRow(connection, isPicked, panels._pickReply(connection)));
    }

    columns.columnList[1].appendChild(destinationList);

    var out = null;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

panels._pickReply = function(name) {

    var out = function() {

        wizard.state.respondFrom = name;

        $.fn.zato.wizard_kit.lines.closePanel();
        destinations.render();
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
