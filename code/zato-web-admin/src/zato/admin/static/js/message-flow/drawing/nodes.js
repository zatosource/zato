
// /////////////////////////////////////////////////////////////////////////////

// The cards and their event lines, and the render that places them.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var drawing = $.fn.zato.message_flow.drawing;

// /////////////////////////////////////////////////////////////////////////////
// The measures of one node
// /////////////////////////////////////////////////////////////////////////////

// How wide the role chips of one node stand - the widest of its lines' role words,
// never under the least width, so every line's chips after it start in one column
drawing.roleChipWidthOf = function(lines) {
    var config = drawing.config;
    var width = config.roleChipMinWidth;

    for (var lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        var labelWidth = drawing.chipWidth(config.roleLabels[lines[lineIndex].role]);

        if (labelWidth > width) {
            width = labelWidth;
        }
    }

    return width;
};

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

        // A line with no word of its own after the id chip takes no room for one
        if (line.kind === 'type') {
            if (line.label === '') {
                labelWidth = 0;
            }
            else {
                labelWidth = 8 + Math.round(line.label.length * config.typeCharWidth);
            }
        }
        else {
            labelWidth = 8 + drawing.chipWidth(line.label);
        }

        var timeWidth = Math.round(line.time.length * config.subCharWidth);

        var lineWidth = config.bodyPadLeft + node.roleChipWidth + 6 + drawing.chipWidth(line.id) +
            labelWidth + config.lineMinGap + timeWidth + config.bodyPadLeft;

        // The source's note after the chip takes its own room, or it runs into the time
        if (line.note !== '') {
            lineWidth += 8 + Math.round(line.note.length * config.subCharWidth);
        }

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

