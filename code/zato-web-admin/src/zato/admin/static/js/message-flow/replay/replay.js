
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the replay. The drawn journey played back in the order things
// truly ran - the room falls dark, the clock starts, and each event lights its
// node as its moment comes, connectors drawing themselves in and elapsed chips
// staying behind, so one pass leaves the drawing annotated with where the time
// went. The bar under the canvas walks the same timeline both ways, a failure
// freezes the clock on the node that failed, and the keyboard drives all of it.
//
// This file is the replay's spine - its words, its state, and the pass's
// dress going on and off the drawing. The timeline and its two axes live in
// timeline.js, moving the playhead in playback.js, the bar with the keyboard
// in bar.js, the bar off its moorings in float.js, and the canvas drifting
// after the pass in camera.js.

$.fn.zato.message_flow.replay = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

replay.config = {

    barId: 'message-flow-replay-bar',

    // How long one whole pass takes on the compressed clock, whatever the
    // flow's real span was
    compressedDurationMs: 6000,

    // Each event holds the compressed clock for at least this long, so two
    // events of the same millisecond still read one after another, and the
    // clock runs this much past the last event before the pass is over
    eventBeat: 0.6,

    // The three clocks - the compressed one, the real one and no clock at all,
    // the arrows alone moving the playhead
    modes: [
        {key: 'compressed', label: 'Compressed', icon: 'compressed'},
        {key: 'real', label: 'Real time', icon: 'clock'},
        {key: 'step', label: 'Step', icon: 'step'}
    ],

    // The words of the bar - each control says its own name natively
    playLabel: 'Play',
    pauseLabel: 'Pause',
    speedLabel: 'Speed',
    speedUnit: 'x',
    shortcutsLabel: 'Keyboard shortcuts',
    moveLabel: 'Move',
    minimizeLabel: 'Minimize',

    // How fast the clock may be run, in hundredths of its own speed
    speedLeast: 25,
    speedMost: 300,
    speedStep: 25,
    speedPlain: 100,

    // What the keys do, read under the keyboard control
    shortcuts: [
        {keys: 'Space', label: 'Play and pause'},
        {keys: 'Right', label: 'Next event'},
        {keys: 'Left', label: 'Previous event'},
        {keys: 'Up / Down', label: 'Clock mode'},
        {keys: 'Esc', label: 'End the pass'}
    ],

    // The one outcome that is not a failure - an event reporting any other
    // outcome freezes the playback on its node
    goodOutcome: 'ok',

    labelSeparator: ' \u00b7 '
};

// /////////////////////////////////////////////////////////////////////////////

replay.state = {
    isActive: false,
    isPlaying: false,
    modeIndex: 0,

    // How fast the clock runs against its own speed - one is the clock's own
    speed: 1,

    // Where the playhead stands on the compressed axis
    position: 0,

    // The timeline - every event of the drawing in the order it happened,
    // each entry carrying its real moment and its place on the compressed axis
    events: [],
    totalScaled: 0,
    startMs: 0,
    endMs: 0,

    // The drawn things the playback moves - the nodes by their exchange key,
    // the connector sets, and the chips the replay itself put on the drawing
    nodes: {},
    connectors: [],
    replayChips: [],
    svg: null,

    // How many events the last frame had already played, which is what a new
    // frame compares against to see what has just happened
    playedCount: 0,

    // The event whose node the canvas last drifted toward
    cameraFocusIndex: -1,

    frameHandle: null,
    lastFrameMs: 0
};

// /////////////////////////////////////////////////////////////////////////////

replay.bar = function() {
    return document.getElementById(replay.config.barId);
};

// /////////////////////////////////////////////////////////////////////////////

// A reported outcome that is not the good one is a failure
replay.isBadOutcome = function(model) {
    if (model.outcome === '') {
        return false;
    }

    return model.outcome !== replay.config.goodOutcome;
};

// /////////////////////////////////////////////////////////////////////////////
// The pass's dress on the drawing - put on when a pass starts, taken off by Esc
// /////////////////////////////////////////////////////////////////////////////

// The room falls dark, the connectors ready their dashes and the elapsed chips
// take their places - the first press of Play, a step or a scrub is what asks
// for this, the bar itself is always on the page
replay.arm = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var state = replay.state;

    if (state.isActive) {
        return;
    }

    // A held selection would keep its branch lit through the dark room
    if (drawing.deselect !== null) {
        drawing.deselect();
    }

    replay.addElapsedChips();

    state.isActive = true;

    state.svg.classList.add('message-flow-replay');
};

// /////////////////////////////////////////////////////////////////////////////

// Everything the pass put on the drawing comes off it - classes, inline dash
// styles and chips alike - and the drawing stands as it stood before, the bar
// standing by with the playhead back at the start
replay.disarm = function() {
    var state = replay.state;

    if (!state.isActive) {
        return;
    }

    replay.pause();
    replay.stopCamera();

    state.isActive = false;
    state.position = 0;
    state.playedCount = 0;
    state.cameraFocusIndex = -1;

    for (var key in state.nodes) {
        var element = state.nodes[key].element;

        element.classList.remove('message-flow-replay-unplayed');
        element.classList.remove('message-flow-replay-waiting');
        element.classList.remove('message-flow-replay-failed');
    }

    for (var connectorIndex = 0; connectorIndex < state.connectors.length; connectorIndex++) {
        var connector = state.connectors[connectorIndex];

        connector.element.classList.remove('message-flow-replay-drawn');

        for (var chipIndex = 0; chipIndex < connector.chipGroups.length; chipIndex++) {
            connector.chipGroups[chipIndex].classList.remove('message-flow-replay-drawn');
        }

        for (var lineIndex = 0; lineIndex < connector.lines.length; lineIndex++) {
            connector.lines[lineIndex].style.strokeDashoffset = '';
        }
    }

    // The chips the pass added leave the drawing and their connectors' own
    // registers alike, so the next pass starts from a clean slate
    for (var replayChipIndex = 0; replayChipIndex < state.replayChips.length; replayChipIndex++) {
        var replayChip = state.replayChips[replayChipIndex];

        replayChip.element.remove();

        var chipPlace = replayChip.connector.chipGroups.indexOf(replayChip.element);
        replayChip.connector.chipGroups.splice(chipPlace, 1);
    }

    state.replayChips = [];

    state.svg.classList.remove('message-flow-replay');

    replay.setNote('');
    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

// A journey has just been drawn - whatever pass was running belonged to the
// drawing that is gone, and the bar stands ready over the new one
replay.onJourney = function() {
    replay.disarm();

    replay.buildTimeline();
    replay.buildTicks();

    replay.state.position = 0;
    replay.state.playedCount = 0;

    replay.bar().classList.add('message-flow-replay-bar-active');

    // Wherever the bar was left - pulled loose or folded away - is where the
    // new journey finds it
    replay.applyFloat();

    replay.setMode(0);
    replay.setNote('');
    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

// The canvas holds no drawing - a hint, a spinner - so there is nothing to play
// and no bar to hold it
replay.onCleared = function() {
    replay.disarm();

    replay.state.events = [];

    replay.bar().classList.remove('message-flow-replay-bar-active');
    replay.hideDock();
};

// /////////////////////////////////////////////////////////////////////////////

replay.init = function() {
    replay.buildBar();

    replay.loadFloatState();
    replay.buildFloat();

    replay.initCamera();

    document.addEventListener('keydown', replay.onKeyDown);
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
