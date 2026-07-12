
// Mapper kit - canvas dragging.
// Pointer Events between the two trees, starting on either side, with
// a ghost following the pointer, a ghost connection line snapping onto
// the drop candidate and the drop row highlighted with its whole
// root-to-field path.

(function($) {

    zato.mapper.canvas.drag = {};

// ////////////////////////////////////////////////////////////////////////

    var dragThresholdPixels = 4;

    // How close the pointer must come to a row's anchor for the ghost
    // line to snap onto it from the gutter - a gentler magnet than
    // pointing at the row itself.
    var ghostSnapRadius = 3 * zato.mapper.canvas.rootFontSize;

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.canvas.drag.setup = function(shared) {

        var canvasConfig = shared.config;
        var container = shared.container;
        var svg = shared.svg;

        var drag = null;

        // The gutter hover stays out of the way while a drag leads.
        shared.isDragActive = function() {
            var out = drag !== null && drag.active;
            return out;
        };

        // Each side's tree and the edge its anchors sit on - a drag
        // may start on either side and drops onto the other one.
        var sides = {
            source: {body: canvasConfig.sourceBody, column: canvasConfig.sourceColumn, edge: 'right'},
            target: {body: canvasConfig.targetBody, column: canvasConfig.targetColumn, edge: 'left'}
        };

        function oppositeOf(side) {
            var out = side === 'source' ? 'target' : 'source';
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function clearDropHighlight() {
            $(container).find('.mapper-tree-row-drop-target').removeClass('mapper-tree-row-drop-target');
        }

// ////////////////////////////////////////////////////////////////////////

        // The drop-side tree row under the pointer, if any.
        function dropRowAt(clientX, clientY, dropSide) {

            var element = document.elementFromPoint(clientX, clientY);
            if (element === null) {
                return null;
            }

            var row = element.closest('.mapper-tree-row');
            if (row === null) {
                return null;
            }

            if (!sides[dropSide].body.contains(row)) {
                return null;
            }

            return row;
        }

// ////////////////////////////////////////////////////////////////////////

        // The drop-side row the ghost line snaps onto - the row
        // directly under the pointer, or the one whose anchor is close
        // enough when the pointer floats in the gutter between the trees.
        function snapRowAt(clientX, clientY, dropSide) {

            var out = dropRowAt(clientX, clientY, dropSide);
            if (out !== null) {
                return out;
            }

            var columnRect = sides[dropSide].column.getBoundingClientRect();
            var bodyRect = sides[dropSide].body.getBoundingClientRect();

            // The anchors all sit on the column's facing edge, so the
            // horizontal part of the distance is the same for each row.
            var anchorX = sides[dropSide].edge === 'right' ? columnRect.right : columnRect.left;
            var deltaX = clientX - anchorX;

            var bestDistance = ghostSnapRadius;
            var rows = sides[dropSide].body.querySelectorAll('.mapper-tree-row');

            for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
                var rect = rows[rowIdx].getBoundingClientRect();

                // A collapsed row has no geometry to snap onto ..
                if (rect.height === 0) {
                    continue;
                }

                // .. and one scrolled out of the body has no anchor
                // in view.
                var centerY = rect.top + rect.height / 2;
                if (centerY < bodyRect.top || centerY > bodyRect.bottom) {
                    continue;
                }

                var deltaY = clientY - centerY;
                var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                if (distance < bestDistance) {
                    bestDistance = distance;
                    out = rows[rowIdx];
                }
            }

            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        // The ghost line a drag draws from its starting field to the
        // pointer, snapping onto the drop-side row under it, together
        // with its own endpoint dots.
        var ghostLine = null;
        var ghostDots = null;

        function drawGhostLine(dragSide, dragPath, clientX, clientY, dropRow) {

            var containerRect = container.getBoundingClientRect();

            var dragSideInfo = sides[dragSide];
            var startAnchor = shared.anchorOf(dragSideInfo.body, dragSideInfo.column, dragPath, dragSideInfo.edge, containerRect);
            if (startAnchor === null) {
                return;
            }

            // The line ends at the pointer, unless a drop-side row
            // sits under it - then it snaps onto that row's own anchor.
            var endX = clientX - containerRect.left;
            var endY = clientY - containerRect.top;

            if (dropRow !== null) {
                var dropSideInfo = sides[oppositeOf(dragSide)];
                var dropPath = dropRow.closest('.mapper-tree-item').getAttribute('data-path');
                var dropAnchor = shared.anchorOf(dropSideInfo.body, dropSideInfo.column, dropPath, dropSideInfo.edge, containerRect);
                if (dropAnchor !== null) {
                    endX = dropAnchor.x;
                    endY = dropAnchor.y;
                }
            }

            if (ghostLine === null) {
                ghostLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                ghostLine.setAttribute('class', 'mapper-canvas-line-ghost');

                ghostDots = [];
                for (var dotIdx = 0; dotIdx < 2; dotIdx++) {
                    var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    dot.setAttribute('r', 3.5);
                    dot.setAttribute('class', 'mapper-canvas-line-ghost');
                    ghostDots.push(dot);
                }
            }

            // Re-appending keeps the ghost on top and puts it back
            // whenever a redraw has just emptied the layer.
            svg.appendChild(ghostLine);
            svg.appendChild(ghostDots[0]);
            svg.appendChild(ghostDots[1]);

            var middleX = (startAnchor.x + endX) / 2;
            ghostLine.setAttribute('d',
                'M ' + startAnchor.x + ' ' + startAnchor.y +
                ' C ' + middleX + ' ' + startAnchor.y +
                ', ' + middleX + ' ' + endY +
                ', ' + endX + ' ' + endY);

            ghostDots[0].setAttribute('cx', startAnchor.x);
            ghostDots[0].setAttribute('cy', startAnchor.y);
            ghostDots[1].setAttribute('cx', endX);
            ghostDots[1].setAttribute('cy', endY);
        }

// ////////////////////////////////////////////////////////////////////////

        function removeGhostLine() {

            if (ghostLine !== null) {
                $(ghostLine).remove();
                $(ghostDots[0]).remove();
                $(ghostDots[1]).remove();
                ghostLine = null;
                ghostDots = null;
            }

            shared.clearDim();
        }

// ////////////////////////////////////////////////////////////////////////

        // Wires the drag handlers onto one side's tree - a drag may
        // start on either side, the drop lands on the other one, and
        // the mapping always reads source to target whichever way the
        // pointer traveled.
        function bindDrag(dragSide) {

            var body = sides[dragSide].body;
            var dropSide = oppositeOf(dragSide);

            $(body).on('pointerdown', '.mapper-tree-row', function(event) {

                // Only the primary button starts a drag.
                if (event.button !== 0) {
                    return;
                }

                var item = this.closest('.mapper-tree-item');

                drag = {
                    side: dragSide,
                    row: this,
                    path: item.getAttribute('data-path'),
                    startX: event.clientX,
                    startY: event.clientY,
                    active: false,
                    ghost: null
                };

                this.setPointerCapture(event.originalEvent.pointerId);
            });

            $(body).on('pointermove', '.mapper-tree-row', function(event) {

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

                    // Every existing line dims for as long as the ghost
                    // line leads the way.
                    shared.clearFieldHover();
                    shared.dimAll();

                    zato.mapper.log('canvas', 'drag starts', {side: dragSide, path: drag.path});
                }

                drag.ghost.style.left = (event.clientX + 12) + 'px';
                drag.ghost.style.top = (event.clientY + 12) + 'px';

                clearDropHighlight();
                shared.clearLinkedRows();

                // The dragged field stays lit for the whole drag,
                // path and all.
                shared.lightRow(drag.row);

                var dropRow = snapRowAt(event.clientX, event.clientY, dropSide);
                if (dropRow !== null) {
                    $(dropRow).addClass('mapper-tree-row-drop-target');

                    // The drop candidate lights up with its whole
                    // root-to-field path, like a hover would light it.
                    shared.lightRow(dropRow);
                }

                drawGhostLine(dragSide, drag.path, event.clientX, event.clientY, dropRow);
            });

            $(body).on('pointerup pointercancel', '.mapper-tree-row', function(event) {

                if (drag === null) {
                    return;
                }

                var wasActive = drag.active;
                var dragPath = drag.path;

                if (drag.ghost !== null) {
                    $(drag.ghost).remove();
                }
                clearDropHighlight();
                shared.clearLinkedRows();
                removeGhostLine();
                drag = null;

                if (!wasActive || event.type === 'pointercancel') {
                    return;
                }

                // The click this pointerup releases must not toggle the
                // row the drag started on.
                zato.mapper.tree.suppressNextToggle = true;

                // The drop lands wherever the ghost line snapped, so
                // what the line showed is what the release does.
                var dropRow = snapRowAt(event.clientX, event.clientY, dropSide);
                if (dropRow === null) {
                    zato.mapper.log('canvas', 'drag ended outside the other tree', {side: dragSide, path: dragPath});
                    return;
                }

                var dropPath = dropRow.closest('.mapper-tree-item').getAttribute('data-path');

                // Whichever side the drag started on, the mapping goes
                // from the source field to the target one.
                if (dragSide === 'source') {
                    shared.applyDrop(dragPath, dropPath);
                }
                else {
                    shared.applyDrop(dropPath, dragPath);
                }
            });
        }

        bindDrag('source');
        bindDrag('target');
    };

})(jQuery);
