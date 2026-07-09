
// Mapper kit - the panel resizer.
// The panels resize by their facing borders: the right border of the
// left panel and the left border of the right panel both act as drag
// handles, built on the Pointer Events API so mouse and touch share
// one code path. The handles are keyboard-operable and the split is
// remembered in browser storage.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.resizer = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes one resizer.
    // resizerConfig:
    //   container:      the flex container holding both panels
    //   first:          the panel whose size carries the split - it receives the explicit size
    //   handles:        the edge handle elements, one per draggable border
    //   storageKey:     browser storage key the split percentage is kept under
    //   defaultPercent: the split used when browser storage has nothing saved
    //   axis:           'x' for a left/right split, 'y' for a top/bottom one
    zato.mapper.resizer.init = function(resizerConfig) {

        var container = resizerConfig.container;
        var first = resizerConfig.first;
        var storageKey = resizerConfig.storageKey;
        var defaultPercent = resizerConfig.defaultPercent;
        var isVertical = resizerConfig.axis === 'y';

        function clamp(percent) {
            if (percent < config.splitMinPercent) {
                return config.splitMinPercent;
            }
            if (percent > config.splitMaxPercent) {
                return config.splitMaxPercent;
            }

            return percent;
        }

        function currentPercent() {

            // Browser storage is an external boundary, so absence is explicit.
            var saved = window.store.get(storageKey);
            if (saved === null) {
                return defaultPercent;
            }

            var out = clamp(parseFloat(saved));
            return out;
        }

        function apply(percent) {
            first.style.flex = '0 0 ' + percent + '%';
        }

        function save(percent) {
            window.store.set(storageKey, String(percent));
        }

// ////////////////////////////////////////////////////////////////////////

        // The pointer coordinate along the split axis.
        function pointerPosition(event) {
            if (isVertical) {
                return event.clientY;
            }

            return event.clientX;
        }

        // The first panel's trailing edge along the split axis.
        function firstEdge() {

            var bounds = first.getBoundingClientRect();
            if (isVertical) {
                return bounds.bottom;
            }

            return bounds.right;
        }

        // The first panel's share of the container along the split axis.
        function firstPercent() {

            var bounds = first.getBoundingClientRect();
            var containerBounds = container.getBoundingClientRect();

            if (isVertical) {
                return bounds.height / containerBounds.height * 100;
            }

            return bounds.width / containerBounds.width * 100;
        }

// ////////////////////////////////////////////////////////////////////////

        function bindHandle(handle) {

            // The pointer's distance to the first panel's trailing edge at
            // the moment of the grab - keeping it constant during the drag
            // means either border drags without a jump.
            var grabOffset = 0;

            // The keys that move the split one step back or forward.
            var backwardKey = isVertical ? 'ArrowUp' : 'ArrowLeft';
            var forwardKey = isVertical ? 'ArrowDown' : 'ArrowRight';

            // Dragging - the handle captures the pointer, so the drag keeps
            // working even when the pointer leaves the handle itself.
            $(handle).on('pointerdown', function(event) {
                event.preventDefault();
                handle.setPointerCapture(event.originalEvent.pointerId);
                handle.classList.add('mapper-resizer-active');

                grabOffset = pointerPosition(event) - firstEdge();
            });

            $(handle).on('pointermove', function(event) {
                if (!handle.hasPointerCapture(event.originalEvent.pointerId)) {
                    return;
                }

                var bounds = container.getBoundingClientRect();
                var start = isVertical ? bounds.top : bounds.left;
                var size = isVertical ? bounds.height : bounds.width;

                var percent = clamp((pointerPosition(event) - grabOffset - start) / size * 100);
                apply(percent);
            });

            $(handle).on('pointerup pointercancel', function(event) {
                if (!handle.hasPointerCapture(event.originalEvent.pointerId)) {
                    return;
                }

                handle.releasePointerCapture(event.originalEvent.pointerId);
                handle.classList.remove('mapper-resizer-active');

                // The split as dragged is what gets remembered.
                save(clamp(firstPercent()));
            });

            // Arrow keys move the split by one step in either direction.
            $(handle).on('keydown', function(event) {

                var step = 0;
                if (event.key === backwardKey) {
                    step = -config.splitKeyboardStepPercent;
                }
                else if (event.key === forwardKey) {
                    step = config.splitKeyboardStepPercent;
                }
                else {
                    return;
                }

                event.preventDefault();

                var percent = clamp(currentPercent() + step);
                apply(percent);
                save(percent);
            });
        }

// ////////////////////////////////////////////////////////////////////////

        for (var handleIdx = 0; handleIdx < resizerConfig.handles.length; handleIdx++) {
            bindHandle(resizerConfig.handles[handleIdx]);
        }

        apply(currentPercent());
    };

})(jQuery);
