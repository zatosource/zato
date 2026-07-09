
// Mapper kit - the mapping detail panel.
// Opens when a mapping row is selected: the target field, the expression
// in either the raw editor or the builder, an optional condition, the
// default value, the omit-if-empty toggle, a comment and the row's
// evaluated value against the active sample. Edits preview instantly
// and commit to the store when the field loses focus.

(function($) {

    zato.mapper.detailPanel = {};

// ////////////////////////////////////////////////////////////////////////

    // Initializes the panel.
    // panelConfig:
    //   store:            the artifact store
    //   panel:            the panel element, hidden while nothing is selected
    //   preview:          the preview controller, for pending-edit previews
    //   getElementIndex:  function(scopeIndex) - the previewed element index
    // Returns {setSelection, setResults}.
    zato.mapper.detailPanel.init = function(panelConfig) {

        var store = panelConfig.store;
        var panel = panelConfig.panel;

        var selection = null;
        var pendingRow = null;
        var results = null;
        var mode = 'raw';

        var targetInput = document.getElementById('mapper-detail-target');
        var targetPaths = document.getElementById('mapper-detail-target-paths');
        var rawButton = document.getElementById('mapper-detail-mode-raw');
        var builderButton = document.getElementById('mapper-detail-mode-builder');
        var builderContainer = document.getElementById('mapper-detail-builder');
        var expressionContainer = document.getElementById('mapper-detail-expression');
        var conditionContainer = document.getElementById('mapper-detail-condition');
        var defaultInput = document.getElementById('mapper-detail-default');
        var omitInput = document.getElementById('mapper-detail-omit');
        var commentInput = document.getElementById('mapper-detail-comment');
        var valueDisplay = document.getElementById('mapper-detail-value');

// ////////////////////////////////////////////////////////////////////////

        function sourcePaths() {

            var out = zato.mapper.schema.listPaths(store.getArtifact().source_schema.root);
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // Autocomplete offers the source schema paths first, then the
        // function reference grouped under its category headers.
        function completions() {

            var out = [];

            var paths = sourcePaths();
            for (var pathIdx = 0; pathIdx < paths.length; pathIdx++) {
                out.push({label: paths[pathIdx], doc: '', category: ''});
            }

            var categories = zato.mapper.config.functionCategories;
            var reference = zato.mapper.config.functionReference;

            for (var categoryIdx = 0; categoryIdx < categories.length; categoryIdx++) {
                var category = categories[categoryIdx];

                for (var functionIdx = 0; functionIdx < reference.length; functionIdx++) {
                    var item = reference[functionIdx];
                    if (item.category === category.name) {
                        out.push({label: item.name, doc: item.doc, category: category.label});
                    }
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function selectedRow() {

            var artifact = store.getArtifact();

            if (selection.scopeIndex === null) {
                var out = artifact.mappings[selection.rowIndex];
                return out;
            }

            var scope = artifact.scopes[selection.scopeIndex];
            var childOut = scope.mappings[selection.rowIndex];
            return childOut;
        }

// ////////////////////////////////////////////////////////////////////////

        function commit() {

            if (selection === null) {
                return;
            }

            // An unchanged row is not an edit - committing it anyway would
            // grow the undo stack on every focus change.
            if (JSON.stringify(pendingRow) === JSON.stringify(selectedRow())) {
                return;
            }

            zato.mapper.log('detail-panel', 'committing the edited row', {selection: selection, row: pendingRow});

            if (selection.scopeIndex === null) {
                store.updateMapping(selection.rowIndex, pendingRow);
            }
            else {
                store.updateScopeMapping(selection.scopeIndex, selection.rowIndex, pendingRow);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        // A keystroke previews the pending row without committing it,
        // so the output pane follows as the user types.
        function previewPending() {
            panelConfig.preview.setPending(selection, pendingRow);
        }

// ////////////////////////////////////////////////////////////////////////

        function expressionErrors(text) {

            var out = [];

            if (text !== '') {
                try {
                    jsonata(text);
                } catch(error) {
                    out.push({line: 1, message: error.message});
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        var expressionEditor = zato.mapper.overlayEditor.create({
            container: expressionContainer,
            language: 'expression',
            value: '',
            ariaLabel: 'Mapping expression',
            completions: completions,
            onChange: function(text) {
                pendingRow.expression = text;
                expressionEditor.setErrors(expressionErrors(text));
                previewPending();
            }
        });

        var conditionEditor = zato.mapper.overlayEditor.create({
            container: conditionContainer,
            language: 'expression',
            value: '',
            ariaLabel: 'Mapping condition',
            completions: completions,
            onChange: function(text) {
                pendingRow.condition = text;
                conditionEditor.setErrors(expressionErrors(text));
                previewPending();
            }
        });

        var builder = zato.mapper.builder.create({
            container: builderContainer,
            paths: sourcePaths,
            onChange: function(text) {

                // A chip action is a discrete edit, so it commits right away.
                pendingRow.expression = text;
                expressionEditor.setValue(text);
                expressionEditor.setErrors(expressionErrors(text));
                commit();
            }
        });

// ////////////////////////////////////////////////////////////////////////

        function showRawMode() {
            $(rawButton).addClass('mapper-detail-mode-active');
            $(builderButton).removeClass('mapper-detail-mode-active');
            expressionContainer.hidden = false;
            builderContainer.hidden = true;
        }

        function showBuilderMode() {
            $(builderButton).addClass('mapper-detail-mode-active');
            $(rawButton).removeClass('mapper-detail-mode-active');
            expressionContainer.hidden = true;
            builderContainer.hidden = false;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderTargetPaths() {

            $(targetPaths).empty();

            var paths = zato.mapper.schema.listPaths(store.getArtifact().target_schema.root);
            for (var pathIdx = 0; pathIdx < paths.length; pathIdx++) {
                var option = document.createElement('option');
                option.value = paths[pathIdx];
                targetPaths.appendChild(option);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function formatDefault(value) {

            if (value === null) {
                return '';
            }

            var out = JSON.stringify(value);
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderValue() {

            if (selection === null || results === null) {
                valueDisplay.textContent = '';
                return;
            }

            // The results may lag one change behind the artifact, so a
            // just-added row has no result until the next evaluator run.
            var result;
            if (selection.scopeIndex === null) {
                result = results.rows[selection.rowIndex];
            }
            else {
                var scopeResult = results.scopes[selection.scopeIndex];
                if (scopeResult === undefined || scopeResult.elements.length === 0) {
                    valueDisplay.textContent = '';
                    return;
                }
                var elementIdx = panelConfig.getElementIndex(selection.scopeIndex);
                result = scopeResult.elements[elementIdx][selection.rowIndex];
            }

            if (result === undefined) {
                valueDisplay.textContent = '';
            }
            else if (result.error !== '') {
                valueDisplay.textContent = result.error;
                valueDisplay.className = 'mapper-detail-value mapper-detail-value-error';
            }
            else if (result.skipped) {
                valueDisplay.textContent = 'skipped';
                valueDisplay.className = 'mapper-detail-value';
            }
            else {
                var text = JSON.stringify(result.value);
                if (text === undefined) {
                    text = zato.mapper.config.previewEmptyValueLabel;
                }
                valueDisplay.textContent = text;
                valueDisplay.className = 'mapper-detail-value';
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function render() {

            if (selection === null) {
                panel.hidden = true;
                return;
            }

            var row = selectedRow();
            pendingRow = {
                target: row.target,
                expression: row.expression,
                condition: row.condition,
                comment: row.comment,
                origin: row.origin,
                'default': row['default'],
                omit_if_empty: row.omit_if_empty
            };

            panel.hidden = false;

            targetInput.value = row.target;
            expressionEditor.setValue(row.expression);
            expressionEditor.setErrors(expressionErrors(row.expression));
            conditionEditor.setValue(row.condition);
            conditionEditor.setErrors(expressionErrors(row.condition));
            defaultInput.value = formatDefault(row['default']);
            omitInput.checked = row.omit_if_empty;
            commentInput.value = row.comment;

            renderTargetPaths();

            // The builder opens only for expressions it can represent -
            // an expression it cannot parse leaves the builder model as-is,
            // which keeps an in-progress build (say, a trailing operator)
            // on screen across commits.
            var canBuild = builder.setExpression(row.expression);
            builderButton.disabled = !canBuild;

            if (mode === 'builder') {
                showBuilderMode();
            }
            else {
                showRawMode();
            }

            renderValue();
        }

// ////////////////////////////////////////////////////////////////////////

        $(targetInput).on('change', function() {
            pendingRow.target = targetInput.value;
            commit();
        });

        $(expressionContainer).on('focusout', function() {
            commit();
        });

        $(conditionContainer).on('focusout', function() {
            commit();
        });

        $(defaultInput).on('change', function() {

            // An empty input means no default, valid JSON is taken as
            // typed and anything else becomes a plain string.
            if (defaultInput.value === '') {
                pendingRow['default'] = null;
            }
            else {
                try {
                    pendingRow['default'] = JSON.parse(defaultInput.value);
                } catch(error) {
                    pendingRow['default'] = defaultInput.value;
                }
            }

            commit();
        });

        $(omitInput).on('change', function() {
            pendingRow.omit_if_empty = omitInput.checked;
            commit();
        });

        $(commentInput).on('change', function() {
            pendingRow.comment = commentInput.value;
            commit();
        });

        $(rawButton).on('click', function() {
            mode = 'raw';
            showRawMode();
        });

        $(builderButton).on('click', function() {
            if (builderButton.disabled) {
                return;
            }

            // Loading the current text keeps the switch lossless.
            var canBuild = builder.setExpression(pendingRow.expression);
            if (canBuild) {
                mode = 'builder';
                showBuilderMode();
            }
        });

        store.subscribe(function() {

            if (selection === null) {
                return;
            }

            // The selected row may be gone after an undo or a removal.
            var artifact = store.getArtifact();
            if (selection.scopeIndex === null) {
                if (selection.rowIndex >= artifact.mappings.length) {
                    selection = null;
                }
            }
            else if (selection.scopeIndex >= artifact.scopes.length) {
                selection = null;
            }
            else if (selection.rowIndex >= artifact.scopes[selection.scopeIndex].mappings.length) {
                selection = null;
            }

            render();
        });

        return {

            setSelection: function(newSelection) {
                selection = newSelection;
                mode = 'raw';
                panelConfig.preview.clearPending();
                render();
            },

            setResults: function(newResults) {
                results = newResults;
                renderValue();
            }
        };
    };

})(jQuery);
