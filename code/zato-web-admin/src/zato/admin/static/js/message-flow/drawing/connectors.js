
// /////////////////////////////////////////////////////////////////////////////

// The connectors, chips and arrows between the cards.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var drawing = $.fn.zato.message_flow.drawing;

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

// How wide a row of chips of {label, kind} stands, gaps included.
drawing.chipRowWidth = function(chips) {
    var config = drawing.config;
    var width = 0;

    for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
        width += drawing.chipWidth(chips[chipIndex].label);
    }

    width += (chips.length - 1) * config.chipRowGap;

    return width;
};

// /////////////////////////////////////////////////////////////////////////////

// A row of chips of {label, kind} side by side, from x on.
drawing.addChipRow = function(host, x, y, chips) {
    var config = drawing.config;
    var cursor = x;

    for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
        var chip = chips[chipIndex];
        cursor += drawing.addChip(host, cursor, y, chip.label, chip.kind, false);
        cursor += config.chipRowGap;
    }

    return cursor - config.chipRowGap - x;
};

// /////////////////////////////////////////////////////////////////////////////

// The class of the connector leading into a node.
drawing.connectorClass = function(node) {
    var out = 'message-flow-connector';

    if (node.isDotted === true) {
        out += ' message-flow-connector-dotted';
    }

    return out;
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

})(jQuery);
