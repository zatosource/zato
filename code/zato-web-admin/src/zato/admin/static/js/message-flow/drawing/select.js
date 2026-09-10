
// /////////////////////////////////////////////////////////////////////////////

// Panning, selecting and the page hooks.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var drawing = $.fn.zato.message_flow.drawing;

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

                // A hand on a node ends whatever pass was on - the pass's own marks,
                // the amber on the node it last stood on among them, would otherwise
                // stay on the drawing beside the selection
                var replay = $.fn.zato.message_flow.replay;

                if (replay.state.isActive) {
                    replay.disarm();
                }

                // On a card of several events the click may be on one of its lines,
                // which then is the event the pane opens on - a card of one event
                // is picked as a whole, whichever of its parts was clicked
                var lineEventId = null;

                if (node.classList.contains('message-flow-node-multi')) {
                    var line = event.target.closest('.message-flow-line');

                    if (line !== null) {
                        lineEventId = parseInt(line.getAttribute('data-event-id'), 10);
                    }
                }

                if (drawing.selectedNode === node) {

                    // Another line of the picked card brings the pane to its event ..
                    if (lineEventId !== null && lineEventId !== detail.currentEventId) {
                        detail.openEvent(lineEventId);
                        return;
                    }

                    // .. and a second click on the same thing lets everything go
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

                // The picked node's exchange opens under the drawing, on the line
                // that was clicked when one was
                var detailIndex = parseInt(node.getAttribute('data-node-index'), 10);
                detail.show(drawing.nodeDetails[detailIndex]);

                if (lineEventId !== null) {
                    detail.openEvent(lineEventId);
                }

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

    // Clicks the node whose exchange holds the event and brings the pane's tabs to that
    // very event, false when no node holds it.
    drawing.selectEvent = function(eventId) {
        var wanted = String(eventId);

        for (var findIndex = 0; findIndex < nodes.length; findIndex++) {
            var candidate = nodes[findIndex];
            var candidateDetail = drawing.nodeDetails[parseInt(candidate.getAttribute('data-node-index'), 10)];

            for (var modelIndex = 0; modelIndex < candidateDetail.models.length; modelIndex++) {
                if (String(candidateDetail.models[modelIndex].id) === wanted) {

                    // Clicking the node already picked would deselect it.
                    if (drawing.selectedNode !== candidate) {
                        candidate.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                    }

                    detail.openEvent(eventId);

                    return true;
                }
            }
        }

        return false;
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

})(jQuery);
