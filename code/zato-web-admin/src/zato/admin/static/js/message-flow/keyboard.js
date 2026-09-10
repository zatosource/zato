
// /////////////////////////////////////////////////////////////////////////////

// Message flow - keyboard navigation over the drawing's nodes and their rows.

$.fn.zato.message_flow.keyboard = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var keyboard = $.fn.zato.message_flow.keyboard;

// /////////////////////////////////////////////////////////////////////////////

keyboard.config = {

    keys: {
        previousNode: 'ArrowLeft',
        nextNode: 'ArrowRight',
        previousRow: 'ArrowUp',
        nextRow: 'ArrowDown',
        firstNode: 'Home',
        lastNode: 'End'
    },

    typingSelector: 'input, textarea, select',

    canvasSVGSelector: 'svg',
    rootSelector: '.message-flow-root',
    exchangeSelector: '.message-flow-node-selectable:not(.message-flow-root)',
    nodeIndexAttribute: 'data-node-index',

    clickEventOptions: {bubbles: true, cancelable: true}
};

// /////////////////////////////////////////////////////////////////////////////

// True while a node is selected, the replay is not playing and no field is being typed into.
keyboard.isWalking = function(event) {
    var drawing = $.fn.zato.message_flow.drawing;
    var replay = $.fn.zato.message_flow.replay;

    var out = false;

    if (drawing.selectedNode !== null) {
        if (!replay.state.isPlaying) {
            var isTyping = event.target.matches(keyboard.config.typingSelector);
            out = !isTyping;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The root first, then every exchange by the moment of its earliest event.
keyboard.nodeOrder = function() {
    var config = keyboard.config;
    var drawing = $.fn.zato.message_flow.drawing;

    var canvas = drawing.canvas();
    var drawingRoot = canvas.querySelector(config.canvasSVGSelector);

    var root = drawingRoot.querySelector(config.rootSelector);
    var elements = drawingRoot.querySelectorAll(config.exchangeSelector);

    var exchanges = [];

    for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var models = keyboard.modelsOf(element);

        var firstMilliseconds = Infinity;

        for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
            var model = models[modelIndex];
            var time = new Date(model.timeIso);
            var milliseconds = time.getTime();

            if (milliseconds < firstMilliseconds) {
                firstMilliseconds = milliseconds;
            }
        }

        exchanges.push({element: element, firstMilliseconds: firstMilliseconds});
    }

    exchanges.sort(function(first, second) {
        var out = first.firstMilliseconds - second.firstMilliseconds;
        return out;
    });

    var out = [root];

    for (var exchangeIndex = 0; exchangeIndex < exchanges.length; exchangeIndex++) {
        var exchange = exchanges[exchangeIndex];
        out.push(exchange.element);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.modelsOf = function(element) {
    var drawing = $.fn.zato.message_flow.drawing;

    var indexText = element.getAttribute(keyboard.config.nodeIndexAttribute);
    var nodeIndex = parseInt(indexText, 10);
    var nodeDetail = drawing.nodeDetails[nodeIndex];

    var out = nodeDetail.models;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The first row when the event is none of the node's, which is the root's case.
keyboard.rowOf = function(models, eventId) {
    var wanted = String(eventId);
    var out = 0;

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        var model = models[modelIndex];
        var modelId = String(model.id);

        if (modelId === wanted) {
            out = modelIndex;
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.goTo = function(element, model) {
    var drawing = $.fn.zato.message_flow.drawing;
    var detail = $.fn.zato.message_flow.detail;
    var replay = $.fn.zato.message_flow.replay;

    if (drawing.selectedNode !== element) {
        var click = new MouseEvent('click', keyboard.config.clickEventOptions);
        element.dispatchEvent(click);
    }

    detail.openEvent(model.id);
    replay.followNode(element);
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.position = function() {
    var drawing = $.fn.zato.message_flow.drawing;
    var detail = $.fn.zato.message_flow.detail;

    var order = keyboard.nodeOrder();
    var nodeIndex = order.indexOf(drawing.selectedNode);
    var models = keyboard.modelsOf(drawing.selectedNode);
    var rowIndex = keyboard.rowOf(models, detail.currentEventId);

    var out = {
        order: order,
        nodeIndex: nodeIndex,
        models: models,
        rowIndex: rowIndex
    };

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.isWalkKey = function(key) {
    var keys = keyboard.config.keys;
    var out = false;

    for (var name in keys) {
        if (keys[name] === key) {
            out = true;
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// With nothing selected, a key selects something first. During a pass the pass's event is taken over
// and the key still has a step to make. Otherwise the first node or the last node's last row is selected
// and that is the whole step. Returns whether the key still has a step to make.
keyboard.pickStart = function(key) {
    var replay = $.fn.zato.message_flow.replay;
    var keys = keyboard.config.keys;
    var state = replay.state;

    var out = false;

    if (state.isActive) {
        if (state.detailKey !== '') {
            var passNode = state.nodes[state.detailKey];
            var passElement = passNode.element;
            var passModels = keyboard.modelsOf(passElement);
            var passRowIndex = keyboard.rowOf(passModels, state.detailEventId);
            var passModel = passModels[passRowIndex];

            keyboard.goTo(passElement, passModel);

            out = true;
            return out;
        }
    }

    var order = keyboard.nodeOrder();

    var forwardKeys = [keys.nextNode, keys.nextRow, keys.firstNode];
    var forwardIndex = forwardKeys.indexOf(key);
    var isForward = forwardIndex !== -1;

    if (isForward) {
        var firstElement = order[0];
        var firstModels = keyboard.modelsOf(firstElement);
        var firstModel = firstModels[0];

        keyboard.goTo(firstElement, firstModel);
    }
    else {
        var lastElement = order[order.length - 1];
        var lastModels = keyboard.modelsOf(lastElement);
        var lastModel = lastModels[lastModels.length - 1];

        keyboard.goTo(lastElement, lastModel);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A step past either end of the order stays where it is.
keyboard.onKeyDown = function(event) {
    var config = keyboard.config;
    var drawing = $.fn.zato.message_flow.drawing;
    var replay = $.fn.zato.message_flow.replay;
    var keys = config.keys;
    var key = event.key;

    var isTyping = event.target.matches(config.typingSelector);

    if (isTyping) {
        return;
    }

    if (replay.state.isPlaying) {
        return;
    }

    // With nothing selected, only the row keys take over from a running pass.
    if (drawing.selectedNode === null) {
        var isWalkKey = keyboard.isWalkKey(key);

        if (!isWalkKey) {
            return;
        }

        var rowKeys = [keys.nextRow, keys.previousRow];
        var rowKeyIndex = rowKeys.indexOf(key);
        var isRowKey = rowKeyIndex !== -1;

        if (replay.state.isActive) {
            if (!isRowKey) {
                return;
            }
        }

        var hasStep = keyboard.pickStart(key);

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

    if (key === keys.nextNode) {
        if (nodeIndex < lastNodeIndex) {
            var nextElement = order[nodeIndex + 1];
            var nextModels = keyboard.modelsOf(nextElement);
            var nextModel = nextModels[0];

            keyboard.goTo(nextElement, nextModel);
        }
    }
    else if (key === keys.previousNode) {
        if (nodeIndex > 0) {
            var previousElement = order[nodeIndex - 1];
            var previousModels = keyboard.modelsOf(previousElement);
            var previousModel = previousModels[0];

            keyboard.goTo(previousElement, previousModel);
        }
    }
    else if (key === keys.nextRow) {
        if (rowIndex < lastRowIndex) {
            var currentElement = order[nodeIndex];
            var nextRowModel = position.models[rowIndex + 1];

            keyboard.goTo(currentElement, nextRowModel);
        }
        else if (nodeIndex < lastNodeIndex) {
            var downElement = order[nodeIndex + 1];
            var downModels = keyboard.modelsOf(downElement);
            var downModel = downModels[0];

            keyboard.goTo(downElement, downModel);
        }
    }
    else if (key === keys.previousRow) {
        if (rowIndex > 0) {
            var sameElement = order[nodeIndex];
            var previousRowModel = position.models[rowIndex - 1];

            keyboard.goTo(sameElement, previousRowModel);
        }
        else if (nodeIndex > 0) {
            var upElement = order[nodeIndex - 1];
            var upModels = keyboard.modelsOf(upElement);
            var upModel = upModels[upModels.length - 1];

            keyboard.goTo(upElement, upModel);
        }
    }
    else if (key === keys.firstNode) {
        var firstElement = order[0];
        var firstModels = keyboard.modelsOf(firstElement);
        var firstModel = firstModels[0];

        keyboard.goTo(firstElement, firstModel);
    }
    else if (key === keys.lastNode) {
        var lastElement = order[lastNodeIndex];
        var lastModels = keyboard.modelsOf(lastElement);
        var lastModel = lastModels[0];

        keyboard.goTo(lastElement, lastModel);
    }
    else {
        return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
};

// /////////////////////////////////////////////////////////////////////////////

keyboard.init = function() {
    document.addEventListener('keydown', keyboard.onKeyDown);
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
