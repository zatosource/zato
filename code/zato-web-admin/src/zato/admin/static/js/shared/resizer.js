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
//   edge                 - which edge of that panel the handle sits on, 'end' for a
//                          panel that grows as the handle is dragged away from the
//                          container's start, 'start' for one at the far side that
//                          grows as the handle is dragged towards it
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
    var isHandleAtStart = options.edge === 'start';

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

    // The panel edge the handle sits on, along the split axis
    var handleEdge = function() {

        var bounds = first.getBoundingClientRect();

        if(isVertical) {
            return isHandleAtStart ? bounds.top : bounds.bottom;
        }

        return isHandleAtStart ? bounds.left : bounds.right;
    };

    // The panel edge that stands still while the handle travels, which is the one
    // the panel's size is measured back from
    var anchorEdge = function() {

        var bounds = first.getBoundingClientRect();

        if(isVertical) {
            return isHandleAtStart ? bounds.bottom : bounds.top;
        }

        return isHandleAtStart ? bounds.right : bounds.left;
    };

    // What the panel's share of the container is with its handle edge at the given
    // position - the distance between that position and the edge standing still
    var percentAt = function(position) {

        var containerBounds = container.getBoundingClientRect();
        var size = isVertical ? containerBounds.height : containerBounds.width;
        var span = isHandleAtStart ? anchorEdge() - position : position - anchorEdge();

        return span / size * 100;
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

        // A panel at the far side grows as its handle goes the other way, so the
        // two keys mean to it the opposite of what they mean to the near one
        var growSign = isHandleAtStart ? -1 : 1;

        // The handle captures the pointer, so the drag keeps working even when
        // the pointer leaves the handle itself
        $(handle).on('pointerdown', function(event) {

            event.preventDefault();
            handle.setPointerCapture(event.originalEvent.pointerId);
            handle.classList.add(options.activeClass);

            grabOffset = pointerPosition(event) - handleEdge();
        });

        $(handle).on('pointermove', function(event) {

            if(!handle.hasPointerCapture(event.originalEvent.pointerId)) {
                return;
            }

            var percent = clamp(percentAt(pointerPosition(event) - grabOffset));
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
                step = -options.keyboardStepPercent * growSign;
            }
            else if(event.key === forwardKey) {
                step = options.keyboardStepPercent * growSign;
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
