(function() {
    'use strict';

    var ZatoIDELayout = {

        render: function(instance) {
            var themeClass = 'zato-ide-theme-' + instance.options.theme;
            var html = '';
            html += '<div class="zato-ide-container ' + themeClass + '">';
            html += '<div class="zato-ide-toolbar">';
            html += '<div class="zato-ide-toolbar-left">';
            html += '<select id="' + instance.id + '-symbol-select" class="zato-ide-symbol-select"><option value="">-- symbols --</option></select>';
            html += '<select id="' + instance.id + '-method-select" class="zato-ide-method-select" style="display: none;"><option value="">-- methods --</option></select>';
            html += '</div>';
            html += '<div class="zato-ide-toolbar-center">';
            html += '<div class="zato-ide-debug-container" id="' + instance.id + '-debug-container">';
            html += '<select class="zato-ide-debug-select zato-ide-symbol-select" id="' + instance.id + '-debug-select">';
            html += '<option value="">Debug</option>';
            html += '<option value="debug-file">Debug current file</option>';
            html += '<option value="connect-server">Connect to server</option>';
            html += '</select>';
            html += '</div>';
            html += '<span class="zato-ide-toolbar-separator"></span>';
            html += '<span class="zato-ide-search-button" title="Search"></span>';
            html += '</div></div>';
            html += '<div class="zato-ide-tabs-area"><div id="' + instance.id + '-tabs"></div></div>';
            html += '<div class="zato-ide-main-area" id="' + instance.id + '-main-split"></div>';
            html += '<div class="zato-ide-statusbar" id="' + instance.id + '-statusbar"></div>';
            html += '</div>';
            instance.container.innerHTML = html;

            console.log('[ZatoIDE] render: container set, initializing main split');
            ZatoIDEPanels.initMainSplit(instance);
            console.log('[ZatoIDE] render: main split initialized, initializing files');
            ZatoIDEEditorSetup.initFiles(instance);
            console.log('[ZatoIDE] render: files initialized, initializing code editor');
            ZatoIDEEditorSetup.initCodeEditor(instance);
            console.log('[ZatoIDE] render: code editor initialized');

            ZatoIDEDropdowns.initDropdowns(instance);

            console.log('[ZatoIDE] render: initializing tabs');
            ZatoIDETabs.initTabs(instance);

            ZatoIDEPanels.loadSearchIcon(instance);
            ZatoIDEPanels.loadSidePanel1Icons(instance);
            ZatoIDEPanels.initSidePanel1Content(instance);

            this.bindEvents(instance);

            var activeTab = ZatoIDEEditorSetup.getActiveTab(instance);
            if (activeTab && activeTab.title) {
                console.log('[ZatoIDE] render: switching to initial file ' + activeTab.title);
                ZatoIDEEditorSetup.switchToFile(instance, activeTab.title);
            }
            console.log('[ZatoIDE] render: complete');
        },

        bindEvents: function(instance) {
            var searchButton = instance.container.querySelector('.zato-ide-search-button');
            if (searchButton) {
                searchButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    ZatoIDEPanels.toggleSearchPopup(instance, searchButton);
                });
            }
            document.addEventListener('click', function(e) {
                var popup = instance.container.querySelector('.zato-ide-search-popup');
                if (popup && popup.classList.contains('open')) {
                    if (!popup.contains(e.target) && !searchButton.contains(e.target)) {
                        popup.classList.remove('open');
                    }
                }
            });
            window.addEventListener('beforeunload', function() {
                if (instance.activeFile && instance.codeEditor) {
                    var cursorPos = ZatoIDEEditorAce.getCursorPosition(instance.codeEditor);
                    instance.files[instance.activeFile].cursorLine = cursorPos.line;
                    instance.files[instance.activeFile].cursorCol = cursorPos.col;
                }
                ZatoIDETabs.saveTabsState(instance);
            });
        }
    };

    window.ZatoIDELayout = ZatoIDELayout;

})();
