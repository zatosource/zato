
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the keyboard walking the drawing. With a node picked, the
// arrows move the pick the way a hand would - left and right from node to
// node in the order the message reached them, up and down from row to row
// of one node and on past its ends into the neighbouring node, Home and End
// to the first and the last node - so a reader who picked one node need not
// reach for the mouse again. With nothing picked, up and down pick something
// first - the event a standing pass is on, or the first or the last node when
// there is no pass. The replay's own keys take over while its clock runs.

$.fn.zato.message_flow.keyboard = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var keyboard = $.fn.zato.message_flow.keyboard;

// /////////////////////////////////////////////////////////////////////////////

keyboard.config = {

    // The keys the walk answers to - anything else stays the page's own
    keys: {
        previousNode: 'ArrowLeft',
        nextNode: 'ArrowRight',
        previousRow: 'ArrowUp',
        nextRow: 'ArrowDown',
        firstNode: 'Home',
        lastNode: 'End'
    },

    // Where a keypress is someone typing rather than walking
    typingSelector: 'input, textarea, select'
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the walk is what the keys are for right now - a node picked by hand,
// the replay's clock not running, and no field being typed into
keyboard.isWalking = function(event) {
    var drawing = $.fn.zato.message_flow.drawing;
    var replay = $.fn.zato.message_flow.replay;

    if (drawing.selectedNode === null) {
        return false;
    }

    if (replay.state.isPlaying) {
        return false;
    }

    return !event.target.matches(keyboard.config.typingSelector);
};

// /////////////////////////////////////////////////////////////////////////////

// The nodes in the order the message reached them - the root first, being the
// message itself, then every exchange by the moment of its earliest event
keyboard.nodeOrder = function() {
    var drawing = $.fn.zato.message_flow.drawing;

    var svg = drawing.canvas().querySelector('svg');
    var elements = svg.querySelectorAll('.message-flow-node-selectable');

    var root = null;
    var exchanges = [];

    for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var nodeDetail = drawing.nodeDetails[parseInt(element.getAttribute('data-node-index'), 10)];

        if (nodeDetail.key === '') {
            root = element;
            continue;
        }

        var firstMs = Infinity;

        for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
            var ms = new Date(nodeDetail.models[modelIndex].timeIso).getTime();

            if (ms < firstMs) {
                firstMs = ms;
            }
        }

        exchanges.push({element: element, firstMs: firstMs});
    }

    exchanges.sort(function(first, second) {
        return first.firstMs - second.firstMs;
    });

    var out = [root];

    for (var exchangeIndex = 0; exchangeIndex < exchanges.length; exchangeIndex++) {
        out.push(exchanges[exchangeIndex].element);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The events of one node in the order its card reads them
keyboard.modelsOf = function(element) {
    var drawing = $.fn.zato.message_flow.drawing;
    return drawing.nodeDetails[parseInt(element.getAttribute('data-node-index'), 10)].models;
};

// /////////////////////////////////////////////////////////////////////////////

// The row of one node an event stands on - the first row when the event is
// none of the node's, which is the root's case, the seed being another node's
keyboard.rowOf = function(models, eventId) {
    var wanted = String(eventId);
    var out = 0;

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        if (String(models[modelIndex].id) === wanted) {
            out = modelIndex;
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The pick brought to one row of one node - the node clicked the way a hand
// would click it when it is not the picked one already, the pane then brought
// to the row's event, and the room drifting so the node stands in view
keyboard.goTo = function(element, model) {
    var drawing = $.fn.zato.message_flow.drawing;
    var detail = $.fn.zato.message_flow.detail;
    var replay = $.fn.zato.message_flow.replay;

    if (drawing.selectedNode !== element) {
        element.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
    }

    detail.openEvent(model.id);
    replay.followNode(element);
};

// /////////////////////////////////////////////////////////////////////////////

// Where the pick stands - which node of the order and which row of it
keyboard.position = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var detail = $.fn.zato.message_flow.detail;

    var order = keyboard.nodeOrder();
    var nodeIndex = order.indexOf(drawing.selectedNode);
    var models = keyboard.modelsOf(drawing.selectedNode);

    var out = {
        order: order,
        nodeIndex: nodeIndex,
        models: models,
        rowIndex: keyboard.rowOf(models, detail.currentEventId)
    };

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Whether a key is one of the walk's at all
keyboard.isWalkKey = function(key) {
    var keys = keyboard.config.keys;

    for (var name in keys) {
        if (keys[name] === key) {
            return true;
        }
    }

    return false;
};

// /////////////////////////////////////////////////////////////////////////////

// With nothing picked by hand, a key of the walk picks something first. A
// pass standing on an event hands that event over - the pass ends and the
// pick takes its place, and the key then walks on from there. With no pass, a
// key that goes forward picks the first node and one that goes back the last
// node's last row, and that is the whole of the step. Whether the key still
// has a step to make is what comes back.
keyboard.pickStart = function(key) {
    var replay = $.fn.zato.message_flow.replay;
    var keys = keyboard.config.keys;
    var state = replay.state;

    var order = keyboard.nodeOrder();

    if (state.isActive && state.detailKey !== '') {
        var element = state.nodes[state.detailKey].element;
        var models = keyboard.modelsOf(element);

        keyboard.goTo(element, models[keyboard.rowOf(models, state.detailEventId)]);

        return true;
    }

    var isForward = key === keys.nextNode || key === keys.nextRow || key === keys.firstNode;

    if (isForward) {
        keyboard.goTo(order[0], keyboard.modelsOf(order[0])[0]);
    }
    else {
        var lastElement = order[order.length - 1];
        var lastModels = keyboard.modelsOf(lastElement);

        keyboard.goTo(lastElement, lastModels[lastModels.length - 1]);
    }

    return false;
};

// /////////////////////////////////////////////////////////////////////////////

// One key of the walk answered - a step past either end of the order stays
// where it is, the drawing having nothing further to show that way
keyboard.onKeyDown = function(event) {
    var drawing = $.fn.zato.message_flow.drawing;
    var replay = $.fn.zato.message_flow.replay;
    var keys = keyboard.config.keys;

    if (event.target.matches(keyboard.config.typingSelector)) {
        return;
    }

    if (replay.state.isPlaying) {
        return;
    }

    // Nothing picked yet - a key of the walk picks something first. During a
    // pass only up and down take the pick over from it, the other keys stay
    // the pass's own.
    if (drawing.selectedNode === null) {
        if (!keyboard.isWalkKey(event.key)) {
            return;
        }

        var isRowKey = event.key === keys.nextRow || event.key === keys.previousRow;

        if (replay.state.isActive && !isRowKey) {
            return;
        }

        var hasStep = keyboard.pickStart(event.key);

        // The pick was the whole of the step, and the key is spent either way
        // so the pass never answers it too
        event.preventDefault();
        event.stopImmediatePropagation();

        if (!hasStep) {
            return;
        }
    }

    var position = keyboard.position();

    var order = position.order;
    var nodeIndex = position.nodeIndex;
    var rowIndex = position.rowIndex;

    var lastNodeIndex = order.length - 1;
    var lastRowIndex = position.models.length - 1;

    if (event.key === keys.nextNode) {
        if (nodeIndex < lastNodeIndex) {
            var nextElement = order[nodeIndex + 1];
            keyboard.goTo(nextElement, keyboard.modelsOf(nextElement)[0]);
        }
    }
    else if (event.key === keys.previousNode) {
        if (nodeIndex > 0) {
            var previousElement = order[nodeIndex - 1];
            keyboard.goTo(previousElement, keyboard.modelsOf(previousElement)[0]);
        }
    }
    else if (event.key === keys.nextRow) {

        // The row after this one, or the first row of the node after this one
        if (rowIndex < lastRowIndex) {
            keyboard.goTo(order[nodeIndex], position.models[rowIndex + 1]);
        }
        else if (nodeIndex < lastNodeIndex) {
            var downElement = order[nodeIndex + 1];
            keyboard.goTo(downElement, keyboard.modelsOf(downElement)[0]);
        }
    }
    else if (event.key === keys.previousRow) {

        // The row before this one, or the last row of the node before this one
        if (rowIndex > 0) {
            keyboard.goTo(order[nodeIndex], position.models[rowIndex - 1]);
        }
        else if (nodeIndex > 0) {
            var upElement = order[nodeIndex - 1];
            var upModels = keyboard.modelsOf(upElement);
            keyboard.goTo(upElement, upModels[upModels.length - 1]);
        }
    }
    else if (event.key === keys.firstNode) {
        keyboard.goTo(order[0], keyboard.modelsOf(order[0])[0]);
    }
    else if (event.key === keys.lastNode) {
        var lastElement = order[lastNodeIndex];
        keyboard.goTo(lastElement, keyboard.modelsOf(lastElement)[0]);
    }
    else {
        return;
    }

    // The key was the walk's - the page must not scroll on it, nor the pass
    // answer it as well
    event.preventDefault();
    event.stopImmediatePropagation();
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.init = function() {
    document.addEventListener('keydown', keyboard.onKeyDown);
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
