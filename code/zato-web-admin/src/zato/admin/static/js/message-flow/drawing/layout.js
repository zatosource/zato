
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the drawing. One message drawn from its flow rows, the message on the left and each exchange a card to the right.

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

    // The air between two chips standing in a row, and how far a chip's top stands above its text baseline
    chipRowGap: 6,
    chipTextBaseline: 12,

    // How far in from the card's edges a line's backing stands
    lineBackInset: 3,

    // The least width a role chip stands at - the chips of one card all take the width
    // of the widest word among them, so the columns after them line up
    roleChipMinWidth: 70,

    // The word each kind of line wears - the part the event played in its exchange,
    // and a pair of eyes reading a message after the fact. A service's request and
    // response wear the plain words, the card already being the service's own.
    roleLabels: {
        'request': 'REQUEST',
        'response': 'RESPONSE',
        'none': 'SYS',
        'view': 'VIEW',
        'job': 'SCHEDULER',
        'service': 'AUDIT WRITE',
        'service-request': 'REQUEST',
        'service-response': 'RESPONSE',
        'transfer': 'TRANSFER',
        'access': 'ACCESS'
    },

    // The one event type that is a person reading rather than a message moving
    viewEventType: 'content-viewed',

    // What the hub's top line says when the seed's source has no message id
    // of its own and the message reads by its CID alone
    cidLabel: 'CID',

    // The outcome worn as a good chip - every other reported outcome is a bad one
    goodOutcome: 'ok',

    // What a card's line wears in place of its action once the message did go out again
    resubmittedLabel: 'RESUBMITTED',

    // What the tippy beside a pressed action chip says while the message is going out
    // again and once it has
    resubmittingLabel: 'Resubmitting',
    resubmittedOpenLabel: 'Resubmitted. Click to open.',

    // The room between a card's title and the action chips at the band's right,
    // and between two such chips - and the chips' own height, top and text baseline
    bandActionGap: 12,
    bandChipGap: 6,
    bandActionChipHeight: 28,
    bandActionChipTop: -3,
    bandActionChipTextOffset: 4,

    // How much room past the point a pull reached is added at a time
    roomStep: 400,

    // The theme, the arrow and the keep selector of a chip's tippy
    resubmitTippyTheme: 'message-flow',
    resubmitTippyArrow: '<svg width="16" height="6" viewBox="0 0 16 6" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M0 6 L8 1.2 L16 6" stroke-linejoin="round"/></svg>',
    resubmitTippyKeepSelector: '.tippy-box, .message-flow-action',

    // The word a connector wears for why the chained exchange exists at all -
    // relations that name no event in particular never chain, so they are not here
    relationWords: {
        'resubmit-of': 'Resubmitted',
        'resubmitted-as': 'Resubmitted',
        'parent': 'Linked',
        'child': 'Linked',
        'member-of': 'File',
        'has-member': 'Run',
        'triggered-by': 'Triggered',
        'handed-to': 'Handed to',
        'same-content': 'Same content'
    },

    // The relations drawn as a dotted connector.
    dottedRelations: {
        'same-content': true
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

// Picks the node holding one event the way a click on it would, left by each render.
drawing.selectEvent = null;

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

// The margins around the drawing, grown on whichever side a pull reaches. Null until a drawing is up.
drawing.room = null;

drawing.applyRoom = function() {
    var svg = drawing.canvas().querySelector('svg');
    var room = drawing.room;

    svg.style.margin = room.top + 'px ' + room.right + 'px ' + room.bottom + 'px ' + room.left + 'px';
};

// A fresh drawing gets room on every side as large as the canvas, a hidden canvas has no size to measure yet.
drawing.giveRoom = function() {
    var host = drawing.canvas();

    var roomX = host.clientWidth;
    var roomY = host.clientHeight;

    if (roomX === 0) {
        drawing.room = null;
        return;
    }

    if (roomY === 0) {
        drawing.room = null;
        return;
    }

    drawing.room = {top: roomY, right: roomX, bottom: roomY, left: roomX};
    drawing.applyRoom();

    host.scrollLeft = roomX;
    host.scrollTop = roomY;
};

// A drawing that came up while its canvas was hidden gets its room the first time the canvas is shown.
drawing.ensureRoom = function() {
    var svg = drawing.canvas().querySelector('svg');

    if (svg !== null) {
        if (drawing.room === null) {
            drawing.giveRoom();
        }
    }
};

// Scrolls the canvas to a position, growing the room wherever the position lies past it.
// Returns what was added on the left and the top, which shifts every scroll position by as much.
drawing.panTo = function(left, top) {
    var config = drawing.config;
    var host = drawing.canvas();
    var room = drawing.room;

    var grown = {left: 0, top: 0};

    if (room !== null) {

        // Past the left or the top - the room there grows by what is missing and a step more
        if (left < 0) {
            grown.left = config.roomStep - left;
            room.left += grown.left;
            left += grown.left;
        }

        if (top < 0) {
            grown.top = config.roomStep - top;
            room.top += grown.top;
            top += grown.top;
        }

        drawing.applyRoom();

        // Past the right or the bottom - the room there simply grows, nothing on the canvas moves
        var mostLeft = host.scrollWidth - host.clientWidth;
        var mostTop = host.scrollHeight - host.clientHeight;

        if (left > mostLeft) {
            var missingRight = left - mostLeft;
            room.right += config.roomStep + missingRight;
        }

        if (top > mostTop) {
            var missingBottom = top - mostTop;
            room.bottom += config.roomStep + missingBottom;
        }

        drawing.applyRoom();
    }

    host.scrollLeft = left;
    host.scrollTop = top;

    return grown;
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
// The drawing itself
// /////////////////////////////////////////////////////////////////////////////

drawing.clear = function() {
    drawing.canvas().textContent = '';
    drawing.room = null;
    drawing.nodeDetails = [];
    drawing.selectedNode = null;
    drawing.selectedKey = '';
};

})(jQuery);
