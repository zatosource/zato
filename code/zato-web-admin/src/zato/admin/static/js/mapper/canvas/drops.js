
// Mapper kit - the canvas drop rules.
// What a drag from a source path onto a target path means: two lists
// make an iteration scope, two structures open the scoped auto-map,
// two leaves make a mapping row - inside the right scope when both
// sides repeat - and anything else is refused with a notice.

(function($) {

    zato.mapper.canvas.drops = {};

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.canvas.drops.setup = function(shared) {

        var canvasConfig = shared.config;
        var store = shared.store;

// ////////////////////////////////////////////////////////////////////////

        function findScope(scopes, sourcePath, targetPath) {

            for (var scopeIdx = 0; scopeIdx < scopes.length; scopeIdx++) {
                if (scopes[scopeIdx].source === sourcePath && scopes[scopeIdx].target === targetPath) {
                    return scopeIdx;
                }
            }

            return -1;
        }

// ////////////////////////////////////////////////////////////////////////

        function findMapping(mappings, targetPath) {

            for (var rowIdx = 0; rowIdx < mappings.length; rowIdx++) {
                if (mappings[rowIdx].target === targetPath) {
                    return rowIdx;
                }
            }

            return -1;
        }

// ////////////////////////////////////////////////////////////////////////

        shared.newDragRow = function(targetPath, expression) {

            var out = zato.mapper.store.newMapping();
            out.target = targetPath;
            out.expression = expression;
            out.origin = 'canvas';

            return out;
        };

// ////////////////////////////////////////////////////////////////////////

        // Grows a row's expression by one more source - a bare expression
        // becomes a list of inputs, a list grows by one entry - so every
        // source dropped onto the target keeps its own line to it.
        function expressionWithSource(expression, sourcePath) {

            var trimmed = expression.trim();

            if (/^\[[\s\S]*\]$/.test(trimmed)) {
                var out = trimmed.substring(0, trimmed.length - 1) + ', ' + sourcePath + ']';
                return out;
            }

            return '[' + trimmed + ', ' + sourcePath + ']';
        }

// ////////////////////////////////////////////////////////////////////////

        // A drop onto a target that is mapped already attaches the new
        // source to the existing row instead of refusing - unless the
        // row references that source already, in which case the row is
        // only selected.
        function addSourceToRow(selection, row, sourcePath) {

            var referenced = zato.mapper.connections.extractPaths(row.expression, [sourcePath]);
            if (referenced.length > 0) {
                zato.mapper.log('canvas', 'the row references this source already, selecting it', {source: sourcePath, target: row.target});
                canvasConfig.onRowCreated(selection);
                return;
            }

            var updated = zato.mapper.store.newMapping();
            updated.target = row.target;
            updated.expression = expressionWithSource(row.expression, sourcePath);
            updated.condition = row.condition;
            updated.comment = row.comment;
            updated.origin = row.origin;
            updated['default'] = row['default'];
            updated.omit_if_empty = row.omit_if_empty;

            zato.mapper.log('canvas', 'adding a source to a mapped target', {source: sourcePath, target: row.target, expression: updated.expression});

            if (selection.scopeIndex === null) {
                store.updateMapping(selection.rowIndex, updated);
            }
            else {
                store.updateScopeMapping(selection.scopeIndex, selection.rowIndex, updated);
            }

            canvasConfig.onRowCreated(selection);
        }

// ////////////////////////////////////////////////////////////////////////

        shared.applyDrop = function(sourcePath, targetPath) {

            var artifact = store.getArtifact();
            var sourceNode = zato.mapper.schema.nodeAtPath(artifact.source_schema.root, sourcePath);
            var targetNode = zato.mapper.schema.nodeAtPath(artifact.target_schema.root, targetPath);

            zato.mapper.log('canvas', 'drop', {source: sourcePath, target: targetPath});

            // Two repeating nodes make an iteration scope - the children
            // then map relatively with further drags.
            if (sourceNode.kind === 'array' && targetNode.kind === 'array') {

                if (findScope(artifact.scopes, sourcePath, targetPath) !== -1) {
                    zato.mapper.log('canvas', 'the scope already exists', {source: sourcePath, target: targetPath});
                    return;
                }

                store.addScope({target: targetPath, source: sourcePath, mappings: []});
                return;
            }

            // One structure dropped onto another asks for the scoped
            // auto-map suggestions over the pair - reviewable, never
            // applied silently.
            if (sourceNode.kind === 'object' && targetNode.kind === 'object') {
                zato.mapper.log('canvas', 'structure drop, opening scoped auto-map', {source: sourcePath, target: targetPath});
                canvasConfig.onStructureDrop(sourcePath, targetPath);
                return;
            }

            // A structure dropped on a leaf (or the reverse) means nothing.
            if (sourceNode.kind !== 'leaf' || targetNode.kind !== 'leaf') {
                zato.mapper.log('canvas', 'refused - the two sides have different shapes', {source: sourcePath, target: targetPath});
                canvasConfig.onNotice('Drop a field onto a field, a list onto a list, or a structure onto a structure - `' + sourcePath + '` onto `' + targetPath + '` is none of these.');
                return;
            }

            // A leaf inside a repeating node dropped onto a leaf inside
            // another repeating node maps within an iteration scope,
            // which is created automatically when missing.
            var sourceArray = zato.mapper.schema.nearestArrayAncestor(artifact.source_schema.root, sourcePath);
            var targetArray = zato.mapper.schema.nearestArrayAncestor(artifact.target_schema.root, targetPath);

            // A target that repeats per element cannot take a single
            // source value - that would fight the list over its shape.
            if (targetArray !== '' && sourceArray === '') {
                zato.mapper.log('canvas', 'refused - the target repeats but the source does not', {source: sourcePath, target: targetPath});
                canvasConfig.onNotice('`' + targetPath + '` repeats per element of `' + targetArray + '` - map it from a field inside a repeating source list.');
                return;
            }

            if (sourceArray !== '' && targetArray !== '') {

                var relativeSource = sourcePath.substring(sourceArray.length + 1);
                var relativeTarget = targetPath.substring(targetArray.length + 1);
                var childRow = shared.newDragRow(relativeTarget, relativeSource);

                var scopeIdx = findScope(artifact.scopes, sourceArray, targetArray);
                if (scopeIdx === -1) {

                    // The new scope arrives with its first row in one step.
                    store.addScope({target: targetArray, source: sourceArray, mappings: [childRow]});
                    canvasConfig.onRowCreated({scopeIndex: store.getArtifact().scopes.length - 1, rowIndex: 0});
                    return;
                }

                var scope = artifact.scopes[scopeIdx];

                // A target mapped already is never overwritten silently -
                // the new source joins the existing row instead.
                var existingChildIdx = findMapping(scope.mappings, relativeTarget);
                if (existingChildIdx !== -1) {
                    addSourceToRow({scopeIndex: scopeIdx, rowIndex: existingChildIdx}, scope.mappings[existingChildIdx], relativeSource);
                    return;
                }

                store.addScopeMapping(scopeIdx, childRow);

                // The index of the row just appended, read back after
                // the mutation so it can never drift.
                var newChildIdx = store.getArtifact().scopes[scopeIdx].mappings.length - 1;
                canvasConfig.onRowCreated({scopeIndex: scopeIdx, rowIndex: newChildIdx});
                return;
            }

            // A plain field-to-field drop is one top-level row. A target
            // mapped already takes the new source into its row.
            var existingIdx = findMapping(artifact.mappings, targetPath);
            if (existingIdx !== -1) {
                addSourceToRow({scopeIndex: null, rowIndex: existingIdx}, artifact.mappings[existingIdx], sourcePath);
                return;
            }

            store.addMapping(shared.newDragRow(targetPath, sourcePath));
            canvasConfig.onRowCreated({scopeIndex: null, rowIndex: store.getArtifact().mappings.length - 1});
        };
    };

})(jQuery);
