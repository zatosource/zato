// The shared drag to scroll - a box that is scrolled by taking hold of it and moving,
// the way a sheet of paper on a desk is moved, rather than only by its scrollbar.
//
// The content goes with the pointer, and the quicker the pointer travels the further it
// carries - a slow drag places the content exactly, a quick one covers a long file in one
// go. Letting go throws what is left of that speed, which then dies away under friction,
// so the box comes to rest instead of stopping dead. A pointer brought to rest before it
// is let go throws nothing, since the speed is read over the moment just gone rather than
// off the last two positions.
//
// It is built on the Pointer Events API, so a mouse and a finger share the one code path,
// and the box is captured for the length of the drag, so leaving the box mid-drag carries
// on rather than stopping.
//
// options:
//   element  - the box that scrolls
//   skip(event)
//            - whether a press is not to be taken as a grab, which is how the things
//              inside a box stay pressable

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.drag_scroll = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.drag_scroll.config = {

    // How far the content goes per pixel the pointer travels - what a slow drag gets, and
    // what is added to it as the pointer reaches the speed below. A slow drag goes a little
    // further than the pointer does, so a long file is covered without the arm work, while
    // still staying near enough to the pointer to place a line by hand.
    gain: 1.2,
    gainExtra: 1.1,
    speedFull: 1.6,

    // How long a stretch of the drag the speed is read over, so what is thrown is what the
    // pointer was doing as it was let go rather than what one event of it said
    sampleMs: 70,

    // The throw - how much of the speed it starts with, how much of it survives each frame
    // and the speed it is called finished at
    flingGain: 1.15,
    friction: 0.94,
    frameMs: 16,
    stopSpeed: 0.02,

    // The class the box wears while it is being dragged
    activeClass: 'zato-drag-scrolling'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.drag_scroll.attach = function(options) {

    var config = $.fn.zato.drag_scroll.config;
    var element = options.element;

    var state = {

        // Where the pointer was last seen and when, which is what one move is measured from
        lastY: 0,
        lastMs: 0,

        // How fast it is going, in pixels per millisecond, downwards being the positive way
        speed: 0,

        // The throw in progress, 0 while the box is at rest or being dragged
        frame: 0
    };

    // ////////////////////////////////////////////////////////////////////////

    var stopFling = function() {

        if(state.frame) {
            window.cancelAnimationFrame(state.frame);
            state.frame = 0;
        }
    };

    // What is left of the speed, spent frame by frame - the content keeps going the way the
    // pointer was going, less what friction takes off it each time
    var fling = function(nowMs) {

        var elapsedMs = nowMs - state.lastMs;

        state.lastMs = nowMs;
        element.scrollTop = element.scrollTop - state.speed * elapsedMs * config.flingGain;
        state.speed = state.speed * Math.pow(config.friction, elapsedMs / config.frameMs);

        // Slow enough to be standing still, so it is left standing still
        if(Math.abs(state.speed) < config.stopSpeed) {
            state.frame = 0;
            return;
        }

        state.frame = window.requestAnimationFrame(fling);
    };

    // ////////////////////////////////////////////////////////////////////////

    // One movement of the pointer - the content follows it, by more than it moved when it
    // is moving quickly, and the speed it is going at is kept up to date
    var follow = function(y, nowMs) {

        var travel = y - state.lastY;
        var elapsedMs = Math.max(1, nowMs - state.lastMs);
        var speed = travel / elapsedMs;

        var reach = Math.min(1, Math.abs(speed) / config.speedFull);
        var gain = config.gain + config.gainExtra * reach;

        element.scrollTop = element.scrollTop - travel * gain;

        // The speed is what it has been over the last stretch rather than what this one
        // movement says, which is what makes a pointer held still before the release throw
        // nothing at all
        var weight = Math.min(1, elapsedMs / config.sampleMs);

        state.speed = state.speed * (1 - weight) + speed * weight;
        state.lastY = y;
        state.lastMs = nowMs;
    };

    // ////////////////////////////////////////////////////////////////////////

    $(element).on('pointerdown', function(event) {

        if(options.skip(event)) {
            return;
        }

        // A press on a box already on its way stops it there, which is how a throw that
        // went too far is caught
        stopFling();

        // Otherwise the box itself is dragged about as an image
        event.preventDefault();

        element.setPointerCapture(event.originalEvent.pointerId);
        element.classList.add(config.activeClass);

        state.lastY = event.clientY;
        state.lastMs = window.performance.now();
        state.speed = 0;
    });

    $(element).on('pointermove', function(event) {

        if(!element.hasPointerCapture(event.originalEvent.pointerId)) {
            return;
        }

        follow(event.clientY, window.performance.now());
    });

    $(element).on('pointerup pointercancel', function(event) {

        if(!element.hasPointerCapture(event.originalEvent.pointerId)) {
            return;
        }

        element.releasePointerCapture(event.originalEvent.pointerId);
        element.classList.remove(config.activeClass);

        // Let go while still moving, so what is left of that movement carries on
        if(Math.abs(state.speed) > config.stopSpeed) {
            state.lastMs = window.performance.now();
            state.frame = window.requestAnimationFrame(fling);
        }
    });

    // The wheel is the reader saying where to be, which is the last word on it
    $(element).on('wheel', stopFling);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
