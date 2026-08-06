
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

    // One node card and its regions - the title band and, under it, one line
    // for each half of the exchange. A node is as wide as its own words need,
    // so the ruling measures of each script are written down here.
    boxHeight: 74,
    bandHeight: 22,
    lineTop: 6,
    lineStride: 22,

    // The writing inside a node
    bodyPadLeft: 10,

    // How wide one character runs in each of the scripts a node is written in,
    // and the least room kept between a line's words and its timestamp
    titleCharWidth: 6.6,
    typeCharWidth: 6.2,
    subCharWidth: 6,
    lineMinGap: 18,

    // Chips - height, side padding and how wide one character runs, with the
    // direction chips sharing one width so their column lines up
    chipHeight: 16,
    chipPadX: 6,
    chipCharWidth: 6,
    directionChipWidth: 46,

    // The word each kind of line wears - what arrived on a channel, the request
    // an outgoing connection made, and the answer either of them got
    directionLabels: {
        'in': 'IN',
        'request': 'REQ',
        'reply': 'REPLY'
    },

    // Connectors - a labelled one is long enough for its chip, a bare one is short
    connectorLong: 190,
    connectorShort: 84,

    // Connectors - the corner radius of an elbow and the arrowhead
    elbowRadius: 6,
    arrowLength: 8,
    arrowWidth: 4.5,

    // How long a left branch stays lit - long enough to walk the pointer over
    // the gap to the next one without the room flickering back to light
    dimHoldMs: 180,

    // Dragging the canvas - how far the pointer travels before a press becomes
    // a drag, how much of the let-go speed survives each frame, the speed at
    // which the glide is over, and the frame the pointer's speed is scaled to
    panDragThreshold: 4,
    panFriction: 0.92,
    panMinSpeed: 0.4,
    panVelocityFrameMs: 16
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

