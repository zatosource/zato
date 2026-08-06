
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the drawing demo. One real journey drawn from hardcoded data - the
// message on the left, each delivery of it a branch to the right, the failed one
// continuing through the reprocess to the repair and onward. Everything here is
// throwaway, the real page will draw through the dashboard kit.

$.fn.zato.message_flow = {};
$.fn.zato.message_flow.demo = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var demo = $.fn.zato.message_flow.demo;

var svgNamespace = 'http://www.w3.org/2000/svg';

// /////////////////////////////////////////////////////////////////////////////

demo.config = {

    // One step box and the writing inside it
    boxPadLeft: 12,
    firstBaseline: 17,
    lineHeight: 14,

    // The status ball inside a box's right edge
    ballRadius: 5,
    ballInset: 16,

    // The corner square carrying the event id - its width follows its text
    numberPad: 10,
    numberCharWidth: 5.5,
    numberHeight: 14,
    numberOverhang: 6,

    // Arrowheads on the connectors
    arrowLength: 8,
    arrowWidth: 4.5
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

demo.addRect = function(svg, x, y, width, height, className, radius) {
    var rect = demo.createElement('rect');

    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('rx', radius);
    rect.setAttribute('class', className);

    svg.appendChild(rect);

    return rect;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addCircle = function(svg, centerX, centerY, radius, className) {
    var circle = demo.createElement('circle');

    circle.setAttribute('cx', centerX);
    circle.setAttribute('cy', centerY);
    circle.setAttribute('r', radius);
    circle.setAttribute('class', className);

    svg.appendChild(circle);

    return circle;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addText = function(svg, x, y, text, className, anchor) {
    var element = demo.createElement('text');

    element.setAttribute('x', x);
    element.setAttribute('y', y);
    element.setAttribute('class', className);
    element.setAttribute('text-anchor', anchor);
    element.textContent = text;

    svg.appendChild(element);

    return element;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addPolyline = function(svg, points, className) {
    var line = demo.createElement('polyline');

    var parts = [];

    for (var pointIndex = 0; pointIndex < points.length; pointIndex++) {
        parts.push(points[pointIndex][0] + ',' + points[pointIndex][1]);
    }

    line.setAttribute('points', parts.join(' '));
    line.setAttribute('class', className);

    svg.appendChild(line);

    return line;
};

// /////////////////////////////////////////////////////////////////////////////

// A solid triangle at the end of a connector, pointing the way the message went
demo.addArrow = function(svg, x, y, className) {
    var config = demo.config;
    var arrow = demo.createElement('path');

    var d = 'M ' + (x - config.arrowLength) + ' ' + (y - config.arrowWidth) +
            ' L ' + (x - config.arrowLength) + ' ' + (y + config.arrowWidth) +
            ' L ' + x + ' ' + y + ' Z';

    arrow.setAttribute('d', d);
    arrow.setAttribute('class', className);

    svg.appendChild(arrow);

    return arrow;
};

// /////////////////////////////////////////////////////////////////////////////

demo.addBox = function(svg, x, y, width, height, isSeed) {
    var boxClass = 'mf-box';

    if (isSeed) {
        boxClass += ' mf-box-seed';
    }

    demo.addRect(svg, x, y, width, height, boxClass, 3);
};

// /////////////////////////////////////////////////////////////////////////////

demo.addBall = function(svg, centerX, centerY, status) {
    demo.addCircle(svg, centerX, centerY, demo.config.ballRadius, 'mf-ball-' + status);
};

// /////////////////////////////////////////////////////////////////////////////

// How wide a corner square has to be for its own text
demo.numberChipWidth = function(label) {
    var config = demo.config;
    return Math.round(config.numberPad + label.length * config.numberCharWidth);
};

// /////////////////////////////////////////////////////////////////////////////

demo.addNumber = function(svg, x, y, label) {
    var config = demo.config;

    var chipWidth = demo.numberChipWidth(label);

    var numberX = x - config.numberOverhang;
    var numberY = y - config.numberOverhang;

    demo.addRect(svg, numberX, numberY, chipWidth, config.numberHeight, 'mf-number-frame', 2);
    demo.addText(svg, numberX + chipWidth / 2, numberY + 10.5, label, 'mf-number-text', 'middle');
};

// /////////////////////////////////////////////////////////////////////////////

// One step box with everything on it - the id square, the writing, the status ball
demo.addStep = function(svg, x, y, width, height, step) {
    var config = demo.config;

    demo.addBox(svg, x, y, width, height, step.isSeed);
    demo.addNumber(svg, x, y, step.number);

    var baseline = y + config.firstBaseline;

    demo.addText(svg, x + config.boxPadLeft, baseline, step.title, 'mf-title', 'start');

    for (var subIndex = 0; subIndex < step.subs.length; subIndex++) {
        baseline += config.lineHeight;
        demo.addText(svg, x + config.boxPadLeft, baseline, step.subs[subIndex], 'mf-sub', 'start');
    }

    demo.addBall(svg, x + width - config.ballInset, y + height / 2, step.status);
};

// /////////////////////////////////////////////////////////////////////////////
// The drawing - one message, its deliveries
// /////////////////////////////////////////////////////////////////////////////

demo.render = function() {
    var hubX = 20;
    var hubWidth = 200;
    var hubHeight = 60;
    var fanX = 250;
    var boxWidth = 220;
    var boxHeight = 52;
    var rowGap = 26;
    var marginTop = 20;

    // Each exchange wears the id of the arrival that started it
    var rows = [
        [
            {number: '8272', title: 'demo.hl7.adt.main', subs: ['2 days ago \u00b7 16:55:37.962', 'ack-sent \u00b7 AE'], status: 'error', isSeed: false, connectorLabel: ''}
        ],
        [
            {number: '4594', title: 'demo.hl7.oru.lab', subs: ['Yesterday \u00b7 20:00:11.156', 'ack-sent \u00b7 AE'], status: 'error', isSeed: false, connectorLabel: ''},
            {number: '9198', title: 'demo.hl7.adt.main', subs: ['Today \u00b7 00:47:32.525', 'message-received'], status: 'ok', isSeed: true, connectorLabel: 'Reprocessed \u00b7 +4h 47m 21s'},
            {number: '9199', title: 'demo.hl7.forward', subs: ['Today \u00b7 00:47:32.546', 'sent (outconn)'], status: 'ok', isSeed: false, connectorLabel: '+0.021s'}
        ],
        [
            {number: '9194', title: 'demo.hl7.adt.main', subs: ['Yesterday \u00b7 20:00:14.421', 'ack-sent \u00b7 AA'], status: 'ok', isSeed: false, connectorLabel: ''}
        ]
    ];

    // A labelled connector is long enough for its words, a bare one stays short
    var longConnector = 150;
    var shortConnector = 60;

    var height = marginTop + rows.length * (boxHeight + rowGap) - rowGap + 20;
    var width = fanX + boxWidth + longConnector + boxWidth + shortConnector + boxWidth + 20;

    var svg = demo.newSVG('message-flow-canvas', width, height);

    var hubCenterY = marginTop + 1 * (boxHeight + rowGap) + boxHeight / 2;
    var hubRight = hubX + hubWidth;
    var fanElbowX = hubRight + 14;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var y = marginTop + rowIndex * (boxHeight + rowGap);
        var centerY = y + boxHeight / 2;

        // The branch from the message to this delivery's first station
        demo.addPolyline(svg, [
            [hubRight, hubCenterY],
            [fanElbowX, hubCenterY],
            [fanElbowX, centerY],
            [fanX, centerY]
        ], 'mf-connector');
        demo.addArrow(svg, fanX, centerY, 'mf-connector-arrow');

        var x = fanX;

        for (var boxIndex = 0; boxIndex < row.length; boxIndex++) {
            var step = row[boxIndex];

            // From the second station on, the connector to it carries the words
            // of how the message got there
            if (boxIndex > 0) {
                var connectorLength = shortConnector;

                if (step.connectorLabel.length > 10) {
                    connectorLength = longConnector;
                }

                var connectorClass = 'mf-connector';
                var arrowClass = 'mf-connector-arrow';

                if (step.isSeed) {
                    connectorClass += ' mf-connector-seed';
                    arrowClass = 'mf-connector-arrow-seed';
                }

                demo.addPolyline(svg, [[x, centerY], [x + connectorLength, centerY]], connectorClass);
                demo.addArrow(svg, x + connectorLength, centerY, arrowClass);
                demo.addText(svg, x + connectorLength / 2, centerY - 8, step.connectorLabel, 'mf-connector-label', 'middle');

                x += connectorLength;
            }

            demo.addStep(svg, x, y, boxWidth, boxHeight, step);
            x += boxWidth;
        }
    }

    // The message itself, standing before all of its deliveries
    demo.addBox(svg, hubX, hubCenterY - hubHeight / 2, hubWidth, hubHeight, false);
    demo.addText(svg, hubX + hubWidth / 2, hubCenterY - 6, 'ORU^R01', 'mf-title', 'middle');
    demo.addText(svg, hubX + hubWidth / 2, hubCenterY + 12, 'FEED-00000020', 'mf-sub', 'middle');
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    demo.render();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
