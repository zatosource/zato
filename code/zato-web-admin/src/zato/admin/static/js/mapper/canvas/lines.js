
// Mapper kit - the canvas line layer.
// The geometry of the canvas: where tree rows anchor their lines,
// drawing every connection as a cubic curve with endpoint dots, and
// finding the line nearest to a point for the hover and the menus.

(function($) {

    zato.mapper.canvas.lines = {};

// ////////////////////////////////////////////////////////////////////////

    // The sampling step along a line when measuring distances to it.
    var lineSampleStepPixels = 10;

    // How close the pointer must come to a line for it to light up.
    var lineHoverRadius = 0.75 * zato.mapper.canvas.rootFontSize;

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.canvas.lines.setup = function(shared) {

        var canvasConfig = shared.config;
        var container = shared.container;
        var svg = shared.svg;

// ////////////////////////////////////////////////////////////////////////

        shared.treeRowAt = function(body, path) {

            var item = body.querySelector('.mapper-tree-item[data-path="' + path + '"]');
            if (item === null) {
                return null;
            }

            var out = item.querySelector(':scope > .mapper-tree-row');
            return out;
        };

// ////////////////////////////////////////////////////////////////////////

        shared.anchorOf = function(body, column, path, edge, containerRect) {

            var row = shared.treeRowAt(body, path);
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
        };

// ////////////////////////////////////////////////////////////////////////

        function drawLines(connections) {

            $(svg).empty();

            var containerRect = container.getBoundingClientRect();
            svg.setAttribute('width', containerRect.width);
            svg.setAttribute('height', containerRect.height);

            for (var connectionIdx = 0; connectionIdx < connections.length; connectionIdx++) {
                var connection = connections[connectionIdx];

                var targetAnchor = shared.anchorOf(canvasConfig.targetBody, canvasConfig.targetColumn, connection.target, 'left', containerRect);
                if (targetAnchor === null) {
                    continue;
                }

                // One line per referenced source field, converging on the target.
                for (var sourceIdx = 0; sourceIdx < connection.sources.length; sourceIdx++) {
                    var sourceAnchor = shared.anchorOf(canvasConfig.sourceBody, canvasConfig.sourceColumn, connection.sources[sourceIdx], 'right', containerRect);
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

                    path.setAttribute('class', 'mapper-canvas-line');

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
                        dot.setAttribute('class', 'mapper-canvas-line mapper-canvas-dot');
                        dot.setAttribute('data-line', lineId);
                        svg.appendChild(dot);
                    }
                }
            }
        }

// ////////////////////////////////////////////////////////////////////////

        shared.redraw = function() {

            shared.lastConnections = zato.mapper.connections.list(shared.store.getArtifact());
            drawLines(shared.lastConnections);
        };

// ////////////////////////////////////////////////////////////////////////

        // Whether a viewport x coordinate falls into the strip between
        // the two trees - the only place lines react to the pointer.
        shared.isInGutter = function(clientX) {

            var sourceRect = canvasConfig.sourceColumn.getBoundingClientRect();
            var targetRect = canvasConfig.targetColumn.getBoundingClientRect();

            var out = clientX > sourceRect.right && clientX < targetRect.left;
            return out;
        };

// ////////////////////////////////////////////////////////////////////////

        // The connection a drawn line belongs to - the line id starts
        // with the index into the connections drawn most recently.
        shared.connectionOfLineId = function(lineId) {

            var connectionIdx = parseInt(lineId, 10);
            var out = shared.lastConnections[connectionIdx];
            return out;
        };

// ////////////////////////////////////////////////////////////////////////

        // The line whose curve passes closest to the point, if any comes
        // within the hover radius. The curves are sampled because SVG has
        // no direct point-to-path distance.
        shared.nearestLineId = function(pointX, pointY) {

            var out = null;
            var bestDistance = lineHoverRadius;

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
        };

// ////////////////////////////////////////////////////////////////////////

        // The vertical band the lines occupy - everything between the
        // topmost one and the bottommost one, in container coordinates.
        shared.lineBand = function() {

            var paths = svg.querySelectorAll('path.mapper-canvas-line');
            if (paths.length === 0) {
                return null;
            }

            var top = Infinity;
            var bottom = -Infinity;

            for (var pathIdx = 0; pathIdx < paths.length; pathIdx++) {
                var box = paths[pathIdx].getBBox();
                if (box.y < top) {
                    top = box.y;
                }
                if (box.y + box.height > bottom) {
                    bottom = box.y + box.height;
                }
            }

            var out = {top: top, bottom: bottom};
            return out;
        };
    };

})(jQuery);
