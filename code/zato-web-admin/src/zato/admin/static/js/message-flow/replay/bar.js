
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the bar under the canvas and the keys. Play with the
// speed beside it, the three clocks, the track the playhead walks with one
// tick per event, the clock face, a failure's freeze note, and the keyboard
// control whose overlay reads the keys out. Every control wears an icon and
// says its own name natively.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

// The strokes every icon on the bar is drawn from
replay.icons = {

    play: [
        {d: 'M8 5v14l11-7z', isFilled: true}
    ],

    pause: [
        {d: 'M6 5h4v14H6z', isFilled: true},
        {d: 'M14 5h4v14h-4z', isFilled: true}
    ],

    // Auto-play is the clock running on its own
    autoplay: [
        {d: 'M12 3a9 9 0 1 1-0.01 0'},
        {d: 'M12 7v5l3.5 2'}
    ],

    // Step mode is a chevron leaving a dot behind - one move at a time
    step: [
        {d: 'M5 12h0.01'},
        {d: 'M10 7l5 5-5 5'}
    ],

    keyboard: [
        {d: 'M3 7h18a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z'},
        {d: 'M6 10h0.01'},
        {d: 'M10 10h0.01'},
        {d: 'M14 10h0.01'},
        {d: 'M18 10h0.01'},
        {d: 'M6 13.5h0.01'},
        {d: 'M18 13.5h0.01'},
        {d: 'M9 13.5h6'}
    ]
};

// /////////////////////////////////////////////////////////////////////////////

replay.newIcon = function(name, className) {
    var svgNamespace = 'http://www.w3.org/2000/svg';

    var icon = document.createElementNS(svgNamespace, 'svg');
    icon.setAttribute('viewBox', '0 0 24 24');
    icon.setAttribute('width', '13');
    icon.setAttribute('height', '13');
    icon.setAttribute('class', className);

    var parts = replay.icons[name];

    for (var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];

        var path = document.createElementNS(svgNamespace, 'path');
        path.setAttribute('d', part.d);

        if (part.isFilled) {
            path.setAttribute('fill', 'currentColor');
            path.setAttribute('stroke', 'none');
        }
        else {
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', 'currentColor');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
        }

        icon.appendChild(path);
    }

    return icon;
};

// /////////////////////////////////////////////////////////////////////////////

replay.updateBar = function() {
    var state = replay.state;
    var bar = replay.bar();

    var playhead = bar.querySelector('.message-flow-replay-playhead');
    playhead.style.left = (state.position / state.totalScaled * 100) + '%';

    // The one control that changes its face - the triangle while the clock
    // stands, the bars while it runs
    var playButton = bar.querySelector('.message-flow-replay-play');

    playButton.classList.toggle('message-flow-replay-playing', state.isPlaying);
    playButton.title = state.isPlaying ? replay.config.pauseLabel : replay.config.playLabel;

    // The clock face - the wall time the playhead stands at and how far past
    // the first event that is
    var realMs = replay.positionToRealMs(state.position);
    var wallMs = state.startMs + realMs;

    var wallText = kit.format_local_time_precise(new Date(wallMs).toISOString()).slice(11);

    bar.querySelector('.message-flow-replay-wall').textContent = wallText;
    bar.querySelector('.message-flow-replay-elapsed').textContent = '+' + kit.format_duration_ms(Math.round(realMs));
};

// /////////////////////////////////////////////////////////////////////////////

