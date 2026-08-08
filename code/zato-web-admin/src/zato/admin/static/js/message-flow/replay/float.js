
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the bar as a movable instrument. A grip on its left
// end lets it be picked up and put down anywhere over the canvas, a control on
// its right end folds it away into a small tab docked to the canvas edge, and
// the tab brings it back. Where the bar stands and whether it is folded away
// is kept by the browser, so it comes up the way it was left.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

replay.floatConfig = {

    // Where the browser keeps how the bar was left
    storageKey: 'zato.message-flow.replay-bar',

    // The least room the bar keeps to the frame's edges, both when dragged
    // and when a remembered position no longer fits the frame
    margin: 12,

    // What the docked tab says
    dockLabel: 'Replay'
};

// /////////////////////////////////////////////////////////////////////////////

replay.floatState = {

    // Where the bar was put down, in the frame's own coordinates - null while
    // it has never been dragged and still rides the frame's foot
    x: null,
    y: null,

    isMinimized: false,

    dock: null
};

// /////////////////////////////////////////////////////////////////////////////

replay.floatFrame = function() {
    return replay.bar().parentElement;
};

// /////////////////////////////////////////////////////////////////////////////

replay.loadFloatState = function() {
    var state = replay.floatState;
    var kept = window.localStorage.getItem(replay.floatConfig.storageKey);

    // Nothing kept yet - the bar rides the frame's foot, unfolded
    if (kept === null) {
        return;
    }

    var parsed = JSON.parse(kept);

    state.x = parsed.x;
    state.y = parsed.y;
    state.isMinimized = parsed.isMinimized;
};

// /////////////////////////////////////////////////////////////////////////////

replay.saveFloatState = function() {
    var state = replay.floatState;

    var kept = {
        x: state.x,
        y: state.y,
        isMinimized: state.isMinimized
    };

    window.localStorage.setItem(replay.floatConfig.storageKey, JSON.stringify(kept));
};

// /////////////////////////////////////////////////////////////////////////////

// A remembered position is only as good as the room it was remembered in -
// whatever no longer fits is pulled back inside the frame
replay.clampFloat = function(x, y) {
    var margin = replay.floatConfig.margin;
    var frame = replay.floatFrame();
    var bar = replay.bar();

    var maxX = frame.clientWidth - bar.offsetWidth - margin;
    var maxY = frame.clientHeight - bar.offsetHeight - margin;

    if (x > maxX) {
        x = maxX;
    }

    if (y > maxY) {
        y = maxY;
    }

    if (x < margin) {
        x = margin;
    }

    if (y < margin) {
        y = margin;
    }

    return {x: x, y: y};
};

// /////////////////////////////////////////////////////////////////////////////

