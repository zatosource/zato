
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

    // How long one whole auto-play pass takes, whatever the flow's real
    // span was
    autoPlayDurationMs: 6000,

    // Each event holds the auto-play clock for at least this long, so two
    // events of the same millisecond still read one after another, and the
    // clock runs this much past the last event before the pass is over
    eventBeat: 0.6,

    // The words of the bar - each control says its own name natively
    playLabel: 'Play',
    pauseLabel: 'Pause',

    // The control that lays the events out on the track by the real time between
    // them - off, they stand an even step apart whatever the time between them was
    actualTimeLabel: 'Actual time',
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

    // What the keys do, read under the keyboard control - one group for a node
    // picked by hand, whose keys walk the drawing, one for the pass, whose keys
    // drive the clock
    shortcutGroups: [
        {
            title: 'With a node picked',
            shortcuts: [
                {keys: 'Left / Right', label: 'Previous / next node'},
                {keys: 'Up / Down', label: 'Previous / next row, on past the node\'s ends'},
                {keys: 'Home / End', label: 'First / last node'},
                {keys: 'Esc', label: 'Let the node go'}
            ]
        },
        {
            title: 'During a pass',
            shortcuts: [
                {keys: 'Space', label: 'Play and pause'},
                {keys: 'Left / Right', label: 'Previous / next event'},
                {keys: 'Home / End', label: 'Start / end'},
                {keys: 'T', label: 'Actual time on / off'},
                {keys: 'Esc', label: 'End the pass'}
            ]
        }
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

    // Whether the events stand on the track by the real time between them
    // rather than an even step apart - off until the reader asks for it
    isActualTime: false,

    // How fast the clock runs against its own speed - one is the clock's own
    speed: 1,

    // Where the playhead stands on the scaled axis
    position: 0,

    // The timeline - every event of the drawing in the order it happened,
    // each entry carrying its real moment and its place on the scaled axis
    events: [],
    totalScaled: 0,
    startMs: 0,
    endMs: 0,

    // The drawn things the playback moves - the nodes by their exchange key
    // and the connector sets with their words, each also found by the node
    // it leads into
    nodes: {},
    connectors: [],
    connectorByTo: {},
    svg: null,

    // How many events the last frame had already played, which is what a new
    // frame compares against to see what has just happened
    playedCount: 0,

    // The event whose node the canvas last drifted toward
    cameraFocusIndex: -1,

    // The node whose exchange the pass last opened under the drawing, and the
    // event of it the pane's tabs were last brought to
    detailKey: '',
    detailEventId: null,

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

// The room falls dark and the connectors ready their dashes - the first press
// of Play, a step or a scrub is what asks for this, the bar itself is always
// on the page
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

    state.isActive = true;

    state.svg.classList.add('message-flow-replay');
};

// /////////////////////////////////////////////////////////////////////////////

// Everything the pass put on the drawing comes off it - classes and inline
// dash styles alike - and the drawing stands as it stood before, the bar
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
    state.detailKey = '';
    state.detailEventId = null;

    for (var key in state.nodes) {
        var element = state.nodes[key].element;

        element.classList.remove('message-flow-replay-unplayed');
        element.classList.remove('message-flow-replay-waiting');
        element.classList.remove('message-flow-replay-failed');
        element.classList.remove('message-flow-replay-current');
    }

    for (var connectorIndex = 0; connectorIndex < state.connectors.length; connectorIndex++) {
        var connector = state.connectors[connectorIndex];

        connector.element.classList.remove('message-flow-replay-drawn');
        connector.element.classList.remove('message-flow-connector-current');

        for (var chipIndex = 0; chipIndex < connector.chipGroups.length; chipIndex++) {
            connector.chipGroups[chipIndex].classList.remove('message-flow-replay-drawn');
        }

        for (var lineIndex = 0; lineIndex < connector.lines.length; lineIndex++) {
            connector.lines[lineIndex].style.strokeDashoffset = '';
        }
    }

    state.svg.classList.remove('message-flow-replay');

    replay.markCurrentTick(0);

    // The pane the pass had open on its last event closes with the pass, and
    // with it the marks on that event's row
    $.fn.zato.message_flow.detail.hide();

    replay.setNote('');
    replay.updateBar();
};

// /////////////////////////////////////////////////////////////////////////////

// A journey has just been drawn - whatever pass was running belonged to the
// drawing that is gone, and the bar stands ready over the new one
replay.onJourney = function() {
    replay.disarm();

    // The keys belong to the pass now - the field the search was typed into
    // lets the focus go, so the space bar plays rather than types
    if (document.activeElement.matches('input, textarea')) {
        document.activeElement.blur();
    }

    replay.buildTimeline();
    replay.buildTicks();

    replay.state.position = 0;
    replay.state.playedCount = 0;

    replay.bar().classList.add('message-flow-replay-bar-active');

    // Wherever the bar was left - pulled loose or folded away - is where the
    // new journey finds it
    replay.applyFloat();

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