replay.setNote = function(text) {
    var note = replay.bar().querySelector('.message-flow-replay-note');

    note.textContent = text;
    note.classList.toggle('message-flow-replay-note-bad', text !== '');
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the keys' overlay is on screen
replay.isShortcutsOpen = function() {
    var overlay = replay.bar().querySelector('.message-flow-replay-shortcuts');
    return overlay.classList.contains('message-flow-replay-shortcuts-open');
};

// /////////////////////////////////////////////////////////////////////////////

replay.setShortcutsOpen = function(isOpen) {
    var overlay = replay.bar().querySelector('.message-flow-replay-shortcuts');
    overlay.classList.toggle('message-flow-replay-shortcuts-open', isOpen);
};

// /////////////////////////////////////////////////////////////////////////////

// The bar's own parts, built once - only the ticks are each journey's own
replay.buildBar = function() {
    var config = replay.config;
    var bar = replay.bar();

    var playButton = document.createElement('button');
    playButton.type = 'button';
    playButton.className = 'message-flow-replay-button message-flow-replay-play';
    playButton.title = config.playLabel;
    playButton.appendChild(replay.newIcon('play', 'message-flow-replay-icon-play'));
    playButton.appendChild(replay.newIcon('pause', 'message-flow-replay-icon-pause'));
    bar.appendChild(playButton);

    playButton.addEventListener('click', function(event) {
        replay.togglePlay();

        // The button lets the focus go, so the space bar stays the clock's
        event.currentTarget.blur();
    });

    // How fast the clock runs, worn the way a volume slider is
    var speed = document.createElement('input');
    speed.type = 'range';
    speed.className = 'message-flow-replay-speed';
    speed.min = String(config.speedLeast);
    speed.max = String(config.speedMost);
    speed.step = String(config.speedStep);
    speed.value = String(config.speedPlain);
    speed.title = config.speedLabel + ' ' + (config.speedPlain / 100) + config.speedUnit;
    bar.appendChild(speed);

    speed.addEventListener('input', function(event) {
        var hundredths = parseInt(event.currentTarget.value, 10);

        replay.state.speed = hundredths / 100;
        event.currentTarget.title = config.speedLabel + ' ' + (hundredths / 100) + config.speedUnit;
    });

    // The slider lets the focus go once set, so the keys stay the pass's own
    speed.addEventListener('change', function(event) {
        event.currentTarget.blur();
    });

    var modes = document.createElement('div');
    modes.className = 'message-flow-replay-modes';
    bar.appendChild(modes);

    for (var modeIndex = 0; modeIndex < config.modes.length; modeIndex++) {

        var wireModeButton = function(index) {
            var mode = config.modes[index];

            var modeButton = document.createElement('button');
            modeButton.type = 'button';
            modeButton.className = 'message-flow-replay-button message-flow-replay-mode';
            modeButton.title = mode.label;
            modeButton.appendChild(replay.newIcon(mode.icon, 'message-flow-replay-icon'));
            modes.appendChild(modeButton);

            modeButton.addEventListener('click', function(event) {
                replay.setMode(index);
                event.currentTarget.blur();
            });
        };

        wireModeButton(modeIndex);
    }

    var track = document.createElement('div');
    track.className = 'message-flow-replay-track';
    bar.appendChild(track);

    var ticks = document.createElement('div');
    ticks.className = 'message-flow-replay-ticks';
    track.appendChild(ticks);

    var playhead = document.createElement('div');
    playhead.className = 'message-flow-replay-playhead';
    track.appendChild(playhead);

    // The track is a debugger - a press puts the playhead there and a pull
    // walks it both ways, the drawing following live
    var isScrubbing = false;

    var seekToPointer = function(event) {
        var rect = track.getBoundingClientRect();
        var share = (event.clientX - rect.left) / rect.width;

        if (share < 0) {
            share = 0;
        }

        if (share > 1) {
            share = 1;
        }

        replay.seek(share * replay.state.totalScaled);
    };

    track.addEventListener('mousedown', function(event) {
        if (event.button !== 0) {
            return;
        }

        isScrubbing = true;
        seekToPointer(event);

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (isScrubbing) {
            seekToPointer(event);
        }
    });

    window.addEventListener('mouseup', function() {
        isScrubbing = false;
    });

    var clock = document.createElement('div');
    clock.className = 'message-flow-replay-clock';
    bar.appendChild(clock);

    var wall = document.createElement('span');
    wall.className = 'message-flow-replay-wall';
    clock.appendChild(wall);

    var elapsed = document.createElement('span');
    elapsed.className = 'message-flow-replay-elapsed';
    clock.appendChild(elapsed);

    var note = document.createElement('span');
    note.className = 'message-flow-replay-note';
    bar.appendChild(note);

    // The keyboard control and the overlay that reads its keys out
    var keyboardButton = document.createElement('button');
    keyboardButton.type = 'button';
    keyboardButton.className = 'message-flow-replay-button message-flow-replay-keyboard';
    keyboardButton.title = config.shortcutsLabel;
    keyboardButton.appendChild(replay.newIcon('keyboard', 'message-flow-replay-icon'));
    bar.appendChild(keyboardButton);

    var shortcuts = document.createElement('div');
    shortcuts.className = 'message-flow-replay-shortcuts';
    bar.appendChild(shortcuts);

    for (var shortcutIndex = 0; shortcutIndex < config.shortcuts.length; shortcutIndex++) {
        var shortcut = config.shortcuts[shortcutIndex];

        var shortcutRow = document.createElement('div');
        shortcutRow.className = 'message-flow-replay-shortcut';
        shortcuts.appendChild(shortcutRow);

        var shortcutKeys = document.createElement('span');
        shortcutKeys.className = 'message-flow-replay-shortcut-keys';
        shortcutKeys.textContent = shortcut.keys;
        shortcutRow.appendChild(shortcutKeys);

        var shortcutLabel = document.createElement('span');
        shortcutLabel.className = 'message-flow-replay-shortcut-label';
        shortcutLabel.textContent = shortcut.label;
        shortcutRow.appendChild(shortcutLabel);
    }

    keyboardButton.addEventListener('click', function(event) {
        replay.setShortcutsOpen(!replay.isShortcutsOpen());
        event.currentTarget.blur();
    });

    // A click anywhere off the overlay and its control folds the overlay away
    document.addEventListener('click', function(event) {
        if (!replay.isShortcutsOpen()) {
            return;
        }

        // The click a drag of the bar ends in reaches for nothing
        if (replay.floatState.isDragClick) {
            return;
        }

        if (event.target.closest('.message-flow-replay-shortcuts, .message-flow-replay-keyboard') !== null) {
            return;
        }

        replay.setShortcutsOpen(false);
    });
};

// /////////////////////////////////////////////////////////////////////////////

// One tick per event, standing where the event stands on the scaled axis,
// a failure's tick in the failure's own ink
replay.buildTicks = function() {
    var state = replay.state;
    var ticks = replay.bar().querySelector('.message-flow-replay-ticks');

    ticks.textContent = '';

    for (var eventIndex = 0; eventIndex < state.events.length; eventIndex++) {
        var event = state.events[eventIndex];

        var tick = document.createElement('span');
        tick.className = 'message-flow-replay-tick';

        if (replay.isBadOutcome(event.model)) {
            tick.className += ' message-flow-replay-tick-bad';
        }

        tick.style.left = (event.scaled / state.totalScaled * 100) + '%';
        ticks.appendChild(tick);
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The keyboard - the keys are live whenever a journey is on the bar, and the
// first of them starts the pass the way the buttons do
replay.onKeyDown = function(event) {
    if (replay.state.events.length === 0) {
        return;
    }

    // Whatever is being typed elsewhere is not for the clock - only the
    // bar's own slider is no such place, its keys stay the pass's own
    if (event.target.matches('input, textarea') && !event.target.matches('.message-flow-replay-speed')) {
        return;
    }

    if (event.key === ' ') {
        replay.togglePlay();
    }
    else if (event.key === 'ArrowRight') {
        replay.stepForward();
    }
    else if (event.key === 'ArrowLeft') {
        replay.stepBack();
    }
    else if (event.key === 'Home') {

        // Home is the first node standing lit with its exchange open, not
        // the dark room before it
        replay.seek(replay.state.events[0].scaled);
    }
    else if (event.key === 'End') {
        replay.seek(replay.state.totalScaled);
    }
    else if (event.key === 'ArrowDown') {
        replay.setMode((replay.state.modeIndex + 1) % replay.config.modes.length);
    }
    else if (event.key === 'ArrowUp') {
        var modeCount = replay.config.modes.length;
        replay.setMode((replay.state.modeIndex + modeCount - 1) % modeCount);
    }
    else if (event.key === 'Escape') {

        // The overlay folds away first, then the pass, and with neither on
        // Esc stays the page's own - it is what lets a held selection go
        if (replay.isShortcutsOpen()) {
            replay.setShortcutsOpen(false);
        }
        else if (replay.state.isActive) {
            replay.disarm();
        }
        else {
            return;
        }
    }
    else {
        return;
    }

    event.preventDefault();
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
