// Config tables - the answer for a mapping set, drawn rather than written.
//
// A mapping set is a file of systems, so its answer reads as a small process: what came
// in, what this file holds for it, and what a system on the other side sends it as.
// Everything hangs off one spine down the left, dashed the way a drawing of a plan is
// dashed, and a value that a system keeps under more than one code opens as a gateway
// with a branch per code - which is how a conflict of that kind is seen rather than read.
//
// The drawing is laid out in units of its own and scaled to the column it sits in, so
// what is below reads as a plan of it rather than as pixels on a screen.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var flow = tables.flow;

var svgNamespace = 'http://www.w3.org/2000/svg';

// ////////////////////////////////////////////////////////////////////////

flow.config = {

    // How wide the drawing is and how much of that is kept clear around it
    width: 240,
    padding: 10,

    // A node on the spine, and one a branch leads out to
    nodeX: 8,
    nodeWidth: 224,
    branchX: 56,
    branchWidth: 176,

    // How tall a node is with one line in it and with two
    nodeHeight: 26,
    nodeHeightTall: 40,

    // Where the text inside a node starts, where the one line of a node sits, and where
    // the two lines of a node that has two sit
    textInset: 12,
    linePlain: 17,
    lineTallFirst: 16,
    lineTallSecond: 32,

    // The spine every connector runs down, the room a connector takes between one node
    // and the next, and how far apart the branches are
    spineX: 28,
    connectorLength: 26,
    branchGap: 9,

    // The gateway a value under more than one code opens as
    gateSize: 9,

    // A label goes beside the spine rather than on it, clear of the gateway that may
    // stand where it starts
    labelX: 42,
    labelOffset: 5,

    // The arrow head at the end of a connector
    arrowLength: 6,
    arrowWidth: 4,

    // Where the spine meets a node
    jointRadius: 2,

    // How wide one character of the monospace face is, which is what says how much of a
    // long name fits into a node
    charWidth: 6.7,
    ellipsis: '\u2026',

    // The corners are kept as tight as the ones the badges in the listing wear
    corner: 2,

    // How many systems the drawing names before it says the rest as a count
    maxBranches: 3,

    // The classes the parts of the drawing wear, so what they look like stays in the
    // stylesheet
    nodeClass: 'config-tables-flow-node',
    nodeValueClass: 'config-tables-flow-node config-tables-flow-node-value',
    nodeBranchClass: 'config-tables-flow-node config-tables-flow-node-branch',
    nodeMutedClass: 'config-tables-flow-node config-tables-flow-node-muted',
    nameClass: 'config-tables-flow-name',
    codeClass: 'config-tables-flow-code',
    valueClass: 'config-tables-flow-value',
    countClass: 'config-tables-flow-count',
    labelClass: 'config-tables-flow-label',
    lineClass: 'config-tables-flow-line',
    gateClass: 'config-tables-flow-gate',
    arrowClass: 'config-tables-flow-arrow',
    jointClass: 'config-tables-flow-joint',
    drawnClass: 'config-tables-result-drawn'
};

// ////////////////////////////////////////////////////////////////////////

