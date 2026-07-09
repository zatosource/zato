
// Mapper kit - the schema panel.
// One controller per side (source or target): pasting a JSON example,
// pasting a JSON Schema, saving and loading named schemas, scaffolding
// a sample and rendering the schema tree or a designed empty state.

(function($) {

    zato.mapper.schemaPanel = {};

// ////////////////////////////////////////////////////////////////////////

    var sideLabels = {source: 'source', target: 'target'};

// ////////////////////////////////////////////////////////////////////////

    // Initializes one schema column.
    // panelConfig:
    //   side:      'source' or 'target'
    //   store:     the artifact store instance
    //   body:      the column body element the tree renders into
    //   actions:   the element holding the column's action buttons
    //   sampleCountBadge: the element showing how many samples this side has
    zato.mapper.schemaPanel.init = function(panelConfig) {

        var side = panelConfig.side;
        var store = panelConfig.store;
        var body = panelConfig.body;

        function schemaRoot() {
            var out = store.getArtifact()[side + '_schema'].root;
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function sampleCount() {

            var samples = store.getArtifact().samples;

            var out = 0;
            for (var sampleIdx = 0; sampleIdx < samples.length; sampleIdx++) {
                if (samples[sampleIdx].side === side) {
                    out += 1;
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function nextSampleName(prefix) {
            var count = sampleCount();

            var out = sideLabels[side] + '-' + prefix + '-' + (count + 1);
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderEmptyState() {

            var wrapper = document.createElement('div');
            wrapper.className = 'mapper-empty-state';

            var title = document.createElement('h3');
            title.className = 'mapper-empty-state-title';
            title.textContent = 'No ' + sideLabels[side] + ' schema yet';
            wrapper.appendChild(title);

            var text = document.createElement('p');
            text.className = 'mapper-empty-state-text';
            text.textContent = 'Paste a JSON example to infer the schema from it, ' +
                'paste a JSON Schema document, or pick a schema saved in this browser.';
            wrapper.appendChild(text);

            $(body).empty();
            body.appendChild(wrapper);
        }

// ////////////////////////////////////////////////////////////////////////

        function render() {

            var root = schemaRoot();

            if (root === null) {
                renderEmptyState();
            }
            else {
                zato.mapper.tree.render(body, root);
            }

            $(panelConfig.sampleCountBadge).text(sampleCount());
        }

// ////////////////////////////////////////////////////////////////////////

        // Pasted text is an external boundary, so it is parsed explicitly
        // and a parse failure becomes a dialog error, never an exception.
        function parsePastedJSON(text) {
            try {
                var out = {value: JSON.parse(text), error: ''};
                return out;
            } catch(error) {
                var failed = {value: null, error: 'Not valid JSON: ' + error.message};
                return failed;
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function openPasteExampleDialog() {
            zato.mapper.dialog.open({
                title: 'Paste a JSON example - ' + sideLabels[side],
                withTextarea: true,
                okLabel: 'Infer schema',
                onSubmit: function(result) {

                    var parsed = parsePastedJSON(result.text);
                    if (parsed.error) {
                        return parsed.error;
                    }

                    // Infer the tree from the example ..
                    var root = zato.mapper.schema.inferFromExample(parsed.value);

                    // .. an existing schema is refined, never replaced outright,
                    // so a second sample makes missing fields optional ..
                    var current = schemaRoot();
                    if (current !== null) {
                        zato.mapper.log('schema-panel', 'refining the existing schema with the pasted example', {side: side});
                        root = zato.mapper.schema.mergeNodes(current, root);
                    }

                    store.setSchemaRoot(side, root);

                    // .. and the example itself becomes a stored sample, so the
                    // tree and the preview are always fed by the same data.
                    store.addSample({
                        name: nextSampleName('example'),
                        side: side,
                        payload: parsed.value
                    });
                }
            });
        }

// ////////////////////////////////////////////////////////////////////////

        function openPasteJSONSchemaDialog() {
            zato.mapper.dialog.open({
                title: 'Paste a JSON Schema - ' + sideLabels[side],
                withTextarea: true,
                okLabel: 'Import schema',
                onSubmit: function(result) {

                    var parsed = parsePastedJSON(result.text);
                    if (parsed.error) {
                        return parsed.error;
                    }

                    var converted = zato.mapper.schema.fromJSONSchema(parsed.value);
                    store.setSchemaRoot(side, converted.root);

                    // Unsupported keywords are listed in a notice, never dropped silently.
                    if (converted.unsupported.length > 0) {
                        var lines = [];
                        for (var itemIdx = 0; itemIdx < converted.unsupported.length; itemIdx++) {
                            var item = converted.unsupported[itemIdx];
                            lines.push(item.keyword + ' at ' + item.path);
                        }
                        showNotice('Keywords outside the supported subset were ignored: ' + lines.join(', '));
                    }
                }
            });
        }

// ////////////////////////////////////////////////////////////////////////

        function openSaveNamedDialog() {
            zato.mapper.dialog.open({
                title: 'Save schema under a name - ' + sideLabels[side],
                withInput: true,
                inputLabel: 'Schema name',
                okLabel: 'Save schema',
                onSubmit: function(result) {

                    if (result.value === '') {
                        return 'A name is required';
                    }

                    var root = schemaRoot();
                    zato.mapper.schema.named.save(result.value, root);
                }
            });
        }

// ////////////////////////////////////////////////////////////////////////

        function openLoadNamedDialog() {

            var names = zato.mapper.schema.named.list();
            if (names.length === 0) {
                showNotice('No schemas are saved in this browser yet');
                return;
            }

            zato.mapper.dialog.open({
                title: 'Load a named schema - ' + sideLabels[side],
                withInput: true,
                inputLabel: 'Schema name (' + names.join(', ') + ')',
                okLabel: 'Load schema',
                onSubmit: function(result) {

                    var root = zato.mapper.schema.named.get(result.value);
                    if (!root) {
                        return 'No schema is saved under `' + result.value + '`';
                    }

                    store.setSchemaRoot(side, root);
                }
            });
        }

// ////////////////////////////////////////////////////////////////////////

        function scaffoldSample() {

            var root = schemaRoot();
            var payload = zato.mapper.schema.scaffold(root);

            // A new scaffold is always a new sample - user edits to
            // existing samples are never overwritten.
            store.addSample({
                name: nextSampleName('scaffold'),
                side: side,
                payload: payload
            });
        }

// ////////////////////////////////////////////////////////////////////////

        function showNotice(text) {
            var notice = $(panelConfig.notice);
            notice.text(text);
            notice.prop('hidden', false);
        }

// ////////////////////////////////////////////////////////////////////////

        function buildActionButton(label, cssClass, onClick) {
            var button = document.createElement('button');
            button.className = 'mapper-button zato-action-button ' + cssClass;
            button.type = 'button';
            button.textContent = label;
            $(button).on('click', onClick);
            panelConfig.actions.appendChild(button);
            return button;
        }

        buildActionButton('Paste example', 'mapper-action-paste-example', openPasteExampleDialog);
        buildActionButton('Paste JSON Schema', 'mapper-action-paste-json-schema', openPasteJSONSchemaDialog);
        buildActionButton('Re-import', 'mapper-action-reimport', function() {
            zato.mapper.reimport.openDialog({store: store, side: side});
        });
        buildActionButton('Save as named', 'mapper-action-save-named', openSaveNamedDialog);
        buildActionButton('Load named', 'mapper-action-load-named', openLoadNamedDialog);
        var scaffoldButton = buildActionButton('Scaffold sample', 'mapper-action-scaffold', scaffoldSample);

        // Actions that need a schema are disabled until one exists.
        function refreshActionStates() {
            var hasSchema = schemaRoot() !== null;
            $(panelConfig.actions).find('.mapper-action-save-named').prop('disabled', !hasSchema);
            $(scaffoldButton).prop('disabled', !hasSchema);
        }

        store.subscribe(function() {
            render();
            refreshActionStates();
        });

        render();
        refreshActionStates();
    };

})(jQuery);
