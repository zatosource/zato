
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the drawing. One message's journey drawn from its flow rows - the
// message on the left, each exchange of it a lit card to the right, exchanges that
// grew out of another one chained behind a labelled connector. The rows come from
// the journey endpoint and arrive as the flow rows the List tab reads, so what is drawn is
// what the list says.

$.fn.zato.message_flow = {};
$.fn.zato.message_flow.drawing = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var drawing = $.fn.zato.message_flow.drawing;

// /////////////////////////////////////////////////////////////////////////////

drawing.config = {

    // Where the drawing lives
    canvasId: 'message-flow-canvas',

    // One node card and its regions - the title band and, under it, one line
    // for each event of the exchange. A node is as wide as its own words need
    // and as tall as it has lines, so the ruling measures of each script are
    // written down here.
    bandHeight: 22,
    lineTop: 6,
    lineStride: 22,
    lineBottomPad: 2,

    // The strip across every node's foot, where the node says how long after
    // the flow's first moment its own exchange began
    footerHeight: 19,

    // The writing inside a node
    bodyPadLeft: 10,

    // How wide one character runs in each of the scripts a node is written in,
    // and the least room kept between a line's words and its timestamp
    titleCharWidth: 6.6,
    typeCharWidth: 6.2,
    subCharWidth: 6,
    lineMinGap: 18,

    // Chips - height, side padding and how wide one character runs, the run
    // including the letter-spacing the chip text wears, so a long label still
    // ends before its padding does
    chipHeight: 16,
    chipPadX: 6,
    chipCharWidth: 6.4,
    roleChipWidth: 70,

    // The word each kind of line wears - the part the event played in its exchange,
    // and a pair of eyes reading a message after the fact
    roleLabels: {
        'request': 'REQ',
        'response': 'REPLY',
        'none': 'SYS',
        'view': 'VIEW',
        'job': 'SCHEDULER'
    },

    // The one event type that is a person reading rather than a message moving
    viewEventType: 'content-viewed',

    // What the hub's top line says when the seed's source has no message id
    // of its own and the message reads by its CID alone
    cidLabel: 'CID',

    // The outcome worn as a good chip - every other reported outcome is a bad one
    goodOutcome: 'ok',

    // The word a connector wears for why the chained exchange exists at all -
    // relations that name no event in particular never chain, so they are not here
    relationWords: {
        'resubmit-of': 'Resubmitted',
        'resubmitted-as': 'Resubmitted',
        'parent': 'Linked',
        'child': 'Linked'
    },

    // What stands between the day and the time of day on a node's lines
    labelSeparator: ' \u00b7 ',

    // How much of a labelled connector's line shows on each side of its chip,
    // whatever the chip's own width turns out to be
    connectorLineReach: 30,

    // Connectors - the corner radius of an elbow, the arrowhead, and how far
    // past a node's edge a branch connector swings before it drops
    elbowRadius: 6,
    arrowLength: 8,
    arrowWidth: 4.5,
    branchElbowOffset: 16,

    // The message itself, standing before its deliveries - two lines tall when
    // it has a control id to show under its name, one line tall when it does not
    hubX: 24,
    hubMinWidth: 200,
    hubHeight: 64,
    hubHeightOneLine: 40,
    hubFanGap: 40,

    // The room the drawing keeps around itself
    marginTop: 28,
    marginBottom: 28,
    marginRight: 28,
    rowGap: 30,

    // The least room a chip keeps to any card it steers clear of
    chipClearance: 4,

    // How long a branch stays lit - long enough to walk the pointer over
    // the gap to the next one without the room flickering back to light
    dimHoldMs: 180,

    // Dragging the canvas - how far the pointer travels before a press becomes
    // a drag, how much of the let-go speed survives each frame, the speed at
    // which the glide is over, and the frame the pointer's speed is scaled to
    panDragThreshold: 4,
    panFriction: 0.92,
    panMinSpeed: 0.4,
    panVelocityFrameMs: 16,

    // Where the browser keeps how closely the drawing was being looked at
    zoomStorageKey: 'zato.message-flow.zoom',

    // Where a click does not let a held selection go - the pane the selection
    // is being read in, the bar over it, and the replay's own bar
    deselectExemptSelector: '#message-flow-detail, #message-flow-resize, #message-flow-replay-bar, .message-flow-replay-dock'
};

// /////////////////////////////////////////////////////////////////////////////

// The details the nodes on the canvas stand for, by their place in this register,
// and the node the reader picked - held by its element and by its exchange key,
// which is what the amber on its connector is set and cleared by
drawing.nodeDetails = [];
drawing.selectedNode = null;
drawing.selectedKey = '';

// Lets a held selection go - each render leaves its own here, closing over that
// drawing's nodes and branches, and there is nothing to let go before the first one
drawing.deselect = null;

// How closely the drawing is looked at - created once, in init
drawing.zoom = null;

// /////////////////////////////////////////////////////////////////////////////

drawing.canvas = function() {
    return document.getElementById(drawing.config.canvasId);
};

// /////////////////////////////////////////////////////////////////////////////
// The SVG helpers the kit's primitives do not carry - groups, elbowed paths,
// right-pointing arrowheads and chips
// /////////////////////////////////////////////////////////////////////////////

drawing.newSVG = function(width, height) {
    var svg = kit.draw.createElement('svg');

    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);

    drawing.canvas().appendChild(svg);

    return svg;
};

// /////////////////////////////////////////////////////////////////////////////

// The gradient every node face is filled with - a touch of light along the top
// falling away toward the foot, the way the flow's raised cards catch it
drawing.addDefs = function(svg) {
    var defs = kit.draw.createElement('defs');

    var gradient = kit.draw.createElement('linearGradient');
    gradient.setAttribute('id', 'message-flow-node-fill');
    gradient.setAttribute('x1', '0');
    gradient.setAttribute('y1', '0');
    gradient.setAttribute('x2', '0');
    gradient.setAttribute('y2', '1');

    var stopTop = kit.draw.createElement('stop');
    stopTop.setAttribute('offset', '0');
    stopTop.setAttribute('stop-color', '#3a3a5c');

    var stopBottom = kit.draw.createElement('stop');
    stopBottom.setAttribute('offset', '1');
    stopBottom.setAttribute('stop-color', '#2d2d48');

    gradient.appendChild(stopTop);
    gradient.appendChild(stopBottom);
    defs.appendChild(gradient);
    svg.appendChild(defs);
};

