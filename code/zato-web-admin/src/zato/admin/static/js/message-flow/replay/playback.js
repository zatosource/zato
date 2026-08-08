
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the playback. What the drawing shows at a given
// playhead, the clock that moves it one frame at a time, and every deliberate
// move of it - play, pause, a seek, a step, a change of clock.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

// What the drawing shows at the current playhead - idempotent, so the same
// walk serves the clock, a scrub in either direction and a step
replay.applyState = function() {
    var state = replay.state;
    var playedCount = replay.playedCountAt(state.position);

    state.playedCount = playedCount;

    // The node the pass currently stands on - the newest played event's
    var currentKey = '';

    if (playedCount > 0) {
        currentKey = state.events[playedCount - 1].key;
    }

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

        // The node the pass stands on wears the page's own selection amber
        node.element.classList.toggle('message-flow-replay-current', key === currentKey);
    }

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

        // The connector's words in the chip layer fade in and out with it
        for (var chipIndex = 0; chipIndex < connector.chipGroups.length; chipIndex++) {
            connector.chipGroups[chipIndex].classList.toggle('message-flow-replay-drawn', isDrawn);
        }

        for (var lineIndex = 0; lineIndex < connector.lines.length; lineIndex++) {
            connector.lines[lineIndex].style.strokeDashoffset = isDrawn ? '0' : String(connector.lineLengths[lineIndex]);
        }
    }

    // The room follows the pass - the newest played event's node is what the
    // canvas drifts toward, gently, never in a jump
    if (playedCount > 0) {
        var focusIndex = playedCount - 1;

        if (focusIndex !== state.cameraFocusIndex) {
            state.cameraFocusIndex = focusIndex;
            replay.followNode(state.nodes[state.events[focusIndex].key].element);
        }
    }
    else {
        state.cameraFocusIndex = -1;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The clock - one frame at a time, on whichever of the two axes the mode says
replay.tick = function(frameMs) {
    var state = replay.state;

    if (!state.isPlaying) {
        state.frameHandle = null;
        return;
    }

    // The speed control stretches or shrinks the frame's own ms, so it bends
    // both clocks alike - the real one and the compressed one
    var frameElapsedMs = (frameMs - state.lastFrameMs) * state.speed;
    state.lastFrameMs = frameMs;

    var previousCount = state.playedCount;
    var mode = replay.config.modes[state.modeIndex].key;

    if (mode === 'real') {

        // The real clock - the playhead advances by the wall's own ms
        var realMs = replay.positionToRealMs(state.position) + frameElapsedMs;
        state.position = replay.realMsToPosition(realMs);
    }
    else {

        // The compressed clock - the whole pass fits its few seconds
        state.position += frameElapsedMs * state.totalScaled / replay.config.compressedDurationMs;
    }

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

replay.stepForward = function() {
    var state = replay.state;
    var events = state.events;

    // The next unplayed event's own moment, or the end once there is none left
    if (state.playedCount < events.length) {
        replay.seek(events[state.playedCount].scaled);
    }
    else {
        replay.seek(state.totalScaled);
    }
};

// /////////////////////////////////////////////////////////////////////////////

replay.stepBack = function() {
    var state = replay.state;

    // Back to the moment of the event before the last played one, or all the
    // way to the dark room before the first
    if (state.playedCount >= 2) {
        replay.seek(state.events[state.playedCount - 2].scaled);
    }
    else {
        replay.seek(0);
    }
};

// /////////////////////////////////////////////////////////////////////////////

replay.setMode = function(modeIndex) {
    var state = replay.state;

    state.modeIndex = modeIndex;

    // No clock at all in step mode - the arrows alone move the playhead
    if (replay.config.modes[modeIndex].key === 'step') {
        replay.pause();
    }

    var modeButtons = replay.bar().querySelectorAll('.message-flow-replay-mode');

    for (var buttonIndex = 0; buttonIndex < modeButtons.length; buttonIndex++) {
        modeButtons[buttonIndex].classList.toggle('dashboard-panel-action-badge-active',
            buttonIndex === modeIndex);
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
