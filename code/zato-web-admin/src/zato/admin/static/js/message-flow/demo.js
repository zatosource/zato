
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
    // for each half of the exchange. A node is as wide as its own words need
    // and as tall as it has lines - a single-event node has one - so the
    // ruling measures of each script are written down here.
    bandHeight: 22,
    lineTop: 6,
    lineStride: 22,
    lineBottomPad: 2,

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
    directionChipWidth: 46,

    // The word each kind of line wears - what arrived on a channel, the request
    // an outgoing connection made, the answer either of them got, and a pair of
    // eyes reading a message after the fact
    directionLabels: {
        'in': 'IN',
        'request': 'REQ',
        'reply': 'REPLY',
        'view': 'VIEW'
    },

    // How much of a labelled connector's line shows on each side of its chip,
    // whatever the chip's own width turns out to be
    connectorLineReach: 30,

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
    panVelocityFrameMs: 16,

    // How small either side of the split may get when the bar between the
    // drawing and the pane is pulled
    detailMinHeight: 120,
    canvasMinHeight: 160
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

// How wide one node has to be for its own words - the channel across the band
// and the longer of its two lines, each line being its chips, its label and its
// timestamp with breathing room between them
demo.nodeWidth = function(node) {
    var config = demo.config;

    var width = config.bodyPadLeft + 2 + Math.round(node.channel.length * config.titleCharWidth) + config.bodyPadLeft;

    for (var lineIndex = 0; lineIndex < node.events.length; lineIndex++) {
        var event = node.events[lineIndex];

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

// How long the connector into a node runs - always its own chip's width plus
// the same reach of visible line on either side, so no label can ever leave
// the line to be nothing but its arrowhead
demo.connectorLength = function(node) {
    var config = demo.config;
    return demo.chipWidth(node.connectorLabel) + 2 * config.connectorLineReach;
};

// /////////////////////////////////////////////////////////////////////////////

// How tall one node stands - the band plus one line for each event it holds,
// so an exchange of two reads as a pair and a single write stays a single line
demo.nodeHeight = function(node) {
    var config = demo.config;
    return config.bandHeight + config.lineTop + node.events.length * config.lineStride + config.lineBottomPad;
};

// /////////////////////////////////////////////////////////////////////////////

// One node - the lit card for a whole exchange: gradient face, top rim, the
// channel across the title band, and one line per half of the pair under it,
// so the in and the out are read together, each with its own id and time
demo.addNode = function(host, x, y, width, node) {
    var config = demo.config;

    var height = demo.nodeHeight(node);
    var bandHeight = config.bandHeight;

    var group = demo.addGroup(host, 'message-flow-node message-flow-node-selectable');

    // Clicking the node opens its exchange under the drawing - the detail the
    // node stands for is remembered by its place in the register
    group.setAttribute('data-node-index', demo.nodeDetails.length);
    demo.nodeDetails.push(demo.nodeDetail(node));

    demo.addRect(group, x, y, width, height, 'message-flow-box', 4);

    // The band keeps the node's rounded top and is squared off at its own foot
    demo.addRect(group, x, y, width, bandHeight, 'message-flow-band', 4);
    demo.addRect(group, x, y + bandHeight - 6, width, 6, 'message-flow-band-square', 0);
    demo.addPolyline(group, [[x + 1, y + bandHeight], [x + width - 1, y + bandHeight]], 'message-flow-band-line');

    // The hairline of light along the top edge
    demo.addPolyline(group, [[x + 4, y + 1], [x + width - 4, y + 1]], 'message-flow-rim');

    // The band carries the channel the exchange happened on
    demo.addText(group, x + config.bodyPadLeft + 2, y + 15, node.channel, 'message-flow-title', 'start');

    // Each event of the exchange on its own line
    for (var lineIndex = 0; lineIndex < node.events.length; lineIndex++) {
        var event = node.events[lineIndex];
        var lineY = y + bandHeight + config.lineTop + lineIndex * config.lineStride;

        demo.addEventLine(group, x, lineY, width, event);
    }
};

// /////////////////////////////////////////////////////////////////////////////
// The detail pane - the bodies of a clicked node's exchange
// /////////////////////////////////////////////////////////////////////////////

// What one tab of the pane wears - the direction in its own ink, the event's
// id in amber, and an outcome in the outcome's own colour. The plain label
// stays beside the markup, being what a tab is told apart by.
demo.detailTab = function(event) {
    var config = demo.config;

    var direction = config.directionLabels[event.direction];

    var labelHtml = '<span class="message-flow-detail-tab-direction-' + event.direction + '">' +
        direction + '</span>';
    labelHtml += '<span class="message-flow-detail-tab-id">' + event.id + '</span>';

    // A half whose word is an outcome carries it on the tab, so a failed leg
    // says so before it is even opened
    if (event.kind !== 'type') {
        labelHtml += '<span class="message-flow-detail-tab-outcome-' + event.kind + '">' +
            event.label + '</span>';
    }

    var tab = {
        label: direction + ' \u00b7 ' + event.id,
        label_html: labelHtml
    };

    // An event that is rows out of a database is read as a table, any other as text
    if (event.table === undefined) {
        tab.text = event.body;
    }
    else {
        tab.table = event.table;
    }

    return tab;
};

// /////////////////////////////////////////////////////////////////////////////

// What a node shows when opened - its channel over one tab per half of the
// exchange, each tab holding that event's own body
demo.nodeDetail = function(node) {
    var tabs = [];

    for (var eventIndex = 0; eventIndex < node.events.length; eventIndex++) {
        tabs.push(demo.detailTab(node.events[eventIndex]));
    }

    return {
        title: node.channel,
        controlId: demo.messageControlId,
        time: node.events[0].time,
        attachments: node.attachments,
        tabs: tabs
    };
};

// /////////////////////////////////////////////////////////////////////////////

demo.detailHost = function() {
    return document.getElementById('message-flow-detail');
};

// /////////////////////////////////////////////////////////////////////////////

// How big an attachment is, said in the unit it is best read in
demo.formatSize = function(size) {
    var kilobyte = 1024;
    var megabyte = kilobyte * kilobyte;

    if (size >= megabyte) {
        return (size / megabyte).toFixed(1) + ' MB';
    }

    if (size >= kilobyte) {
        return (size / kilobyte).toFixed(1) + ' KB';
    }

    return size + ' B';
};

// /////////////////////////////////////////////////////////////////////////////

// The pane under the drawing - one constant size whatever it is holding, so
// opening, switching and closing nodes never moves anything around it. The
// bodies inside are read through the kit's own payload panel - the same tabs,
// highlighting and Copy the flow reads its messages with.
demo.showDetail = function(detail) {
    var host = demo.detailHost();

    demo.openDetail = detail;

    host.textContent = '';

    var header = document.createElement('div');
    header.className = 'message-flow-detail-header';
    host.appendChild(header);

    var title = document.createElement('span');
    title.className = 'message-flow-detail-title';
    title.textContent = detail.title;
    header.appendChild(title);

    var meta = document.createElement('span');
    meta.className = 'message-flow-detail-meta';
    header.appendChild(meta);

    var controlId = document.createElement('span');
    controlId.className = 'message-flow-detail-control-id';
    controlId.textContent = detail.controlId;
    meta.appendChild(controlId);

    var time = document.createElement('span');
    time.className = 'message-flow-detail-time';
    time.textContent = detail.time;
    meta.appendChild(time);

    // A message that carried attachments lists them under the header, each one
    // a badge that downloads its file
    if (detail.attachments.length) {
        var strip = document.createElement('div');
        strip.className = 'message-flow-detail-attachments';
        host.appendChild(strip);

        var stripLabel = document.createElement('span');
        stripLabel.className = 'message-flow-detail-attachments-label';
        stripLabel.textContent = 'Attachments';
        strip.appendChild(stripLabel);

        for (var attachmentIndex = 0; attachmentIndex < detail.attachments.length; attachmentIndex++) {
            var attachment = detail.attachments[attachmentIndex];

            var link = document.createElement('a');
            link.className = 'dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
                'message-flow-detail-attachment';
            link.href = attachment.url;
            link.setAttribute('download', attachment.name);
            link.textContent = attachment.name;
            strip.appendChild(link);

            var size = document.createElement('span');
            size.className = 'message-flow-detail-attachment-size';
            size.textContent = demo.formatSize(attachment.size);
            link.appendChild(size);
        }
    }

    var panelHost = document.createElement('div');
    panelHost.className = 'message-flow-detail-panel';
    host.appendChild(panelHost);

    var caption = document.createElement('div');
    caption.className = 'message-flow-detail-caption';
    host.appendChild(caption);

    $.fn.zato.dashboard_kit.payload_panel.render($(panelHost), detail.tabs);

    demo.updateCaption(0);
};

// /////////////////////////////////////////////////////////////////////////////

// The words under the body - how much of it there is, in the same dim ink
// the flow's captions use. A table is measured in its own units.
demo.updateCaption = function(tabIndex) {
    var host = demo.detailHost();
    var caption = host.querySelector('.message-flow-detail-caption');
    var tab = demo.openDetail.tabs[tabIndex];

    if (tab.table === undefined) {
        caption.textContent = tab.text.length.toLocaleString('en-US') + ' characters';
    }
    else {
        var rowWord = tab.table.rows.length === 1 ? 'row' : 'rows';
        caption.textContent = tab.table.rows.length + ' ' + rowWord + ' \u00b7 ' +
            tab.table.columns.length + ' columns';
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The bar between the drawing and the pane - a press on it and a pull shares
// the page between the two, neither side ever pushed below what it needs
demo.wireResize = function() {
    var config = demo.config;

    var page = document.querySelector('.message-flow-page');
    var bar = document.getElementById('message-flow-resize');
    var detail = demo.detailHost();

    var isPressed = false;
    var startPointerY = 0;
    var startHeight = 0;

    bar.addEventListener('mousedown', function(event) {

        // Only the main button grabs the bar
        if (event.button !== 0) {
            return;
        }

        isPressed = true;
        startPointerY = event.clientY;
        startHeight = detail.offsetHeight;

        bar.classList.add('message-flow-resizing');

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) {
            return;
        }

        // Pulling the bar up grows the pane by as much as the pointer travelled
        var height = startHeight + (startPointerY - event.clientY);

        // Neither side gives up the least room it needs
        var maxHeight = page.clientHeight - config.canvasMinHeight;

        if (height < config.detailMinHeight) {
            height = config.detailMinHeight;
        }

        if (height > maxHeight) {
            height = maxHeight;
        }

        page.style.setProperty('--message-flow-detail-height', height + 'px');
    });

    window.addEventListener('mouseup', function() {
        if (isPressed) {
            isPressed = false;
            bar.classList.remove('message-flow-resizing');
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// With nothing picked, the pane stands where it always stands and says what
// it is waiting for
demo.hideDetail = function() {
    var host = demo.detailHost();

    demo.openDetail = null;

    host.textContent = '';

    var hint = document.createElement('div');
    hint.className = 'message-flow-detail-hint';
    hint.textContent = 'No node selected';
    host.appendChild(hint);
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

    // One admission, three deliveries, each leg a different kind of system -
    // the EHR speaking HL7 over MLLP, a medication system taking the admission
    // over HTTPS and failing until it is reprocessed, and a medical-mail
    // service whose reply is the delivery report a later poll of the mailbox
    // finds. Every event carries its own body, readable under the drawing.
    var admissionBody =
        'MSH|^~\\&|EHR|SUNRISE-MED|ZATO|INTEGRATION|20260805091501||ADT^A01|ADM-00004217|P|2.4\n' +
        'EVN|A01|20260805091501|||4823^Carter^Michael\n' +
        'PID|1||1234567^^^SUNRISE-MED^MR||Smith^Emily||19780314|F|||210 Maple Street^^Springfield^IL^62704^US||' +
            '217-555-0134^PRN^PH~217-555-0178^PRN^CP|||M|||||||Springfield\n' +
        'PD1||||2841^Brooks^Sarah^^^dr\n' +
        'NK1|1|Smith^John|SPO^Spouse|210 Maple Street^^Springfield^IL^62704^US|217-555-0134\n' +
        'NK1|2|Smith^Emma|DAU^Daughter|88 Oak Avenue^^Springfield^IL^62704^US|217-555-0192\n' +
        'PV1|1|I|MAT-3^12^1^SUNRISE-MED|||^^^SUNRISE-MED|4823^Carter^Michael^^^dr|2841^Brooks^Sarah^^^dr|OBS||||2|||' +
            '4823^Carter^Michael^^^dr|IN|V2026-081234|||||||||||||||||||SUNRISE-MED|||||20260805091500\n' +
        'PV2||S|^Planned admission for childbirth\n' +
        'ROL|1|AD|AT|4823^Carter^Michael^^^dr\n' +
        'DG1|1|I10|O80^Full-term uncomplicated delivery^ICD10|||A\n' +
        'DG1|2|I10|Z37.0^Single live birth^ICD10|||A\n' +
        'DG1|3|I10|Z39.0^Care immediately after delivery^ICD10|||A\n' +
        'AL1|1|DA|^Penicillin|SV^Severe^HL70128|Anaphylaxis\n' +
        'AL1|2|FA|^Peanut|MO^Moderate^HL70128|Urticaria\n' +
        'IN1|1|PLAN-A|BSH|BlueSky Health|PO Box 444^^Springfield^IL^62705^US||||||||||Smith^Emily|SEL^Self|19780314\n' +
        'OBX|1|NM|8302-2^Body height^LN||168|cm|||||F\n' +
        'OBX|2|NM|29463-7^Body weight^LN||64.5|kg|||||F\n' +
        'OBX|3|NM|8480-6^Systolic blood pressure^LN||118|mmHg|90-120|N|||F\n' +
        'OBX|4|NM|8462-4^Diastolic blood pressure^LN||76|mmHg|60-80|N|||F\n' +
        'OBX|5|TX|10160-0^Medication list^LN||Prenatal vitamins daily, Folic acid 400mcg daily|||||F\n' +
        'ZBE|1|20260805091500|ADMIT|MAT-3^12^1|Planned admission to the maternity ward';

    var admissionAckBody =
        'MSH|^~\\&|ZATO|INTEGRATION|EHR|SUNRISE-MED|20260805091501||ACK^A01|ACK-00004217|P|2.4\n' +
        'MSA|AA|ADM-00004217';

    var medicationRequestBody =
        'POST /api/v1/admissions\n' +
        '{\n' +
        '    "control_id": "ADM-00004217",\n' +
        '    "visit_number": "V2026-081234",\n' +
        '    "admitted_at": "2026-08-05T09:15:01-05:00",\n' +
        '    "ward": "MAT-3",\n' +
        '    "room": "12",\n' +
        '    "bed": "1",\n' +
        '    "attending": {\n' +
        '        "id": "4823",\n' +
        '        "name": "Michael Carter",\n' +
        '        "role": "obstetrician"\n' +
        '    },\n' +
        '    "patient": {\n' +
        '        "id": "1234567",\n' +
        '        "family_name": "Smith",\n' +
        '        "given_name": "Emily",\n' +
        '        "date_of_birth": "1978-03-14",\n' +
        '        "sex": "F",\n' +
        '        "address": {\n' +
        '            "street": "210 Maple Street",\n' +
        '            "city": "Springfield",\n' +
        '            "state": "IL",\n' +
        '            "postal_code": "62704",\n' +
        '            "country": "US"\n' +
        '        }\n' +
        '    },\n' +
        '    "diagnoses": [\n' +
        '        {"code": "O80", "system": "ICD10", "rank": 1},\n' +
        '        {"code": "Z37.0", "system": "ICD10", "rank": 2},\n' +
        '        {"code": "Z39.0", "system": "ICD10", "rank": 3}\n' +
        '    ],\n' +
        '    "allergies": [\n' +
        '        {"agent": "Penicillin", "severity": "severe", "reaction": "Anaphylaxis"},\n' +
        '        {"agent": "Peanut", "severity": "moderate", "reaction": "Urticaria"}\n' +
        '    ],\n' +
        '    "current_medication": [\n' +
        '        {"name": "Prenatal vitamins", "dose": "1 tablet", "frequency": "daily"},\n' +
        '        {"name": "Folic acid", "dose": "400mcg", "frequency": "daily"}\n' +
        '    ]\n' +
        '}';

    var medicationFailureBody =
        'HTTP/1.1 503 Service Unavailable\n' +
        'Content-Type: application/json\n' +
        'Retry-After: 3600\n' +
        'X-Request-Id: 7f3a2c91-4b1e-4d6a-9c2f-8e5b1a0d3f47\n' +
        '\n' +
        '{\n' +
        '    "error": "Service Unavailable",\n' +
        '    "detail": "Scheduled maintenance window, the admissions API is offline until 2026-08-06 06:00",\n' +
        '    "maintenance_window": {\n' +
        '        "started_at": "2026-08-05T22:00:00-05:00",\n' +
        '        "ends_at": "2026-08-06T06:00:00-05:00"\n' +
        '    },\n' +
        '    "support_reference": "INC-2026-081455"\n' +
        '}';

    var medicationSuccessBody =
        'HTTP/1.1 200 OK\n' +
        'Content-Type: application/json\n' +
        'X-Request-Id: 2b8e6f04-9a3d-41c7-b5e2-1f7c9d8a6e30\n' +
        '\n' +
        '{\n' +
        '    "status": "created",\n' +
        '    "admission_id": "adm-9932",\n' +
        '    "patient_id": "1234567",\n' +
        '    "medication_review": {\n' +
        '        "required": true,\n' +
        '        "due_by": "2026-08-06T12:00:00-05:00",\n' +
        '        "assigned_to": "pharmacy-service"\n' +
        '    },\n' +
        '    "newborn_checkup": {\n' +
        '        "scheduled": "2026-08-12T10:00:00-05:00",\n' +
        '        "location": "Sunrise Family Clinic"\n' +
        '    },\n' +
        '    "interactions_checked": 2,\n' +
        '    "warnings": [\n' +
        '        "Prenatal vitamins: safe to continue while breastfeeding",\n' +
        '        "Folic acid: safe to continue daily"\n' +
        '    ]\n' +
        '}';

    var mailRequestBody =
        'From: noreply@sunrise-med.example\n' +
        'To: admissions@medmail.example\n' +
        'Subject: Admission notice ADM-00004217\n' +
        'Date: Wed, 5 Aug 2026 09:15:03 -0500\n' +
        'Message-Id: <ADM-00004217@medmail.example>\n' +
        'MIME-Version: 1.0\n' +
        'Content-Type: multipart/mixed; boundary="=_adm-00004217"\n' +
        '\n' +
        '--=_adm-00004217\n' +
        'Content-Type: text/plain; charset=utf-8\n' +
        '\n' +
        'Dear colleague,\n' +
        '\n' +
        'This is the admission notice for patient 1234567 (Smith, Emily, 1978-03-14).\n' +
        '\n' +
        'Admitted:    2026-08-05 09:15, ward MAT-3, room 12, bed 1\n' +
        'Attending:   dr. Michael Carter, obstetrician\n' +
        'Diagnoses:   O80, Z37.0, Z39.0 (ICD-10)\n' +
        'Allergies:   Penicillin (severe), Peanut (moderate)\n' +
        '\n' +
        'Emily gave birth to a healthy baby girl on 2026-08-05 at 14:22, weighing\n' +
        '3.4 kg with an Apgar score of 9/10. Mother and daughter are both doing\n' +
        'great and are expected home on 2026-08-07. The care documents are\n' +
        'attached as PDFs.\n' +
        '\n' +
        'Kind regards,\n' +
        'Sunrise Medical Center integration platform\n' +
        '\n' +
        '--=_adm-00004217\n' +
        'Content-Type: application/pdf; name="admission-letter-ADM-00004217.pdf"\n' +
        'Content-Disposition: attachment; filename="admission-letter-ADM-00004217.pdf"\n' +
        'Content-Transfer-Encoding: base64\n' +
        '\n' +
        'JVBERi0xLjcKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0\n' +
        'ZURlY29kZT4+CnN0cmVhbQp4nK1WwW7bMAy96yt4XArUlihZsnwc0G7YbUOA3YMkbYclKZoU\n' +
        '2N+PlOw4ttM2AXYIIkrke+QjKUXBd/gDCtDga4Oz2sPTGn6sYAFfl9DAcgVfllDDcvV38ftm\n' +
        '[.. 18,344 more characters of the attachment ..]\n' +
        '--=_adm-00004217--';

    var mailDeliveryReportBody =
        'From: postmaster@medmail.example\n' +
        'To: noreply@sunrise-med.example\n' +
        'Subject: Delivery report: Admission notice ADM-00004217\n' +
        'Date: Thu, 6 Aug 2026 08:05:11 -0500\n' +
        'Content-Type: multipart/report; report-type=delivery-status\n' +
        '\n' +
        'This is the mail system at host medmail.example.\n' +
        '\n' +
        'Your message was successfully delivered to the destination(s)\n' +
        'listed below. If the message was delivered to a mailbox you will\n' +
        'receive no further notifications. Otherwise you may still receive\n' +
        'notifications of mail delivery errors from other systems.\n' +
        '\n' +
        'Reporting-MTA: dns; medmail.example\n' +
        'X-Queue-ID: 4XkP2n1zqTz9rxW\n' +
        'Arrival-Date: Wed, 5 Aug 2026 09:15:04 -0500 (CDT)\n' +
        '\n' +
        'Final-Recipient: rfc822; admissions@medmail.example\n' +
        'Original-Recipient: rfc822; admissions@medmail.example\n' +
        'Action: delivered\n' +
        'Status: 2.0.0\n' +
        'Remote-MTA: dns; mx1.medmail.example\n' +
        'Diagnostic-Code: smtp; 250 2.0.0 OK: queued as 4XkP2n1zqTz9rxW\n' +
        'Delivered-At: Thu, 6 Aug 2026 08:05:11 -0500\n' +
        '\n' +
        'Original-Message-Id: <ADM-00004217@medmail.example>';

    // The statement the platform ran against the warehouse to enrich the
    // admission - this connection captures values and rows, so the statement
    // carries its values and the reply is the rows themselves
    var warehouseRequestBody =
        'SELECT\n' +
        '    coverage.plan_code,\n' +
        '    coverage.payer_name,\n' +
        '    coverage.valid_until,\n' +
        '    ward.name AS ward_name,\n' +
        '    ward.phone AS ward_phone\n' +
        'FROM patient_coverage AS coverage\n' +
        'JOIN ward_directory AS ward\n' +
        '    ON ward.code = :ward_code\n' +
        'WHERE coverage.patient_id = :patient_id\n' +
        '    AND coverage.valid_until >= :admitted_on\n' +
        'ORDER BY coverage.valid_until DESC\n' +
        '\n' +
        ':ward_code = \'MAT-3\'\n' +
        ':patient_id = \'1234567\'\n' +
        ':admitted_on = \'2026-08-05\'';

    var warehouseReplyTable = {
        columns: ['plan_code', 'payer_name', 'valid_until', 'ward_name', 'ward_phone'],
        rows: [
            ['PLAN-A', 'BlueSky Health', '2027-01-31', 'Maternity ward 3', '217-555-0500']
        ]
    };

    // The archive copy of the admission, as it was written to the document share
    var archiveFileBody =
        'ADMISSION NOTICE                                    ADM-00004217\n' +
        '================================================================\n' +
        '\n' +
        'Patient:        Smith, Emily (1234567)\n' +
        'Date of birth:  1978-03-14\n' +
        'Admitted:       2026-08-05 09:15, ward MAT-3, room 12, bed 1\n' +
        'Attending:      dr. Michael Carter, obstetrician\n' +
        '\n' +
        'Diagnoses:      O80    Full-term uncomplicated delivery\n' +
        '                Z37.0  Single live birth\n' +
        '                Z39.0  Care immediately after delivery\n' +
        '\n' +
        'Allergies:      Penicillin (severe, anaphylaxis)\n' +
        '                Peanut (moderate, urticaria)\n' +
        '\n' +
        'Insurance:      BlueSky Health, plan PLAN-A\n' +
        '\n' +
        'Next of kin:    Smith, John (spouse), 217-555-0134\n' +
        '                Smith, Emma (daughter), 217-555-0192';

    // The audit's own record of a person reading the failed delivery this
    // morning, moments before reprocessing it
    var accessViewBody =
        '{\n' +
        '    "actor": "maria.jones",\n' +
        '    "viewed_event": 4601,\n' +
        '    "viewed_source": "rest-outgoing",\n' +
        '    "viewed_object": "demo.medication.sync",\n' +
        '    "what": "message body",\n' +
        '    "at": "2026-08-06T07:39:58.114-05:00",\n' +
        '    "address": "10.152.0.44"\n' +
        '}';

    // The mail went out with twenty attachments - the demo keeps three real
    // files, so the twenty walk through them in a loop, every entry
    // downloading one of the three
    var attachmentFiles = [
        {stem: 'admission-letter', size: 1463},
        {stem: 'medication-review', size: 1022},
        {stem: 'lab-results', size: 1224}
    ];

    var attachmentCount = 20;
    var mailAttachments = [];

    for (var attachmentIndex = 0; attachmentIndex < attachmentCount; attachmentIndex++) {
        var attachmentFile = attachmentFiles[attachmentIndex % attachmentFiles.length];

        // The two-digit ordinal every name carries, so the twenty read in order
        var ordinal = String(attachmentIndex + 1);

        if (ordinal.length < 2) {
            ordinal = '0' + ordinal;
        }

        mailAttachments.push({
            name: attachmentFile.stem + '-' + ordinal + '-ADM-00004217.pdf',
            size: attachmentFile.size,
            url: '/static/demo/message-flow/' + attachmentFile.stem + '-ADM-00004217.pdf'
        });
    }

    var rows = [
        [
            {channel: 'demo.ehr.adt', connectorLabel: '', attachments: [], events: [
                {direction: 'in', id: '4594', kind: 'type', label: 'message-received', time: 'Yesterday \u00b7 09:15:01.412', body: admissionBody},
                {direction: 'reply', id: '4595', kind: 'good', label: 'ACK AA', time: 'Yesterday \u00b7 09:15:01.414', body: admissionAckBody}
            ]}
        ],
        [
            {channel: 'demo.warehouse.lookup', connectorLabel: '', attachments: [], events: [
                {direction: 'request', id: '4597', kind: 'type', label: 'sql-request', time: 'Yesterday \u00b7 09:15:01.622', body: warehouseRequestBody},
                {direction: 'reply', id: '4598', kind: 'good', label: '1 ROW', time: 'Yesterday \u00b7 09:15:01.634', table: warehouseReplyTable}
            ]}
        ],
        [
            {channel: 'demo.medication.sync', connectorLabel: '', attachments: [], events: [
                {direction: 'request', id: '4600', kind: 'type', label: 'http-request', time: 'Yesterday \u00b7 09:15:02.033', body: medicationRequestBody},
                {direction: 'reply', id: '4601', kind: 'bad', label: 'HTTP 503', time: 'Yesterday \u00b7 09:15:02.291', body: medicationFailureBody}
            ]},
            {channel: 'demo.medication.sync', connectorLabel: 'Reprocessed by maria.jones \u00b7 +22h 25m', attachments: [], events: [
                {direction: 'request', id: '9210', kind: 'type', label: 'http-request', time: 'Today \u00b7 07:40:12.008', body: medicationRequestBody},
                {direction: 'reply', id: '9211', kind: 'good', label: 'HTTP 200', time: 'Today \u00b7 07:40:12.301', body: medicationSuccessBody}
            ]}
        ],
        [
            {channel: 'demo.docs.archive', connectorLabel: '', attachments: [], events: [
                {direction: 'request', id: '4612', kind: 'type', label: 'file-stored', time: 'Yesterday \u00b7 09:15:02.518', body: archiveFileBody}
            ]}
        ],
        [
            {channel: 'demo.medmail.notify', connectorLabel: '', attachments: mailAttachments, events: [
                {direction: 'request', id: '4620', kind: 'type', label: 'message-sent', time: 'Yesterday \u00b7 09:15:03.077', body: mailRequestBody},
                {direction: 'reply', id: '9302', kind: 'good', label: 'DELIVERED', time: 'Today \u00b7 08:05:11.204', body: mailDeliveryReportBody}
            ]}
        ],
        [
            {channel: 'dashboard.audit-log', connectorLabel: '', attachments: [], events: [
                {direction: 'view', id: '9207', kind: 'type', label: 'content-viewed', time: 'Today \u00b7 07:39:58.114', body: accessViewBody}
            ]}
        ]
    ];

    // The message every delivery answers to, and its own detail - the admission itself
    demo.messageControlId = 'ADM-00004217';

    var rootDetail = {
        title: 'ADT^A01',
        controlId: demo.messageControlId,
        time: 'Yesterday \u00b7 09:15:01.412',
        attachments: [],
        tabs: [
            {label: 'Message', text: admissionBody}
        ]
    };

    // Every row is as tall as its tallest node, and a connector aims at the
    // centre of a node's main section, under the title band - so each row's
    // top and its connector line are measured before anything is drawn
    var rowTops = [];
    var rowCenters = [];
    var layoutY = marginTop;

    for (var rowMeasureIndex = 0; rowMeasureIndex < rows.length; rowMeasureIndex++) {
        var heightRow = rows[rowMeasureIndex];
        var rowHeight = 0;

        for (var heightBoxIndex = 0; heightBoxIndex < heightRow.length; heightBoxIndex++) {
            var boxHeight = demo.nodeHeight(heightRow[heightBoxIndex]);

            if (boxHeight > rowHeight) {
                rowHeight = boxHeight;
            }
        }

        rowTops.push(layoutY);
        rowCenters.push(layoutY + config.bandHeight + (rowHeight - config.bandHeight) / 2);

        layoutY += rowHeight + rowGap;
    }

    var height = layoutY - rowGap + 28;

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

    // The register the nodes put their details into as they are drawn
    demo.nodeDetails = [];

    // The message stands halfway down its own fan of deliveries
    var hubCenterY = (rowCenters[0] + rowCenters[rowCenters.length - 1]) / 2;
    var hubRight = hubX + hubWidth;
    var fanElbowX = hubRight + 16;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var y = rowTops[rowIndex];
        var centerY = rowCenters[rowIndex];

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

    hub.setAttribute('data-node-index', demo.nodeDetails.length);
    demo.nodeDetails.push(rootDetail);

    demo.addRect(hub, hubX, hubTop, hubWidth, hubHeight, 'message-flow-box', 4);
    demo.addPolyline(hub, [[hubX + 4, hubTop + 1], [hubX + hubWidth - 4, hubTop + 1]], 'message-flow-rim');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY - 8, 'ADT^A01', 'message-flow-title', 'middle');
    demo.addText(hub, hubX + hubWidth / 2, hubCenterY + 14, 'ADM-00004217', 'message-flow-control-id', 'middle');

    demo.wireDrawing(svg);
    demo.wirePanning(document.getElementById('message-flow-canvas'));

    // The pane starts the size it will always be, waiting for the first click
    demo.hideDetail();
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
            demo.hideDetail();
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

                // The picked node's exchange opens under the drawing
                var detailIndex = parseInt(node.getAttribute('data-node-index'), 10);
                demo.showDetail(demo.nodeDetails[detailIndex]);

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
    demo.wireResize();
});

// The panel's own handler has already put the clicked tab in front by the time
// this one runs, so all that is left is saying how much text the tab holds
$(document).on('click', '.message-flow-detail .dashboard-payload-tab', function() {
    demo.updateCaption(parseInt($(this).attr('data-tab-index'), 10));
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
