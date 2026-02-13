(function() {
    'use strict';

    var AIChatZoom = {

        handleWheel: function(widget, e, currentScale) {
            if (!e.ctrlKey) {
                return currentScale;
            }

            e.preventDefault();
            var delta = e.deltaY > 0 ? -0.1 : 0.1;
            var newScale = Math.max(0.5, Math.min(2.0, currentScale + delta));
            widget.style.transform = 'scale(' + newScale + ')';
            widget.style.transformOrigin = 'top left';
            console.debug('AIChatZoom.handleWheel: zoom scale:', newScale);
            return newScale;
        },

        applyZoom: function(widget, scale) {
            widget.style.transform = 'scale(' + scale + ')';
            widget.style.transformOrigin = 'top left';
        },

        resetZoom: function(widget) {
            widget.style.transform = '';
            return 1.0;
        }
    };

    window.AIChatZoom = AIChatZoom;

})();
