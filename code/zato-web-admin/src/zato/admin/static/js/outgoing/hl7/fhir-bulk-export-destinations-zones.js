// The destinations popover of the Bulk export tab - the badge picker of the security groups and the MCP
// gateways. Every connection of every type is a badge in the Available zone, with its type as a tag in
// front of its name, and a badge dragged or clicked over to the Assigned zone is a destination. A badge
// of a type that takes options carries them, shown as a link once the badge is assigned, and the link
// opens the options popover of fhir-bulk-export-destinations.js over the zones. A filter above the zones
// narrows the Available zone by type and by name. Loaded after fhir-bulk-export-destinations.js, next to
// common/badge-picker.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tab = $.fn.zato.outgoing.hl7.fhir.bulk_export_tab;

// ////////////////////////////////////////////////////////////////////////

tab.zones = {

    config: {

        // The badge picker names its elements after this
        action: 'fhir-bulk-export',

        fieldClass: 'fhir-bulk-export-zones-field',
        availableZoneClass: 'fhir-bulk-export-zone-available',
        optionsClass: 'fhir-bulk-export-zone-options',
        optionsLinkClass: 'zato-link-face fhir-bulk-export-zone-options-link',

        filterPlaceholder: 'Filter connections',
        allTypesLabel: 'All types',
        clearLabel: 'Clear',
        availableLabel: 'Available',
        assignedLabel: 'Assigned',

        // What tells a badge's type and name apart in its id
        idSeparator: '|',

        typeAttr: 'data-type',
        connectionAttr: 'data-connection',
        optionsAttr: 'data-options'
    }
};

var zones = tab.zones;

// ////////////////////////////////////////////////////////////////////////

zones.build = function(fieldSpec, row) {

    var config = tab.config;
    var zonesConfig = zones.config;

    row.className = config.ownFieldClass + ' ' + zonesConfig.fieldClass;

    row.appendChild(zones.buildFilter());
    row.appendChild(zones.buildPicker());

    // The picker looks its zones up by id through the document, so it is wired once the popover is mounted
    tab.whenOnScreen(row, function() {
        $.fn.zato.badge_picker.init(zonesConfig.action, zones.buildItems(), zones.pickerConfig());
    });
};

// ////////////////////////////////////////////////////////////////////////

