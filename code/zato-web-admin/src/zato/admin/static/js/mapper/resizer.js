
// Mapper kit - the panel resizer.
// The panels resize by their facing borders: the right border of the
// left panel and the left border of the right panel both act as drag
// handles. The dragging itself is the shared resizer from
// js/shared/resizer.js, this is where the mapper's own limits, its
// handle class and its browser storage meet it.

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

        $.fn.zato.resizer.init({

            container: resizerConfig.container,
            first: resizerConfig.first,
            handles: resizerConfig.handles,
            axis: resizerConfig.axis,

            // The mapper always sizes the panel nearer the container's start
            edge: 'end',

            minPercent: config.splitMinPercent,
            maxPercent: config.splitMaxPercent,
            keyboardStepPercent: config.splitKeyboardStepPercent,
            activeClass: 'mapper-resizer-active',

            read: function() {

                // Browser storage is an external boundary, so absence is explicit.
                var saved = window.store.get(resizerConfig.storageKey);

                if (saved === null) {
                    return resizerConfig.defaultPercent;
                }

                return parseFloat(saved);
            },

            write: function(percent) {
                window.store.set(resizerConfig.storageKey, String(percent));
            },

            // The mapper's panels go exactly where they are dragged, and neither
            // of them is ever dragged shut
            snap: function(percent) {
                return percent;
            },

            applied: function() {
            }
        });
    };

})(jQuery);
