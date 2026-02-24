(function() {
    'use strict';

    var ZatoIDEPanels = {

        initMainSplit: function(instance) {
            console.log('[ZatoIDE] initMainSplit: START');
            if (typeof ZatoIDESplit === 'undefined') {
                console.log('[ZatoIDE] initMainSplit: ZatoIDESplit undefined, returning');
                return;
            }
            var splitContainerId = instance.id + '-main-split';
            console.log('[ZatoIDE] initMainSplit: splitContainerId=' + splitContainerId);
            var container = document.getElementById(splitContainerId);
            console.log('[ZatoIDE] initMainSplit: container found=' + !!container);
            if (container) {
                console.log('[ZatoIDE] initMainSplit: container.innerHTML length=' + container.innerHTML.length);
                console.log('[ZatoIDE] initMainSplit: container.children.length=' + container.children.length);
            }
            instance.mainSplit = ZatoIDESplit.create(splitContainerId, {
                storageKey: 'zato.ide.main-split-position',
                defaultSplitPercent: 75,
                onResize: function() {
                    if (instance.aceEditor) {
                        instance.aceEditor.resize();
                    }
                }
            });
            console.log('[ZatoIDE] initMainSplit: mainSplit created=' + !!instance.mainSplit);
            if (!instance.mainSplit) {
                console.log('[ZatoIDE] initMainSplit: mainSplit is null, returning');
                return;
            }
            var leftPanel = ZatoIDESplit.getLeftPanel(instance.mainSplit);
            var rightPanel = ZatoIDESplit.getRightPanel(instance.mainSplit);
            console.log('[ZatoIDE] initMainSplit: leftPanel=' + !!leftPanel + ', rightPanel=' + !!rightPanel);
            if (leftPanel) {
                console.log('[ZatoIDE] initMainSplit: setting leftPanel id to ' + instance.id + '-editor-area');
                leftPanel.id = instance.id + '-editor-area';
                leftPanel.className += ' zato-ide-editor-area';
            }
            if (rightPanel) {
                console.log('[ZatoIDE] initMainSplit: setting rightPanel id to ' + instance.id + '-side-panel-1');
                console.log('[ZatoIDE] initMainSplit: rightPanel current innerHTML length=' + rightPanel.innerHTML.length);
                rightPanel.id = instance.id + '-side-panel-1';
                rightPanel.className += ' zato-ide-side-panel-1';
                var iconsDiv = document.createElement('div');
                iconsDiv.id = instance.id + '-side-panel-1-icons';
                iconsDiv.className = 'zato-ide-side-panel-1-icons';
                rightPanel.appendChild(iconsDiv);
                var contentDiv = document.createElement('div');
                contentDiv.id = instance.id + '-side-panel-1-content';
                contentDiv.className = 'zato-ide-side-panel-1-content';
                rightPanel.appendChild(contentDiv);
                console.log('[ZatoIDE] initMainSplit: side panel elements created');
            }
            console.log('[ZatoIDE] initMainSplit: END');
        },

        initSidePanel1Content: function(instance) {
            var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
            if (!contentContainer) { return; }
            if (instance.sidePanel1ActiveView === 'explorer') {
                this.initExplorer(instance, contentContainer);
            } else if (instance.sidePanel1ActiveView === 'debugger') {
                this.initDebuggerPanel(instance, contentContainer);
            }
        },

        loadSidePanel1Icons: function(instance) {
            var self = this;
            var iconsContainer = document.getElementById(instance.id + '-side-panel-1-icons');
            if (!iconsContainer) { return; }
            var icons = [
                { id: 'explorer', file: 'explorer.svg', tooltip: 'Explorer' },
                { id: 'debugger', file: 'debugger.svg', tooltip: 'Debugger' },
                { id: 'notes', file: 'notes.svg', tooltip: 'Notes' }
            ];
            var savedView = localStorage.getItem('zato.ide.sidePanel1View');
            instance.sidePanel1ActiveView = savedView || 'explorer';
            icons.forEach(function(iconDef) {
                var iconDiv = document.createElement('div');
                iconDiv.className = 'zato-ide-side-panel-1-icon';
                iconDiv.setAttribute('data-view', iconDef.id);
                iconDiv.setAttribute('data-tooltip', iconDef.tooltip);
                iconDiv.setAttribute('data-tooltip-position', 'left');
                if (iconDef.id === instance.sidePanel1ActiveView) {
                    iconDiv.classList.add('active');
                }
                iconsContainer.appendChild(iconDiv);
                var xhr = new XMLHttpRequest();
                xhr.open('GET', '/static/img/side-panel/' + iconDef.file, true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        iconDiv.innerHTML = xhr.responseText;
                    }
                };
                xhr.send();
                iconDiv.addEventListener('click', function() {
                    var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
                    var isCollapsed = contentContainer && contentContainer.classList.contains('collapsed');
                    if (isCollapsed) {
                        if (typeof ZatoIDEKeyboard !== 'undefined' && ZatoIDEKeyboard.toggleSidePanelContent) {
                            ZatoIDEKeyboard.toggleSidePanelContent();
                        }
                    }
                    self.switchSidePanel1View(instance, iconDef.id);
                });
            });
        },

        switchSidePanel1View: function(instance, viewId) {
            console.log('[ZatoIDEPanels] switchSidePanel1View: viewId=' + viewId);
            var self = this;
            var iconsContainer = document.getElementById(instance.id + '-side-panel-1-icons');
            if (!iconsContainer) { return; }
            var icons = iconsContainer.querySelectorAll('.zato-ide-side-panel-1-icon');
            icons.forEach(function(icon) {
                if (icon.getAttribute('data-view') === viewId) {
                    icon.classList.add('active');
                } else {
                    icon.classList.remove('active');
                }
            });
            instance.sidePanel1ActiveView = viewId;
            localStorage.setItem('zato.ide.sidePanel1View', viewId);
            var contentContainer = document.getElementById(instance.id + '-side-panel-1-content');
            if (contentContainer) {
                console.log('[ZatoIDEPanels] switchSidePanel1View: clearing contentContainer');
                contentContainer.innerHTML = '';
                if (viewId === 'explorer') {
                    console.log('[ZatoIDEPanels] switchSidePanel1View: initializing explorer');
                    self.initExplorer(instance, contentContainer);
                } else if (viewId === 'debugger') {
                    console.log('[ZatoIDEPanels] switchSidePanel1View: initializing debugger panel');
                    self.initDebuggerPanel(instance, contentContainer);
                }
            }
        },

        initDebuggerPanel: function(instance, container) {
            console.log('[ZatoIDEPanels] initDebuggerPanel: START');
            if (typeof ZatoDebuggerIDE === 'undefined') { return; }
            var debuggerIDE = ZatoDebuggerIDE.getInstanceForIDE(instance);
            console.log('[ZatoIDEPanels] initDebuggerPanel: existing debuggerIDE=' + !!debuggerIDE);
            if (!debuggerIDE) {
                debuggerIDE = ZatoDebuggerIDE.create(instance, {});
            }
            console.log('[ZatoIDEPanels] initDebuggerPanel: debuggerIDE.debuggerUI=' + !!debuggerIDE.debuggerUI);
            if (debuggerIDE.debuggerUI) {
                console.log('[ZatoIDEPanels] initDebuggerPanel: debuggerUI.isConnected=' + debuggerIDE.debuggerUI.isConnected);
                console.log('[ZatoIDEPanels] initDebuggerPanel: debuggerUI.isConnecting=' + debuggerIDE.debuggerUI.isConnecting);
            }
            var debuggerDiv = document.createElement('div');
            debuggerDiv.id = instance.id + '-debugger-panel';
            debuggerDiv.className = 'zato-ide-debugger-panel';
            container.appendChild(debuggerDiv);
            ZatoDebuggerIDE.showDebugPanelInContainer(debuggerIDE, debuggerDiv.id);
            console.log('[ZatoIDEPanels] initDebuggerPanel: END');
        },

        initExplorer: function(instance, container) {
            var self = this;
            if (typeof ZatoIDEExplorer === 'undefined') { return; }
            var explorerDiv = document.createElement('div');
            var explorerId = instance.id + '-explorer';
            explorerDiv.id = explorerId;
            container.appendChild(explorerDiv);
            instance.explorer = ZatoIDEExplorer.create(explorerId, {
                rootPath: '~/projects/zatosource-zato/4.1/code/zato-server/src/zato/server/connection/http_soap',
                onFileSelect: function(item) {
                    console.log('[ZatoIDE] File selected:', item.path);
                },
                onFileDoubleClick: function(item) {
                    if (typeof ZatoIDEEditorAce !== 'undefined' && ZatoIDEEditorAce.isEditableFile(item.name)) {
                        ZatoIDE.openFileFromPath(instance, item.path, item.name);
                    } else {
                        self.downloadFile(item.path, item.name);
                    }
                }
            });
        },

        downloadFile: function(filePath, fileName) {
            var link = document.createElement('a');
            link.href = '/zato/ide/explorer/download/?path=' + encodeURIComponent(filePath);
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        loadSearchIcon: function(instance) {
            var searchButton = instance.container.querySelector('.zato-ide-search-button');
            if (!searchButton) { return; }
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/static/img/search.svg', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var svgContent = xhr.responseText;
                    svgContent = svgContent.replace(/width="24"/, 'width="25"');
                    svgContent = svgContent.replace(/height="24"/, 'height="25"');
                    searchButton.innerHTML = svgContent;
                }
            };
            xhr.send();
        },

        toggleSearchPopup: function(instance, button) {
            var existingPopup = instance.container.querySelector('.zato-ide-search-popup');
            if (existingPopup) {
                existingPopup.classList.toggle('open');
                return;
            }
            var popup = document.createElement('div');
            popup.className = 'zato-ide-search-popup open';
            popup.innerHTML = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.';
            var rect = button.getBoundingClientRect();
            popup.style.position = 'fixed';
            popup.style.top = (rect.bottom + 4) + 'px';
            popup.style.left = rect.left + 'px';
            instance.container.appendChild(popup);
        },

        initBottomPanel1: function(instance) {
            var self = this;
            var panelContainer = document.getElementById(instance.id + '-bottom-panel-1');
            var tabsContainer = document.getElementById(instance.id + '-bottom-panel-1-tabs');
            var contentContainer = document.getElementById(instance.id + '-bottom-panel-1-content');

            if (!panelContainer || !tabsContainer || !contentContainer) {
                return;
            }

            var savedCollapsed = localStorage.getItem('zato.ide.bottomPanel1Collapsed');
            if (savedCollapsed === 'true') {
                panelContainer.classList.add('collapsed');
            }

            instance.bottomPanel1TabsManager = ZatoTabsManager.create(instance.id + '-bottom-panel-1-tabs', {
                theme: 'dark',
                onTabChange: function(tab) {
                    self.updateBottomPanel1Content(instance, tab);
                }
            });

            var defaultTabs = [
                { id: 'tab-1', title: 'Tab 1' },
                { id: 'tab-2', title: 'Tab 2' },
                { id: 'tab-3', title: 'Tab 3' }
            ];

            instance.bottomPanel1TabsManager.tabs = defaultTabs;
            instance.bottomPanel1TabsManager.activeTabId = 'tab-1';
            instance.bottomPanel1TabsManager.allowCloseLastTab = false;

            ZatoTabsRenderer.render(instance.bottomPanel1TabsManager, tabsContainer, {
                theme: 'dark',
                showAddButton: true,
                showCloseButton: true,
                showPinIcon: false,
                showLockIcon: false
            });

            ZatoTabsEvents.bind(tabsContainer, instance.bottomPanel1TabsManager, {
                onTabChange: function(tab) {
                    self.updateBottomPanel1Content(instance, tab);
                    self.renderBottomPanel1Tabs(instance);
                },
                onSave: function() {},
                onRender: function() {
                    self.renderBottomPanel1Tabs(instance);
                }
            });

            this.updateBottomPanel1Content(instance, defaultTabs[0]);
            this.initBottomPanel1Resizer(instance);
        },

        initBottomPanel1Resizer: function(instance) {
            var self = this;
            var resizer = document.getElementById(instance.id + '-bottom-panel-1-resizer');
            var panelContainer = document.getElementById(instance.id + '-bottom-panel-1');

            if (!resizer || !panelContainer) {
                return;
            }

            var savedHeight = localStorage.getItem('zato.ide.bottomPanel1Height');
            if (savedHeight) {
                panelContainer.style.height = savedHeight + 'px';
            }

            var isDragging = false;
            var startY = 0;
            var startHeight = 0;

            resizer.addEventListener('mousedown', function(e) {
                if (panelContainer.classList.contains('collapsed')) {
                    return;
                }
                e.preventDefault();
                isDragging = true;
                startY = e.clientY;
                startHeight = panelContainer.offsetHeight;
                resizer.classList.add('dragging');
                document.body.style.cursor = 'row-resize';
                document.body.style.userSelect = 'none';
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) {
                    return;
                }

                var deltaY = startY - e.clientY;
                var newHeight = startHeight + deltaY;

                var minHeight = 100;
                var maxHeight = 500;

                if (newHeight < minHeight) {
                    newHeight = minHeight;
                }
                if (newHeight > maxHeight) {
                    newHeight = maxHeight;
                }

                panelContainer.style.height = newHeight + 'px';

                var sidePanelContent = document.getElementById(instance.id + '-side-panel-1-content');
                var debuggerPanels = sidePanelContent ? sidePanelContent.querySelector('.zato-debugger-panels') : null;
                var debuggerConsole = sidePanelContent ? sidePanelContent.querySelector('.zato-debugger-console') : null;
                var consoleOutput = debuggerConsole ? debuggerConsole.querySelector('.zato-debugger-console-output') : null;

                console.log('[BottomPanel1Resizer] mousemove:');
                console.log('  sidePanelContent:', sidePanelContent ? 'found' : 'n/a');
                console.log('  sidePanelContent height:', sidePanelContent ? sidePanelContent.offsetHeight : 'n/a');
                console.log('  sidePanelContent overflow-y:', sidePanelContent ? getComputedStyle(sidePanelContent).overflowY : 'n/a');
                console.log('  debuggerPanels:', debuggerPanels ? 'found' : 'n/a');
                console.log('  debuggerPanels height:', debuggerPanels ? debuggerPanels.offsetHeight : 'n/a');
                console.log('  debuggerPanels scrollHeight:', debuggerPanels ? debuggerPanels.scrollHeight : 'n/a');
                console.log('  debuggerPanels overflow-y:', debuggerPanels ? getComputedStyle(debuggerPanels).overflowY : 'n/a');
                console.log('  debuggerConsole:', debuggerConsole ? 'found' : 'n/a');
                console.log('  debuggerConsole height:', debuggerConsole ? debuggerConsole.offsetHeight : 'n/a');
                console.log('  debuggerConsole overflow-y:', debuggerConsole ? getComputedStyle(debuggerConsole).overflowY : 'n/a');
                console.log('  consoleOutput:', consoleOutput ? 'found' : 'n/a');
                console.log('  consoleOutput height:', consoleOutput ? consoleOutput.offsetHeight : 'n/a');
                console.log('  consoleOutput overflow-y:', consoleOutput ? getComputedStyle(consoleOutput).overflowY : 'n/a');

                var allPanels = sidePanelContent ? sidePanelContent.querySelectorAll('.zato-debugger-panel') : [];
                console.log('  allPanels count:', allPanels.length);
                for (var i = 0; i < allPanels.length; i++) {
                    var panel = allPanels[i];
                    var panelTitle = panel.querySelector('.zato-debugger-panel-title');
                    var panelContent = panel.querySelector('.zato-debugger-panel-content');
                    console.log('  panel[' + i + '] title:', panelTitle ? panelTitle.textContent : 'n/a');
                    console.log('  panel[' + i + '] height:', panel.offsetHeight);
                    console.log('  panel[' + i + '] overflow-y:', getComputedStyle(panel).overflowY);
                    if (panelContent) {
                        console.log('  panel[' + i + '] content height:', panelContent.offsetHeight);
                        console.log('  panel[' + i + '] content scrollHeight:', panelContent.scrollHeight);
                        console.log('  panel[' + i + '] content overflow-y:', getComputedStyle(panelContent).overflowY);
                    }
                }

                if (instance.codeEditor && instance.codeEditor.aceEditor) {
                    instance.codeEditor.aceEditor.resize();
                }
            });

            var sidePanelContentForScroll = document.getElementById(instance.id + '-side-panel-1-content');
            if (sidePanelContentForScroll) {
                var scrollableElements = sidePanelContentForScroll.querySelectorAll('*');
                for (var j = 0; j < scrollableElements.length; j++) {
                    (function(elem) {
                        elem.addEventListener('scroll', function() {
                            var classes = elem.className || '';
                            var id = elem.id || '';
                            console.log('[Scroll] element scrolled: id=' + id + ' class=' + classes);
                            console.log('[Scroll] scrollTop=' + elem.scrollTop + ' scrollHeight=' + elem.scrollHeight + ' clientHeight=' + elem.clientHeight);
                        });
                    })(scrollableElements[j]);
                }
                sidePanelContentForScroll.addEventListener('scroll', function() {
                    console.log('[Scroll] sidePanelContent scrolled: scrollTop=' + sidePanelContentForScroll.scrollTop);
                });
            }

            document.addEventListener('mouseup', function() {
                if (isDragging) {
                    isDragging = false;
                    resizer.classList.remove('dragging');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';

                    var currentHeight = panelContainer.offsetHeight;
                    localStorage.setItem('zato.ide.bottomPanel1Height', currentHeight);

                    if (instance.codeEditor && instance.codeEditor.aceEditor) {
                        instance.codeEditor.aceEditor.resize();
                    }
                }
            });
        },

        renderBottomPanel1Tabs: function(instance) {
            var tabsContainer = document.getElementById(instance.id + '-bottom-panel-1-tabs');
            if (!tabsContainer || !instance.bottomPanel1TabsManager) {
                return;
            }
            ZatoTabsRenderer.render(instance.bottomPanel1TabsManager, tabsContainer, {
                theme: 'dark',
                showAddButton: true,
                showCloseButton: true,
                showPinIcon: false,
                showLockIcon: false
            });
            ZatoTabsEvents.bind(tabsContainer, instance.bottomPanel1TabsManager, {
                onTabChange: function(tab) {
                    ZatoIDEPanels.updateBottomPanel1Content(instance, tab);
                    ZatoIDEPanels.renderBottomPanel1Tabs(instance);
                },
                onSave: function() {},
                onRender: function() {
                    ZatoIDEPanels.renderBottomPanel1Tabs(instance);
                }
            });
        },

        updateBottomPanel1Content: function(instance, tab) {
            var contentContainer = document.getElementById(instance.id + '-bottom-panel-1-content');
            if (!contentContainer || !tab) {
                return;
            }
            contentContainer.innerHTML = '<div class="zato-ide-bottom-panel-1-tab-name">' + tab.title + '</div>';
        },

        toggleBottomPanel1: function(instance) {
            var panelContainer = document.getElementById(instance.id + '-bottom-panel-1');
            if (!panelContainer) {
                return;
            }

            if (panelContainer.classList.contains('collapsed')) {
                panelContainer.classList.remove('collapsed');
                localStorage.setItem('zato.ide.bottomPanel1Collapsed', 'false');
            } else {
                panelContainer.classList.add('collapsed');
                localStorage.setItem('zato.ide.bottomPanel1Collapsed', 'true');
            }

            if (instance.codeEditor && instance.codeEditor.aceEditor) {
                instance.codeEditor.aceEditor.resize();
            }
        }
    };

    window.ZatoIDEPanels = ZatoIDEPanels;

})();
