(function() {
    'use strict';

    var AIChatEvents = {

        bind: function(widget, core) {
            var self = this;

            widget.addEventListener('click', function(e) {
                AIChatClickHandlers.handleClick(e, widget, core);
            });

            widget.addEventListener('mouseenter', function(e) {
                if (e.target.id === 'ai-chat-menu-button' || e.target.closest('#ai-chat-menu-button')) {
                    AIChatSettings.showMenu(widget);
                }
            }, true);

            widget.addEventListener('mousedown', function(e) {
                AIChatDrag.handleMouseDown(e, widget, core.isMinimized, core.zoomScale, function() {
                    AIChatWindow.toggleMinimize(widget, core);
                });
            });

            widget.addEventListener('dblclick', function(e) {
                var header = e.target.closest('#ai-chat-header');
                if (header && !e.target.closest('.ai-chat-header-button')) {
                    AIChatWindow.toggleMaximize(widget, core);
                }
            });

            widget.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                widget.classList.add('drag-over');
            });

            widget.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                widget.classList.remove('drag-over');
            });

            widget.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                widget.classList.remove('drag-over');
                var files = e.dataTransfer.files;
                if (files && files.length > 0) {
                    for (var i = 0; i < files.length; i++) {
                        AIChatAttachments.addFile(files[i], core.activeTabId, function() {
                            AIChatAttachments.render(widget, core.activeTabId, core.tabs);
                        });
                    }
                }
            });

            document.addEventListener('mousemove', function(e) {
                AIChatDrag.handleMouseMove(e, widget, core.zoomScale);
            });

            document.addEventListener('mouseup', function(e) {
                var result = AIChatDrag.handleMouseUp(widget, core.tabs, function() {
                    core.saveState();
                }, function() {
                    core.render();
                });
                if (result.tabsChanged) {
                    core.tabs = result.tabs;
                    core.saveState();
                    core.render();
                }
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    if (AIChatContextHelp && AIChatContextHelp.isOpen && AIChatContextHelp.isOpen()) {
                        AIChatContextHelp.close();
                        e.preventDefault();
                        return;
                    }
                    if (AIChatPreview.closeTop()) {
                        e.preventDefault();
                        return;
                    }
                    var backBtn = widget.querySelector('.ai-chat-config-back');
                    if (backBtn) {
                        e.preventDefault();
                        backBtn.click();
                        return;
                    }
                }

                if (e.key === 'Enter' && !e.shiftKey) {
                    var mcpEndpoint = e.target.closest('#ai-chat-mcp-endpoint');
                    if (mcpEndpoint) {
                        e.preventDefault();
                        var saveBtn = widget.querySelector('#ai-chat-mcp-save');
                        if (saveBtn) {
                            saveBtn.click();
                        }
                        return;
                    }
                }

                if (e.key === 'Backspace') {
                    var isInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable;
                    if (!isInput) {
                        var backBtn = widget.querySelector('.ai-chat-config-back');
                        if (backBtn) {
                            e.preventDefault();
                            backBtn.click();
                        }
                    }
                }

                AIChatInput.handleKeyDown(e, function(tabId) {
                    AIChatStreaming.sendMessage(widget, core, tabId);
                });
            });

            widget.addEventListener('paste', function(e) {
                var inputElement = e.target.closest('.ai-chat-input');
                if (!inputElement) return;
                AIChatInput.handlePaste(e, function(attachment, tabId) {
                    AIChatAttachments.render(widget, tabId, core.tabs);
                });
            });

            document.addEventListener('input', function(e) {
                AIChatInput.handleInput(e);
            });

            document.addEventListener('keyup', function(e) {
                AIChatInput.handleKeyUp(e);
            });

            widget.addEventListener('contextmenu', function(e) {
                var tabElement = e.target.closest('.ai-chat-tab');
                if (tabElement) {
                    e.preventDefault();
                    var tabId = tabElement.getAttribute('data-tab-id');
                    AIChatContextMenu.show(e.clientX, e.clientY, tabId, core);
                }
            });

            widget.addEventListener('wheel', function(e) {
                if (e.ctrlKey) {
                    return;
                }
                core.zoomScale = AIChatZoom.handleWheel(widget, e, core.zoomScale);
                AIChatState.saveZoom(core.zoomScale);
            }, { passive: true });

            document.addEventListener('click', function(e) {
                AIChatContextMenu.hide();
                AIChatSettings.hideMenu();
                AIChatOptionsMenu.hide(widget);
            });

            widget.addEventListener('change', function(e) {
                var target = e.target;
                if (target.classList.contains('ai-chat-model-select')) {
                    var tabId = target.getAttribute('data-tab-id');
                    var modelId = target.value;
                    AIChatTabState.setModel(tabId, modelId);
                    for (var i = 0; i < core.tabs.length; i++) {
                        if (core.tabs[i].id === tabId) {
                            AIChatTabState.saveToTab(core.tabs[i]);
                            AIChatState.saveTabs(core.tabs);
                            break;
                        }
                    }
                }
            });
        }
    };

    window.AIChatEvents = AIChatEvents;

})();
