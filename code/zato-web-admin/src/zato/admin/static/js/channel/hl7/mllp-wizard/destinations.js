// HL7 MLLP channel wizard - what happens to a message on step 2.
//
// The step is four sentences, one decision each - where messages go, which
// service handles them, in what order the destinations receive them and
// which one of them produces the reply. Every value is a chip opening a
// panel of the wizard kit's decision lines, the panels themselves are in
// destination-panels.js. The answers serialize into the form's hidden
// "destinations", "respond_from" and "delivery_mode" fields in the very
// shape the full-page editor produces, reusing the type and option
// definitions of the shared destinations module.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.channel.hl7.mllp.wizard;
var destinations = wizard.destinations;

// ////////////////////////////////////////////////////////////////////////

destinations.config = {

    // What the caller's response defaults to
    respondFromService: 'service',

    // What a service is called where it is listed next to destinations, so
    // that both read the same way - the kind first, then the name
    serviceKindLabel: 'Service',

    // The slots on the step the four values are written into
    slots: {
        destinations: 'mllp-wizard-slot-destinations',
        service: 'mllp-wizard-slot-service',
        delivery: 'mllp-wizard-slot-delivery',
        reply: 'mllp-wizard-slot-reply'
    },

    // The line that only makes sense once there is a destination
    deliveryLineId: 'mllp-wizard-line-delivery',

    // How the destinations reach their messages - the last one is the
    // service's own call, made through self.destination[name]
    deliveryModeList: [
        {name: 'same-time', label: 'At the same time'},
        {name: 'in-order', label: 'One after another'},
        {name: 'service-decides', label: 'The service decides'}
    ],

    // What a chip says
    noDestinationsLabel: 'none yet',
    oneDestinationLabel: '1 destination',
    manyDestinationsLabel: ' destinations',
    pausedLabel: ' paused',
    noServiceLabel: 'none',
    noReplyLabel: 'nothing replies'
};

// Connections grouped by destination type, loaded once per page
destinations._connectionData = null;

// ////////////////////////////////////////////////////////////////////////

destinations.init = function() {

    // The step reads as soon as it is opened, so the connections are on
    // their way before anything is clicked ..
    destinations._loadConnectionData();

    // .. and until they arrive the lines already show what the state holds.
    destinations.settle();
    destinations.render();
};

// ////////////////////////////////////////////////////////////////////////

// Loads the connection list once and redraws the lines with it.
destinations._loadConnectionData = function() {

    var onLoaded = function(data, status) {

        if(status === 'success') {
            destinations._connectionData = JSON.parse(data.responseText);
            destinations.render();
        }
    };

    $.fn.zato.post($.fn.zato.destinations.config.connectionListUrl, onLoaded, '', '', true);
};

// ////////////////////////////////////////////////////////////////////////