// /////////////////////////////////////////////////////////////////////////////

drawing.addGroup = function(host, className) {
    var group = kit.draw.createElement('g');

    group.setAttribute('class', className);
    host.appendChild(group);

    return group;
};

// /////////////////////////////////////////////////////////////////////////////

drawing.addPolyline = function(host, points, className) {
    var line = kit.draw.createElement('polyline');

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
drawing.addRoundedPath = function(host, points, className) {
    var radius = drawing.config.elbowRadius;
    var path = kit.draw.createElement('path');

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
drawing.addArrow = function(host, x, y, className) {
    var config = drawing.config;
    var arrow = kit.draw.createElement('path');

    var d = 'M ' + (x - config.arrowLength) + ' ' + (y - config.arrowWidth) +
            ' L ' + (x - config.arrowLength) + ' ' + (y + config.arrowWidth) +
            ' L ' + x + ' ' + y + ' Z';

    arrow.setAttribute('d', d);
    arrow.setAttribute('class', className);

    host.appendChild(arrow);

    return arrow;
};

// /////////////////////////////////////////////////////////////////////////////

drawing.chipWidth = function(label) {
    var config = drawing.config;
    return Math.round(label.length * config.chipCharWidth + 2 * config.chipPadX);
};

// /////////////////////////////////////////////////////////////////////////////

// A chip - the same tinted tag the listing and the list wear. On the canvas it
// stands on a solid backing so a connector running under it is hidden.
drawing.addChip = function(host, x, y, label, kind, onCanvas) {
    var config = drawing.config;

    var width = drawing.chipWidth(label);

    if (onCanvas) {
        kit.draw.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-back', 3);
    }

    kit.draw.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-' + kind, 3);
    kit.draw.addText(host, x + width / 2, y + 12, label, 'message-flow-chip-text message-flow-chip-text-' + kind, 'middle');

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// One connector - the line and the arrowhead - held in a group of its own that
// says which branch and which node it leads into and out of what, which is what
// lets it light with its branch and lets the replay draw it in as its node's
// moment comes.
drawing.addConnectorSet = function(connectorLayer, branchIndex, toKey, fromKey) {
    var group = drawing.addGroup(connectorLayer, 'message-flow-connector-set');

    group.setAttribute('data-branch-index', branchIndex);
    group.setAttribute('data-connector-to', toKey);
    group.setAttribute('data-connector-from', fromKey);

    return group;
};

// /////////////////////////////////////////////////////////////////////////////

// One connector's words, held in the layer over the whole drawing - painted
// after every line and every card, so nothing can run through them, while the
// words themselves steer clear of the cards, so they stand on lines only. The
// group knows its branch, so it lights and dims with it, and the connector it
// speaks for.
drawing.addChipGroup = function(chipLayer, branchIndex, toKey) {
    var group = drawing.addGroup(chipLayer, 'message-flow-connector-chip');

    group.setAttribute('data-branch-index', branchIndex);
    group.setAttribute('data-connector-to', toKey);

    return group;
};

// /////////////////////////////////////////////////////////////////////////////

// Every card's box, for the chips to steer clear of - filled anew by each
// render, read both while the drawing goes up and when the replay writes its
// own elapsed words onto it
drawing.nodeRects = [];

// /////////////////////////////////////////////////////////////////////////////

// Where on its run a chip can stand without standing on any card - the spot it
// asks for when that spot is clear, otherwise the clear spot nearest to it
// along the run, and the asked-for spot again when the whole run is covered
drawing.clearChipX = function(desiredX, chipWidth, chipTop, chipBottom, runFromX, runToX) {
    var clearance = drawing.config.chipClearance;

    var lowX = runFromX + clearance;
    var highX = runToX - chipWidth - clearance;

    // A run too short to choose on - the chip stands where it was asked to
    if (highX < lowX) {
        return desiredX;
    }

    if (desiredX < lowX) {
        desiredX = lowX;
    }

    if (desiredX > highX) {
        desiredX = highX;
    }

    // Only the cards sharing the chip's vertical band can be stood on
    var blockers = [];

    for (var rectIndex = 0; rectIndex < drawing.nodeRects.length; rectIndex++) {
        var rect = drawing.nodeRects[rectIndex];

        if (rect.top < chipBottom && chipTop < rect.bottom) {
            blockers.push(rect);
        }
    }

    var isClear = function(x) {
        for (var blockerIndex = 0; blockerIndex < blockers.length; blockerIndex++) {
            var blocker = blockers[blockerIndex];

            if (blocker.left < x + chipWidth + clearance && x - clearance < blocker.right) {
                return false;
            }
        }

        return true;
    };

    if (isClear(desiredX)) {
        return desiredX;
    }

    // The clear spots hug the covering cards' edges - the one nearest to the
    // asked-for spot wins
    var bestX = desiredX;
    var bestDistance = Infinity;

    for (var edgeIndex = 0; edgeIndex < blockers.length; edgeIndex++) {
        var edgeBlocker = blockers[edgeIndex];

        var candidates = [edgeBlocker.left - chipWidth - clearance, edgeBlocker.right + clearance];

        for (var sideIndex = 0; sideIndex < candidates.length; sideIndex++) {
            var candidate = candidates[sideIndex];

            if (candidate < lowX || candidate > highX) {
                continue;
            }

            if (!isClear(candidate)) {
                continue;
            }

            var distance = Math.abs(candidate - desiredX);

            if (distance < bestDistance) {
                bestDistance = distance;
                bestX = candidate;
            }
        }
    }

    return bestX;
};

// /////////////////////////////////////////////////////////////////////////////

// A role chip - every one shares one width, so the lines of a node line up
drawing.addRoleChip = function(host, x, y, label, kind) {
    var config = drawing.config;

    var width = config.roleChipWidth;

    kit.draw.addRect(host, x, y, width, config.chipHeight, 'message-flow-chip-' + kind, 3);
    kit.draw.addText(host, x + width / 2, y + 12, label, 'message-flow-chip-text message-flow-chip-text-' + kind, 'middle');

    return width;
};

// /////////////////////////////////////////////////////////////////////////////
// From the flow models to the drawing's own shapes
// /////////////////////////////////////////////////////////////////////////////

// One event written as one line of a node - the role, the event's own id,
// what happened or how it turned out, and when
drawing.lineOf = function(model) {
    var config = drawing.config;

    var role = model.role;

    // A person reading a stored message is its own kind of line
    if (model.eventType === config.viewEventType) {
        role = 'view';
    }

    var line = {
        role: role,
        id: String(model.id),
        time: kit.time_ago_label(model.timeIso) + config.labelSeparator + model.timeLocal.slice(11)
    };

    // An event that reports no outcome is read by what it was, one that does
    // is read by how it went
    if (model.outcome === '') {
        line.kind = 'type';
        line.label = model.eventLabel;
    }
    else if (model.outcome === config.goodOutcome) {
        line.kind = 'good';
        line.label = model.outcome.toUpperCase();
    }
    else {
        line.kind = 'bad';
        line.label = model.outcome.toUpperCase();
    }

    return line;
};

// /////////////////////////////////////////////////////////////////////////////

// The flow's models regrouped into exchanges - the events of one cid on one
// object read as one card, oldest first inside it, the cards themselves oldest
// first too. An event with no cid stands as a card of its own.
drawing.buildExchanges = function(models) {
    var list = [];
    var byKey = {};
    var keyByEventId = {};

    // The models arrive newest first the way the list reads - the drawing
    // reads time forward
    var ascending = models.slice().reverse();

    for (var modelIndex = 0; modelIndex < ascending.length; modelIndex++) {
        var model = ascending[modelIndex];

        var key;

        if (model.cid === '') {
            key = 'event-' + model.id;
        }
        else {
            key = model.cid + '|' + model.objectName;
        }

        if (!(key in byKey)) {
            var exchange = {
                key: key,
                objectName: model.objectName,
                source: model.source,
                models: [],
                parentKey: '',
                connectorLabel: ''
            };

            byKey[key] = exchange;
            list.push(exchange);
        }

        byKey[key].models.push(model);
        keyByEventId[String(model.id)] = key;
    }

    return {list: list, byKey: byKey, keyByEventId: keyByEventId};
};

// /////////////////////////////////////////////////////////////////////////////

// When an exchange begins, which is what two linked exchanges are ordered by
drawing.firstMsOf = function(exchange) {
    var out = new Date(exchange.models[0].timeIso).getTime();
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The pointed relations chained onto the cards - an event found through an event
// of another exchange hangs that exchange behind this one, the later of the two
// always behind the earlier, wearing the relation's word
drawing.linkExchanges = function(exchanges, models) {
    var config = drawing.config;

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        var model = models[modelIndex];

        if (!model.viaId) {
            continue;
        }

        var ownKey = exchanges.keyByEventId[String(model.id)];
        var viaKey = exchanges.keyByEventId[String(model.viaId)];

        // A via pointing inside the same card says nothing about the cards
        if (viaKey === undefined || ownKey === viaKey) {
            continue;
        }

        var own = exchanges.byKey[ownKey];
        var via = exchanges.byKey[viaKey];

        var earlier = own;
        var later = via;

        if (drawing.firstMsOf(own) > drawing.firstMsOf(via)) {
            earlier = via;
            later = own;
        }

        // The first link an exchange is found under is the one it keeps
        if (later.parentKey !== '') {
            continue;
        }

        var word = config.relationWords[model.relation];

        // A shared relation names no event in particular and chains nothing
        if (word === undefined) {
            continue;
        }

        later.parentKey = earlier.key;

        // The connector carries the relation's word alone - how long after the
        // flow began each exchange spoke is on the exchange's own footer
        later.connectorLabel = word;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The cards laid out into rows - an exchange with no parent starts a row off the
// hub, its first child continues the row rightward, and every further child opens
// a row of its own right under, hanging off the parent card rather than the hub
drawing.buildLayoutRows = function(exchanges) {
    var rows = [];

    var childrenByKey = {};

    for (var exchangeIndex = 0; exchangeIndex < exchanges.list.length; exchangeIndex++) {
        var exchange = exchanges.list[exchangeIndex];

        if (exchange.parentKey === '') {
            continue;
        }

        if (!(exchange.parentKey in childrenByKey)) {
            childrenByKey[exchange.parentKey] = [];
        }

        childrenByKey[exchange.parentKey].push(exchange);
    }

    var placeChain = function(exchange, fromKey) {
        var row = [];
        rows.push(row);

        // The further children met along the chain, each to open a row of its own
        // right after this one
        var branches = [];

        var current = exchange;
        var from = fromKey;

        while (current !== null) {
            row.push({exchange: current, fromKey: from});

            var next = null;

            if (current.key in childrenByKey) {
                var children = childrenByKey[current.key];

                next = children[0];

                for (var childIndex = 1; childIndex < children.length; childIndex++) {
                    branches.push(children[childIndex]);
                }
            }

            from = current.key;
            current = next;
        }

        for (var branchIndex = 0; branchIndex < branches.length; branchIndex++) {
            placeChain(branches[branchIndex], branches[branchIndex].parentKey);
        }
    };

    for (var topIndex = 0; topIndex < exchanges.list.length; topIndex++) {
        var top = exchanges.list[topIndex];

        if (top.parentKey === '') {
            placeChain(top, '');
        }
    }

    return rows;
};

// /////////////////////////////////////////////////////////////////////////////
// The measures of one node
// /////////////////////////////////////////////////////////////////////////////

// How wide one node has to be for its own words - the channel across the band
// and the longest of its lines, each line being its chips, its label and its
// timestamp with breathing room between them
drawing.nodeWidth = function(node) {
    var config = drawing.config;

    var width = config.bodyPadLeft + 2 + Math.round(node.channel.length * config.titleCharWidth) + config.bodyPadLeft;

    for (var lineIndex = 0; lineIndex < node.lines.length; lineIndex++) {
        var line = node.lines[lineIndex];

        var labelWidth;

        if (line.kind === 'type') {
            labelWidth = Math.round(line.label.length * config.typeCharWidth);
        }
        else {
            labelWidth = drawing.chipWidth(line.label);
        }

        var timeWidth = Math.round(line.time.length * config.subCharWidth);

        var lineWidth = config.bodyPadLeft + config.roleChipWidth + 6 + drawing.chipWidth(line.id) + 8 +
            labelWidth + config.lineMinGap + timeWidth + config.bodyPadLeft;

        if (lineWidth > width) {
            width = lineWidth;
        }
    }

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// How long the connector into a chained node runs - always its own chip's width
// plus the same reach of visible line on either side, so no label can ever leave
// the line to be nothing but its arrowhead
drawing.connectorLength = function(node) {
    var config = drawing.config;
    return drawing.chipWidth(node.connectorLabel) + 2 * config.connectorLineReach;
};

// /////////////////////////////////////////////////////////////////////////////

// How tall one node stands - the band, one line for each event it holds, and
// the footer strip with the node's own elapsed words
drawing.nodeHeight = function(node) {
    var config = drawing.config;

    return config.bandHeight + config.lineTop + node.lines.length * config.lineStride +
        config.lineBottomPad + config.footerHeight;
};

// /////////////////////////////////////////////////////////////////////////////
// Drawing the parts
// /////////////////////////////////////////////////////////////////////////////

// One event of the exchange written on its own line
drawing.addEventLine = function(group, x, lineY, width, line) {
    var config = drawing.config;

    var cursor = x + config.bodyPadLeft;

    cursor += drawing.addRoleChip(group, cursor, lineY, config.roleLabels[line.role], line.role);
    cursor += 6;
    cursor += drawing.addChip(group, cursor, lineY, line.id, 'id', false);
    cursor += 8;

    // A plain event type is written as a tag, an outcome is worn as a chip
    if (line.kind === 'type') {
        kit.draw.addText(group, cursor, lineY + 12, line.label.toUpperCase(), 'message-flow-band-type', 'start');
    }
    else {
        drawing.addChip(group, cursor, lineY, line.label, line.kind, false);
    }

    kit.draw.addText(group, x + width - config.bodyPadLeft, lineY + 12, line.time,
        'message-flow-sub message-flow-timestamp', 'end');
};

// /////////////////////////////////////////////////////////////////////////////

// One node - the lit card for a whole exchange: gradient face, top rim, the
// channel across the title band, and one line per event under it
drawing.addNode = function(host, x, y, width, node) {
    var config = drawing.config;

    var height = drawing.nodeHeight(node);
    var bandHeight = config.bandHeight;

    var group = drawing.addGroup(host, 'message-flow-node message-flow-node-selectable');

    // Clicking the node opens its exchange under the drawing - the detail the
    // node stands for is remembered by its place in the register, and the key
    // is what the replay finds the node's connector by
    group.setAttribute('data-node-index', drawing.nodeDetails.length);
    group.setAttribute('data-exchange-key', node.key);

    drawing.nodeDetails.push({
        key: node.key,
        title: node.channel,
        time: node.lines[0].time,
        models: node.models,

        // Only the root sums the flow up - an exchange's card speaks for
        // its own events alone
        flowSummary: null
    });

    kit.draw.addRect(group, x, y, width, height, 'message-flow-box', 4);

    // The band keeps the node's rounded top and is squared off at its own foot
    kit.draw.addRect(group, x, y, width, bandHeight, 'message-flow-band', 4);
    kit.draw.addRect(group, x, y + bandHeight - 6, width, 6, 'message-flow-band-square', 0);
    drawing.addPolyline(group, [[x + 1, y + bandHeight], [x + width - 1, y + bandHeight]], 'message-flow-band-line');

    // The hairline of light along the top edge
    drawing.addPolyline(group, [[x + 4, y + 1], [x + width - 4, y + 1]], 'message-flow-rim');

    // The band carries the channel the exchange happened on
    kit.draw.addText(group, x + config.bodyPadLeft + 2, y + 15, node.channel, 'message-flow-title', 'start');

    // Each event of the exchange on its own line
    for (var lineIndex = 0; lineIndex < node.lines.length; lineIndex++) {
        var lineY = y + bandHeight + config.lineTop + lineIndex * config.lineStride;

        drawing.addEventLine(group, x, lineY, width, node.lines[lineIndex]);
    }

    // The footer strip - how long after the flow's first moment this node's
    // own exchange began, always on the card, in the caption's dim ink
    var footerTop = y + height - config.footerHeight;

    drawing.addPolyline(group, [[x + 1, footerTop], [x + width - 1, footerTop]],
        'message-flow-node-footer-line');
    kit.draw.addText(group, x + config.bodyPadLeft, footerTop + 13, node.footerLabel,
        'message-flow-node-footer', 'start');
};

// /////////////////////////////////////////////////////////////////////////////
// The drawing itself
// /////////////////////////////////////////////////////////////////////////////

drawing.clear = function() {
    drawing.canvas().textContent = '';
    drawing.nodeDetails = [];
    drawing.selectedNode = null;
    drawing.selectedKey = '';
};

// /////////////////////////////////////////////////////////////////////////////

// The whole journey - the hub on the left, one row per delivery, chained
// exchanges continuing their rows and branch rows hanging off their parents.
// `models` are the flow's own row models, newest first, `seedModel` is the
// model of the event the journey was resolved to.
drawing.render = function(models, seedModel) {
    var config = drawing.config;

    drawing.clear();

    // What the message is known by - the hub's own words, the headline above
    // and the source's own identity for the message under it
    var hubTitle = seedModel.headline;
    var hubIdentity = seedModel.identity;

    // A seed whose source has no message id of its own reads by its CID, and
    // its headline says the same thing - one id written twice names nothing,
    // so the top line says what kind of id the reader is looking at
    if (hubTitle === hubIdentity) {
        hubTitle = config.cidLabel;
    }

    // The exchanges, their pointed links and the rows they lay out into
    var exchanges = drawing.buildExchanges(models);

    drawing.linkExchanges(exchanges, models);

    var layoutRows = drawing.buildLayoutRows(exchanges);

    // One walk over every event of the flow - its first and last moments, of
    // which the first is what every node's footer counts from, and how many
    // events reported a bad outcome, all of which the root's pane says
    var firstModel = models[0];
    var lastModel = models[0];

    var flowStartMs = new Date(firstModel.timeIso).getTime();
    var flowEndMs = flowStartMs;

    var errorCount = 0;

    for (var summaryIndex = 0; summaryIndex < models.length; summaryIndex++) {
        var summaryModel = models[summaryIndex];
        var summaryMs = new Date(summaryModel.timeIso).getTime();

        if (summaryMs < flowStartMs) {
            flowStartMs = summaryMs;
            firstModel = summaryModel;
        }

        if (summaryMs > flowEndMs) {
            flowEndMs = summaryMs;
            lastModel = summaryModel;
        }

        if (summaryModel.outcome !== '' && summaryModel.outcome !== config.goodOutcome) {
            errorCount += 1;
        }
    }

    // Every exchange becomes a node - the card, its lines, its connector words
    // and its footer's elapsed words
    var nodeByKey = {};

    for (var nodeIndex = 0; nodeIndex < exchanges.list.length; nodeIndex++) {
        var exchange = exchanges.list[nodeIndex];

        var lines = [];

        for (var lineModelIndex = 0; lineModelIndex < exchange.models.length; lineModelIndex++) {
            lines.push(drawing.lineOf(exchange.models[lineModelIndex]));
        }

        var footerElapsedMs = drawing.firstMsOf(exchange) - flowStartMs;

        nodeByKey[exchange.key] = {
            key: exchange.key,
            channel: exchange.objectName,
            connectorLabel: exchange.connectorLabel,
            footerLabel: '+' + kit.format_duration_ms(footerElapsedMs),
            lines: lines,
            models: exchange.models
        };
    }

    // The hub is as wide as its own words ask, and the fan starts past it
    var hubTitleWidth = Math.round(hubTitle.length * config.titleCharWidth) + 4 * config.bodyPadLeft;
    var hubIdentityWidth = Math.round(hubIdentity.length * config.titleCharWidth) + 4 * config.bodyPadLeft;
    var hubWidth = Math.max(config.hubMinWidth, hubTitleWidth, hubIdentityWidth);

    var hubRight = config.hubX + hubWidth;
    var fanX = hubRight + config.hubFanGap;
    var fanElbowX = hubRight + config.branchElbowOffset;

    // Pass one - where every node stands from the left. A row off the hub starts
    // at the fan, a branch row starts past its parent's right edge, and within a
    // row each next node follows its own connector.
    var placementByKey = {};

    for (var measureRowIndex = 0; measureRowIndex < layoutRows.length; measureRowIndex++) {
        var measuredRow = layoutRows[measureRowIndex];
        var x = 0;

        for (var measureItemIndex = 0; measureItemIndex < measuredRow.length; measureItemIndex++) {
            var measuredItem = measuredRow[measureItemIndex];
            var measuredNode = nodeByKey[measuredItem.exchange.key];

            if (measureItemIndex === 0) {
                if (measuredItem.fromKey === '') {
                    x = fanX;
                }
                else {

                    // A branch row hangs off a node of an earlier row, which is
                    // already placed because parents always lay out first
                    var parentPlacement = placementByKey[measuredItem.fromKey];
                    x = parentPlacement.right + config.branchElbowOffset + drawing.connectorLength(measuredNode);
                }
            }
            else {
                x += drawing.connectorLength(measuredNode);
            }

            var nodeWidth = drawing.nodeWidth(measuredNode);

            placementByKey[measuredItem.exchange.key] = {
                x: x,
                width: nodeWidth,
                right: x + nodeWidth,
                rowIndex: measureRowIndex
            };

            x += nodeWidth;
        }
    }

    // Pass two - how tall every row stands and where its connector line runs.
    // A connector aims at the centre of a node's main section, under the band.
    // The rows pack like a skyline - a row only goes below the earlier rows it
    // overlaps horizontally, so a branch stack on the right does not punch a
    // hole through a column on the left.
    var rowTops = [];
    var rowCenters = [];
    var rowBottoms = [];
    var rowExtents = [];

    for (var heightRowIndex = 0; heightRowIndex < layoutRows.length; heightRowIndex++) {
        var heightRow = layoutRows[heightRowIndex];
        var rowHeight = 0;

        for (var heightItemIndex = 0; heightItemIndex < heightRow.length; heightItemIndex++) {
            var boxHeight = drawing.nodeHeight(nodeByKey[heightRow[heightItemIndex].exchange.key]);

            if (boxHeight > rowHeight) {
                rowHeight = boxHeight;
            }
        }

        // The row's horizontal reach - from where its opening connector leaves, so
        // nothing slides up into the elbow band, to its last node's right edge
        var extentLeft;

        if (heightRow[0].fromKey === '') {
            extentLeft = fanX;
        }
        else {
            extentLeft = placementByKey[heightRow[0].fromKey].right;
        }

        var extentRight = placementByKey[heightRow[heightRow.length - 1].exchange.key].right;

        // The row lands just under the lowest of the earlier rows it overlaps -
        // rows sharing no x-band share their vertical band instead
        var rowTop = config.marginTop;

        for (var earlierIndex = 0; earlierIndex < heightRowIndex; earlierIndex++) {
            var earlierExtent = rowExtents[earlierIndex];

            // Two rows overlap when neither one ends before the other begins
            if (earlierExtent.left < extentRight && extentLeft < earlierExtent.right) {
                var rowTopCandidate = rowBottoms[earlierIndex] + config.rowGap;

                if (rowTopCandidate > rowTop) {
                    rowTop = rowTopCandidate;
                }
            }
        }

        rowExtents.push({left: extentLeft, right: extentRight});
        rowTops.push(rowTop);
        rowCenters.push(rowTop + config.bandHeight + (rowHeight - config.bandHeight) / 2);
        rowBottoms.push(rowTop + rowHeight);
    }

    // The drawing is as tall as the lowest row reaches
    var lowestBottom = config.marginTop;

    for (var bottomIndex = 0; bottomIndex < rowBottoms.length; bottomIndex++) {
        if (rowBottoms[bottomIndex] > lowestBottom) {
            lowestBottom = rowBottoms[bottomIndex];
        }
    }

    var height = lowestBottom + config.marginBottom;

    // The drawing's width is the furthest right edge of anything on it
    var width = fanX;

    for (var widthKey in placementByKey) {
        if (placementByKey[widthKey].right > width) {
            width = placementByKey[widthKey].right;
        }
    }

    width += config.marginRight;

    var svg = drawing.newSVG(width, height);

    drawing.addDefs(svg);

    // The message stands halfway down its own fan - only the rows hanging off
    // the hub have a say in where that is
    var hubRowCenters = [];

    for (var hubRowIndex = 0; hubRowIndex < layoutRows.length; hubRowIndex++) {
        if (layoutRows[hubRowIndex][0].fromKey === '') {
            hubRowCenters.push(rowCenters[hubRowIndex]);
        }
    }

    var hubCenterY = (hubRowCenters[0] + hubRowCenters[hubRowCenters.length - 1]) / 2;

    // Every card's box - what the chips steer clear of when they choose where
    // on their runs to stand
    drawing.nodeRects = [];

    for (var rectRowIndex = 0; rectRowIndex < layoutRows.length; rectRowIndex++) {
        var rectRow = layoutRows[rectRowIndex];

        for (var rectItemIndex = 0; rectItemIndex < rectRow.length; rectItemIndex++) {
            var rectPlacement = placementByKey[rectRow[rectItemIndex].exchange.key];
            var rectNode = nodeByKey[rectRow[rectItemIndex].exchange.key];

            drawing.nodeRects.push({
                left: rectPlacement.x,
                right: rectPlacement.right,
                top: rowTops[rectRowIndex],
                bottom: rowTops[rectRowIndex] + drawing.nodeHeight(rectNode)
            });
        }
    }

    // The drawing stands in layers - every connector line first, under the
    // cards, so a crossing line passes behind them, and the connectors' words
    // last, over everything, standing only where no card is
    var connectorLayer = drawing.addGroup(svg, 'message-flow-connector-layer');

    var chipLayer = kit.draw.createElement('g');
    chipLayer.setAttribute('class', 'message-flow-chip-layer');

    // The rows - each one a branch group of its own, so its nodes light up
    // as one, its lines and words lighting with them by their branch index
    for (var rowIndex = 0; rowIndex < layoutRows.length; rowIndex++) {
        var row = layoutRows[rowIndex];
        var y = rowTops[rowIndex];
        var centerY = rowCenters[rowIndex];

        var branch = drawing.addGroup(svg, 'message-flow-branch');
        branch.setAttribute('data-branch-index', rowIndex);

        for (var itemIndex = 0; itemIndex < row.length; itemIndex++) {
            var item = row[itemIndex];
            var node = nodeByKey[item.exchange.key];
            var placement = placementByKey[item.exchange.key];

            if (itemIndex === 0) {

                // The row's opening connector - from the hub, or from the parent
                // node an earlier row holds
                if (item.fromKey === '') {
                    var fanSet = drawing.addConnectorSet(connectorLayer, rowIndex, item.exchange.key, '');

                    drawing.addRoundedPath(fanSet, [
                        [hubRight, hubCenterY],
                        [fanElbowX, hubCenterY],
                        [fanElbowX, centerY],
                        [placement.x, centerY]
                    ], 'message-flow-connector');
                    drawing.addArrow(fanSet, placement.x, centerY, 'message-flow-connector-arrow');
                }
                else {
                    var parent = placementByKey[item.fromKey];
                    var parentCenterY = rowCenters[parent.rowIndex];
                    var branchElbowX = parent.right + config.branchElbowOffset;

                    var branchSet = drawing.addConnectorSet(connectorLayer, rowIndex, item.exchange.key,
                        item.fromKey);

                    drawing.addRoundedPath(branchSet, [
                        [parent.right, parentCenterY],
                        [branchElbowX, parentCenterY],
                        [branchElbowX, centerY],
                        [placement.x, centerY]
                    ], 'message-flow-connector');
                    drawing.addArrow(branchSet, placement.x, centerY, 'message-flow-connector-arrow');

                    // The words of how the message got here, on the horizontal
                    // run, standing where no card is
                    var branchChipWidth = drawing.chipWidth(node.connectorLabel);
                    var branchChipX = branchElbowX + (placement.x - branchElbowX - branchChipWidth) / 2;

                    branchChipX = drawing.clearChipX(branchChipX, branchChipWidth,
                        centerY - config.chipHeight / 2, centerY + config.chipHeight / 2,
                        branchElbowX, placement.x);

                    var branchChipGroup = drawing.addChipGroup(chipLayer, rowIndex, item.exchange.key);

                    drawing.addChip(branchChipGroup, branchChipX, centerY - config.chipHeight / 2,
                        node.connectorLabel, 'muted', true);
                }
            }
            else {

                // From the second station of a row on, the connector to it
                // carries the words of how the message got there
                var previousKey = row[itemIndex - 1].exchange.key;
                var previousPlacement = placementByKey[previousKey];

                var chainSet = drawing.addConnectorSet(connectorLayer, rowIndex, item.exchange.key,
                    previousKey);

                drawing.addPolyline(chainSet, [[previousPlacement.right, centerY], [placement.x, centerY]],
                    'message-flow-connector');
                drawing.addArrow(chainSet, placement.x, centerY, 'message-flow-connector-arrow');

                var chipWidth = drawing.chipWidth(node.connectorLabel);
                var chipX = previousPlacement.right + (placement.x - previousPlacement.right - chipWidth) / 2;

                chipX = drawing.clearChipX(chipX, chipWidth,
                    centerY - config.chipHeight / 2, centerY + config.chipHeight / 2,
                    previousPlacement.right, placement.x);

                var chainChipGroup = drawing.addChipGroup(chipLayer, rowIndex, item.exchange.key);

                drawing.addChip(chainChipGroup, chipX, centerY - config.chipHeight / 2, node.connectorLabel,
                    'muted', true);
            }

            drawing.addNode(branch, placement.x, y, placement.width, node);
        }
    }

    // The message itself, standing before all of its deliveries. The card is only
    // as tall as it has words - a message says its identity under its name, and the
    // rare one whose identity is genuinely empty stands as a single centred line.
    var hub = drawing.addGroup(svg, 'message-flow-node message-flow-node-selectable message-flow-root');

    var hubHeight = hubIdentity === '' ? config.hubHeightOneLine : config.hubHeight;
    var hubTop = hubCenterY - hubHeight / 2;

    hub.setAttribute('data-node-index', drawing.nodeDetails.length);
    drawing.nodeDetails.push({
        key: '',
        title: hubTitle,
        time: kit.time_ago_label(seedModel.timeIso) + config.labelSeparator + seedModel.timeLocal.slice(11),
        models: [seedModel],

        // The root stands for the message itself, so its pane's right side
        // sums the whole flow up rather than looking for a reply of its own
        flowSummary: {
            exchangeCount: exchanges.list.length,
            eventCount: models.length,
            firstLocal: firstModel.timeLocal,
            lastLocal: lastModel.timeLocal,
            spanMs: flowEndMs - flowStartMs,
            errorCount: errorCount
        }
    });

    kit.draw.addRect(hub, config.hubX, hubTop, hubWidth, hubHeight, 'message-flow-box', 4);
    drawing.addPolyline(hub, [[config.hubX + 4, hubTop + 1], [config.hubX + hubWidth - 4, hubTop + 1]],
        'message-flow-rim');

    if (hubIdentity === '') {
        kit.draw.addText(hub, config.hubX + hubWidth / 2, hubCenterY + 5, hubTitle, 'message-flow-title', 'middle');
    }
    else {
        kit.draw.addText(hub, config.hubX + hubWidth / 2, hubCenterY - 8, hubTitle, 'message-flow-title', 'middle');
        kit.draw.addText(hub, config.hubX + hubWidth / 2, hubCenterY + 14, hubIdentity,
            'message-flow-identity', 'middle');
    }

    // The connectors' words go on last, over everything - having already
    // chosen spots where no card is, they stand over lines only
    svg.appendChild(chipLayer);

    drawing.wireDrawing(svg);

    // The drawing comes up as large as the last one was left
    drawing.zoom.remember(width, height);
    drawing.zoom.apply();
};

// /////////////////////////////////////////////////////////////////////////////

// The canvas is walked by grabbing it - a press and a pull scroll it directly,
// and letting go mid-motion sends it gliding on, friction bleeding the speed
// off frame by frame until it settles
drawing.wirePanning = function() {
    var config = drawing.config;
    var host = drawing.canvas();

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
// on a node selects it - the amber border - opens its exchange under the drawing
// and holds its branch lit until the node is clicked again or the empty canvas is.
drawing.wireDrawing = function(svg) {
    var detail = $.fn.zato.message_flow.detail;

    var branches = svg.querySelectorAll('.message-flow-branch');
    var nodes = svg.querySelectorAll('.message-flow-node-selectable');

    // The lines and their words live in layers of their own under the cards,
    // so they light and dim by the branch they speak for rather than by
    // where they sit
    var connectorSets = svg.querySelectorAll('.message-flow-connector-set');
    var chipGroups = svg.querySelectorAll('.message-flow-connector-chip');

    drawing.selectedNode = null;
    drawing.selectedKey = '';

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

    // Everything of one branch, wherever its layer - the cards one by one,
    // the lines and the words. The cards light and dim each on its own, so a
    // selection can keep one node of a row in colour without its row-mates.
    var setLitOn = function(element, isLit) {
        element.classList.toggle('message-flow-lit', isLit);
    };

    // `litIndexes` is null to mean every branch, or an object whose keys are
    // the branch indexes to light
    var setLitEverywhere = function(litIndexes, isLit) {
        var isChosen = function(element) {
            return litIndexes === null || litIndexes[element.getAttribute('data-branch-index')] === true;
        };

        for (var litNodeIndex = 0; litNodeIndex < nodes.length; litNodeIndex++) {
            var litNode = nodes[litNodeIndex];
            var litNodeBranch = litNode.closest('.message-flow-branch');

            // The root stands outside every branch and never dims
            if (litNodeBranch === null) {
                continue;
            }

            if (isChosen(litNodeBranch)) {
                setLitOn(litNode, isLit);
            }
        }

        for (var setIndex = 0; setIndex < connectorSets.length; setIndex++) {
            var connectorSet = connectorSets[setIndex];

            if (isChosen(connectorSet)) {
                setLitOn(connectorSet, isLit);
            }
        }

        for (var chipIndex = 0; chipIndex < chipGroups.length; chipIndex++) {
            var chipGroup = chipGroups[chipIndex];

            if (isChosen(chipGroup)) {
                setLitOn(chipGroup, isLit);
            }
        }
    };

    var clearLit = function() {
        cancelUnlit();
        setLitEverywhere(null, false);
        svg.classList.remove('message-flow-focus');
    };

    var setLit = function(branch) {
        var litIndexes = {};
        litIndexes[branch.getAttribute('data-branch-index')] = true;

        clearLit();
        setLitEverywhere(litIndexes, true);
        svg.classList.add('message-flow-focus');
    };

    // The root belongs to every branch, so under it they all stay lit and only
    // the room around the drawing falls dark
    var setLitAll = function() {
        cancelUnlit();
        setLitEverywhere(null, true);
        svg.classList.add('message-flow-focus');
    };

    var scheduleUnlit = function() {
        cancelUnlit();
        unlitTimer = window.setTimeout(clearLit, drawing.config.dimHoldMs);
    };

    // Which connector leads into which node and which card wears which key -
    // the way back to the root is walked along these
    var connectorByTo = {};

    for (var mapSetIndex = 0; mapSetIndex < connectorSets.length; mapSetIndex++) {
        var mapSet = connectorSets[mapSetIndex];
        connectorByTo[mapSet.getAttribute('data-connector-to')] = mapSet;
    }

    var nodeByKey = {};

    for (var mapNodeIndex = 0; mapNodeIndex < nodes.length; mapNodeIndex++) {
        var mapNode = nodes[mapNodeIndex];
        var mapNodeKey = mapNode.getAttribute('data-exchange-key');

        // The root carries no exchange key and is in no walk
        if (mapNodeKey !== null) {
            nodeByKey[mapNodeKey] = mapNode;
        }
    }

    // The whole way from the root to one node wears the selection amber with
    // it - every connector from the node back to the hub, and every node the
    // way came by wears the selection border too, the root included, though
    // only the picked node holds the selection itself. The key names the
    // node, and no key lights nothing.
    var setConnectorCurrent = function(key, isOn) {
        var wayKey = key;

        while (wayKey !== '') {
            var waySet = connectorByTo[wayKey];

            waySet.classList.toggle('message-flow-connector-current', isOn);
            wayKey = waySet.getAttribute('data-connector-from');

            // The next node up the way - the picked node itself already
            // wears its own border
            if (wayKey !== '') {
                nodeByKey[wayKey].classList.toggle('message-flow-node-way', isOn);
            }
        }

        // The root heads every way there is
        if (key !== '') {
            root.classList.toggle('message-flow-node-way', isOn);
        }
    };

    // A picked node keeps its whole ancestry in colour - the way itself and
    // nothing more: the cards the walk passes, the connectors between them
    // and their words. A row-mate of an ancestor - another resubmission off
    // the same parent - is not on the way and dims like the rest of the room.
    var setLitWay = function(key) {
        clearLit();

        var wayKey = key;

        while (wayKey !== '') {
            setLitOn(nodeByKey[wayKey], true);

            var waySet = connectorByTo[wayKey];
            setLitOn(waySet, true);

            for (var wayChipIndex = 0; wayChipIndex < chipGroups.length; wayChipIndex++) {
                if (chipGroups[wayChipIndex].getAttribute('data-connector-to') === wayKey) {
                    setLitOn(chipGroups[wayChipIndex], true);
                }
            }

            wayKey = waySet.getAttribute('data-connector-from');
        }

        svg.classList.add('message-flow-focus');
    };

    var clearSelection = function() {
        if (drawing.selectedNode !== null) {
            drawing.selectedNode.classList.remove('message-flow-node-selected');
            drawing.selectedNode = null;

            setConnectorCurrent(drawing.selectedKey, false);
            drawing.selectedKey = '';

            detail.hide();
        }
    };

    for (var branchIndex = 0; branchIndex < branches.length; branchIndex++) {

        var wireBranch = function(branch) {

            branch.addEventListener('mouseenter', function() {
                if (drawing.selectedNode === null) {
                    setLit(branch);
                }
            });

            branch.addEventListener('mouseleave', function() {
                if (drawing.selectedNode === null) {
                    scheduleUnlit();
                }
            });
        };

        wireBranch(branches[branchIndex]);
    }

    // A line lights its branch the way the branch's own cards do - the lines
    // live in their own layer, so they answer for their branch by its index
    for (var wireSetIndex = 0; wireSetIndex < connectorSets.length; wireSetIndex++) {

        var wireConnectorSet = function(connectorSet) {
            var setIndex = connectorSet.getAttribute('data-branch-index');
            var setBranch = svg.querySelector('.message-flow-branch[data-branch-index="' + setIndex + '"]');

            connectorSet.addEventListener('mouseenter', function() {
                if (drawing.selectedNode === null) {
                    setLit(setBranch);
                }
            });

            connectorSet.addEventListener('mouseleave', function() {
                if (drawing.selectedNode === null) {
                    scheduleUnlit();
                }
            });
        };

        wireConnectorSet(connectorSets[wireSetIndex]);
    }

    // The root lights the whole drawing the way a branch lights itself
    var root = svg.querySelector('.message-flow-root');

    root.addEventListener('mouseenter', function() {
        if (drawing.selectedNode === null) {
            setLitAll();
        }
    });

    root.addEventListener('mouseleave', function() {
        if (drawing.selectedNode === null) {
            scheduleUnlit();
        }
    });

    for (var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {

        var wireNode = function(node) {

            node.addEventListener('click', function(event) {
                event.stopPropagation();

                // A second click on the picked node lets everything go
                if (drawing.selectedNode === node) {
                    clearSelection();
                    clearLit();
                    return;
                }

                clearSelection();

                drawing.selectedNode = node;
                node.classList.add('message-flow-node-selected');

                // The way in lights up with the node - the root has no way in
                // and no key, and lights nothing
                drawing.selectedKey = node.getAttribute('data-exchange-key');

                if (drawing.selectedKey === null) {
                    drawing.selectedKey = '';
                }

                setConnectorCurrent(drawing.selectedKey, true);

                // The picked node's exchange opens under the drawing
                var detailIndex = parseInt(node.getAttribute('data-node-index'), 10);
                detail.show(drawing.nodeDetails[detailIndex]);

                // The picked node's whole way from the root stays lit around
                // it, and the root, standing outside every branch, keeps them
                // all lit
                if (drawing.selectedKey !== '') {
                    setLitWay(drawing.selectedKey);
                }
                else {
                    setLitAll();
                }
            });
        };

        wireNode(nodes[nodeIndex]);
    }

    // Letting a held selection go - the canvas click and the Esc key, both wired
    // once in init, call whatever render left here last
    drawing.deselect = function() {
        if (drawing.selectedNode !== null) {
            clearSelection();
            clearLit();
        }
    };
};

// /////////////////////////////////////////////////////////////////////////////

drawing.init = function() {
    drawing.wirePanning();

    // A click anywhere on the page that is not a node lets a held selection go -
    // the canvas, the room around it, the head, all of it. Only the pane the
    // selection is being read in and the bar over it stay out of this. A node's
    // own click never bubbles this far, and a pan is not a click, which the
    // panning's own suppressor already sees to.
    document.addEventListener('click', function(event) {
        if (drawing.deselect === null) {
            return;
        }

        if (event.target.closest(drawing.config.deselectExemptSelector) !== null) {
            return;
        }

        drawing.deselect();
    });

    // Esc lets go too, from wherever the pointer happens to be - unless the
    // replay is on, whose own Esc it then is
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && drawing.deselect !== null) {
            if ($.fn.zato.message_flow.replay.state.isActive) {
                return;
            }

            drawing.deselect();
        }
    });

    drawing.zoom = kit.draw_zoom.create({
        host: drawing.canvas,
        storage_key: drawing.config.zoomStorageKey
    });

    drawing.zoom.init();
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
