(function() {
    'use strict';

    var AIChatResize = {

        startDrag: function(widget, e) {
            var rect = widget.getBoundingClientRect();
            return {
                isDragging: true,
                dragOffsetX: e.clientX - rect.left,
                dragOffsetY: e.clientY - rect.top
            };
        },

        handleDrag: function(widget, e, dragOffsetX, dragOffsetY, zoomScale) {
            var newLeft = e.clientX - dragOffsetX;
            var newTop = e.clientY - dragOffsetY;

            newLeft = Math.max(0, newLeft);
            newTop = Math.max(0, newTop);

            widget.style.left = newLeft + 'px';
            widget.style.top = newTop + 'px';
        },

        startResize: function(widget, e, direction) {
            var rect = widget.getBoundingClientRect();
            return {
                isResizing: true,
                resizeDirection: direction,
                resizeStartX: e.clientX,
                resizeStartY: e.clientY,
                resizeStartWidth: widget.offsetWidth,
                resizeStartHeight: widget.offsetHeight,
                resizeStartLeft: rect.left,
                resizeStartTop: rect.top
            };
        },

        handleResize: function(widget, e, state) {
            var deltaX = e.clientX - state.resizeStartX;
            var deltaY = e.clientY - state.resizeStartY;
            var dir = state.resizeDirection;

            var newWidth = state.resizeStartWidth;
            var newHeight = state.resizeStartHeight;
            var newLeft = state.resizeStartLeft;
            var newTop = state.resizeStartTop;

            if (dir === 'se') {
                newWidth = Math.max(300, state.resizeStartWidth + deltaX);
                newHeight = Math.max(200, state.resizeStartHeight + deltaY);
            } else if (dir === 'sw') {
                newWidth = Math.max(300, state.resizeStartWidth - deltaX);
                newHeight = Math.max(200, state.resizeStartHeight + deltaY);
                newLeft = state.resizeStartLeft + (state.resizeStartWidth - newWidth);
            } else if (dir === 'ne') {
                newWidth = Math.max(300, state.resizeStartWidth + deltaX);
                newHeight = Math.max(200, state.resizeStartHeight - deltaY);
                newTop = state.resizeStartTop + (state.resizeStartHeight - newHeight);
            } else if (dir === 'nw') {
                newWidth = Math.max(300, state.resizeStartWidth - deltaX);
                newHeight = Math.max(200, state.resizeStartHeight - deltaY);
                newLeft = state.resizeStartLeft + (state.resizeStartWidth - newWidth);
                newTop = state.resizeStartTop + (state.resizeStartHeight - newHeight);
            }

            widget.style.width = newWidth + 'px';
            widget.style.height = newHeight + 'px';
            widget.style.left = newLeft + 'px';
            widget.style.top = newTop + 'px';
        },

        convertToLeftTop: function(widget) {
            var rect = widget.getBoundingClientRect();
            widget.style.right = 'auto';
            widget.style.bottom = 'auto';
            widget.style.left = rect.left + 'px';
            widget.style.top = rect.top + 'px';
        }
    };

    window.AIChatResize = AIChatResize;

})();