// The destinations messages are actually delivered to.
destinations.activeList = function() {

    var out = [];

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {

        var destination = wizard.state.destinationList[destinationIdx];

        if(destination.isActive) {
            out.push(destination);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many destinations are there but receive nothing.
destinations.pausedCount = function() {

    var activeCount = destinations.activeList().length;
    var out = wizard.state.destinationList.length - activeCount;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A destination taken off the list cannot be the one replying any more, so
// the reply falls back to the service.
destinations.settle = function() {

    if(wizard.state.respondFrom === destinations.config.respondFromService) {
        return;
    }

    var destinationList = wizard.state.destinationList;
    var names = [];

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {
        names.push(destinationList[destinationIdx].connection);
    }

    if(names.indexOf(wizard.state.respondFrom) === -1) {
        wizard.state.respondFrom = destinations.config.respondFromService;
    }
};

// ////////////////////////////////////////////////////////////////////////

destinations.render = function() {

    var lines = $.fn.zato.wizard_kit.lines;
    var destinationsConfig = destinations.config;

    lines.setChip(destinationsConfig.slots.destinations, destinations._destinationChip());
    lines.setChip(destinationsConfig.slots.service, destinations._serviceChip());
    lines.setChip(destinationsConfig.slots.reply, destinations._replyChip());

    lines.setSegments(destinationsConfig.slots.delivery, destinationsConfig.deliveryModeList,
        wizard.state.delivery, destinations._pickDelivery);

    // The order they receive messages in is a question only a list can raise
    var hasDestinations = wizard.state.destinationList.length > 0;
    $('#' + destinationsConfig.deliveryLineId).prop('hidden', !hasDestinations);

    wizard.review.refreshSummaries();
};

// ////////////////////////////////////////////////////////////////////////

destinations._pickDelivery = function(name) {

    wizard.state.delivery = name;
    destinations.render();
};

// ////////////////////////////////////////////////////////////////////////

destinations._destinationChip = function() {

    var destinationsConfig = destinations.config;
    var count = wizard.state.destinationList.length;
    var paused = destinations.pausedCount();

    var text = count + destinationsConfig.manyDestinationsLabel;

    if(count === 0) {
        text = destinationsConfig.noDestinationsLabel;
    }
    else if(count === 1) {
        text = destinationsConfig.oneDestinationLabel;
    }

    var out = {
        text: text,
        note: paused ? paused + destinationsConfig.pausedLabel : '',
        isBlank: count === 0,
        panel: destinations.panels.destinationsPanel()
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

destinations._serviceChip = function() {

    var name = wizard.field('service').val();

    var out = {
        text: name ? name : destinations.config.noServiceLabel,
        note: '',
        isBlank: !name,
        panel: destinations.panels.servicePanel()
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

destinations._replyChip = function() {

    var text = destinations.replyLabel();

    var out = {
        text: text,
        note: '',
        isBlank: text === destinations.config.noReplyLabel,
        panel: destinations.panels.replyPanel()
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What each destination type is called, keyed by the type itself, so that
// labelling a list of destinations reads the type list once rather than
// searching it once per destination.
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

// What the review says about the order messages are delivered in.
destinations.deliveryLabel = function() {

    var modeList = destinations.config.deliveryModeList;

    for(var modeIdx = 0; modeIdx < modeList.length; modeIdx++) {
        if(modeList[modeIdx].name === wizard.state.delivery) {
            var out = modeList[modeIdx].label;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What replies to the caller, named the way the reply panel names it - the
// kind first, then the name, whether that is the service or a destination.
destinations.replyLabel = function() {

    var destinationsConfig = destinations.config;
    var name = wizard.state.respondFrom;

    if(name === destinationsConfig.respondFromService) {

        var serviceName = wizard.field('service').val();

        if(!serviceName) {
            return destinationsConfig.noReplyLabel;
        }

        var out = destinationsConfig.serviceKindLabel + ' - ' + serviceName;
        return out;
    }

    var typeLabelMap = destinations._getTypeLabelMap();
    var destinationList = wizard.state.destinationList;

    for(var destinationIdx = 0; destinationIdx < destinationList.length; destinationIdx++) {

        var destination = destinationList[destinationIdx];

        if(destination.connection === name) {
            out = typeLabelMap[destination.type] + ' - ' + name;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Writes the answers into the form's hidden fields before submit.
destinations.serialize = function() {

    var serialized = [];

    for(var destinationIdx = 0; destinationIdx < wizard.state.destinationList.length; destinationIdx++) {

        var destination = wizard.state.destinationList[destinationIdx];

        serialized.push({
            'name': destination.connection,
            'type': destination.type,
            'connection': destination.connection,
            'is_active': destination.isActive,
            'options': destination.options
        });
    }

    wizard.field('destinations').val(serialized.length ? JSON.stringify(serialized) : '');
    wizard.field('respond_from').val(wizard.state.respondFrom);
    wizard.field('delivery_mode').val(wizard.state.delivery);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
