
// Mapper kit - page bootstrap.
// Wires the header, tabs, undo and redo, export and import and both
// schema panels to one artifact store. Loads last, after every other
// kit file.

(function($) {

    var config = zato.mapper.config;

// ////////////////////////////////////////////////////////////////////////

    function buildTabs() {

        var strip = document.getElementById('mapper-tabs');

        for (var tabIdx = 0; tabIdx < config.tabs.length; tabIdx++) {
            var tab = config.tabs[tabIdx];

            var button = document.createElement('button');
            button.className = 'mapper-tab dashboard-tab';
            button.type = 'button';
            button.setAttribute('data-tab', tab.name);
            button.setAttribute('role', 'tab');
            button.textContent = tab.label;

            strip.appendChild(button);
        }

        var out = zato.mapper.tabs.init({
            tabSelector: '.mapper-tab',
            panelPrefix: 'mapper-panel-',
            activeClass: config.tabActiveClass,
            storageKey: config.activeTabStorageKey,
            defaultTab: config.defaultTab
        });

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function wireHeader(store) {

        var nameInput = document.getElementById('mapper-name');
        var undoButton = document.getElementById('mapper-undo');
        var redoButton = document.getElementById('mapper-redo');
        var exportButton = document.getElementById('mapper-export');
        var importButton = document.getElementById('mapper-import');
        var importFile = document.getElementById('mapper-import-file');

        // The name input follows the store and the store follows the input.
        nameInput.value = store.getArtifact().name;

        $(nameInput).on('change', function() {
            store.setName(nameInput.value);
        });

        function refreshUndoRedo() {
            $(undoButton).prop('disabled', !store.canUndo());
            $(redoButton).prop('disabled', !store.canRedo());
        }

        store.subscribe(function(artifact) {

            // Refreshing the input while it is being edited would
            // fight the user, so only a non-focused input follows.
            if (document.activeElement !== nameInput) {
                nameInput.value = artifact.name;
            }

            refreshUndoRedo();
        });

        $(undoButton).on('click', function() {
            store.undo();
            refreshUndoRedo();
        });

        $(redoButton).on('click', function() {
            store.redo();
            refreshUndoRedo();
        });

        // Ctrl-Z and Ctrl-Shift-Z mirror the buttons. The hotkeys library
        // skips text inputs by default, so native editing undo still works.
        hotkeys('ctrl+z,command+z', function(event) {
            event.preventDefault();
            store.undo();
            refreshUndoRedo();
        });

        hotkeys('ctrl+shift+z,command+shift+z', function(event) {
            event.preventDefault();
            store.redo();
            refreshUndoRedo();
        });

        // Export downloads the artifact exactly as it serializes.
        $(exportButton).on('click', function() {

            var text = store.serialize();
            var blob = new Blob([text], {type: 'application/json'});
            var url = URL.createObjectURL(blob);

            var link = document.createElement('a');
            link.href = url;
            link.download = config.exportFileName;
            link.click();

            URL.revokeObjectURL(url);
        });

        // Import reads a .json file, validates it and replaces the artifact
        // only when the document is clean.
        $(importButton).on('click', function() {
            importFile.click();
        });

        $(importFile).on('change', function() {

            var file = importFile.files[0];
            var reader = new FileReader();

            reader.onload = function() {

                // An uploaded file is an external boundary, so parse errors
                // and validation errors both surface as a visible notice.
                var candidate = null;
                try {
                    candidate = JSON.parse(reader.result);
                } catch(error) {
                    showPageNotice('The file is not valid JSON: ' + error.message);
                    return;
                }

                var records = store.loadArtifact(candidate);
                if (records.length > 0) {
                    var lines = [];
                    for (var recordIdx = 0; recordIdx < records.length; recordIdx++) {
                        lines.push(records[recordIdx].path + ': ' + records[recordIdx].message);
                    }
                    showPageNotice('The file is not a valid mapping: ' + lines.join(', '));
                }
            };

            reader.readAsText(file);
            importFile.value = '';
        });

        refreshUndoRedo();
    }

// ////////////////////////////////////////////////////////////////////////

    var noticeTimer = null;

    function showPageNotice(text) {
        var notice = $('#mapper-page-notice');
        notice.text(text);
        notice.prop('hidden', false);

        // A notice explains one action, so it leaves on its own.
        if (noticeTimer !== null) {
            clearTimeout(noticeTimer);
        }
        noticeTimer = setTimeout(function() {
            notice.prop('hidden', true);
        }, config.noticeAutoHideMs);
    }

// ////////////////////////////////////////////////////////////////////////

    function initSchemaPanels(store) {

        for (var sideIdx = 0; sideIdx < config.sides.length; sideIdx++) {
            var side = config.sides[sideIdx];

            zato.mapper.schemaPanel.init({
                side: side,
                store: store,
                body: document.getElementById('mapper-schema-body-' + side),
                actions: document.getElementById('mapper-schema-actions-' + side),
                sampleCountBadge: document.getElementById('mapper-sample-count-' + side),
                notice: document.getElementById('mapper-schema-notice-' + side)
            });
        }
    }

// ////////////////////////////////////////////////////////////////////////

    // A brand-new browser (no autosaved artifact at all) starts with the
    // default examples on both sides, so the page is never blank. The
    // seeded artifact is written straight into browser storage before the
    // store starts, so it restores like any other autosave and leaves the
    // undo stack empty.
    function seedDefaultArtifact() {

        var saved = window.store.get(config.artifactStorageKey);
        if (saved) {
            return;
        }

        var artifact = zato.mapper.store.newArtifact();
        var examples = config.defaultExamples;

        artifact.source_schema.root = zato.mapper.schema.inferFromExample(examples.source.payload);
        artifact.target_schema.root = zato.mapper.schema.inferFromExample(examples.target.payload);

        artifact.samples.push({name: examples.source.name, side: 'source', payload: examples.source.payload});
        artifact.samples.push({name: examples.target.name, side: 'target', payload: examples.target.payload});

        window.store.set(config.artifactStorageKey, zato.mapper.store.serialize(artifact));
        zato.mapper.log('page', 'seeded the default examples', {source: examples.source.name, target: examples.target.name});
    }

// ////////////////////////////////////////////////////////////////////////

    $(function() {

        seedDefaultArtifact();

        var store = zato.mapper.store.create({storageKey: config.artifactStorageKey});

        // The store is exposed on the namespace so other kit files
        // and the browser console can reach it.
        zato.mapper.pageStore = store;

        buildTabs();
        wireHeader(store);
        initSchemaPanels(store);

        // The side Design-tab area is tabbed the same way the page is -
        // the mappings and their detail under one tab, the live preview
        // under the other.
        var sideTabs = zato.mapper.tabs.init({
            tabSelector: '.mapper-subtab',
            panelPrefix: 'mapper-side-panel-',
            activeClass: config.subtabActiveClass,
            storageKey: config.designSideTabStorageKey,
            defaultTab: config.designSideDefaultTab
        });

        zato.mapper.resizer.init({
            container: document.querySelector('.mapper-design-columns'),
            first: document.getElementById('mapper-schema-column-source'),
            handles: [
                document.getElementById('mapper-resize-edge-source'),
                document.getElementById('mapper-resize-edge-target')
            ],
            storageKey: config.designSplitStorageKey,
            defaultPercent: config.splitDefaultPercent,
            axis: 'x'
        });

        // The divider between the maps area and the side area.
        zato.mapper.resizer.init({
            container: document.querySelector('.mapper-design-areas'),
            first: document.getElementById('mapper-design-maps'),
            handles: [
                document.getElementById('mapper-design-split')
            ],
            storageKey: config.designSideSplitStorageKey,
            defaultPercent: config.designSideSplitDefaultPercent,
            axis: 'x'
        });

        // The divider between the preview's input and output panes.
        zato.mapper.resizer.init({
            container: document.querySelector('.mapper-preview'),
            first: document.querySelector('.mapper-preview .mapper-preview-pane'),
            handles: [
                document.getElementById('mapper-preview-split')
            ],
            storageKey: config.previewSplitStorageKey,
            defaultPercent: config.previewSplitDefaultPercent,
            axis: 'y'
        });

        // The preview, the mapping list and the detail panel all feed
        // each other: the preview evaluates, the list and the panel show
        // the per-row results, the panel's pending edits re-run the preview.
        var mappingList;
        var detailPanel;

        var preview = zato.mapper.preview.init({
            store: store,
            onResults: function(results) {
                mappingList.setResults(results);
                detailPanel.setResults(results);
            }
        });

        var canvas;

        mappingList = zato.mapper.mappingList.init({
            store: store,
            container: document.getElementById('mapper-mapping-list'),
            addButton: document.getElementById('mapper-add-mapping'),
            onSelect: function(selection) {
                detailPanel.setSelection(selection);
                canvas.redraw();
            }
        });

        detailPanel = zato.mapper.detailPanel.init({
            store: store,
            panel: document.getElementById('mapper-detail'),
            preview: preview,
            getElementIndex: function(scopeIndex) {
                var out = mappingList.getElementIndex(scopeIndex);
                return out;
            }
        });

        // The detail fields a line menu can ask the panel to focus.
        // Focusing never scrolls - the canvas the menu was used on
        // stays exactly where it was.
        var detailFieldFocusers = {
            expression: function() {
                document.querySelector('#mapper-detail-expression textarea').focus({preventScroll: true});
            },
            condition: function() {
                document.querySelector('#mapper-detail-condition textarea').focus({preventScroll: true});
            },
            'default': function() {
                document.getElementById('mapper-detail-default').focus({preventScroll: true});
            }
        };

        function openRow(selection, field) {

            // The row opens in the mappings, so they come forward
            // even when the preview was open.
            sideTabs.setTab('mappings');
            mappingList.select(selection);

            if (field !== '') {
                detailFieldFocusers[field]();
            }
        }

        canvas = zato.mapper.canvas.init({
            store: store,
            container: document.querySelector('.mapper-design-columns'),
            sourceColumn: document.getElementById('mapper-schema-column-source'),
            targetColumn: document.getElementById('mapper-schema-column-target'),
            sourceBody: document.getElementById('mapper-schema-body-source'),
            targetBody: document.getElementById('mapper-schema-body-target'),
            svg: document.getElementById('mapper-canvas-lines'),
            getSelected: function() {
                var out = mappingList.getSelected();
                return out;
            },
            onRowCreated: function(selection) {
                openRow(selection, '');
            },
            onRowOpen: openRow,
            onDeselect: function() {
                mappingList.deselect();
            },
            onNotice: showPageNotice,
            onStructureDrop: function(sourcePath, targetPath) {
                zato.mapper.automap.openReview({store: store, sourceScope: sourcePath, targetScope: targetPath});
            },
            onRenameField: function(side, path) {
                zato.mapper.refactor.openRenameDialog({store: store, side: side, path: path});
            }
        });

        // The search, the filters and the tree operations all move rows
        // around, so the lines redraw after each of them.
        zato.mapper.search.init({
            store: store,
            input: document.getElementById('mapper-search-input'),
            countDisplay: document.getElementById('mapper-search-count'),
            previousButton: document.getElementById('mapper-search-previous'),
            nextButton: document.getElementById('mapper-search-next'),
            filtersContainer: document.getElementById('mapper-tree-filters'),
            collapseAllButton: document.getElementById('mapper-collapse-all'),
            expandMappedButton: document.getElementById('mapper-expand-mapped'),
            sourceBody: document.getElementById('mapper-schema-body-source'),
            targetBody: document.getElementById('mapper-schema-body-target'),
            listContainer: document.getElementById('mapper-mapping-list'),
            onLayoutChanged: function() {
                canvas.redraw();
            }
        });

        // Auto-map over the whole schemas - the scoped variant lives on
        // the canvas, one structure dropped onto another.
        $('#mapper-automap').on('click', function() {
            zato.mapper.automap.openReview({store: store, sourceScope: '', targetScope: ''});
        });

        // Escape deselects the current row. An open context menu takes
        // the key first and closes instead.
        hotkeys('esc', function() {
            mappingList.deselect();
        });

        // Delete removes the selected row. The hotkeys library skips
        // text inputs, so editing a field never deletes anything.
        hotkeys('delete', function() {

            var selection = mappingList.getSelected();
            if (selection === null) {
                return;
            }

            zato.mapper.log('page', 'deleting the selected row', {selection: selection});

            mappingList.deselect();
            if (selection.scopeIndex === null) {
                store.removeMapping(selection.rowIndex);
            }
            else {
                store.removeScopeMapping(selection.scopeIndex, selection.rowIndex);
            }
        });

        // Delete all clears every row and scope after one confirmation.
        $('#mapper-delete-all-mappings').on('click', function() {

            zato.mapper.dialog.open({
                title: 'Delete all mappings?',
                okLabel: 'Delete all',
                onSubmit: function() {
                    mappingList.deselect();
                    store.clearMappings();
                }
            });
        });
    });

})(jQuery);
