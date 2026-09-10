
// /////////////////////////////////////////////////////////////////////////////

// The flow rows regrouped into exchanges and laid out in rows.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var drawing = $.fn.zato.message_flow.drawing;

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

    // An event that reports no outcome is read by what it was, in the source's
    // words, one that does is read by how it went
    var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);

    if (model.outcome === '') {
        line.kind = 'type';
        line.label = presenter.lineTypeLabel(model);
    }
    else if (model.outcome === config.goodOutcome) {
        line.kind = 'good';
        line.label = model.outcome.toUpperCase();
    }
    else {
        line.kind = 'bad';
        line.label = model.outcome.toUpperCase();
    }

    // The source says what the line reads after its chip and on hover.
    line.note = presenter.lineNote(model);
    line.tooltip = presenter.lineTooltip(model);

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

        // The source says which card an event belongs to and what the card is called.
        var presenter = $.fn.zato.audit_log.presenterFor(model.source);
        var title = presenter.cardTitle(model.raw);

        if (model.cid === '') {
            key = 'event-' + model.id;
        }
        else {
            key = presenter.cardKey(model.raw);
        }

        if (!(key in byKey)) {
            var exchange = {
                key: key,
                objectName: model.objectName,
                title: title,
                source: model.source,
                models: [],
                parentKey: '',
                connectorLabel: '',
                isDotted: false
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

        // A relation shown for the record hangs off its card on a dotted line.
        if (config.dottedRelations[model.relation] === true) {
            later.isDotted = true;
        }
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

})(jQuery);