// The type select, the name filter and Clear above the zones, under the ids the picker listens on
zones.buildFilter = function() {

    var zonesConfig = zones.config;
    var action = zonesConfig.action;
    var typeLabelMap = tab.typeLabelMap();

    var filter = document.createElement('div');
    filter.className = 'badge-picker-filter';
    filter.id = 'badge-filter-' + action;

    var typeSelect = document.createElement('select');
    typeSelect.id = 'badge-security-type-' + action;

    var allOption = document.createElement('option');
    allOption.value = '';
    allOption.textContent = zonesConfig.allTypesLabel;
    typeSelect.appendChild(allOption);

    tab.config.typeOrder.forEach(function(type) {
        var option = document.createElement('option');
        option.value = type;
        option.textContent = typeLabelMap[type];
        typeSelect.appendChild(option);
    });

    filter.appendChild(typeSelect);

    var textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.id = 'badge-filter-text-' + action;
    textInput.placeholder = zonesConfig.filterPlaceholder;
    filter.appendChild(textInput);

    var clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'badge-filter-clear';
    clear.id = 'badge-filter-clear-' + action;
    clear.textContent = zonesConfig.clearLabel;
    filter.appendChild(clear);

    var out = filter;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zones.buildZone = function(name, label, extraClass) {

    var zone = document.createElement('div');
    zone.className = 'badge-zone ' + extraClass;
    zone.id = 'badge-zone-' + name + '-' + zones.config.action;

    var header = document.createElement('div');
    header.className = 'badge-zone-header';
    header.textContent = label + ' (';

    var count = document.createElement('span');
    count.className = 'badge-zone-count';
    count.textContent = '0';
    header.appendChild(count);

    header.appendChild(document.createTextNode(')'));
    zone.appendChild(header);

    var body = document.createElement('div');
    body.className = 'badge-zone-body';
    zone.appendChild(body);

    var out = zone;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The two zones with the resizer between them, the markup the picker wires itself to
zones.buildPicker = function() {

    var zonesConfig = zones.config;

    var picker = document.createElement('div');
    picker.className = 'badge-picker';
    picker.id = 'badge-picker-' + zonesConfig.action;

    picker.appendChild(zones.buildZone('available', zonesConfig.availableLabel, zonesConfig.availableZoneClass));

    var resizer = document.createElement('div');
    resizer.className = 'badge-picker-resizer';
    picker.appendChild(resizer);

    picker.appendChild(zones.buildZone('assigned', zonesConfig.assignedLabel, ''));

    var out = picker;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every connection of every type as a picker item, the ones on the list assigned
zones.buildItems = function() {

    var zonesConfig = zones.config;
    var out = [];

    tab.config.typeOrder.forEach(function(type) {

        var rows = tab.connectionRows(type);

        for(var rowIdx = 0; rowIdx < rows.length; rowIdx++) {

            var name = rows[rowIdx].name;
            var destination = tab.findDestination(type, name);

            var options = {};
            if(destination !== null) {
                options = destination.options;
            }

            out.push({
                id: type + zonesConfig.idSeparator + name,
                name: name,
                type: type,
                is_member: destination !== null,
                options: options
            });
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How the picker builds, sorts, places and filters the badges
zones.pickerConfig = function() {

    var zonesConfig = zones.config;
    var typeOrder = tab.config.typeOrder;

    var out = {

        make_badge: function(item, num) {

            var badge = $('<div/>', {'class': 'security-badge', 'data-id': item.id, 'data-name': item.name.toLowerCase()});
            badge.attr(zonesConfig.typeAttr, item.type);
            badge.attr(zonesConfig.connectionAttr, item.name);
            badge.attr(zonesConfig.optionsAttr, JSON.stringify(item.options));

            badge.append($('<span/>', {'class': 'security-badge-indicator'}));
            badge.append($('<span/>', {'class': 'security-badge-number', 'text': num + '.'}));
            badge.append(tab.buildTypeTag(item.type));
            badge.append($('<span/>', {'class': 'security-badge-name', 'text': item.name}));

            // A type that takes options carries them on its badge, on show once it stands in the Assigned zone
            if(tab.typeHasOptions(item.type)) {
                badge.append(zones.buildOptionsLink(badge[0]));
            }

            return badge;
        },

        sort_items: function(a, b) {

            var typeOrderDiff = typeOrder.indexOf(a.type) - typeOrder.indexOf(b.type);

            if(typeOrderDiff !== 0) {
                return typeOrderDiff;
            }

            return a.name.localeCompare(b.name);
        },

        is_assigned: function(item) {
            return item.is_member;
        },

        filter_badge: function(badge, textWords, typeValue) {

            if(typeValue && badge.attr(zonesConfig.typeAttr) !== typeValue) {
                return false;
            }

            var name = badge.data('name');

            for(var wordIdx = 0; wordIdx < textWords.length; wordIdx++) {
                if(name.indexOf(textWords[wordIdx]) === -1) {
                    return false;
                }
            }

            return true;
        }
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The options of a badge - a link reading what they are, which opens the popover that edits them
zones.buildOptionsLink = function(badge) {

    var zonesConfig = zones.config;

    var holder = document.createElement('span');
    holder.className = zonesConfig.optionsClass;

    var link = document.createElement('a');
    link.href = 'javascript:void(0)';
    link.className = zonesConfig.optionsLinkClass;
    holder.appendChild(link);

    zones.renderOptions(badge, link);

    // The link answers to its own click, the badge is not moved by it
    link.addEventListener('click', function(event) {
        event.stopPropagation();
        tab.state.optionsBadge = badge;
        tab.openOptions(zones.badgeType(badge), zones.badgeConnection(badge), zones.badgeOptions(badge), link);
    });

    link.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    var out = holder;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zones.renderOptions = function(badge, link) {
    link.textContent = tab.optionsText(zones.badgeType(badge), zones.badgeOptions(badge));
};

// ////////////////////////////////////////////////////////////////////////

zones.badgeType = function(badge) {
    var out = badge.getAttribute(zones.config.typeAttr);
    return out;
};

zones.badgeConnection = function(badge) {
    var out = badge.getAttribute(zones.config.connectionAttr);
    return out;
};

zones.badgeOptions = function(badge) {
    var out = JSON.parse(badge.getAttribute(zones.config.optionsAttr));
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// OK in the options popover puts what it holds on the badge it was opened for
zones.takeOptions = function() {

    var zonesConfig = zones.config;
    var badge = tab.state.optionsBadge;

    var options = tab.readOptionsStore(zones.badgeType(badge));
    badge.setAttribute(zonesConfig.optionsAttr, JSON.stringify(options));

    var link = badge.querySelector('.' + zonesConfig.optionsClass + ' a');
    zones.renderOptions(badge, link);
};

// ////////////////////////////////////////////////////////////////////////

// OK reads the Assigned zone back into the list
zones.save = function(popper, fieldSpec) {

    var zonesConfig = zones.config;
    var badges = popper.querySelectorAll('#badge-zone-assigned-' + zonesConfig.action + ' .security-badge');
    var destinationList = [];

    // An options popover still open belongs to the zones being closed
    tab.optionsHost.forms.close();

    for(var badgeIdx = 0; badgeIdx < badges.length; badgeIdx++) {

        var badge = badges[badgeIdx];

        destinationList.push({
            type: zones.badgeType(badge),
            connection: zones.badgeConnection(badge),
            isActive: true,
            options: zones.badgeOptions(badge)
        });
    }

    tab.state.destinationList = destinationList;
    tab.serialize();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
