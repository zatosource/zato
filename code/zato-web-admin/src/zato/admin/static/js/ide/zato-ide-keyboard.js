(function() {
    'use strict';

    var ZatoIDEKeyboard = {

        lastFocusedPanel: 'ide',
        initialized: false,

        init: function() {
            if (this.initialized) {
                return;
            }
            this.initialized = true;

            var self = this;

            document.addEventListener('click', function(e) {
                self.trackFocus(e.target);
            }, true);

            document.addEventListener('focusin', function(e) {
                self.trackFocus(e.target);
            }, true);

            var handleCtrlW = function(e) {
                if (e.ctrlKey && (e.key === 'w' || e.key === 'W' || e.keyCode === 87 || e.which === 87 || e.which === 119)) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    self.handleCloseTab();
                    return false;
                }
                if (e.key === 'F2' || e.keyCode === 113) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    self.toggleSidePanelContent();
                    return false;
                }
            };

            document.addEventListener('keydown', handleCtrlW, true);
            window.addEventListener('keydown', handleCtrlW, true);
            document.addEventListener('keypress', handleCtrlW, true);
            window.addEventListener('keypress', handleCtrlW, true);
            document.addEventListener('keyup', function(e) {
                if (e.ctrlKey && (e.key === 'w' || e.key === 'W' || e.keyCode === 87)) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);
        },

        trackFocus: function(target) {
            var idePanel = document.querySelector('.zato-ide-split-panel-left');
            var aiPanel = document.querySelector('.zato-ide-split-panel-right');

            if (!idePanel || !aiPanel) {
                return;
            }

            if (idePanel.contains(target)) {
                this.lastFocusedPanel = 'ide';
            } else if (aiPanel.contains(target)) {
                this.lastFocusedPanel = 'ai';
            }
        },

        isIDEVisible: function() {
            var idePanel = document.querySelector('.zato-ide-split-panel-left');
            if (!idePanel) {
                return false;
            }
            var style = getComputedStyle(idePanel);
            return style.display !== 'none' && idePanel.offsetWidth > 0;
        },

        isAIWidgetVisible: function() {
            var aiPanel = document.querySelector('.zato-ide-split-panel-right');
            if (!aiPanel) {
                return false;
            }
            var style = getComputedStyle(aiPanel);
            return style.display !== 'none' && aiPanel.offsetWidth > 0;
        },

        handleCloseTab: function() {
            var ideVisible = this.isIDEVisible();
            var aiVisible = this.isAIWidgetVisible();

            if (!ideVisible && aiVisible) {
                this.closeAIWidgetTab();
                return;
            }

            if (ideVisible && !aiVisible) {
                this.closeIDETab();
                return;
            }

            if (this.lastFocusedPanel === 'ide') {
                this.closeIDETab();
            } else {
                this.closeAIWidgetTab();
            }
        },

        closeIDETab: function() {
            var ideInstance = null;
            if (typeof ZatoIDE !== 'undefined' && ZatoIDE.instances) {
                for (var key in ZatoIDE.instances) {
                    ideInstance = ZatoIDE.instances[key];
                    break;
                }
            }

            if (!ideInstance || !ideInstance.tabsManager || !ideInstance.tabsManager.tabs) {
                return;
            }

            var activeTabId = ideInstance.tabsManager.activeTabId;
            if (!activeTabId) {
                return;
            }

            var activeTab = null;
            for (var i = 0; i < ideInstance.tabsManager.tabs.length; i++) {
                if (ideInstance.tabsManager.tabs[i].id === activeTabId) {
                    activeTab = ideInstance.tabsManager.tabs[i];
                    break;
                }
            }

            if (activeTab) {
                ZatoIDE.closeTab(ideInstance, activeTab);
            }
        },

        closeAIWidgetTab: function() {
            var widget = document.getElementById('ai-chat-widget');
            if (!widget) {
                return;
            }

            if (typeof AIChatTabActions === 'undefined' || typeof AIChatCore === 'undefined') {
                return;
            }

            var core = AIChatCore;
            if (!core.tabs || core.tabs.length === 0) {
                return;
            }

            if (core.tabs.length === 1) {
                return;
            }

            AIChatTabActions.closeTab(widget, core, core.activeTabId);
        },

        toggleSidePanelContent: function() {
            var ideInstance = null;
            if (typeof ZatoIDE !== 'undefined' && ZatoIDE.instances) {
                for (var key in ZatoIDE.instances) {
                    ideInstance = ZatoIDE.instances[key];
                    break;
                }
            }

            if (!ideInstance || !ideInstance.mainSplit) {
                return;
            }

            var contentContainer = document.getElementById(ideInstance.id + '-side-panel-1-content');
            var sidePanel = document.getElementById(ideInstance.id + '-side-panel-1');
            
            if (!contentContainer || !sidePanel) {
                return;
            }

            var iconsWidth = 48;
            var activeView = ideInstance.sidePanel1ActiveView || 'explorer';
            
            if (!ideInstance.mainSplit.savedSplitPercentByView) {
                ideInstance.mainSplit.savedSplitPercentByView = {};
            }
            
            var aceScroller = document.querySelector('.ace_scroller');
            
            var syncGutterWidth = function() {
                if (!ideInstance.codeEditor || !ideInstance.codeEditor.aceEditor) {
                    return;
                }
                var renderer = ideInstance.codeEditor.aceEditor.renderer;
                var gutterLayerWidth = renderer && renderer.$gutterLayer ? renderer.$gutterLayer.gutterWidth : null;
                if (renderer && gutterLayerWidth !== null) {
                    var gutterEl = renderer.$gutter;
                    if (gutterEl) {
                        gutterEl.style.width = gutterLayerWidth + 'px';
                    }
                    renderer.gutterWidth = gutterLayerWidth;
                    if (aceScroller) {
                        aceScroller.style.left = gutterLayerWidth + 'px';
                    }
                    var aceScrollBarH = renderer.scrollBarH ? renderer.scrollBarH.element : null;
                    if (aceScrollBarH) {
                        aceScrollBarH.style.left = gutterLayerWidth + 'px';
                    }
                }
            };
            
            if (ideInstance.codeEditor && ideInstance.codeEditor.aceEditor) {
                ideInstance.codeEditor.aceEditor.resize();
                syncGutterWidth();
            }
            
            if (contentContainer.classList.contains('collapsed')) {
                contentContainer.classList.remove('collapsed');
                sidePanel.style.minWidth = '';
                ideInstance.sidePanelContentHidden = false;
                var savedPercent = ideInstance.mainSplit.savedSplitPercentByView[activeView];
                if (typeof ZatoIDESplit !== 'undefined' && savedPercent !== undefined) {
                    ideInstance.mainSplit.splitPercent = savedPercent;
                    ZatoIDESplit.applySplitPosition(ideInstance.mainSplit);
                }
            } else {
                contentContainer.classList.add('collapsed');
                ideInstance.sidePanelContentHidden = true;
                ideInstance.mainSplit.savedSplitPercentByView[activeView] = ideInstance.mainSplit.splitPercent;
                var iconsEl = document.getElementById(ideInstance.id + '-side-panel-1-icons');
                var actualIconsWidth = iconsEl ? iconsEl.offsetWidth : iconsWidth;
                var containerWidth = ideInstance.mainSplit.container.offsetWidth;
                var resizerWidth = ideInstance.mainSplit.resizer ? ideInstance.mainSplit.resizer.offsetWidth : 4;
                var newLeftWidth = Math.round(containerWidth - actualIconsWidth - resizerWidth);
                ideInstance.mainSplit.leftPanel.style.width = newLeftWidth + 'px';
            }

            if (ideInstance.codeEditor && ideInstance.codeEditor.aceEditor) {
                setTimeout(function() {
                    ideInstance.codeEditor.aceEditor.resize();
                    syncGutterWidth();
                }, 20);
            }
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            ZatoIDEKeyboard.init();
        });
    } else {
        ZatoIDEKeyboard.init();
    }

    window.ZatoIDEKeyboard = ZatoIDEKeyboard;

})();