// The bar standing where it was left - at its remembered spot once it has one,
// riding the frame's foot until then - and folded away if that is how it was left
replay.applyFloat = function() {
    var state = replay.floatState;
    var bar = replay.bar();

    if (state.x !== null) {

        // The bar keeps the width it has at the frame's foot even once it
        // floats free, so the track never collapses under it
        bar.classList.add('message-flow-replay-bar-floating');

        var clamped = replay.clampFloat(state.x, state.y);

        state.x = clamped.x;
        state.y = clamped.y;

        bar.style.left = clamped.x + 'px';
        bar.style.top = clamped.y + 'px';
    }
    else {
        bar.classList.remove('message-flow-replay-bar-floating');
        bar.style.left = '';
        bar.style.top = '';
        bar.style.width = '';
    }

    if (state.isMinimized) {
        replay.minimizeBar();
    }
    else {
        replay.restoreBar();
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The bar folded away - only the docked tab stays, at the height the bar
// stood at, and the pass keeps running behind it
replay.minimizeBar = function() {
    var state = replay.floatState;
    var bar = replay.bar();
    var frame = replay.floatFrame();
    var margin = replay.floatConfig.margin;

    var dockTop = bar.offsetTop;

    bar.classList.add('message-flow-replay-bar-minimized');

    // The tab is stood up before it is measured - hidden it has no height
    state.dock.classList.add('message-flow-replay-dock-active');

    var maxTop = frame.clientHeight - state.dock.offsetHeight - margin;

    if (dockTop > maxTop) {
        dockTop = maxTop;
    }

    if (dockTop < margin) {
        dockTop = margin;
    }

    state.dock.style.top = dockTop + 'px';

    state.isMinimized = true;
    replay.saveFloatState();
};

// /////////////////////////////////////////////////////////////////////////////

replay.restoreBar = function() {
    var state = replay.floatState;

    replay.bar().classList.remove('message-flow-replay-bar-minimized');
    state.dock.classList.remove('message-flow-replay-dock-active');

    state.isMinimized = false;
    replay.saveFloatState();
};

// /////////////////////////////////////////////////////////////////////////////

// The tab standing off the canvas edge while the bar is folded away
replay.hideDock = function() {
    replay.floatState.dock.classList.remove('message-flow-replay-dock-active');
};

// /////////////////////////////////////////////////////////////////////////////

// A small chevron pointing the way the bar folds, built as an SVG of its own
replay.newChevron = function() {
    var svgNamespace = 'http://www.w3.org/2000/svg';

    var icon = document.createElementNS(svgNamespace, 'svg');
    icon.setAttribute('viewBox', '0 0 24 24');
    icon.setAttribute('width', '12');
    icon.setAttribute('height', '12');

    var line = document.createElementNS(svgNamespace, 'path');
    line.setAttribute('d', 'M9 18l6-6-6-6');
    line.setAttribute('fill', 'none');
    line.setAttribute('stroke', 'currentColor');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-linecap', 'round');
    line.setAttribute('stroke-linejoin', 'round');

    icon.appendChild(line);

    return icon;
};

// /////////////////////////////////////////////////////////////////////////////

// The grip, the fold-away control and the docked tab, and the drag that
// carries the bar around the frame
replay.buildFloat = function() {
    var state = replay.floatState;
    var bar = replay.bar();
    var frame = replay.floatFrame();

    // The grip stands first on the bar - the one place a drag starts from,
    // so the track and the buttons keep answering to their own presses
    var grip = document.createElement('span');
    grip.className = 'message-flow-replay-grip';
    grip.title = replay.config.moveLabel;
    bar.insertBefore(grip, bar.firstChild);

    // The fold-away control stands last
    var minimizeButton = document.createElement('button');
    minimizeButton.type = 'button';
    minimizeButton.className = 'message-flow-replay-minimize';
    minimizeButton.title = replay.config.minimizeLabel;
    minimizeButton.appendChild(replay.newChevron());
    bar.appendChild(minimizeButton);

    minimizeButton.addEventListener('click', function(event) {
        replay.minimizeBar();
        event.currentTarget.blur();
    });

    // The docked tab, waiting off the edge for the bar to fold away
    var dock = document.createElement('div');
    dock.className = 'message-flow-replay-dock';
    dock.textContent = replay.floatConfig.dockLabel;
    frame.appendChild(dock);

    state.dock = dock;

    dock.addEventListener('click', function() {
        replay.restoreBar();
    });

    // The drag - the pointer picks the bar up by the grip, carries it in the
    // frame's own coordinates and puts it down where it lets go
    var isDragging = false;
    var pointerOffsetX = 0;
    var pointerOffsetY = 0;

    grip.addEventListener('mousedown', function(event) {

        // Only the main button picks the bar up
        if (event.button !== 0) {
            return;
        }

        var barRect = bar.getBoundingClientRect();
        var frameRect = frame.getBoundingClientRect();

        // The bar is pinned exactly where it stands before it floats free,
        // and it keeps the width it had, so letting go of its stretched
        // anchors moves nothing and folds nothing under it
        state.x = barRect.left - frameRect.left;
        state.y = barRect.top - frameRect.top;

        bar.style.width = barRect.width + 'px';
        bar.style.left = state.x + 'px';
        bar.style.top = state.y + 'px';
        bar.classList.add('message-flow-replay-bar-floating');

        pointerOffsetX = event.clientX - barRect.left;
        pointerOffsetY = event.clientY - barRect.top;

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
            event.clientX - frameRect.left - pointerOffsetX,
            event.clientY - frameRect.top - pointerOffsetY);

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