// A direction chip - every in and out shares one width, so the pairs line up
demo.addDirectionChip = function(host, x, y, label, kind) {
    var config = demo.config;

    var width = config.directionChipWidth;

    demo.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-' + kind, 3);
    demo.addText(host, x + width / 2, y + 12, label, 'message-flow-chip-text message-flow-chip-text-' + kind, 'middle');

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// One half of an exchange written on its own line - the direction, the event's
// own id, what the event was, and when it happened, on the right
demo.addEventLine = function(group, x, lineY, width, event) {
    var config = demo.config;

    var cursor = x + config.bodyPadLeft;

    cursor += demo.addDirectionChip(group, cursor, lineY, config.directionLabels[event.direction], event.direction);
    cursor += 6;
    cursor += demo.addChip(group, cursor, lineY, event.id, 'id', false);
    cursor += 8;

    // A plain event type is written as a tag, an outcome is worn as a chip
    if (event.kind === 'type') {
        demo.addText(group, cursor, lineY + 12, event.label.toUpperCase(), 'message-flow-band-type', 'start');
    }
    else {
        demo.addChip(group, cursor, lineY, event.label, event.kind, false);
    }

    demo.addText(group, x + width - config.bodyPadLeft, lineY + 12, event.time,
        'message-flow-sub message-flow-timestamp', 'end');
};

// /////////////////////////////////////////////////////////////////////////////

// The line for the reply that never came - the same word the answered
// exchanges wear, and the plain word that there was nothing
demo.addMissingLine = function(group, x, lineY) {
    var config = demo.config;

    var cursor = x + config.bodyPadLeft;

    cursor += demo.addDirectionChip(group, cursor, lineY, demo.config.directionLabels['reply'], 'muted');
    cursor += 8;

    demo.addText(group, cursor, lineY + 12, 'none', 'message-flow-sub', 'start');
};

// /////////////////////////////////////////////////////////////////////////////

// How wide one node has to be for its own words - the channel across the band
// and the longer of its two lines, each line being its chips, its label and its
// timestamp with breathing room between them
demo.nodeWidth = function(node) {
    var config = demo.config;

    var width = config.bodyPadLeft + 2 + Math.round(node.channel.length * config.titleCharWidth) + config.bodyPadLeft;

    for (var lineIndex = 0; lineIndex < node.events.length; lineIndex++) {
        var event = node.events[lineIndex];

        if (event === null) {
            continue;
        }

        var labelWidth;

        if (event.kind === 'type') {
            labelWidth = Math.round(event.label.length * config.typeCharWidth);
        }
        else {
            labelWidth = demo.chipWidth(event.label);
        }

        var timeWidth = Math.round(event.time.length * config.subCharWidth);

        var lineWidth = config.bodyPadLeft + config.directionChipWidth + 6 + demo.chipWidth(event.id) + 8 +
            labelWidth + config.lineMinGap + timeWidth + config.bodyPadLeft;

        if (lineWidth > width) {
            width = lineWidth;
        }
    }

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// How long the connector into a node runs - a labelled one long enough for its
// chip to sit on it with the line showing on both sides, a bare one short
demo.connectorLength = function(node) {
    var config = demo.config;

    if (node.connectorLabel.length > 10) {
        return config.connectorLong;
    }

    return config.connectorShort;
};

// /////////////////////////////////////////////////////////////////////////////

// One node - the lit card for a whole exchange: gradient face, top rim, the
// channel across the title band, and one line per half of the pair under it,
// so the in and the out are read together, each with its own id and time
demo.addNode = function(host, x, y, width, node) {
    var config = demo.config;

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

    // The band carries the channel the exchange happened on
    demo.addText(group, x + config.bodyPadLeft + 2, y + 15, node.channel, 'message-flow-title', 'start');

    // The two halves of the pair, each on its own line
    for (var lineIndex = 0; lineIndex < node.events.length; lineIndex++) {
        var event = node.events[lineIndex];
        var lineY = y + bandHeight + config.lineTop + lineIndex * config.lineStride;

        if (event === null) {
            demo.addMissingLine(group, x, lineY);
        }
        else {
            demo.addEventLine(group, x, lineY, width, event);
        }
    }
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

    // Each node is a whole exchange - the pair of the event that came in and the
    // one that went out answering it, each with its own id and its own time, and
    // a half that never happened saying so
    var rows = [
        [
            {channel: 'demo.hl7.adt.main', connectorLabel: '', events: [
                {direction: 'in', id: '8272', kind: 'type', label: 'message-received', time: '2 days ago \u00b7 16:55:37.962'},
                {direction: 'reply', id: '8273', kind: 'bad', label: 'ACK AE', time: '2 days ago \u00b7 16:55:38.171'}
            ]}
        ],
        [
            {channel: 'demo.hl7.oru.lab', connectorLabel: '', events: [
                {direction: 'in', id: '4594', kind: 'type', label: 'message-received', time: 'Yesterday \u00b7 20:00:11.156'},
                {direction: 'reply', id: '4595', kind: 'bad', label: 'ACK AE', time: 'Yesterday \u00b7 20:00:11.157'}
            ]},
            {channel: 'demo.hl7.oru.lab', connectorLabel: 'Reprocessed \u00b7 +4h 47m 21s', events: [
                {direction: 'in', id: '9198', kind: 'type', label: 'message-received', time: 'Today \u00b7 00:47:32.525'},
                {direction: 'reply', id: '9200', kind: 'good', label: 'ACK AA', time: 'Today \u00b7 00:47:32.526'}
            ]},
            {channel: 'demo.hl7.forward', connectorLabel: '+0.021s', events: [
                {direction: 'request', id: '9199', kind: 'type', label: 'sent', time: 'Today \u00b7 00:47:32.546'},
                null
            ]}
        ],
        [
            {channel: 'demo.hl7.adt.main', connectorLabel: '', events: [
                {direction: 'in', id: '9194', kind: 'type', label: 'message-received', time: 'Yesterday \u00b7 20:00:14.421'},
                {direction: 'reply', id: '9195', kind: 'good', label: 'ACK AA', time: 'Yesterday \u00b7 20:00:14.421'}
            ]}
        ]
    ];

    var rowStride = config.boxHeight + rowGap;
    var height = marginTop + rows.length * rowStride - rowGap + 28;

    // Every node is as wide as its own words, so the drawing's width is the
    // longest row's - each row being its nodes and the connectors between them
    var width = 0;

    for (var measureIndex = 0; measureIndex < rows.length; measureIndex++) {
        var measuredRow = rows[measureIndex];
        var rowWidth = fanX;

        for (var measureBoxIndex = 0; measureBoxIndex < measuredRow.length; measureBoxIndex++) {
            if (measureBoxIndex > 0) {
                rowWidth += demo.connectorLength(measuredRow[measureBoxIndex]);
            }

            rowWidth += demo.nodeWidth(measuredRow[measureBoxIndex]);
        }

        if (rowWidth > width) {
            width = rowWidth;
        }
    }

    width += 28;

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
                var connectorLength = demo.connectorLength(node);

                demo.addPolyline(branch, [[x, centerY], [x + connectorLength, centerY]], 'message-flow-connector');
                demo.addArrow(branch, x + connectorLength, centerY, 'message-flow-connector-arrow');

                var chipWidth = demo.chipWidth(node.connectorLabel);
                var chipX = x + (connectorLength - chipWidth) / 2;

                demo.addChip(branch, chipX, centerY - config.chipHeight / 2, node.connectorLabel, 'muted', true);

                x += connectorLength;
            }

            var nodeWidth = demo.nodeWidth(node);

            demo.addNode(branch, x, y, nodeWidth, node);
            x += nodeWidth;
        }
    }

    // The message itself, standing before all of its deliveries
    var hub = demo.addGroup(svg, 'message-flow-node message-flow-node-selectable message-flow-root');
    var hubTop = hubCenterY - hubHeight / 2;

    demo.addRect(hub, hubX, hubTop, hubWidth, hubHeight, 'message-flow-box', 4);
    demo.addPolyline(hub, [[hubX + 4, hubTop + 1], [hubX + hubWidth - 4, hubTop + 1]], 'message-flow-rim');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY - 8, 'ORU^R01', 'message-flow-title', 'middle');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY + 14, 'FEED-00000020', 'message-flow-control-id', 'middle');

    demo.wireDrawing(svg);
    demo.wirePanning(document.getElementById('message-flow-canvas'));
};

