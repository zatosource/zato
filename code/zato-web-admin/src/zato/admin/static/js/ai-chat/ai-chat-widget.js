(function() {
    'use strict';

    var AIChatWidget = {

        create: function(isMinimized, zoomScale) {
            var widget = document.createElement('div');
            widget.className = 'ai-chat-widget';
            widget.id = 'ai-chat-widget';

            if (isMinimized) {
                widget.classList.add('minimized');
                widget.style.right = '20px';
                widget.style.bottom = '20px';
                widget.style.left = 'auto';
                widget.style.top = 'auto';
                widget.style.width = '200px';
                widget.style.height = 'auto';
            } else {
                var position = AIChatState.loadPosition();
                var dimensions = AIChatState.loadDimensions();

                if (position) {
                    var clampedLeft = Math.max(0, position.left);
                    var clampedTop = Math.max(0, position.top);
                    widget.style.left = clampedLeft + 'px';
                    widget.style.top = clampedTop + 'px';
                    widget.style.right = 'auto';
                    widget.style.bottom = 'auto';
                }

                if (dimensions) {
                    widget.style.width = dimensions.width + 'px';
                    widget.style.height = dimensions.height + 'px';
                }

                if (zoomScale !== 1.0) {
                    AIChatZoom.applyZoom(widget, zoomScale);
                }
            }

            document.body.appendChild(widget);
            return widget;
        },

        savePosition: function(widget) {
            if (!widget) return;
            var rect = widget.getBoundingClientRect();
            AIChatState.savePosition({ left: rect.left, top: rect.top });
        },

        saveDimensions: function(widget) {
            if (!widget) return;
            AIChatState.saveDimensions({
                width: widget.offsetWidth,
                height: widget.offsetHeight
            });
        },

        toggleMinimize: function(widget, isMinimized, preMinimizePosition, zoomScale, saveCallback) {
            var newIsMinimized = !isMinimized;
            var newPreMinimizePosition = preMinimizePosition;
            var newZoomScale = zoomScale;
            var preMinimizeZoom = zoomScale;

            if (newIsMinimized) {
                widget.style.transform = '';
                preMinimizeZoom = zoomScale;

                var rect = widget.getBoundingClientRect();
                newPreMinimizePosition = {
                    left: rect.left,
                    top: rect.top,
                    width: widget.offsetWidth,
                    height: widget.offsetHeight
                };
                AIChatState.savePreMinimizePosition(newPreMinimizePosition);

                widget.classList.add('minimized');
                widget.style.right = '20px';
                widget.style.bottom = '20px';
                widget.style.left = 'auto';
                widget.style.top = 'auto';
                widget.style.width = '200px';
                widget.style.height = 'auto';
            } else {
                widget.classList.remove('minimized');

                if (preMinimizePosition) {
                    widget.style.left = preMinimizePosition.left + 'px';
                    widget.style.top = preMinimizePosition.top + 'px';
                    widget.style.right = 'auto';
                    widget.style.bottom = 'auto';
                    widget.style.width = preMinimizePosition.width + 'px';
                    widget.style.height = preMinimizePosition.height + 'px';
                } else {
                    var dimensions = AIChatState.loadDimensions();
                    var position = AIChatState.loadPosition();
                    if (position) {
                        widget.style.left = position.left + 'px';
                        widget.style.top = position.top + 'px';
                        widget.style.right = 'auto';
                        widget.style.bottom = 'auto';
                    }
                    if (dimensions) {
                        widget.style.width = dimensions.width + 'px';
                        widget.style.height = dimensions.height + 'px';
                    } else {
                        widget.style.width = '450px';
                        widget.style.height = '500px';
                    }
                }

                if (preMinimizeZoom && preMinimizeZoom !== 1.0) {
                    newZoomScale = preMinimizeZoom;
                    AIChatZoom.applyZoom(widget, newZoomScale);
                }
            }

            if (saveCallback) {
                saveCallback();
            }

            return {
                isMinimized: newIsMinimized,
                preMinimizePosition: newPreMinimizePosition,
                zoomScale: newZoomScale,
                preMinimizeZoom: preMinimizeZoom
            };
        }
    };

    window.AIChatWidget = AIChatWidget;

})();
