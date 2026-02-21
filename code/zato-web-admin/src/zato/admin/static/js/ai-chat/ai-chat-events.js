(function() {
    'use strict';

    var AIChatEvents = {

        logLayoutPositions: function(trigger) {
            var data = {
                trigger: trigger,
                timestamp: new Date().toISOString(),
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                elements: {}
            };

            var widget = document.getElementById('ai-chat-widget');
            if (widget) {
                var rect = widget.getBoundingClientRect();
                data.elements.widget = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: widget.offsetWidth,
                    offsetHeight: widget.offsetHeight,
                    classList: widget.className
                };
            }

            var splitWrapper = document.getElementById('ai-chat-split-wrapper');
            if (splitWrapper) {
                var rect = splitWrapper.getBoundingClientRect();
                data.elements.splitWrapper = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: splitWrapper.offsetWidth,
                    offsetHeight: splitWrapper.offsetHeight
                };
            }

            var leftPanel = document.querySelector('.zato-ide-split-panel-left');
            if (leftPanel) {
                var rect = leftPanel.getBoundingClientRect();
                data.elements.leftPanel = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: leftPanel.offsetWidth,
                    offsetHeight: leftPanel.offsetHeight,
                    styleWidth: leftPanel.style.width
                };
            }

            var rightPanel = document.querySelector('.zato-ide-split-panel-right');
            if (rightPanel) {
                var rect = rightPanel.getBoundingClientRect();
                var computedStyle = getComputedStyle(rightPanel);
                data.elements.rightPanel = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: rightPanel.offsetWidth,
                    offsetHeight: rightPanel.offsetHeight,
                    display: computedStyle.display
                };
            }

            var resizer = document.querySelector('.zato-ide-split-resizer');
            if (resizer) {
                var rect = resizer.getBoundingClientRect();
                var computedStyle = getComputedStyle(resizer);
                data.elements.resizer = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    display: computedStyle.display
                };
            }

            var ideContainer = document.querySelector('.zato-ide-container');
            if (ideContainer) {
                var rect = ideContainer.getBoundingClientRect();
                data.elements.ideContainer = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: ideContainer.offsetWidth,
                    offsetHeight: ideContainer.offsetHeight
                };
            }

            var toolbar = document.querySelector('.zato-ide-toolbar');
            if (toolbar) {
                var rect = toolbar.getBoundingClientRect();
                data.elements.toolbar = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            }

            var editorArea = document.querySelector('.zato-ide-editor-area');
            if (editorArea) {
                var rect = editorArea.getBoundingClientRect();
                data.elements.editorArea = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            }

            var aceEditor = document.querySelector('.ace_editor');
            if (aceEditor) {
                var rect = aceEditor.getBoundingClientRect();
                data.elements.aceEditor = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: aceEditor.offsetWidth,
                    offsetHeight: aceEditor.offsetHeight
                };
            }

            var aceGutter = document.querySelector('.ace_gutter');
            if (aceGutter) {
                var rect = aceGutter.getBoundingClientRect();
                var computedStyle = getComputedStyle(aceGutter);
                data.elements.aceGutter = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    offsetWidth: aceGutter.offsetWidth,
                    styleWidth: computedStyle.width
                };
            }

            var aceScroller = document.querySelector('.ace_scroller');
            if (aceScroller) {
                var rect = aceScroller.getBoundingClientRect();
                var computedStyle = getComputedStyle(aceScroller);
                data.elements.aceScroller = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    styleLeft: computedStyle.left
                };
            }

            var aceContent = document.querySelector('.ace_content');
            if (aceContent) {
                var rect = aceContent.getBoundingClientRect();
                data.elements.aceContent = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            }

            var sidePanel1 = document.querySelector('.zato-ide-side-panel-1');
            if (sidePanel1) {
                var rect = sidePanel1.getBoundingClientRect();
                data.elements.sidePanel1 = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            }

            var sidePanel1Content = document.querySelector('.zato-ide-side-panel-1-content');
            if (sidePanel1Content) {
                var rect = sidePanel1Content.getBoundingClientRect();
                data.elements.sidePanel1Content = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height,
                    collapsed: sidePanel1Content.classList.contains('collapsed')
                };
            }

            var mainSplit = document.getElementById('zato-ide-panel-main-split');
            if (mainSplit) {
                var rect = mainSplit.getBoundingClientRect();
                data.elements.mainSplit = {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            }

            var ideInstance = null;
            if (typeof ZatoIDE !== 'undefined' && ZatoIDE.instances) {
                for (var key in ZatoIDE.instances) {
                    ideInstance = ZatoIDE.instances[key];
                    break;
                }
            }
            if (ideInstance && ideInstance.codeEditor && ideInstance.codeEditor.aceEditor) {
                var renderer = ideInstance.codeEditor.aceEditor.renderer;
                data.aceRenderer = {
                    gutterWidth: renderer.gutterWidth,
                    gutterLayerWidth: renderer.$gutterLayer ? renderer.$gutterLayer.gutterWidth : null,
                    scrollLeft: renderer.scrollLeft,
                    scrollTop: renderer.scrollTop,
                    layerConfig: renderer.layerConfig ? {
                        width: renderer.layerConfig.width,
                        height: renderer.layerConfig.height,
                        gutterOffset: renderer.layerConfig.gutterOffset
                    } : null
                };
            }

            console.log('[layout-diag] ' + trigger + ':', JSON.stringify(data, null, 2));
        },

        toggleIDE: function(core) {
            console.log('[F9] toggleIDE: ideEnabled=' + core.ideEnabled + ' -> ' + !core.ideEnabled);
            if (!window.AIChatIDEIntegration) {
                console.log('[F9] toggleIDE: no AIChatIDEIntegration, returning');
                return;
            }
            core.ideEnabled = !core.ideEnabled;
            core.chatEnabled = true;
            AIChatIDEIntegration.setEnabled(core.ideEnabled);
            AIChatIDEIntegration.setChatEnabled(core.chatEnabled);
            console.log('[F9] toggleIDE: calling render, ideEnabled=' + core.ideEnabled + ' chatEnabled=' + core.chatEnabled);
            core.render();
        },

        toggleChat: function(core) {
            console.log('[F8] toggleChat: ideEnabled=' + core.ideEnabled + ' chatEnabled=' + core.chatEnabled);
            this.logLayoutPositions('F8-before');
            if (!window.AIChatIDEIntegration) {
                console.log('[F8] toggleChat: no AIChatIDEIntegration, returning');
                return;
            }
            if (!core.ideEnabled) {
                console.log('[F8] toggleChat: ide not enabled, enabling ide and hiding chat');
                core.ideEnabled = true;
                core.chatEnabled = false;
                AIChatIDEIntegration.setEnabled(true);
                AIChatIDEIntegration.setChatEnabled(false);
                core.render();
                this.applyChatVisibility(core);
                this.logLayoutPositions('F8-after-render');
                return;
            }
            core.chatEnabled = !core.chatEnabled;
            AIChatIDEIntegration.setChatEnabled(core.chatEnabled);
            console.log('[F8] toggleChat: toggled chatEnabled to ' + core.chatEnabled);
            this.applyChatVisibility(core);
            this.logLayoutPositions('F8-after');
        },

        applyChatVisibility: function(core) {
            var splitWrapper = core.widget.querySelector('#ai-chat-split-wrapper');
            if (!splitWrapper) {
                return;
            }
            var rightPanel = splitWrapper.querySelector('.zato-ide-split-panel-right');
            var resizer = splitWrapper.querySelector('.zato-ide-split-resizer');
            var leftPanel = splitWrapper.querySelector('.zato-ide-split-panel-left');
            if (!rightPanel || !resizer || !leftPanel) {
                return;
            }
            if (core.chatEnabled) {
                rightPanel.style.display = '';
                resizer.style.display = '';
                leftPanel.style.width = '';
                if (window.ZatoIDESplit) {
                    var instance = ZatoIDESplit.getInstance('ai-chat-split-wrapper');
                    if (instance) {
                        ZatoIDESplit.applySplitPosition(instance);
                    }
                }
            } else {
                rightPanel.style.display = 'none';
                resizer.style.display = 'none';
                leftPanel.style.width = '100%';
            }
        },

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
                if (e.key === 'F9') {
                    e.preventDefault();
                    self.toggleIDE(core);
                    return;
                }

                if (e.key === 'F8') {
                    e.preventDefault();
                    self.toggleChat(core);
                    return;
                }

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

                if (!e.target.closest('.ai-chat-context-bar')) {
                    var openTooltips = document.querySelectorAll('.ai-chat-context-tooltip.open');
                    for (var i = 0; i < openTooltips.length; i++) {
                        openTooltips[i].classList.remove('open');
                    }
                }
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
