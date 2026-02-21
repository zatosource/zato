(function() {
    'use strict';

    var AIChatWindow = {

        toggleMinimize: function(widget, core) {
            if (window.AIChatEvents && AIChatEvents.logLayoutPositions) {
                AIChatEvents.logLayoutPositions('minimize-before');
            }
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
                    if (window.AIChat && AIChat.recalculateSplitPositions) {
                        AIChat.recalculateSplitPositions('minimize-after-restore');
                    }
                    var input = widget.querySelector('.ai-chat-input');
                    if (input) {
                        input.focus();
                    }
                }, 50);
            } else {
                if (window.AIChatEvents && AIChatEvents.logLayoutPositions) {
                    AIChatEvents.logLayoutPositions('minimize-after');
                }
            }
        },

        toggleMaximize: function(widget, core) {
            if (window.AIChatEvents && AIChatEvents.logLayoutPositions) {
                AIChatEvents.logLayoutPositions('maximize-before');
            }
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

            if (window.AIChat && AIChat.recalculateSplitPositions) {
                AIChat.recalculateSplitPositions('maximize-after');
            }

            AIChatTabActions.focusInput(widget, core.activeTabId);
        }
    };

    window.AIChatWindow = AIChatWindow;

})();
