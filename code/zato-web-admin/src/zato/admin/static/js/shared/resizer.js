// The shared panel resizer - two panels side by side, or one above the other,
// with a handle on the border between them. The handle is built on the Pointer
// Events API so mouse and touch share one code path, it is keyboard-operable, and
// where the split ends up is read and written by the caller, which is what lets
// each page remember it in whatever way it already does.
//
// options:
//   container            - the flex container holding both panels
//   first                - the panel whose size carries the split, it is the one
//                          that receives the explicit size
//   handles              - the handle elements, one per draggable border
//   axis                 - 'x' for a left/right split, 'y' for a top/bottom one
//   minPercent           - how small the first panel may be dragged
//   maxPercent           - how large the first panel may be dragged
//   keyboardStepPercent  - how far one arrow key press moves the split
//   activeClass          - the class a handle wears mid-drag
//   read()               - the split to open with, null when there is none
//   write(percent)       - called with the split once a drag or a key press ends
//   snap(percent, isDragging)
//                        - the split to use in place of the one arrived at, which
//                          is how a magnet near an edge is had - it is told whether
//                          the split is being dragged or stepped to by key
//   applied(percent)     - called with every split as it lands, which is where a
//                          panel dragged shut is told that it is shut

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.resizer = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.resizer.init = function(options) {

    var container = options.container;
    var first = options.first;
    var isVertical = options.axis === 'y';

    var clamp = function(percent) {

        if(percent < options.minPercent) {
            return options.minPercent;
        }

        if(percent > options.maxPercent) {
            return options.maxPercent;
        }

        return percent;
    };

    // The split the panels open at - what the caller has kept, or nothing,
    // in which case the first panel keeps the size its own styles give it
    var currentPercent = function() {

        var saved = options.read();

        if(saved === null) {
            return null;
        }

        var out = clamp(saved);
        return out;
    };

    var apply = function(percent, isDragging) {

        percent = options.snap(percent, isDragging);

        first.style.flex = '0 0 ' + percent + '%';
        options.applied(percent);
    };

    // ////////////////////////////////////////////////////////////////////////

    // The pointer coordinate along the split axis
    var pointerPosition = function(event) {

        if(isVertical) {
            return event.clientY;
        }

        return event.clientX;
    };

    // The first panel's trailing edge along the split axis
    var firstEdge = function() {

        var bounds = first.getBoundingClientRect();

        if(isVertical) {
            return bounds.bottom;
        }

        return bounds.right;
    };

    // The first panel's share of the container along the split axis
    var firstPercent = function() {

        var bounds = first.getBoundingClientRect();
        var containerBounds = container.getBoundingClientRect();

        if(isVertical) {
            return bounds.height / containerBounds.height * 100;
        }

        return bounds.width / containerBounds.width * 100;
    };

    // ////////////////////////////////////////////////////////////////////////

    var bindHandle = function(handle) {

        // The pointer's distance to the first panel's trailing edge at the moment
        // of the grab - keeping it constant during the drag means either border
        // drags without a jump
        var grabOffset = 0;

        var backwardKey = isVertical ? 'ArrowUp' : 'ArrowLeft';
        var forwardKey = isVertical ? 'ArrowDown' : 'ArrowRight';

        // The handle captures the pointer, so the drag keeps working even when
        // the pointer leaves the handle itself
        $(handle).on('pointerdown', function(event) {

            event.preventDefault();
            handle.setPointerCapture(event.originalEvent.pointerId);
            handle.classList.add(options.activeClass);

            grabOffset = pointerPosition(event) - firstEdge();
        });

        $(handle).on('pointermove', function(event) {

            if(!handle.hasPointerCapture(event.originalEvent.pointerId)) {
                return;
            }

            var bounds = container.getBoundingClientRect();
            var start = isVertical ? bounds.top : bounds.left;
            var size = isVertical ? bounds.height : bounds.width;

            var percent = clamp((pointerPosition(event) - grabOffset - start) / size * 100);
            apply(percent, true);
        });

        $(handle).on('pointerup pointercancel', function(event) {

            if(!handle.hasPointerCapture(event.originalEvent.pointerId)) {
                return;
            }

            handle.releasePointerCapture(event.originalEvent.pointerId);
            handle.classList.remove(options.activeClass);

            // The split as dragged is what gets kept
            options.write(clamp(firstPercent()));
        });

        // Arrow keys move the split by one step in either direction
        $(handle).on('keydown', function(event) {

            var step = 0;

            if(event.key === backwardKey) {
                step = -options.keyboardStepPercent;
            }
            else if(event.key === forwardKey) {
                step = options.keyboardStepPercent;
            }
            else {
                return;
            }

            event.preventDefault();

            // Where the split is now, since a drag may have moved it since
            // the last key press
            var percent = clamp(firstPercent() + step);

            apply(percent, false);
            options.write(percent);
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    for(var handleIdx = 0; handleIdx < options.handles.length; handleIdx++) {
        bindHandle(options.handles[handleIdx]);
    }

    var opening = currentPercent();

    if(opening !== null) {
        apply(opening, false);
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
