
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the drawing demo. One real journey drawn from hardcoded data - the
// message on the left, each delivery of it a branch to the right, the failed one
// continuing through the reprocess and onward. Everything here is throwaway, the
// real page will draw through the dashboard kit.

$.fn.zato.message_flow = {};
$.fn.zato.message_flow.demo = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var demo = $.fn.zato.message_flow.demo;

var svgNamespace = 'http://www.w3.org/2000/svg';

// /////////////////////////////////////////////////////////////////////////////

demo.config = {

    // One node card and its regions
    boxWidth: 250,
    boxHeight: 68,
    bandHeight: 24,

    // The writing inside a node's body
    bodyPadLeft: 14,

    // Chips - height, side padding and how wide one character runs
    chipHeight: 16,
    chipPadX: 6,
    chipCharWidth: 6,

    // Connectors - the corner radius of an elbow and the arrowhead
    elbowRadius: 6,
    arrowLength: 8,
    arrowWidth: 4.5,

    // How long a left branch stays lit - long enough to walk the pointer over
    // the gap to the next one without the room flickering back to light
    dimHoldMs: 180
};

// /////////////////////////////////////////////////////////////////////////////
// The private SVG helpers
// /////////////////////////////////////////////////////////////////////////////

demo.createElement = function(name) {
    return document.createElementNS(svgNamespace, name);
};

// /////////////////////////////////////////////////////////////////////////////

demo.newSVG = function(hostId, width, height) {
    var svg = demo.createElement('svg');

    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);

    var host = document.getElementById(hostId);
    host.appendChild(svg);

    return svg;
};

// /////////////////////////////////////////////////////////////////////////////

// The gradient every node face is filled with - a touch of light along the top
// falling away toward the foot, the way the flow's raised cards catch it
demo.addDefs = function(svg) {
    var defs = demo.createElement('defs');

    var gradient = demo.createElement('linearGradient');
    gradient.setAttribute('id', 'message-flow-node-fill');
    gradient.setAttribute('x1', '0');
    gradient.setAttribute('y1', '0');
    gradient.setAttribute('x2', '0');
    gradient.setAttribute('y2', '1');

    var stopTop = demo.createElement('stop');
    stopTop.setAttribute('offset', '0');
    stopTop.setAttribute('stop-color', '#3a3a5c');

    var stopBottom = demo.createElement('stop');
    stopBottom.setAttribute('offset', '1');
    stopBottom.setAttribute('stop-color', '#2d2d48');

    gradient.appendChild(stopTop);
    gradient.appendChild(stopBottom);
    defs.appendChild(gradient);
    svg.appendChild(defs);
};

// /////////////////////////////////////////////////////////////////////////////