// /////////////////////////////////////////////////////////////////////////////

// The canvas is walked by grabbing it - a press and a pull scroll it directly,
// and letting go mid-motion sends it gliding on, friction bleeding the speed
// off frame by frame until it settles
demo.wirePanning = function(host) {
    var config = demo.config;

    var isPressed = false;
    var hasDragged = false;

    var startPointerX = 0;
    var startPointerY = 0;
    var startScrollLeft = 0;
    var startScrollTop = 0;

    var lastPointerX = 0;
    var lastPointerY = 0;
    var lastMoveTime = 0;

    var velocityX = 0;
    var velocityY = 0;
    var glideFrame = null;

    var stopGlide = function() {
        if (glideFrame !== null) {
            window.cancelAnimationFrame(glideFrame);
            glideFrame = null;
        }
    };

    var glideStep = function() {
        host.scrollLeft -= velocityX;
        host.scrollTop -= velocityY;

        // Friction takes its share of the speed every frame
        velocityX *= config.panFriction;
        velocityY *= config.panFriction;

        var speed = Math.sqrt(velocityX * velocityX + velocityY * velocityY);

        // Slow enough is stopped - anything further would be invisible anyway
        if (speed < config.panMinSpeed) {
            glideFrame = null;
            return;
        }

        glideFrame = window.requestAnimationFrame(glideStep);
    };

    host.addEventListener('mousedown', function(event) {

        // Only the main button grabs the canvas
        if (event.button !== 0) {
            return;
        }

        // A new grab takes over from any glide still running
        stopGlide();

        isPressed = true;
        hasDragged = false;

        startPointerX = event.clientX;
        startPointerY = event.clientY;
        startScrollLeft = host.scrollLeft;
        startScrollTop = host.scrollTop;

        lastPointerX = event.clientX;
        lastPointerY = event.clientY;
        lastMoveTime = window.performance.now();

        velocityX = 0;
        velocityY = 0;

        // The press must not start selecting the drawing's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) {
            return;
        }

        var deltaX = event.clientX - startPointerX;
        var deltaY = event.clientY - startPointerY;

        // A press only becomes a drag once the pointer has really travelled,
        // so plain clicks on nodes stay clicks
        if (!hasDragged) {
            if (Math.abs(deltaX) < config.panDragThreshold && Math.abs(deltaY) < config.panDragThreshold) {
                return;
            }

            hasDragged = true;
            host.classList.add('message-flow-panning');
        }

        host.scrollLeft = startScrollLeft - deltaX;
        host.scrollTop = startScrollTop - deltaY;

        // The pointer's speed right now, scaled to one frame - what the glide
        // will start from if the grab ends here
        var now = window.performance.now();
        var elapsed = now - lastMoveTime;

        if (elapsed > 0) {
            velocityX = (event.clientX - lastPointerX) / elapsed * config.panVelocityFrameMs;
            velocityY = (event.clientY - lastPointerY) / elapsed * config.panVelocityFrameMs;
        }

        lastPointerX = event.clientX;
        lastPointerY = event.clientY;
        lastMoveTime = now;
    });

    window.addEventListener('mouseup', function() {
        if (!isPressed) {
            return;
        }

        isPressed = false;
        host.classList.remove('message-flow-panning');

        // The pull's parting speed carries the canvas on
        if (hasDragged) {
            glideFrame = window.requestAnimationFrame(glideStep);
        }
    });

    // A drag must not land as a click on whatever node it happened to end over
    host.addEventListener('click', function(event) {
        if (hasDragged) {
            event.stopPropagation();
            event.preventDefault();
            hasDragged = false;
        }
    }, true);
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

    // The root belongs to every branch, so under it they all stay lit and only
    // the room around the drawing falls dark
    var setLitAll = function() {
        cancelUnlit();

        for (var branchIndex = 0; branchIndex < branches.length; branchIndex++) {
            branches[branchIndex].classList.add('message-flow-lit');
        }

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

    // The root lights the whole drawing the way a branch lights itself
    var root = svg.querySelector('.message-flow-root');

    root.addEventListener('mouseenter', function() {
        if (demo.selectedNode === null) {
            setLitAll();
        }
    });

    root.addEventListener('mouseleave', function() {
        if (demo.selectedNode === null) {
            scheduleUnlit();
        }
    });

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

                // The picked node's whole branch stays lit around it, and the
                // root, standing outside every branch, keeps them all lit
                var branch = node.closest('.message-flow-branch');

                if (branch !== null) {
                    setLit(branch);
                }
                else {
                    setLitAll();
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
