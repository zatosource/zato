
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the bar off its moorings. A grip at its left end lets
// it be pulled anywhere over the canvas, a control at its right end folds it
// away into a small tab at the canvas foot, and wherever it is left is where
// the next journey finds it.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

replay.floatConfig = {

    // Where the bar's whereabouts survive a reload
    storageKey: 'zato.message-flow.replay-bar',

    // A bar off its moorings gives up the full width for this one
    floatWidth: 640,

    // What the folded-away tab says
    dockLabel: 'Replay'
};

// /////////////////////////////////////////////////////////////////////////////

// Where the bar stands - on its moorings across the canvas foot, pulled loose
// to a place of its own, or folded away into the tab
replay.floatState = {
    isFloating: false,
    isMinimized: false,
    x: 0,
    y: 0
};

// /////////////////////////////////////////////////////////////////////////////

replay.dock = function() {
    return replay.bar().parentElement.querySelector('.message-flow-replay-dock');
};

// /////////////////////////////////////////////////////////////////////////////

replay.loadFloatState = function() {
    var stored = window.localStorage.getItem(replay.floatConfig.storageKey);

    if (stored !== null) {
        replay.floatState = JSON.parse(stored);
    }
};

// /////////////////////////////////////////////////////////////////////////////

replay.saveFloatState = function() {
    window.localStorage.setItem(replay.floatConfig.storageKey, JSON.stringify(replay.floatState));
};

// /////////////////////////////////////////////////////////////////////////////

// The bar and the tab wear whatever the state says - full width on the
// moorings, pinned at its own place when floating, folded away when minimized
replay.applyFloat = function() {
    var state = replay.floatState;
    var bar = replay.bar();

    bar.classList.toggle('message-flow-replay-bar-floating', state.isFloating);
    bar.classList.toggle('message-flow-replay-bar-minimized', state.isMinimized);

    if (state.isFloating) {
        var clamped = replay.clampFloat(state.x, state.y);

        bar.style.width = replay.floatConfig.floatWidth + 'px';
        bar.style.left = clamped.x + 'px';
        bar.style.top = clamped.y + 'px';
    }
    else {
        bar.style.width = '';
        bar.style.left = '';
        bar.style.top = '';
    }

    // The tab stands in for the bar only while a journey is on the canvas
    var isBarWanted = bar.classList.contains('message-flow-replay-bar-active');
    var dock = replay.dock();

    dock.classList.toggle('message-flow-replay-dock-active', isBarWanted && state.isMinimized);
};

// /////////////////////////////////////////////////////////////////////////////

// The bar stays on the canvas whole - however far it is pulled
replay.clampFloat = function(x, y) {
    var bar = replay.bar();
    var frame = bar.parentElement;

    var mostX = frame.clientWidth - replay.floatConfig.floatWidth;
    var mostY = frame.clientHeight - bar.offsetHeight;

    if (x > mostX) {
        x = mostX;
    }

    if (y > mostY) {
        y = mostY;
    }

    if (x < 0) {
        x = 0;
    }

    if (y < 0) {
        y = 0;
    }

    return {x: x, y: y};
};

// /////////////////////////////////////////////////////////////////////////////

replay.hideDock = function() {
    replay.dock().classList.remove('message-flow-replay-dock-active');
};

// /////////////////////////////////////////////////////////////////////////////

// The grip, the fold-away control and the tab - built once with the bar
replay.buildFloat = function() {
    var bar = replay.bar();
    var frame = bar.parentElement;
    var state = replay.floatState;

    var grip = document.createElement('span');
    grip.className = 'message-flow-replay-grip';
    grip.title = replay.config.moveLabel;
    grip.textContent = '\u2059\u2059';
    bar.insertBefore(grip, bar.firstChild);

    var minimize = document.createElement('button');
    minimize.type = 'button';
    minimize.className = 'message-flow-replay-button message-flow-replay-minimize';
    minimize.title = replay.config.minimizeLabel;
    minimize.appendChild(replay.newIcon('fold', 'message-flow-replay-icon'));
    bar.appendChild(minimize);

    var dock = document.createElement('button');
    dock.type = 'button';
    dock.className = 'message-flow-replay-dock';
    dock.textContent = replay.floatConfig.dockLabel;
    frame.appendChild(dock);

    minimize.addEventListener('click', function(event) {
        state.isMinimized = true;

        replay.saveFloatState();
        replay.applyFloat();

        event.currentTarget.blur();
    });

    dock.addEventListener('click', function() {
        state.isMinimized = false;

        replay.saveFloatState();
        replay.applyFloat();
    });

    // The pull itself - the first press pins the bar where it stands, so a
    // click with no movement still leaves it exactly in place
    var dragOffsetX = 0;
    var dragOffsetY = 0;
    var isDragging = false;

    grip.addEventListener('mousedown', function(event) {
        if (event.button !== 0) {
            return;
        }

        var barRect = bar.getBoundingClientRect();
        var frameRect = frame.getBoundingClientRect();

        // Off the moorings and pinned at its own coordinates before any move
        state.isFloating = true;
        state.x = barRect.left - frameRect.left;
        state.y = barRect.top - frameRect.top;

        replay.applyFloat();

        dragOffsetX = event.clientX - barRect.left;
        dragOffsetY = event.clientY - barRect.top;
        isDragging = true;

        bar.classList.add('message-flow-replay-bar-dragging');

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isDragging) {
            return;
        }

        var frameRect = frame.getBoundingClientRect();

        var clamped = replay.clampFloat(
            event.clientX - frameRect.left - dragOffsetX,
            event.clientY - frameRect.top - dragOffsetY);

        state.x = clamped.x;
        state.y = clamped.y;

        bar.style.left = clamped.x + 'px';
        bar.style.top = clamped.y + 'px';
    });

    window.addEventListener('mouseup', function() {
        if (!isDragging) {
            return;
        }

        isDragging = false;
        bar.classList.remove('message-flow-replay-bar-dragging');

        replay.saveFloatState();
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