demo.addGroup = function(host, className) {
    var group = demo.createElement('g');

    group.setAttribute('class', className);
    host.appendChild(group);

    return group;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addRect = function(host, x, y, width, height, className, radius) {
    var rect = demo.createElement('rect');

    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('rx', radius);
    rect.setAttribute('class', className);

    host.appendChild(rect);

    return rect;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addText = function(host, x, y, text, className, anchor) {
    var element = demo.createElement('text');

    element.setAttribute('x', x);
    element.setAttribute('y', y);
    element.setAttribute('class', className);
    element.setAttribute('text-anchor', anchor);
    element.textContent = text;

    host.appendChild(element);

    return element;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addPolyline = function(host, points, className) {
    var line = demo.createElement('polyline');

    var parts = [];

    for (var pointIndex = 0; pointIndex < points.length; pointIndex++) {
        parts.push(points[pointIndex][0] + ',' + points[pointIndex][1]);
    }

    line.setAttribute('points', parts.join(' '));
    line.setAttribute('class', className);

    host.appendChild(line);

    return line;
};

// /////////////////////////////////////////////////////////////////////////////

// A connector path whose corners are rounded - each elbow leaves the incoming leg
// early and swings onto the outgoing one with a small quadratic curve
demo.addRoundedPath = function(host, points, className) {
    var radius = demo.config.elbowRadius;
    var path = demo.createElement('path');

    var d = 'M ' + points[0][0] + ' ' + points[0][1];

    for (var pointIndex = 1; pointIndex < points.length - 1; pointIndex++) {
        var previous = points[pointIndex - 1];
        var corner = points[pointIndex];
        var next = points[pointIndex + 1];

        // Where the incoming leg stops short of the corner
        var inX = corner[0] - Math.sign(corner[0] - previous[0]) * radius;
        var inY = corner[1] - Math.sign(corner[1] - previous[1]) * radius;

        // Where the outgoing leg picks up past it
        var outX = corner[0] + Math.sign(next[0] - corner[0]) * radius;
        var outY = corner[1] + Math.sign(next[1] - corner[1]) * radius;

        d += ' L ' + inX + ' ' + inY;
        d += ' Q ' + corner[0] + ' ' + corner[1] + ' ' + outX + ' ' + outY;
    }

    var last = points[points.length - 1];
    d += ' L ' + last[0] + ' ' + last[1];

    path.setAttribute('d', d);
    path.setAttribute('class', className);

    host.appendChild(path);

    return path;
};

// /////////////////////////////////////////////////////////////////////////////

// A solid triangle at the end of a connector, pointing the way the message went
demo.addArrow = function(host, x, y, className) {
    var config = demo.config;
    var arrow = demo.createElement('path');

    var d = 'M ' + (x - config.arrowLength) + ' ' + (y - config.arrowWidth) +
            ' L ' + (x - config.arrowLength) + ' ' + (y + config.arrowWidth) +
            ' L ' + x + ' ' + y + ' Z';

    arrow.setAttribute('d', d);
    arrow.setAttribute('class', className);

    host.appendChild(arrow);

    return arrow;
};

// /////////////////////////////////////////////////////////////////////////////

demo.chipWidth = function(label) {
    var config = demo.config;
    return Math.round(label.length * config.chipCharWidth + 2 * config.chipPadX);
};

// /////////////////////////////////////////////////////////////////////////////

// A chip - the same tinted tag the listing and the flow wear. On the canvas it
// stands on a solid backing so a connector running under it is hidden.
demo.addChip = function(host, x, y, label, kind, onCanvas) {
    var config = demo.config;

    var width = demo.chipWidth(label);

    if (onCanvas) {
        demo.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-back', 3);
    }

    demo.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-' + kind, 3);
    demo.addText(host, x + width / 2, y + 12, label, 'message-flow-chip-text message-flow-chip-text-' + kind, 'middle');

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// One node - the lit card: gradient face, top rim, title band with the event id,
// the direction and the event type, the body with the channel and the timestamp
// and the outcome chip on the right
demo.addNode = function(host, x, y, node) {
    var config = demo.config;

    var width = config.boxWidth;
    var height = config.boxHeight;
    var bandHeight = config.bandHeight;

    var group = demo.addGroup(host, 'message-flow-node message-flow-node-selectable');

    demo.addRect(group, x, y, width, height, 'message-flow-box', 4);

    // The band keeps the node's rounded top and is squared off at its own foot
    demo.addRect(group, x, y, width, bandHeight, 'message-flow-band', 4);
    demo.addRect(group, x, y + bandHeight - 6, width, 6, 'message-flow-band-square', 0);
    demo.addPolyline(group, [[x + 1, y + bandHeight], [x + width - 1, y + bandHeight]], 'message-flow-band-line');

    // The hairline of light along the top edge
    demo.addPolyline(group, [[x + 4, y + 1], [x + width - 4, y + 1]], 'message-flow-rim');

    // The band's own line - the id chip, the direction, the event type
    var cursor = x + 10;

    cursor += demo.addChip(group, cursor, y + 4, node.id, 'id', false);
    cursor += 6;
    cursor += demo.addChip(group, cursor, y + 4, node.direction.toUpperCase(), node.direction, false);
    cursor += 8;

    demo.addText(group, cursor, y + 16, node.eventType.toUpperCase(), 'message-flow-band-type', 'start');

    // The body - the channel, the timestamp, the outcome chip
    demo.addText(group, x + config.bodyPadLeft, y + bandHeight + 20, node.channel, 'message-flow-title', 'start');
    demo.addText(group, x + config.bodyPadLeft, y + bandHeight + 36, node.time, 'message-flow-sub message-flow-timestamp', 'start');

    var outcomeWidth = demo.chipWidth(node.outcome);
    demo.addChip(group, x + width - 10 - outcomeWidth, y + bandHeight + 14, node.outcome, node.outcomeKind, false);
};

// /////////////////////////////////////////////////////////////////////////////
// The drawing - one message, its deliveries
// /////////////////////////////////////////////////////////////////////////////

demo.render = function() {
    var config = demo.config;

    var hubX = 24;
    var hubWidth = 200;
    var hubHeight = 64;
    var fanX = 264;
    var rowGap = 30;
    var marginTop = 28;

    // Each exchange wears the id of the arrival that started it
    var rows = [
        [
            {id: '8272', direction: 'in', eventType: 'message-received', channel: 'demo.hl7.adt.main',
                time: '2 days ago \u00b7 16:55:37.962', outcome: 'ACK AE', outcomeKind: 'bad',
                connectorLabel: ''}
        ],
        [
            {id: '4594', direction: 'in', eventType: 'message-received', channel: 'demo.hl7.oru.lab',
                time: 'Yesterday \u00b7 20:00:11.156', outcome: 'ACK AE', outcomeKind: 'bad',
                connectorLabel: ''},
            {id: '9198', direction: 'in', eventType: 'message-received', channel: 'demo.hl7.adt.main',
                time: 'Today \u00b7 00:47:32.525', outcome: 'ACK AA', outcomeKind: 'good',
                connectorLabel: 'Reprocessed \u00b7 +4h 47m 21s'},
            {id: '9199', direction: 'out', eventType: 'sent', channel: 'demo.hl7.forward',
                time: 'Today \u00b7 00:47:32.546', outcome: 'OK', outcomeKind: 'good',
                connectorLabel: '+0.021s'}
        ],
        [
            {id: '9194', direction: 'in', eventType: 'message-received', channel: 'demo.hl7.adt.main',
                time: 'Yesterday \u00b7 20:00:14.421', outcome: 'ACK AA', outcomeKind: 'good',
                connectorLabel: ''}
        ]
    ];

    // A labelled connector is long enough for its chip, a bare one stays short
    var longConnector = 190;
    var shortConnector = 84;

    var rowStride = config.boxHeight + rowGap;
    var height = marginTop + rows.length * rowStride - rowGap + 28;
    var width = fanX + config.boxWidth + longConnector + config.boxWidth + shortConnector + config.boxWidth + 28;

    var svg = demo.newSVG('message-flow-canvas', width, height);

    demo.addDefs(svg);

    // A connector aims at the centre of a node's main section, under the title band
    var bodyCenterOffset = config.bandHeight + (config.boxHeight - config.bandHeight) / 2;

    var hubCenterY = marginTop + 1 * rowStride + bodyCenterOffset;
    var hubRight = hubX + hubWidth;
    var fanElbowX = hubRight + 16;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var y = marginTop + rowIndex * rowStride;
        var centerY = y + bodyCenterOffset;

        var branch = demo.addGroup(svg, 'message-flow-branch');

        // The branch from the message to this delivery's first station
        demo.addRoundedPath(branch, [
            [hubRight, hubCenterY],
            [fanElbowX, hubCenterY],
            [fanElbowX, centerY],
            [fanX, centerY]
        ], 'message-flow-connector');
        demo.addArrow(branch, fanX, centerY, 'message-flow-connector-arrow');

        var x = fanX;

        for (var boxIndex = 0; boxIndex < row.length; boxIndex++) {
            var node = row[boxIndex];

            // From the second station on, the connector to it carries the words
            // of how the message got there, worn as a chip on the line
            if (boxIndex > 0) {
                var connectorLength = shortConnector;

                if (node.connectorLabel.length > 10) {
                    connectorLength = longConnector;
                }

                demo.addPolyline(branch, [[x, centerY], [x + connectorLength, centerY]], 'message-flow-connector');
                demo.addArrow(branch, x + connectorLength, centerY, 'message-flow-connector-arrow');

                var chipWidth = demo.chipWidth(node.connectorLabel);
                var chipX = x + (connectorLength - chipWidth) / 2;

                demo.addChip(branch, chipX, centerY - config.chipHeight / 2, node.connectorLabel, 'muted', true);

                x += connectorLength;
            }

            demo.addNode(branch, x, y, node);
            x += config.boxWidth;
        }
    }

    // The message itself, standing before all of its deliveries
    var hub = demo.addGroup(svg, 'message-flow-node message-flow-node-selectable');
    var hubTop = hubCenterY - hubHeight / 2;

    demo.addRect(hub, hubX, hubTop, hubWidth, hubHeight, 'message-flow-box', 4);
    demo.addPolyline(hub, [[hubX + 4, hubTop + 1], [hubX + hubWidth - 4, hubTop + 1]], 'message-flow-rim');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY - 8, 'ORU^R01', 'message-flow-title', 'middle');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY + 14, 'FEED-00000020', 'message-flow-control-id', 'middle');

    demo.wireDrawing(svg);
};

// /////////////////////////////////////////////////////////////////////////////

// A branch under the pointer stays lit while the rest of the room dims. A click
// on a node selects it - the amber border - and holds its branch lit until the
// node is clicked again or the empty canvas is.
demo.wireDrawing = function(svg) {
    var branches = svg.querySelectorAll('.message-flow-branch');
    var nodes = svg.querySelectorAll('.message-flow-node-selectable');

    demo.selectedNode = null;

    // The pending return to full light - leaving a branch only starts it, and
    // reaching another branch in time cancels it, so walking the pointer from
    // node to node never lets the room flicker back between them
    var unlitTimer = null;

    var cancelUnlit = function() {
        if (unlitTimer !== null) {
            window.clearTimeout(unlitTimer);
            unlitTimer = null;
        }
    };

    var clearLit = function() {
        cancelUnlit();

        for (var branchIndex = 0; branchIndex < branches.length; branchIndex++) {
            branches[branchIndex].classList.remove('message-flow-lit');
        }

        svg.classList.remove('message-flow-focus');
    };

    var setLit = function(branch) {
        clearLit();
        branch.classList.add('message-flow-lit');
        svg.classList.add('message-flow-focus');
    };

    var scheduleUnlit = function() {
        cancelUnlit();
        unlitTimer = window.setTimeout(clearLit, demo.config.dimHoldMs);
    };

    var clearSelection = function() {
        if (demo.selectedNode !== null) {
            demo.selectedNode.classList.remove('message-flow-node-selected');
            demo.selectedNode = null;
        }
    };

    for (var branchIndex = 0; branchIndex < branches.length; branchIndex++) {

        var wireBranch = function(branch) {

            branch.addEventListener('mouseenter', function() {
                if (demo.selectedNode === null) {
                    setLit(branch);
                }
            });

            branch.addEventListener('mouseleave', function() {
                if (demo.selectedNode === null) {
                    scheduleUnlit();
                }
            });
        };

        wireBranch(branches[branchIndex]);
    }

    for (var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {

        var wireNode = function(node) {

            node.addEventListener('click', function(event) {
                event.stopPropagation();

                // A second click on the picked node lets everything go
                if (demo.selectedNode === node) {
                    clearSelection();
                    clearLit();
                    return;
                }

                clearSelection();

                demo.selectedNode = node;
                node.classList.add('message-flow-node-selected');

                // The picked node's whole branch stays lit around it - the root
                // stands outside every branch and dims nothing when picked
                var branch = node.closest('.message-flow-branch');

                if (branch !== null) {
                    setLit(branch);
                }
                else {
                    clearLit();
                }
            });
        };

        wireNode(nodes[nodeIndex]);
    }

    // A click on the empty canvas lets a held selection go
    svg.addEventListener('click', function() {
        if (demo.selectedNode !== null) {
            clearSelection();
            clearLit();
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    demo.render();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
