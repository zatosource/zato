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
            
            var logEditorPosition = function(label) {
                var leftPanel = ideInstance.mainSplit.leftPanel;
                var editorArea = document.getElementById(ideInstance.id + '-editor-area');
                var aceContainer = editorArea ? editorArea.querySelector('.ace_editor') : null;
                var aceContent = aceContainer ? aceContainer.querySelector('.ace_content') : null;
                var aceGutter = aceContainer ? aceContainer.querySelector('.ace_gutter') : null;
                var aceScroller = aceContainer ? aceContainer.querySelector('.ace_scroller') : null;
                var aceGutterLayer = aceGutter ? aceGutter.querySelector('.ace_gutter-layer') : null;
                
                console.log('[toggleSidePanelContent] ' + label);
                if (leftPanel) {
                    var lpRect = leftPanel.getBoundingClientRect();
                    var lpStyle = window.getComputedStyle(leftPanel);
                    console.log('  leftPanel: left=' + lpRect.left.toFixed(2) + ', width=' + lpRect.width.toFixed(2) + ', paddingLeft=' + lpStyle.paddingLeft + ', marginLeft=' + lpStyle.marginLeft);
                }
                if (editorArea) {
                    var eaRect = editorArea.getBoundingClientRect();
                    var eaStyle = window.getComputedStyle(editorArea);
                    console.log('  editorArea: left=' + eaRect.left.toFixed(2) + ', width=' + eaRect.width.toFixed(2) + ', paddingLeft=' + eaStyle.paddingLeft + ', marginLeft=' + eaStyle.marginLeft);
                }
                if (aceContainer) {
                    var acRect = aceContainer.getBoundingClientRect();
                    var acStyle = window.getComputedStyle(aceContainer);
                    console.log('  aceContainer: left=' + acRect.left.toFixed(2) + ', width=' + acRect.width.toFixed(2) + ', paddingLeft=' + acStyle.paddingLeft + ', marginLeft=' + acStyle.marginLeft);
                }
                if (aceGutter) {
                    var agRect = aceGutter.getBoundingClientRect();
                    var agStyle = window.getComputedStyle(aceGutter);
                    console.log('  aceGutter: left=' + agRect.left.toFixed(2) + ', width=' + agRect.width.toFixed(2) + ', style.width=' + agStyle.width);
                }
                if (aceGutterLayer) {
                    var aglRect = aceGutterLayer.getBoundingClientRect();
                    var aglStyle = window.getComputedStyle(aceGutterLayer);
                    console.log('  aceGutterLayer: left=' + aglRect.left.toFixed(2) + ', width=' + aglRect.width.toFixed(2) + ', style.width=' + aglStyle.width);
                }
                if (aceScroller) {
                    var asRect = aceScroller.getBoundingClientRect();
                    var asStyle = window.getComputedStyle(aceScroller);
                    console.log('  aceScroller: left=' + asRect.left.toFixed(2) + ', width=' + asRect.width.toFixed(2) + ', style.left=' + asStyle.left);
                }
                if (aceContent) {
                    var acnRect = aceContent.getBoundingClientRect();
                    var acnStyle = window.getComputedStyle(aceContent);
                    console.log('  aceContent: left=' + acnRect.left.toFixed(2) + ', width=' + acnRect.width.toFixed(2) + ', marginLeft=' + acnStyle.marginLeft);
                }
            };
            
            var splitContainer = document.querySelector('.zato-ide-split-container');
            if (splitContainer) {
                var scRect = splitContainer.getBoundingClientRect();
                console.log('[toggleSidePanelContent] splitContainer: left=' + scRect.left.toFixed(2));
            }
            
            logEditorPosition('BEFORE toggle');
            
            var aceScroller = document.querySelector('.ace_scroller');
            if (aceScroller) {
                console.log('[toggleSidePanelContent] aceScroller.style.left raw=' + aceScroller.style.left);
                var renderer = ideInstance.codeEditor && ideInstance.codeEditor.aceEditor ? ideInstance.codeEditor.aceEditor.renderer : null;
                if (renderer) {
                    console.log('[toggleSidePanelContent] renderer.gutterWidth=' + renderer.gutterWidth);
                    console.log('[toggleSidePanelContent] renderer.$gutterLayer.gutterWidth=' + (renderer.$gutterLayer ? renderer.$gutterLayer.gutterWidth : 'n/a'));
                }
            }
            
            if (ideInstance.codeEditor && ideInstance.codeEditor.aceEditor) {
                var renderer = ideInstance.codeEditor.aceEditor.renderer;
                var gutterLayerWidth = renderer && renderer.$gutterLayer ? renderer.$gutterLayer.gutterWidth : null;
                
                ideInstance.codeEditor.aceEditor.resize();
                
                if (renderer && gutterLayerWidth !== null) {
                    var gutterEl = renderer.$gutter;
                    if (gutterEl) {
                        gutterEl.style.width = gutterLayerWidth + 'px';
                    }
                    renderer.gutterWidth = gutterLayerWidth;
                    if (aceScroller) {
                        aceScroller.style.left = gutterLayerWidth + 'px';
                    }
                    console.log('[toggleSidePanelContent] synced gutterWidth to gutterLayer value: ' + gutterLayerWidth);
                }
                logEditorPosition('AFTER pre-resize');
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
                logEditorPosition('AFTER expand');
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
                logEditorPosition('AFTER collapse');
            }

            if (ideInstance.codeEditor && ideInstance.codeEditor.aceEditor) {
                var savedScrollerLeft = aceScroller ? aceScroller.style.left : null;
                setTimeout(function() {
                    ideInstance.codeEditor.aceEditor.resize();
                    if (savedScrollerLeft && aceScroller) {
                        aceScroller.style.left = savedScrollerLeft;
                    }
                    logEditorPosition('AFTER ace resize');
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
