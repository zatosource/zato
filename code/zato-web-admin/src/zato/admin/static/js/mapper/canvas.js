
// Mapper kit - the mapping canvas.
// Drag a source field onto a target field to create a mapping row.
// Dropping a leaf under a repeating node onto a leaf under another
// repeating node creates an iteration scope automatically and the
// children map relatively. An SVG layer always draws every
// connection line.
// While the pointer is over the gutter where the lines live, all of
// them dim except the one under the pointer, which lights up with a
// marching-ants animation. Lines are interactive: a click selects the
// mapping row a line belongs to, a right-click opens a menu over it,
// and right-clicking a target field offers wrapping its expression in
// a function or setting a constant value on an unmapped field.

(function($) {

    zato.mapper.canvas = {};

// ////////////////////////////////////////////////////////////////////////

    var dragThresholdPixels = 4;

    // How close the pointer must come to a line for it to light up.
    var lineHoverRadiusPixels = 12;

    // The sampling step along a line when measuring that distance.
    var lineSampleStepPixels = 10;

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

    // Initializes the canvas.
    // canvasConfig:
    //   store:         the artifact store
    //   container:     the columns container the SVG layer covers
    //   sourceColumn:  the source column element
    //   targetColumn:  the target column element
    //   sourceBody:    the source tree body
    //   targetBody:    the target tree body
    //   svg:           the SVG element of the line layer
    //   getSelected:   function() - the mapping list selection or null
    //   onRowCreated:  called with {scopeIndex, rowIndex} after a drop
    //   onRowOpen:     called with ({scopeIndex, rowIndex}, field) when a
    //                  line or a menu entry asks for the row - field is
    //                  '' or the detail field to focus ('expression',
    //                  'condition', 'default')
    //   onDeselect:    called when a click lands on empty gutter space
    //   onNotice:      called with the reason whenever a drop is refused
    //   onStructureDrop: called with (sourcePath, targetPath) when one
    //                  structure is dropped onto another - the page opens
    //                  the scoped auto-map suggestions over the pair
    //   onRenameField: called with (side, path) when a tree menu asks
    //                  for a field rename
    // Returns {redraw}.
    zato.mapper.canvas.init = function(canvasConfig) {

        var store = canvasConfig.store;
        var container = canvasConfig.container;
        var svg = canvasConfig.svg;

        // The connections behind the lines drawn most recently - the
        // click, hover and menu handlers all look lines up in here.
        var lastConnections = [];

// ////////////////////////////////////////////////////////////////////////
// The SVG line layer
// ////////////////////////////////////////////////////////////////////////

        function treeRowAt(body, path) {

            var item = body.querySelector('.mapper-tree-item[data-path="' + path + '"]');
            if (item === null) {
                return null;
            }

            var out = item.querySelector(':scope > .mapper-tree-row');
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function anchorOf(body, column, path, edge, containerRect) {

            var row = treeRowAt(body, path);
            if (row === null) {
                return null;
            }

            var rowRect = row.getBoundingClientRect();

            // A collapsed or empty row has no geometry to anchor to.
            if (rowRect.height === 0) {
                return null;
            }

            // Rows scrolled out of the body would draw lines outside
            // the columns, so their anchors clamp to the body's edges.
            var bodyRect = body.getBoundingClientRect();
            var anchorY = rowRect.top + rowRect.height / 2;
            if (anchorY < bodyRect.top) {
                anchorY = bodyRect.top;
            }
            if (anchorY > bodyRect.bottom) {
                anchorY = bodyRect.bottom;
            }

            var columnRect = column.getBoundingClientRect();
            var anchorX = edge === 'right' ? columnRect.right : columnRect.left;

            var out = {x: anchorX - containerRect.left, y: anchorY - containerRect.top};
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function isSelectionEqual(first, second) {

            if (first === null || second === null) {
                return false;
            }

            var out = first.scopeIndex === second.scopeIndex && first.rowIndex === second.rowIndex;
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function drawLines(connections) {

            $(svg).empty();

            var containerRect = container.getBoundingClientRect();
            svg.setAttribute('width', containerRect.width);
            svg.setAttribute('height', containerRect.height);

            var selected = canvasConfig.getSelected();

            for (var connectionIdx = 0; connectionIdx < connections.length; connectionIdx++) {
                var connection = connections[connectionIdx];

                var targetAnchor = anchorOf(canvasConfig.targetBody, canvasConfig.targetColumn, connection.target, 'left', containerRect);
                if (targetAnchor === null) {
                    continue;
                }

                // One line per referenced source field, converging on the target.
                for (var sourceIdx = 0; sourceIdx < connection.sources.length; sourceIdx++) {
                    var sourceAnchor = anchorOf(canvasConfig.sourceBody, canvasConfig.sourceColumn, connection.sources[sourceIdx], 'right', containerRect);
                    if (sourceAnchor === null) {
                        continue;
                    }

                    var middleX = (sourceAnchor.x + targetAnchor.x) / 2;
                    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    path.setAttribute('d',
                        'M ' + sourceAnchor.x + ' ' + sourceAnchor.y +
                        ' C ' + middleX + ' ' + sourceAnchor.y +
                        ', ' + middleX + ' ' + targetAnchor.y +
                        ', ' + targetAnchor.x + ' ' + targetAnchor.y);

                    var lineClass = 'mapper-canvas-line';

                    // A computed line is dashed, a conditioned one changes
                    // color - both are visible before any selection.
                    if (connection.computed) {
                        lineClass = lineClass + ' mapper-canvas-line-computed';
                    }
                    if (connection.conditioned) {
                        lineClass = lineClass + ' mapper-canvas-line-conditioned';
                    }
                    if (isSelectionEqual(connection.selection, selected)) {
                        lineClass = lineClass + ' mapper-canvas-line-selected';
                    }
                    path.setAttribute('class', lineClass);

                    // The id ties a line to its endpoint dots, and the paths
                    // let the gutter hover light up the rows it connects.
                    var lineId = connectionIdx + '-' + sourceIdx;
                    path.setAttribute('data-line', lineId);
                    path.setAttribute('data-source-path', connection.sources[sourceIdx]);
                    path.setAttribute('data-target-path', connection.target);

                    svg.appendChild(path);

                    // A dot on each end shows which rows the line attaches to.
                    var anchors = [sourceAnchor, targetAnchor];
                    for (var anchorIdx = 0; anchorIdx < anchors.length; anchorIdx++) {
                        var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        dot.setAttribute('cx', anchors[anchorIdx].x);
                        dot.setAttribute('cy', anchors[anchorIdx].y);
                        dot.setAttribute('r', 3.5);
                        dot.setAttribute('class', lineClass + ' mapper-canvas-dot');
                        dot.setAttribute('data-line', lineId);
                        svg.appendChild(dot);
                    }
                }
            }
        }

// ////////////////////////////////////////////////////////////////////////

        function redraw() {

            lastConnections = zato.mapper.connections.list(store.getArtifact());
            drawLines(lastConnections);
        }

// ////////////////////////////////////////////////////////////////////////
// Drop rules - what a drag from a source path onto a target path means.
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

        function newDragRow(targetPath, expression) {

            var out = zato.mapper.store.newMapping();
            out.target = targetPath;
            out.expression = expression;
            out.origin = 'canvas';

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function applyDrop(sourcePath, targetPath) {

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
                var childRow = newDragRow(relativeTarget, relativeSource);

                var scopeIdx = findScope(artifact.scopes, sourceArray, targetArray);
                if (scopeIdx === -1) {

                    // The new scope arrives with its first row in one step.
                    store.addScope({target: targetArray, source: sourceArray, mappings: [childRow]});
                    canvasConfig.onRowCreated({scopeIndex: store.getArtifact().scopes.length - 1, rowIndex: 0});
                    return;
                }

                var scope = artifact.scopes[scopeIdx];

                // A target mapped already is never overwritten silently -
                // the existing row is selected instead.
                var existingChildIdx = findMapping(scope.mappings, relativeTarget);
                if (existingChildIdx !== -1) {
                    zato.mapper.log('canvas', 'the target is already mapped, selecting its row', {target: targetPath});
                    canvasConfig.onRowCreated({scopeIndex: scopeIdx, rowIndex: existingChildIdx});
                    return;
                }

                store.addScopeMapping(scopeIdx, childRow);

                // The index of the row just appended, read back after
                // the mutation so it can never drift.
                var newChildIdx = store.getArtifact().scopes[scopeIdx].mappings.length - 1;
                canvasConfig.onRowCreated({scopeIndex: scopeIdx, rowIndex: newChildIdx});
                return;
            }

            // A plain field-to-field drop is one top-level row.
            var existingIdx = findMapping(artifact.mappings, targetPath);
            if (existingIdx !== -1) {
                zato.mapper.log('canvas', 'the target is already mapped, selecting its row', {target: targetPath});
                canvasConfig.onRowCreated({scopeIndex: null, rowIndex: existingIdx});
                return;
            }

            store.addMapping(newDragRow(targetPath, sourcePath));
            canvasConfig.onRowCreated({scopeIndex: null, rowIndex: store.getArtifact().mappings.length - 1});
        }

// ////////////////////////////////////////////////////////////////////////
// Dragging - Pointer Events from a source tree row to a target one,
// with a ghost following the pointer and the drop target highlighted.
// ////////////////////////////////////////////////////////////////////////

        var drag = null;

        function clearDropHighlight() {
            $(canvasConfig.targetBody).find('.mapper-tree-row-drop-target').removeClass('mapper-tree-row-drop-target');
        }

// ////////////////////////////////////////////////////////////////////////

        // The target tree row under the pointer, if any.
        function dropRowAt(clientX, clientY) {

            var element = document.elementFromPoint(clientX, clientY);
            if (element === null) {
                return null;
            }

            var row = element.closest('.mapper-tree-row');
            if (row === null) {
                return null;
            }

            if (!canvasConfig.targetBody.contains(row)) {
                return null;
            }

            return row;
        }

// ////////////////////////////////////////////////////////////////////////

        $(canvasConfig.sourceBody).on('pointerdown', '.mapper-tree-row', function(event) {

            // Only the primary button starts a drag.
            if (event.button !== 0) {
                return;
            }

            var item = this.closest('.mapper-tree-item');

            drag = {
                row: this,
                path: item.getAttribute('data-path'),
                startX: event.clientX,
                startY: event.clientY,
                active: false,
                ghost: null
            };

            this.setPointerCapture(event.originalEvent.pointerId);
        });

        $(canvasConfig.sourceBody).on('pointermove', '.mapper-tree-row', function(event) {

            if (drag === null) {
                return;
            }

            // The drag only becomes real past a small threshold,
            // so plain clicks keep working.
            if (!drag.active) {
                var deltaX = Math.abs(event.clientX - drag.startX);
                var deltaY = Math.abs(event.clientY - drag.startY);
                if (deltaX < dragThresholdPixels && deltaY < dragThresholdPixels) {
                    return;
                }

                drag.active = true;

                drag.ghost = document.createElement('div');
                drag.ghost.className = 'mapper-drag-ghost';
                drag.ghost.textContent = drag.path;
                document.body.appendChild(drag.ghost);

                zato.mapper.log('canvas', 'drag starts', {source: drag.path});
            }

            drag.ghost.style.left = (event.clientX + 12) + 'px';
            drag.ghost.style.top = (event.clientY + 12) + 'px';

            clearDropHighlight();
            var dropRow = dropRowAt(event.clientX, event.clientY);
            if (dropRow !== null) {
                $(dropRow).addClass('mapper-tree-row-drop-target');
            }
        });

        $(canvasConfig.sourceBody).on('pointerup pointercancel', '.mapper-tree-row', function(event) {

            if (drag === null) {
                return;
            }

            var wasActive = drag.active;
            var sourcePath = drag.path;

            if (drag.ghost !== null) {
                $(drag.ghost).remove();
            }
            clearDropHighlight();
            drag = null;

            if (!wasActive || event.type === 'pointercancel') {
                return;
            }

            // The click this pointerup releases must not toggle the
            // row the drag started on.
            zato.mapper.tree.suppressNextToggle = true;

            var dropRow = dropRowAt(event.clientX, event.clientY);
            if (dropRow === null) {
                zato.mapper.log('canvas', 'drag ended outside the target tree', {source: sourcePath});
                return;
            }

            var targetPath = dropRow.closest('.mapper-tree-item').getAttribute('data-path');
            applyDrop(sourcePath, targetPath);
        });

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
// Gutter hover - while the pointer is over the strip between the trees,
// every line dims except the one closest to the pointer.
// ////////////////////////////////////////////////////////////////////////

        // Whether a viewport x coordinate falls into the strip between
        // the two trees - the only place lines react to the pointer.
        function isInGutter(clientX) {

            var sourceRect = canvasConfig.sourceColumn.getBoundingClientRect();
            var targetRect = canvasConfig.targetColumn.getBoundingClientRect();

            var out = clientX > sourceRect.right && clientX < targetRect.left;
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The connection a drawn line belongs to - the line id starts
        // with the index into the connections drawn most recently.
        function connectionOfLineId(lineId) {

            var connectionIdx = parseInt(lineId, 10);
            var out = lastConnections[connectionIdx];
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The line whose curve passes closest to the point, if any comes
        // within the hover radius. The curves are sampled because SVG has
        // no direct point-to-path distance.
        function nearestLineId(pointX, pointY) {

            var out = null;
            var bestDistance = lineHoverRadiusPixels;

            var paths = svg.querySelectorAll('path.mapper-canvas-line');

            for (var pathIdx = 0; pathIdx < paths.length; pathIdx++) {
                var linePath = paths[pathIdx];
                var totalLength = linePath.getTotalLength();

                for (var offset = 0; offset <= totalLength; offset += lineSampleStepPixels) {
                    var samplePoint = linePath.getPointAtLength(offset);
                    var deltaX = samplePoint.x - pointX;
                    var deltaY = samplePoint.y - pointY;
                    var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                    if (distance < bestDistance) {
                        bestDistance = distance;
                        out = linePath.getAttribute('data-line');
                    }
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The rows a hovered line connects carry their own highlight,
        // cleared here together in one place.
        function clearConnectedRows() {
            $(container).find('.mapper-tree-row-connected-source').removeClass('mapper-tree-row-connected-source');
            $(container).find('.mapper-tree-row-connected-target').removeClass('mapper-tree-row-connected-target');
        }

// ////////////////////////////////////////////////////////////////////////

        function clearGutterHover() {

            svg.classList.remove('mapper-canvas-dimmed');
            clearConnectedRows();

            var hoveredElements = svg.querySelectorAll('.mapper-canvas-line-hovered');
            for (var elementIdx = 0; elementIdx < hoveredElements.length; elementIdx++) {
                hoveredElements[elementIdx].classList.remove('mapper-canvas-line-hovered');
            }
        }

// ////////////////////////////////////////////////////////////////////////

        $(container).on('mousemove', function(event) {

            // The dimming applies only inside the gutter - the trees
            // themselves keep their lines at full strength.
            if (!isInGutter(event.clientX)) {
                clearGutterHover();
                return;
            }

            svg.classList.add('mapper-canvas-dimmed');

            var containerRect = container.getBoundingClientRect();
            var lineId = nearestLineId(event.clientX - containerRect.left, event.clientY - containerRect.top);

            var hoveredElements = svg.querySelectorAll('.mapper-canvas-line-hovered');
            for (var elementIdx = 0; elementIdx < hoveredElements.length; elementIdx++) {
                hoveredElements[elementIdx].classList.remove('mapper-canvas-line-hovered');
            }
            clearConnectedRows();

            if (lineId !== null) {
                var lineElements = svg.querySelectorAll('[data-line="' + lineId + '"]');
                for (var lineElementIdx = 0; lineElementIdx < lineElements.length; lineElementIdx++) {
                    lineElements[lineElementIdx].classList.add('mapper-canvas-line-hovered');
                }

                // The rows the lit line connects light up with it.
                var linePath = svg.querySelector('path[data-line="' + lineId + '"]');

                var connectedSourceRow = treeRowAt(canvasConfig.sourceBody, linePath.getAttribute('data-source-path'));
                if (connectedSourceRow !== null) {
                    connectedSourceRow.classList.add('mapper-tree-row-connected-source');
                }

                var connectedTargetRow = treeRowAt(canvasConfig.targetBody, linePath.getAttribute('data-target-path'));
                if (connectedTargetRow !== null) {
                    connectedTargetRow.classList.add('mapper-tree-row-connected-target');
                }
            }
        });

        $(container).on('mouseleave', clearGutterHover);

// ////////////////////////////////////////////////////////////////////////
// Line interactions - a click selects the mapping row behind a line,
// a right-click opens a menu over it.
// ////////////////////////////////////////////////////////////////////////

        // The row-backed line under the pointer, or null - scope lines
        // connect two lists rather than one row, so they take no clicks.
        function lineSelectionAt(clientX, clientY) {

            var containerRect = container.getBoundingClientRect();
            var lineId = nearestLineId(clientX - containerRect.left, clientY - containerRect.top);
            if (lineId === null) {
                return null;
            }

            var out = connectionOfLineId(lineId).selection;
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

            if (!isInGutter(event.clientX)) {
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

            if (!isInGutter(event.clientX)) {
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
                store.addMapping(newDragRow(targetPath, literalOf(value)));
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
            store.addScopeMapping(scopeIdx, newDragRow(relativeTarget, literalOf(value)));

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
            for (var connectionIdx = 0; connectionIdx < lastConnections.length; connectionIdx++) {
                var connection = lastConnections[connectionIdx];
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
            for (var otherIdx = 0; otherIdx < lastConnections.length; otherIdx++) {
                if (lastConnections[otherIdx].target === targetPath) {
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

        // Lines track the trees: store changes re-render them, scrolling
        // and column resizes move their rows.
        store.subscribe(redraw);

        $(canvasConfig.sourceBody).on('scroll', redraw);
        $(canvasConfig.targetBody).on('scroll', redraw);
        $(window).on('resize', redraw);

        var observer = new ResizeObserver(redraw);
        observer.observe(canvasConfig.sourceColumn);
        observer.observe(canvasConfig.targetColumn);

        redraw();

        return {redraw: redraw};
    };

})(jQuery);
