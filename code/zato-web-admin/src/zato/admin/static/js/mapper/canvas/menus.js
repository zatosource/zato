
// Mapper kit - canvas line and field menus.
// A click selects the mapping row behind a line, a right-click opens
// a menu over it. Right-clicking a source field offers renaming it,
// right-clicking a target field offers wrapping its expression in a
// function or setting a constant value on an unmapped field.

(function($) {

    zato.mapper.canvas.menus = {};

// ////////////////////////////////////////////////////////////////////////

    // Turns the text typed into a set-value dialog into an expression
    // literal - numbers, booleans and null stay as typed, anything
    // else becomes a quoted string unless it is quoted already.
    function literalOf(text) {

        var out = text.trim();

        if (out === 'true' || out === 'false' || out === 'null') {
            return out;
        }
        if (/^-?\d+(\.\d+)?$/.test(out)) {
            return out;
        }
        if (/^".*"$/.test(out) || /^'.*'$/.test(out)) {
            return out;
        }

        out = '"' + out.replace(/"/g, '\\"') + '"';
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.canvas.menus.setup = function(shared) {

        var canvasConfig = shared.config;
        var container = shared.container;
        var store = shared.store;

// ////////////////////////////////////////////////////////////////////////
// Source field menus - renaming a field, which propagates into every
// referencing expression with a review list.
// ////////////////////////////////////////////////////////////////////////

        $(canvasConfig.sourceBody).on('contextmenu', '.mapper-tree-row', function(event) {

            var sourcePath = this.closest('.mapper-tree-item').getAttribute('data-path');

            event.preventDefault();

            zato.mapper.contextMenu.open({
                x: event.clientX,
                y: event.clientY,
                items: [
                    {label: 'Rename field', onSelect: function() {
                        canvasConfig.onRenameField('source', sourcePath);
                    }}
                ]
            });
        });

// ////////////////////////////////////////////////////////////////////////
// Line interactions - a click selects the mapping row behind a line,
// a right-click opens a menu over it.
// ////////////////////////////////////////////////////////////////////////

        // The row-backed line under the pointer, or null - scope lines
        // connect two lists rather than one row, so they take no clicks.
        function lineSelectionAt(clientX, clientY) {

            var containerRect = container.getBoundingClientRect();
            var lineId = shared.nearestLineId(clientX - containerRect.left, clientY - containerRect.top);
            if (lineId === null) {
                return null;
            }

            var out = shared.connectionOfLineId(lineId).selection;
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The row behind a selection, read from the current artifact.
        function rowOf(selection) {

            var artifact = store.getArtifact();

            if (selection.scopeIndex === null) {
                var out = artifact.mappings[selection.rowIndex];
                return out;
            }

            var childOut = artifact.scopes[selection.scopeIndex].mappings[selection.rowIndex];
            return childOut;
        }

// ////////////////////////////////////////////////////////////////////////

        function removeRow(selection) {

            zato.mapper.log('canvas', 'removing a mapping row', {selection: selection});

            // The selection points at the row about to go, so it clears first.
            canvasConfig.onDeselect();

            if (selection.scopeIndex === null) {
                store.removeMapping(selection.rowIndex);
            }
            else {
                store.removeScopeMapping(selection.scopeIndex, selection.rowIndex);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        $(container).on('click', function(event) {

            if (!shared.isInGutter(event.clientX)) {
                return;
            }

            var selection = lineSelectionAt(event.clientX, event.clientY);

            // Empty gutter space deselects, a line selects its row.
            if (selection === null) {
                canvasConfig.onDeselect();
                return;
            }

            zato.mapper.log('canvas', 'line clicked', {selection: selection});
            canvasConfig.onRowOpen(selection, '');
        });

// ////////////////////////////////////////////////////////////////////////

        $(container).on('contextmenu', function(event) {

            if (!shared.isInGutter(event.clientX)) {
                return;
            }

            var selection = lineSelectionAt(event.clientX, event.clientY);
            if (selection === null) {
                return;
            }

            event.preventDefault();

            zato.mapper.contextMenu.open({
                x: event.clientX,
                y: event.clientY,
                items: [
                    {label: 'Edit', onSelect: function() {
                        canvasConfig.onRowOpen(selection, 'expression');
                    }},
                    {label: 'Add condition', onSelect: function() {
                        canvasConfig.onRowOpen(selection, 'condition');
                    }},
                    {label: 'Set default', onSelect: function() {
                        canvasConfig.onRowOpen(selection, 'default');
                    }},
                    {label: 'Delete', onSelect: function() {
                        removeRow(selection);
                    }}
                ]
            });
        });

// ////////////////////////////////////////////////////////////////////////
// Target field menus - wrapping a mapped field's expression in a
// function, or setting a constant value on an unmapped one.
// ////////////////////////////////////////////////////////////////////////

        // The grouped function entries of the second-level menu.
        function functionMenuItems(onFunction) {

            var out = [];
            var categories = zato.mapper.config.functionCategories;
            var reference = zato.mapper.config.functionReference;

            for (var categoryIdx = 0; categoryIdx < categories.length; categoryIdx++) {
                var category = categories[categoryIdx];
                out.push({header: category.label});

                for (var functionIdx = 0; functionIdx < reference.length; functionIdx++) {
                    var item = reference[functionIdx];
                    if (item.category !== category.name) {
                        continue;
                    }

                    // The name is captured per entry, the handler shared.
                    out.push({label: item.name, onSelect: onFunction.bind(null, item.name)});
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function wrapRowInFunction(selection, functionName) {

            var row = rowOf(selection);

            var updated = zato.mapper.store.newMapping();
            updated.target = row.target;
            updated.expression = functionName + '(' + row.expression + ')';
            updated.condition = row.condition;
            updated.comment = row.comment;
            updated.origin = row.origin;
            updated['default'] = row['default'];
            updated.omit_if_empty = row.omit_if_empty;

            zato.mapper.log('canvas', 'wrapping an expression in a function', {selection: selection, expression: updated.expression});

            if (selection.scopeIndex === null) {
                store.updateMapping(selection.rowIndex, updated);
            }
            else {
                store.updateScopeMapping(selection.scopeIndex, selection.rowIndex, updated);
            }

            canvasConfig.onRowOpen(selection, '');
        }

// ////////////////////////////////////////////////////////////////////////

        // Creates a constant mapping onto an unmapped target field -
        // inside the matching scope when the field repeats per element.
        function setValueOn(targetPath, value) {

            var artifact = store.getArtifact();
            var targetArray = zato.mapper.schema.nearestArrayAncestor(artifact.target_schema.root, targetPath);

            if (targetArray === '') {
                store.addMapping(shared.newDragRow(targetPath, literalOf(value)));
                canvasConfig.onRowCreated({scopeIndex: null, rowIndex: store.getArtifact().mappings.length - 1});
                return '';
            }

            // A repeating field needs its list mapped first, so the
            // constant has a scope to live in.
            var scopeIdx = -1;
            for (var candidateIdx = 0; candidateIdx < artifact.scopes.length; candidateIdx++) {
                if (artifact.scopes[candidateIdx].target === targetArray) {
                    scopeIdx = candidateIdx;
                    break;
                }
            }
            if (scopeIdx === -1) {
                return '`' + targetPath + '` repeats per element of `' + targetArray + '` - map the list itself first.';
            }

            var relativeTarget = targetPath.substring(targetArray.length + 1);
            store.addScopeMapping(scopeIdx, shared.newDragRow(relativeTarget, literalOf(value)));

            canvasConfig.onRowCreated({scopeIndex: scopeIdx, rowIndex: store.getArtifact().scopes[scopeIdx].mappings.length - 1});
            return '';
        }

// ////////////////////////////////////////////////////////////////////////

        function openSetValueDialog(targetPath) {

            zato.mapper.dialog.open({
                title: 'Set a value for ' + targetPath,
                withInput: true,
                inputLabel: 'Value',
                okLabel: 'Set value',
                onSubmit: function(data) {

                    if (data.value.trim() === '') {
                        return 'Enter a value';
                    }

                    zato.mapper.log('canvas', 'setting a constant value', {target: targetPath, value: data.value});

                    var errorText = setValueOn(targetPath, data.value);
                    if (errorText !== '') {
                        return errorText;
                    }
                }
            });
        }

// ////////////////////////////////////////////////////////////////////////

        $(canvasConfig.targetBody).on('contextmenu', '.mapper-tree-row', function(event) {

            var targetPath = this.closest('.mapper-tree-item').getAttribute('data-path');

            // Every target field can be renamed, whatever else its menu offers.
            var renameItem = {label: 'Rename field', onSelect: function() {
                canvasConfig.onRenameField('target', targetPath);
            }};

            // A field mapped by a row offers wrapping that row's expression.
            var rowConnection = null;
            for (var connectionIdx = 0; connectionIdx < shared.lastConnections.length; connectionIdx++) {
                var connection = shared.lastConnections[connectionIdx];
                if (connection.target === targetPath && connection.selection !== null) {
                    rowConnection = connection;
                    break;
                }
            }

            if (rowConnection !== null) {
                event.preventDefault();

                var selection = rowConnection.selection;
                zato.mapper.contextMenu.open({
                    x: event.clientX,
                    y: event.clientY,
                    items: [
                        {label: 'Wrap in function', onSelect: function() {
                            zato.mapper.contextMenu.open({
                                x: event.clientX,
                                y: event.clientY,
                                items: functionMenuItems(function(functionName) {
                                    wrapRowInFunction(selection, functionName);
                                })
                            });
                        }},
                        renameItem
                    ]
                });
                return;
            }

            event.preventDefault();

            // An unmapped plain field offers a constant value on top
            // of the rename every field has.
            var artifact = store.getArtifact();
            var targetNode = zato.mapper.schema.nodeAtPath(artifact.target_schema.root, targetPath);

            var mappedElsewhere = false;
            for (var otherIdx = 0; otherIdx < shared.lastConnections.length; otherIdx++) {
                if (shared.lastConnections[otherIdx].target === targetPath) {
                    mappedElsewhere = true;
                    break;
                }
            }

            var items = [];
            if (targetNode !== null && targetNode.kind === 'leaf' && !mappedElsewhere) {
                items.push({label: 'Set value', onSelect: function() {
                    openSetValueDialog(targetPath);
                }});
            }
            items.push(renameItem);

            zato.mapper.contextMenu.open({
                x: event.clientX,
                y: event.clientY,
                items: items
            });
        });
    };

})(jQuery);
