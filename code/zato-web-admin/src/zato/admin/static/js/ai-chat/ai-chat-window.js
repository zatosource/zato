(function() {
    'use strict';

    var AIChatWindow = {

        toggleMinimize: function(widget, core) {
            if (core.isMaximized && !core.isMinimized) {
                if (core.preMaximizeState) {
                    widget.style.left = core.preMaximizeState.left;
                    widget.style.top = core.preMaximizeState.top;
                    widget.style.width = core.preMaximizeState.width;
                    widget.style.height = core.preMaximizeState.height;
                }
                if (core.preMaximizeZoomScale) {
                    core.zoomScale = core.preMaximizeZoomScale;
                    widget.style.transform = 'scale(' + core.zoomScale + ')';
                }
                widget.classList.remove('maximized');
                document.documentElement.classList.remove('ai-chat-maximized');
                core.isMaximized = false;
            }

            var wasMinimized = core.isMinimized;
            var result = AIChatWidget.toggleMinimize(
                widget,
                core.isMinimized,
                core.preMinimizePosition,
                core.zoomScale,
                function() { core.saveState(); }
            );
            core.isMinimized = result.isMinimized;
            core.preMinimizePosition = result.preMinimizePosition;
            core.zoomScale = result.zoomScale;
            core.preMinimizeZoom = result.preMinimizeZoom;
            core.saveState();
            core.render();

            if (wasMinimized && !core.isMinimized) {
                setTimeout(function() {
                    var input = widget.querySelector('.ai-chat-input');
                    if (input) {
                        input.focus();
                    }
                }, 50);
            }
        },

        toggleMaximize: function(widget, core) {
            if (core.isMinimized) {
                this.toggleMinimize(widget, core);
            }

            if (core.isMaximized) {
                if (core.preMaximizeState) {
                    widget.style.left = core.preMaximizeState.left;
                    widget.style.top = core.preMaximizeState.top;
                    widget.style.width = core.preMaximizeState.width;
                    widget.style.height = core.preMaximizeState.height;
                }
                if (core.preMaximizeZoomScale) {
                    core.zoomScale = core.preMaximizeZoomScale;
                    widget.style.transform = 'scale(' + core.zoomScale + ')';
                }
                widget.classList.remove('maximized');
                document.documentElement.classList.remove('ai-chat-maximized');
                core.isMaximized = false;
            } else {
                core.preMaximizeState = {
                    left: widget.style.left,
                    top: widget.style.top,
                    width: widget.style.width,
                    height: widget.style.height
                };
                core.preMaximizeZoomScale = core.zoomScale;
                core.zoomScale = 1;
                widget.classList.add('maximized');
                document.documentElement.classList.add('ai-chat-maximized');
                core.isMaximized = true;
            }
            core.saveState();
            core.render();
            AIChatTabActions.focusInput(widget, core.activeTabId);
        }
    };

    window.AIChatWindow = AIChatWindow;

})();