// The whole drawing, from the top down. What is being drawn is worked out first, so
// the height is known before anything is put on screen.
flow.render = function(model) {

    var config = flow.config;
    var host = tables.get('flow');

    var svg = flow.createElement('svg');
    var cursor = {y: config.padding, svg: svg};

    // Who sent the value, and what they call it ..
    flow.addTallNode(cursor, model.sourceName, model.code, config.nodeClass);

    // .. down to what this file holds for it, with a note of how many of that system's
    // own codes end up here as well ..
    var sourceCount = model.sourceKeyList.length;
    flow.addConnector(cursor, flow.buildCountText(sourceCount));
    flow.addValueNode(cursor, model.value);

    // .. and out to the systems on the other side.
    flow.addBranches(cursor, model);

    var height = cursor.y + config.padding;

    svg.setAttribute('viewBox', '0 0 ' + config.width + ' ' + height);
    svg.setAttribute('width', config.width);
    svg.setAttribute('height', height);

    host.textContent = '';
    host.appendChild(svg);

    tables.get('result-area').classList.add(config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// The answer as text again, which is what a code list gets and what anything the file
// has nothing for gets.
flow.clear = function() {

    tables.get('flow').textContent = '';
    tables.get('result-area').classList.remove(flow.config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// The system the value came from - its name over the code it came in as.
flow.addTallNode = function(cursor, name, code, className) {

    var config = flow.config;
    var top = cursor.y;

    flow.addRect(cursor.svg, config.nodeX, top, config.nodeWidth, config.nodeHeightTall, className);

    var textX = config.nodeX + config.textInset;
    var nameText = flow.fit(name, config.nodeWidth);
    var codeText = flow.fit(code, config.nodeWidth);

    flow.addText(cursor.svg, textX, top + config.lineTallFirst, nameText, config.nameClass, 'start');
    flow.addText(cursor.svg, textX, top + config.lineTallSecond, codeText, config.codeClass, 'start');

    cursor.y = top + config.nodeHeightTall;
};

// ////////////////////////////////////////////////////////////////////////

// What the file holds for it, which is the one node the whole drawing turns on.
flow.addValueNode = function(cursor, value) {

    var config = flow.config;
    var top = cursor.y;

    flow.addRect(cursor.svg, config.nodeX, top, config.nodeWidth, config.nodeHeight, config.nodeValueClass);

    var textX = config.nodeX + config.textInset;
    var valueText = flow.fit(value, config.nodeWidth);

    flow.addText(cursor.svg, textX, top + config.linePlain, valueText, config.valueClass, 'start');

    cursor.y = top + config.nodeHeight;
};

// ////////////////////////////////////////////////////////////////////////

// A dashed drop down the spine into whatever comes next, with what it is about beside it.
flow.addConnector = function(cursor, labelText) {

    var config = flow.config;
    var top = cursor.y;
    var bottom = top + config.connectorLength;

    flow.addLine(cursor.svg, config.spineX, top, config.spineX, bottom);
    flow.addArrow(cursor.svg, config.spineX, bottom, 'down');

    if(labelText) {
        var middle = top + config.connectorLength / 2 + config.labelOffset;
        flow.addText(cursor.svg, config.labelX, middle, labelText, config.labelClass, 'start');
    }

    cursor.y = bottom;
};

// ////////////////////////////////////////////////////////////////////////

// Everything the value goes out to - the codes the target keeps it under when one was
// asked about, and otherwise the other systems of the file that know it too.
flow.addBranches = function(cursor, model) {

    if(model.targetName) {

        // A target the file has nothing under is named on its own, since there is no
        // count of codes to give for it
        if(model.targetNote) {
            flow.addBranchGroup(cursor, model.targetName, [], model.targetNote);
            return;
        }

        var targetLabel = tables.buildTargetLabel(model.targetName, model.targetKeyList.length);
        flow.addBranchGroup(cursor, targetLabel, model.targetKeyList, '');
        return;
    }

    var alsoCount = model.otherList.length;

    if(!alsoCount) {
        return;
    }

    var nameList = [];

    for(var otherIdx = 0; otherIdx < model.otherList.length; otherIdx++) {
        nameList.push(model.otherList[otherIdx].name);
    }

    var alsoLabel = tables.buildAlsoLabel(alsoCount);
    flow.addBranchGroup(cursor, alsoLabel, nameList, '');
};

// ////////////////////////////////////////////////////////////////////////

// One fan of branches - the label it goes by, a gateway when there is more than one way
// out of it, and a node per branch hanging off the spine.
flow.addBranchGroup = function(cursor, labelText, textList, note) {

    var config = flow.config;

    // A target that has nothing for the value is a branch of its own, so the drawing says
    // as much rather than stopping at the value
    if(note) {
        flow.addConnector(cursor, labelText);
        flow.addNoteNode(cursor, note);
        return;
    }

    var shownList = textList.slice(0, config.maxBranches);
    var restCount = textList.length - shownList.length;
    var hasChoice = textList.length > 1;

    flow.addLine(cursor.svg, config.spineX, cursor.y, config.spineX, cursor.y + config.connectorLength);
    cursor.y = cursor.y + config.connectorLength;

    // More than one way out is what a gateway is for, and the label says how many
    if(hasChoice) {
        flow.addGate(cursor.svg, config.spineX, cursor.y);
    }

    var labelY = cursor.y + config.labelOffset;
    flow.addText(cursor.svg, config.labelX, labelY, labelText, config.labelClass, 'start');

    cursor.y = cursor.y + config.gateSize;

    for(var textIdx = 0; textIdx < shownList.length; textIdx++) {
        flow.addBranchNode(cursor, shownList[textIdx], config.nodeBranchClass);
    }

    if(restCount) {
        var restText = tables.buildRestLabel(restCount);
        flow.addBranchNode(cursor, restText, config.nodeMutedClass);
    }
};

// ////////////////////////////////////////////////////////////////////////

// One branch - the spine drops to it and an elbow leads in from the side.
flow.addBranchNode = function(cursor, text, className) {

    var config = flow.config;
    var top = cursor.y + config.branchGap;
    var middle = top + config.nodeHeight / 2;

    flow.addLine(cursor.svg, config.spineX, cursor.y, config.spineX, middle);
    flow.addLine(cursor.svg, config.spineX, middle, config.branchX, middle);
    flow.addArrow(cursor.svg, config.branchX, middle, 'right');
    flow.addJoint(cursor.svg, config.spineX, middle);

    flow.addRect(cursor.svg, config.branchX, top, config.branchWidth, config.nodeHeight, className);

    var textX = config.branchX + config.textInset;
    var nodeText = flow.fit(text, config.branchWidth);

    flow.addText(cursor.svg, textX, top + config.linePlain, nodeText, config.codeClass, 'start');

    cursor.y = top + config.nodeHeight;
};

// ////////////////////////////////////////////////////////////////////////

// What stands where a branch would be when there is nothing on the other side.
flow.addNoteNode = function(cursor, note) {

    var config = flow.config;
    var top = cursor.y;

    flow.addRect(cursor.svg, config.nodeX, top, config.nodeWidth, config.nodeHeight, config.nodeMutedClass);

    var textX = config.nodeX + config.textInset;
    var noteText = flow.fit(note, config.nodeWidth);

    flow.addText(cursor.svg, textX, top + config.linePlain, noteText, config.countClass, 'start');

    cursor.y = top + config.nodeHeight;
};

// ////////////////////////////////////////////////////////////////////////

// How many codes of the system the value came from end up on the same value, said only
// when there is more than the one that was asked about.
flow.buildCountText = function(count) {

    var out = '';
    var hasOne = count === 1;

    if(!hasOne) {
        out = tables.pluralize(count, 'code');
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The shapes
// ////////////////////////////////////////////////////////////////////////

flow.createElement = function(name) {

    var out = document.createElementNS(svgNamespace, name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.addRect = function(svg, x, y, width, height, className) {

    var rect = flow.createElement('rect');

    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('rx', flow.config.corner);
    rect.setAttribute('class', className);

    svg.appendChild(rect);
};

// ////////////////////////////////////////////////////////////////////////

flow.addText = function(svg, x, y, text, className, anchor) {

    var element = flow.createElement('text');

    element.setAttribute('x', x);
    element.setAttribute('y', y);
    element.setAttribute('text-anchor', anchor);
    element.setAttribute('class', className);
    element.textContent = text;

    svg.appendChild(element);
};

// ////////////////////////////////////////////////////////////////////////

flow.addLine = function(svg, x1, y1, x2, y2) {

    var line = flow.createElement('line');

    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('class', flow.config.lineClass);

    svg.appendChild(line);
};

// ////////////////////////////////////////////////////////////////////////

// The head a connector arrives with, pointing the way the connector runs.
flow.addArrow = function(svg, x, y, direction) {

    var config = flow.config;
    var arrow = flow.createElement('polygon');
    var points = '';

    if(direction === 'down') {
        var top = y - config.arrowLength;
        points = (x - config.arrowWidth) + ',' + top + ' ' + (x + config.arrowWidth) + ',' + top + ' ' + x + ',' + y;
    }
    else {
        var left = x - config.arrowLength;
        points = left + ',' + (y - config.arrowWidth) + ' ' + left + ',' + (y + config.arrowWidth) + ' ' + x + ',' + y;
    }

    arrow.setAttribute('points', points);
    arrow.setAttribute('class', config.arrowClass);

    svg.appendChild(arrow);
};

// ////////////////////////////////////////////////////////////////////////

// The gateway, which stands on the spine where the value turns out to have more than
// one way out of it.
flow.addGate = function(svg, x, y) {

    var config = flow.config;
    var size = config.gateSize;
    var middle = y + size / 2;

    var gate = flow.createElement('polygon');
    var points = x + ',' + y + ' ' + (x + size) + ',' + middle + ' ' + x + ',' + (y + size) + ' ' + (x - size) + ',' + middle;

    gate.setAttribute('points', points);
    gate.setAttribute('class', config.gateClass);

    svg.appendChild(gate);
};

// ////////////////////////////////////////////////////////////////////////

// Where a branch leaves the spine.
flow.addJoint = function(svg, x, y) {

    var joint = flow.createElement('circle');

    joint.setAttribute('cx', x);
    joint.setAttribute('cy', y);
    joint.setAttribute('r', flow.config.jointRadius);
    joint.setAttribute('class', flow.config.jointClass);

    svg.appendChild(joint);
};

// ////////////////////////////////////////////////////////////////////////

// A name too long for the node it goes into is cut where the node ends, since a drawing
// that grows with the longest name in a file is no drawing at all.
flow.fit = function(text, width) {

    var config = flow.config;
    var room = width - config.textInset * 2;
    var maxLength = Math.floor(room / config.charWidth);

    if(text.length <= maxLength) {
        return text;
    }

    var out = text.slice(0, maxLength - 1) + config.ellipsis;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