// One event of the exchange written on its own line - the role chip as wide as
// the node's role chips all are, so the lines' columns agree
drawing.addEventLine = function(host, x, lineY, width, line, roleChipWidth) {
    var config = drawing.config;

    // The line is a group of its own, named by its event, so the pane can mark
    // the line of the event its tabs stand on
    var group = drawing.addGroup(host, 'message-flow-line');
    group.setAttribute('data-event-id', line.id);

    // The line's own backing across the card, under its words - unseen until the
    // line is under the pointer or is the one the pane is open on
    var backTop = lineY - (config.lineStride - config.chipHeight) / 2;
    kit.draw.addRect(group, x + config.lineBackInset, backTop, width - 2 * config.lineBackInset,
        config.lineStride, 'message-flow-line-back', 3);

    var cursor = x + config.bodyPadLeft;

    cursor += drawing.addRoleChip(group, cursor, lineY, config.roleLabels[line.role], line.role, roleChipWidth);
    cursor += 6;
    cursor += drawing.addChip(group, cursor, lineY, line.id, 'id', false);

    // A plain event type is written as a tag, an outcome is worn as a chip, and a
    // line whose role chip already says what it was writes nothing more here
    if (line.kind === 'type') {
        if (line.label !== '') {
            var typeLabel = line.label.toUpperCase();
            cursor += 8;
            kit.draw.addText(group, cursor, lineY + 12, typeLabel, 'message-flow-band-type', 'start');
            cursor += Math.round(typeLabel.length * config.titleCharWidth);
        }
    }
    else {
        cursor += 8;
        cursor += drawing.addChip(group, cursor, lineY, line.label, line.kind, false);
    }

    // The source's note follows the chip.
    if (line.note !== '') {
        cursor += 8;
        kit.draw.addText(group, cursor, lineY + 12, line.note, 'message-flow-sub message-flow-line-note', 'start');
    }

    // The source's tooltip shows on hover.
    if (line.tooltip !== '') {
        var titleElement = kit.draw.createElement('title');
        titleElement.textContent = line.tooltip;
        group.appendChild(titleElement);
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

    // A card of several events lets each of its lines be picked on its own,
    // and says so, so the lines answer the pointer
    if (node.lines.length > 1) {
        group.classList.add('message-flow-node-multi');
    }

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

        drawing.addEventLine(group, x, lineY, width, node.lines[lineIndex], node.roleChipWidth);
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

// The whole journey - the hub on the left, one row per delivery, chained
// exchanges continuing their rows and branch rows hanging off their parents.
// `models` are the flow's own row models, newest first, `seedModel` is the
// model of the event the journey was resolved to.
drawing.render = function(models, seedModel) {
    var config = drawing.config;

    drawing.clear();

    // What the message is known by - the hub's own words, the title the source
    // gives it above and the source's own identity for the message under it
    var seedPresenter = $.fn.zato.audit_log.presenterFor(seedModel.raw.source);
    var hubTitle = seedPresenter.hubTitle(seedModel);
    var hubChips = seedPresenter.hubChips(seedModel);
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
            channel: exchange.title,
            roleChipWidth: drawing.roleChipWidthOf(lines),
            isDotted: exchange.isDotted,
            connectorLabel: exchange.connectorLabel,
            footerLabel: '+' + kit.format_duration_ms(footerElapsedMs),
            lines: lines,
            models: exchange.models
        };
    }

    // The hub is as wide as its own words ask, and the fan starts past it
    var hubTitleWidth = Math.round(hubTitle.length * config.titleCharWidth) + 4 * config.bodyPadLeft;

    // A root wearing chips is as wide as the chips ask
    if (hubChips.length > 0) {
        hubTitleWidth = drawing.chipRowWidth(hubChips) + 4 * config.bodyPadLeft;
    }
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

    // Pass two - how tall every row stands. The rows pack like a skyline - a row
    // only goes below the earlier rows it overlaps horizontally, so a branch
    // stack on the right does not punch a hole through a column on the left.
    var rowTops = [];
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
        rowBottoms.push(rowTop + rowHeight);

        // A connector aims at the centre of its own node's main section, under the
        // band - the nodes of one row share a top, not a height, so each has its own
        for (var centerItemIndex = 0; centerItemIndex < heightRow.length; centerItemIndex++) {
            var centerKey = heightRow[centerItemIndex].exchange.key;
            var centerHeight = drawing.nodeHeight(nodeByKey[centerKey]);

            placementByKey[centerKey].centerY = rowTop + config.bandHeight + (centerHeight - config.bandHeight) / 2;
        }
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

    // The message stands halfway down its own fan - only the first nodes of the
    // rows hanging off the hub have a say in where that is
    var hubRowCenters = [];

    for (var hubRowIndex = 0; hubRowIndex < layoutRows.length; hubRowIndex++) {
        if (layoutRows[hubRowIndex][0].fromKey === '') {
            hubRowCenters.push(placementByKey[layoutRows[hubRowIndex][0].exchange.key].centerY);
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

        var branch = drawing.addGroup(svg, 'message-flow-branch');
        branch.setAttribute('data-branch-index', rowIndex);

        for (var itemIndex = 0; itemIndex < row.length; itemIndex++) {
            var item = row[itemIndex];
            var node = nodeByKey[item.exchange.key];
            var placement = placementByKey[item.exchange.key];
            var centerY = placement.centerY;

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
                    var parentCenterY = parent.centerY;
                    var branchElbowX = parent.right + config.branchElbowOffset;

                    var branchSet = drawing.addConnectorSet(connectorLayer, rowIndex, item.exchange.key,
                        item.fromKey);

                    drawing.addRoundedPath(branchSet, [
                        [parent.right, parentCenterY],
                        [branchElbowX, parentCenterY],
                        [branchElbowX, centerY],
                        [placement.x, centerY]
                    ], drawing.connectorClass(node));
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

                // Two stations of one row stand as tall as their own lines ask, so the
                // run between them steps from the one's centre to the other's halfway across
                var previousCenterY = previousPlacement.centerY;

                // The words of the run stand on its last horizontal leg - the whole run
                // when it is level, what is left past the step otherwise, the step
                // standing as soon as the run has left the previous station
                var chipRunFromX = previousPlacement.right;

                if (previousCenterY === centerY) {
                    drawing.addPolyline(chainSet, [[previousPlacement.right, centerY], [placement.x, centerY]],
                        drawing.connectorClass(node));
                }
                else {
                    var chainElbowX = previousPlacement.right + config.connectorLineReach;
                    chipRunFromX = chainElbowX;

                    drawing.addRoundedPath(chainSet, [
                        [previousPlacement.right, previousCenterY],
                        [chainElbowX, previousCenterY],
                        [chainElbowX, centerY],
                        [placement.x, centerY]
                    ], drawing.connectorClass(node));
                }

                drawing.addArrow(chainSet, placement.x, centerY, 'message-flow-connector-arrow');

                var chipWidth = drawing.chipWidth(node.connectorLabel);
                var chipX = chipRunFromX + (placement.x - chipRunFromX - chipWidth) / 2;

                chipX = drawing.clearChipX(chipX, chipWidth,
                    centerY - config.chipHeight / 2, centerY + config.chipHeight / 2,
                    chipRunFromX, placement.x);

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

    // The title's baseline - alone in the middle, or above the identity
    var hubTitleBaseline = hubCenterY + 5;

    if (hubIdentity !== '') {
        hubTitleBaseline = hubCenterY - 8;

        kit.draw.addText(hub, config.hubX + hubWidth / 2, hubCenterY + 14, hubIdentity,
            'message-flow-identity', 'middle');
    }

    if (hubChips.length > 0) {
        var chipRowX = config.hubX + (hubWidth - drawing.chipRowWidth(hubChips)) / 2;
        drawing.addChipRow(hub, chipRowX, hubTitleBaseline - config.chipTextBaseline, hubChips);
    }
    else {
        kit.draw.addText(hub, config.hubX + hubWidth / 2, hubTitleBaseline, hubTitle, 'message-flow-title', 'middle');
    }

    // The connectors' words go on last, over everything - having already
    // chosen spots where no card is, they stand over lines only
    svg.appendChild(chipLayer);

    drawing.wireDrawing(svg);

    // The drawing comes up as large as the last one was left
    drawing.zoom.remember(width, height);
    drawing.zoom.apply();
};

})(jQuery);
