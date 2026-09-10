
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the playback. What the drawing shows at a given
// playhead, the auto-play clock that moves it one frame at a time, and every
// deliberate move of it - play, pause, a seek, a step, the track laid out anew.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

// What the drawing shows at the current playhead - idempotent, so the same
// walk serves the clock, a scrub in either direction and a step
replay.applyState = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var detail = $.fn.zato.message_flow.detail;

    var state = replay.state;
    var playedCount = replay.playedCountAt(state.position);

    state.playedCount = playedCount;

    // The node the pass currently stands on - the newest played event's
    var currentKey = '';

    if (playedCount > 0) {
        currentKey = state.events[playedCount - 1].key;
    }

    // The pass's node opens its exchange under the drawing the way a click
    // would - once per node - and the pane's tabs then follow the pass from
    // one event of the node to the next
    if (currentKey !== state.detailKey) {
        state.detailKey = currentKey;
        state.detailEventId = null;

        if (currentKey === '') {
            detail.hide();
        }
        else {
            var currentElement = state.nodes[currentKey].element;
            var detailIndex = parseInt(currentElement.getAttribute('data-node-index'), 10);

            detail.show(drawing.nodeDetails[detailIndex]);
        }
    }

    if (playedCount > 0) {
        var currentEventId = state.events[playedCount - 1].model.id;

        if (currentEventId !== state.detailEventId) {
            state.detailEventId = currentEventId;
            detail.openEvent(currentEventId);
        }
    }

    replay.markPlayedTicks(playedCount);

    for (var key in state.nodes) {
        var node = state.nodes[key];

        var playedOfNode = 0;
        var hasPlayedFailure = false;

        for (var indexOfIndex = 0; indexOfIndex < node.eventIndexes.length; indexOfIndex++) {
            var eventIndex = node.eventIndexes[indexOfIndex];

            if (eventIndex < playedCount) {
                playedOfNode += 1;

                if (replay.isBadOutcome(state.events[eventIndex].model)) {
                    hasPlayedFailure = true;
                }
            }
        }

        // A node no event of which has come yet stands dark, one mid-exchange
        // wears the dwell glow that heats with the wait, and one that failed
        // keeps the failure on it for the rest of the pass
        node.element.classList.toggle('message-flow-replay-unplayed', playedOfNode === 0);
        node.element.classList.toggle('message-flow-replay-waiting',
            playedOfNode > 0 && playedOfNode < node.eventIndexes.length);
        node.element.classList.toggle('message-flow-replay-failed', hasPlayedFailure);
    }

    // The whole way from the root to the node the pass stands on wears the
    // selection amber, the same way a hand-picked node's does - every key on
    // the walk from the current node back to the hub is on it
    var wayKeys = {};
    var wayKey = currentKey;

    while (wayKey !== '') {
        wayKeys[wayKey] = true;
        wayKey = state.connectorByTo[wayKey].fromKey;
    }

    // The node the pass stands on wears the selection amber and its glow, the
    // nodes on the way to it the border alone, the root among them whenever
    // the pass stands anywhere at all
    for (var nodeKey in state.nodes) {
        var wayNode = state.nodes[nodeKey].element;

        wayNode.classList.toggle('message-flow-replay-current', nodeKey === currentKey);
        wayNode.classList.toggle('message-flow-node-way', wayKeys[nodeKey] === true && nodeKey !== currentKey);
    }

    state.svg.querySelector('.message-flow-root').classList.toggle('message-flow-node-way', currentKey !== '');

    // A connector draws itself in the moment its node first speaks - seeking
    // back undraws it the same way
    for (var connectorIndex = 0; connectorIndex < state.connectors.length; connectorIndex++) {
        var connector = state.connectors[connectorIndex];

        var isDrawn = false;
        var targetIndexes = state.nodes[connector.toKey].eventIndexes;

        if (targetIndexes[0] < playedCount) {
            isDrawn = true;
        }

        connector.element.classList.toggle('message-flow-replay-drawn', isDrawn);
        connector.element.classList.toggle('message-flow-connector-current', wayKeys[connector.toKey] === true);

        // The connector's words in the chip layer fade in and out with it
        for (var chipIndex = 0; chipIndex < connector.chipGroups.length; chipIndex++) {
            connector.chipGroups[chipIndex].classList.toggle('message-flow-replay-drawn', isDrawn);
        }

        for (var lineIndex = 0; lineIndex < connector.lines.length; lineIndex++) {
            connector.lines[lineIndex].style.strokeDashoffset = isDrawn ? '0' : String(connector.lineLengths[lineIndex]);
        }
    }

    // The room follows the pass - the newest played event's node is what the
    // canvas drifts toward, gently, never in a jump, and a playhead pulled
    // back before the first event drifts the room home to the hub
    if (playedCount > 0) {
        var focusIndex = playedCount - 1;

        if (focusIndex !== state.cameraFocusIndex) {
            state.cameraFocusIndex = focusIndex;
            replay.followNode(state.nodes[state.events[focusIndex].key].element);
        }
    }
    else {
        state.cameraFocusIndex = -1;

        // Wherever the reader left the room standing, home is home
        replay.followNode(state.svg.querySelector('.message-flow-root'));
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The clock - one frame at a time along the scaled axis
replay.tick = function(frameMs) {
    var state = replay.state;

    if (!state.isPlaying) {
        state.frameHandle = null;
        return;
    }

    // The speed control stretches or shrinks the frame's own ms, bending
    // the auto-play clock with it
    var frameElapsedMs = (frameMs - state.lastFrameMs) * state.speed;
    state.lastFrameMs = frameMs;

    var previousCount = state.playedCount;

    // The auto-play clock - the whole pass fits its few seconds
    state.position += frameElapsedMs * state.totalScaled / replay.config.autoPlayDurationMs;

    if (state.position > state.totalScaled) {
        state.position = state.totalScaled;
    }

    // A failure freezes the pass on the node that failed - the playhead is
    // pulled back to that very moment and the clock stops there
    var newCount = replay.playedCountAt(state.position);

    for (var eventIndex = previousCount; eventIndex < newCount; eventIndex++) {
        var event = state.events[eventIndex];

        if (replay.isBadOutcome(event.model)) {
            state.position = event.scaled;
            state.isPlaying = false;

            replay.setNote(event.model.objectName + replay.config.labelSeparator +
                event.model.outcome.toUpperCase());

            break;
        }
    }

    // The end of the pass leaves the drawing standing fully annotated
    if (state.position >= state.totalScaled) {
        state.isPlaying = false;
    }

    replay.applyState();
    replay.updateBar();

    if (state.isPlaying) {
        state.frameHandle = window.requestAnimationFrame(replay.tick);
    }
    else {
        state.frameHandle = null;
    }
};

// /////////////////////////////////////////////////////////////////////////////

replay.play = function() {
    var state = replay.state;

    if (state.isPlaying) {
        return;
    }

    // The first press is what dresses the drawing for the pass
    replay.arm();

    // Playing again off the far end is a fresh pass
    if (state.position >= state.totalScaled) {
        state.position = 0;
    }

    replay.setNote('');

    state.isPlaying = true;
    state.lastFrameMs = window.performance.now();
    state.frameHandle = window.requestAnimationFrame(replay.tick);

    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

replay.pause = function() {
    var state = replay.state;

    state.isPlaying = false;

    if (state.frameHandle !== null) {
        window.cancelAnimationFrame(state.frameHandle);
        state.frameHandle = null;
    }

    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

replay.togglePlay = function() {
    if (replay.state.isPlaying) {
        replay.pause();
    }
    else {
        replay.play();
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A scrub, a step or a click on the track - a deliberate move of the playhead,
// so the clock stops and the drawing follows at once
replay.seek = function(position) {
    var state = replay.state;

    // A scrub is as much the start of a pass as Play is
    replay.arm();

    if (position < 0) {
        position = 0;
    }

    if (position > state.totalScaled) {
        position = state.totalScaled;
    }

    replay.pause();
    replay.setNote('');

    state.position = position;

    replay.applyState();
    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

// A step is event to event - the playhead lands on the moment of the next
// event, whichever node it is a line of, and past the last one on the end
// of the pass
replay.stepForward = function() {
    var state = replay.state;
    var events = state.events;

    if (state.playedCount < events.length) {
        replay.seek(events[state.playedCount].scaled);
        return;
    }

    replay.seek(state.totalScaled);
};

// /////////////////////////////////////////////////////////////////////////////

// Back one event - onto the moment of the one before the newest played, or
// into the dark room before the first event
replay.stepBack = function() {
    var state = replay.state;
    var events = state.events;

    if (state.playedCount < 2) {
        replay.seek(0);
        return;
    }

    replay.seek(events[state.playedCount - 2].scaled);
};

// /////////////////////////////////////////////////////////////////////////////

// The events laid out on the track anew, by the real time between them or an
// even step apart - the playhead stays on the event it stood on, wherever that
// event now stands, and the clock stops for the move
replay.setActualTime = function(isActualTime) {
    var state = replay.state;

    state.isActualTime = isActualTime;

    replay.bar().querySelector('.message-flow-replay-actual').classList.toggle(
        'dashboard-panel-action-badge-active', isActualTime);

    if (state.events.length === 0) {
        return;
    }

    var playedCount = state.playedCount;

    replay.scaleTimeline();
    replay.buildTicks();

    // A playhead that never left the dark room before the first event stays there
    if (playedCount === 0) {
        state.position = 0;
        replay.updateBar();
        return;
    }

    replay.seek(state.events[playedCount - 1].scaled);
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
