
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the timeline. Every event of the drawing in the order
// it happened, each entry tied to the node it lights, and the two axes the
// playback runs on - the compressed one the playhead walks and the real one
// the clock face reads, tied together at every event.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

replay.buildTimeline = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var state = replay.state;

    state.svg = drawing.canvas().querySelector('svg');
    state.events = [];
    state.nodes = {};
    state.connectors = [];
    state.replayChips = [];

    // Every exchange node's events, each remembering the node it lights -
    // the hub stands for the message itself and holds no moment of its own
    for (var detailIndex = 0; detailIndex < drawing.nodeDetails.length; detailIndex++) {
        var nodeDetail = drawing.nodeDetails[detailIndex];

        if (nodeDetail.key === '') {
            continue;
        }

        var nodeElement = state.svg.querySelector('[data-node-index="' + detailIndex + '"]');

        state.nodes[nodeDetail.key] = {
            element: nodeElement,
            title: nodeDetail.title,
            eventIndexes: [],
            firstMs: 0
        };

        for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
            var model = nodeDetail.models[modelIndex];

            state.events.push({
                ms: new Date(model.timeIso).getTime(),
                model: model,
                key: nodeDetail.key
            });
        }
    }

    // Time forward, two events of one moment told apart by their ids
    state.events.sort(function(first, second) {
        if (first.ms !== second.ms) {
            return first.ms - second.ms;
        }

        return Number(first.model.id) - Number(second.model.id);
    });

    state.startMs = state.events[0].ms;
    state.endMs = state.events[state.events.length - 1].ms;

    // The compressed axis - every event holds the clock for at least a beat,
    // and a real gap adds its logarithm, so a 2ms hop still reads next to a
    // 3s one and a view days later does not push the pass into next week
    var scaled = 0;

    for (var eventIndex = 0; eventIndex < state.events.length; eventIndex++) {
        var event = state.events[eventIndex];

        var gapMs = 0;

        if (eventIndex > 0) {
            gapMs = event.ms - state.events[eventIndex - 1].ms;
        }

        scaled += replay.config.eventBeat + Math.log1p(gapMs);
        event.scaled = scaled;

        var node = state.nodes[event.key];

        if (node.eventIndexes.length === 0) {
            node.firstMs = event.ms;
        }

        node.eventIndexes.push(eventIndex);
    }

    // A tail beat past the last event, so the end of the pass is not abrupt
    state.totalScaled = scaled + replay.config.eventBeat;

    // The connectors - each one drawn in when the node it leads into first
    // plays, its line hidden until then by its own full dash offset, and its
    // words in the chip layer fading in with it
    var connectorSets = state.svg.querySelectorAll('.message-flow-connector-set');
    var allChipGroups = state.svg.querySelectorAll('.message-flow-connector-chip');

    for (var setIndex = 0; setIndex < connectorSets.length; setIndex++) {
        var setElement = connectorSets[setIndex];
        var toKey = setElement.getAttribute('data-connector-to');

        var lines = setElement.querySelectorAll('.message-flow-connector');
        var lineLengths = [];

        // Each line becomes one dash as long as itself - sliding the dash's
        // offset between that length and zero is what draws the line in
        for (var lineIndex = 0; lineIndex < lines.length; lineIndex++) {
            var lineLength = lines[lineIndex].getTotalLength();

            lineLengths.push(lineLength);
            lines[lineIndex].style.strokeDasharray = String(lineLength);
        }

        // The connector's words live in the chip layer over the lines, found
        // by the node the connector leads into
        var chipGroups = [];

        for (var chipIndex = 0; chipIndex < allChipGroups.length; chipIndex++) {
            if (allChipGroups[chipIndex].getAttribute('data-connector-to') === toKey) {
                chipGroups.push(allChipGroups[chipIndex]);
            }
        }

        state.connectors.push({
            element: setElement,
            toKey: toKey,
            fromKey: setElement.getAttribute('data-connector-from'),
            anchorX: Number(setElement.getAttribute('data-anchor-x')),
            anchorY: Number(setElement.getAttribute('data-anchor-y')),
            lines: lines,
            lineLengths: lineLengths,
            chipGroups: chipGroups
        });
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The elapsed chips the replay leaves behind - a connector off the hub carries
// none of its own, so the replay writes how long after the flow's first moment
// its node first spoke. Chained connectors already carry their elapsed words.
// The chips go into the chip layer, over every line and under every card, so
// no crossing connector runs through them and they stand over no node.
replay.addElapsedChips = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var state = replay.state;
    var chipHeight = drawing.config.chipHeight;

    var chipLayer = state.svg.querySelector('.message-flow-chip-layer');

    for (var connectorIndex = 0; connectorIndex < state.connectors.length; connectorIndex++) {
        var connector = state.connectors[connectorIndex];

        if (connector.fromKey !== '') {
            continue;
        }

        var elapsedMs = state.nodes[connector.toKey].firstMs - state.startMs;
        var label = '+' + kit.format_duration_ms(elapsedMs);

        var chipGroup = drawing.addGroup(chipLayer, 'message-flow-connector-chip message-flow-replay-chip');
        chipGroup.setAttribute('data-connector-to', connector.toKey);

        var chipWidth = drawing.chipWidth(label);

        drawing.addChip(chipGroup, connector.anchorX - chipWidth / 2, connector.anchorY - chipHeight / 2,
            label, 'muted', true);

        // The pass fades the chip in with its connector, and the disarm takes
        // it off both the drawing and the connector's own register
        connector.chipGroups.push(chipGroup);
        state.replayChips.push({element: chipGroup, connector: connector});
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The real moment the playhead stands at, as ms past the flow's first event
replay.positionToRealMs = function(position) {
    var state = replay.state;
    var events = state.events;

    var firstScaled = events[0].scaled;

    // Before the first event the clock holds at that event's own moment
    if (position <= firstScaled) {
        return 0;
    }

    var lastEvent = events[events.length - 1];

    if (position >= lastEvent.scaled) {
        return lastEvent.ms - state.startMs;
    }

    // Between two events the clock runs the real gap between them, so it
    // visibly accelerates through the dead time the axis compressed
    for (var eventIndex = 1; eventIndex < events.length; eventIndex++) {
        var current = events[eventIndex];

        if (position > current.scaled) {
            continue;
        }

        var previous = events[eventIndex - 1];
        var segmentShare = (position - previous.scaled) / (current.scaled - previous.scaled);

        var out = (previous.ms - state.startMs) + segmentShare * (current.ms - previous.ms);

        return out;
    }

    return lastEvent.ms - state.startMs;
};

// /////////////////////////////////////////////////////////////////////////////

// Where on the compressed axis a real moment falls - the real-time clock
// advances real ms and lands back here
replay.realMsToPosition = function(realMs) {
    var state = replay.state;
    var events = state.events;

    if (realMs <= 0) {
        return events[0].scaled;
    }

    var lastRealMs = events[events.length - 1].ms - state.startMs;

    if (realMs >= lastRealMs) {
        return state.totalScaled;
    }

    for (var eventIndex = 1; eventIndex < events.length; eventIndex++) {
        var current = events[eventIndex];
        var currentRealMs = current.ms - state.startMs;

        if (realMs > currentRealMs) {
            continue;
        }

        var previous = events[eventIndex - 1];
        var previousRealMs = previous.ms - state.startMs;

        // Events of one moment share a point on the real axis - the playhead
        // steps past all of them at once, which is what truly happened
        if (currentRealMs === previousRealMs) {
            return current.scaled;
        }

        var segmentShare = (realMs - previousRealMs) / (currentRealMs - previousRealMs);

        var out = previous.scaled + segmentShare * (current.scaled - previous.scaled);

        return out;
    }

    return state.totalScaled;
};

// /////////////////////////////////////////////////////////////////////////////

// How many events the playhead has passed
replay.playedCountAt = function(position) {
    var events = replay.state.events;
    var out = 0;

    for (var eventIndex = 0; eventIndex < events.length; eventIndex++) {
        if (events[eventIndex].scaled <= position) {
            out = eventIndex + 1;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
