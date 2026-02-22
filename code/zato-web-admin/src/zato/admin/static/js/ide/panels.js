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
                contentContainer.innerHTML = '';
                if (viewId === 'explorer') {
                    self.initExplorer(instance, contentContainer);
                } else if (viewId === 'debugger') {
                    self.initDebuggerPanel(instance, contentContainer);
                }
            }
        },

        initDebuggerPanel: function(instance, container) {
            if (typeof ZatoDebuggerIDE === 'undefined') { return; }
            var debuggerIDE = ZatoDebuggerIDE.getInstanceForIDE(instance);
            if (!debuggerIDE) {
                debuggerIDE = ZatoDebuggerIDE.create(instance, {});
            }
            var debuggerDiv = document.createElement('div');
            debuggerDiv.id = instance.id + '-debugger-panel';
            debuggerDiv.className = 'zato-ide-debugger-panel';
            container.appendChild(debuggerDiv);
            ZatoDebuggerIDE.showDebugPanelInContainer(debuggerIDE, debuggerDiv.id);
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
        }
    };

    window.ZatoIDEPanels = ZatoIDEPanels;

})();
