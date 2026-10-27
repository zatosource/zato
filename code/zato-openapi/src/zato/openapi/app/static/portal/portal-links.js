zatoPortal.links = {};

zatoPortal.links.config = {
    hashPrefix: '#',
    storageKey: 'zato.openapi.portal.link',
    inputSelector: '.portal-editor-input',
    requestSeparator: '?',
    requestKey: 'request',
    headerPrefix: 'header.',
    pathPrefix: 'path.',
    pathEscapes: {
        '%': '%25',
        '?': '%3F',
        '#': '%23',
    },
};

zatoPortal.links.state = {
    entryIdsByOperation: {},
    pendingEntryId: '',
    isUpdatePending: false,
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getOperation = function(entry) {
    var out = zatoPortal.links.config.hashPrefix + entry.method + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.escapePath = function(path) {

    var escapes = zatoPortal.links.config.pathEscapes;

    // A path keeps its characters in a link apart from those that would end it or be read as an escape
    var out = '';

    for(var characterIndex = 0; characterIndex < path.length; characterIndex++) {
        var character = path[characterIndex];

        if(Object.hasOwn(escapes, character)) {
            out += escapes[character];
        }
        else {
            out += character;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getHash = function(entry) {

    var path = zatoPortal.links.escapePath(entry.path);

    var out = zatoPortal.links.config.hashPrefix + entry.method + path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getDefaults = function(entry) {

    var sample = zatoPortal.invoke.buildSample(entry, false);

    var out = {
        requestText: zatoPortal.highlight.format(sample),
        pathValues: zatoPortal.invoke.getPathExamples(entry.operation),
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getCompactText = function(text) {

    var parsed = zatoPortal.invoke.parse(text);

    // A JSON request is compared and linked to without its indentation, and any other one as it was typed
    if(parsed === undefined) {
        return text;
    }

    var out = JSON.stringify(parsed);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getRequestQuery = function(card) {

    var config = zatoPortal.links.config;
    var entry = zatoPortal.state.entriesById[card.id];
    var defaults = zatoPortal.links.getDefaults(entry);
    var params = new URLSearchParams();

    // A link carries only what differs from what the card starts with, beginning with the request ..
    var text = zatoPortal.links.getCompactText(card.querySelector(config.inputSelector).value);
    var defaultText = zatoPortal.links.getCompactText(defaults.requestText);

    if(text !== defaultText) {
        params.append(config.requestKey, text);
    }

    // .. followed by the path parameters ..
    var pathValues = zatoPortal.invoke.getPathValues(card);
    var pathNames = Object.keys(pathValues);

    for(var nameIndex = 0; nameIndex < pathNames.length; nameIndex++) {
        var pathName = pathNames[nameIndex];

        if(pathValues[pathName] !== defaults.pathValues[pathName]) {
            params.append(config.pathPrefix + pathName, pathValues[pathName]);
        }
    }

    // .. and the headers that have a name.
    var headers = zatoPortal.state.exchanges[card.id].headers;

    for(var headerIndex = 0; headerIndex < headers.length; headerIndex++) {
        var header = headers[headerIndex];
        var headerName = header.name.trim();

        if(headerName !== '') {
            params.append(config.headerPrefix + headerName, header.value);
        }
    }

    var out = params.toString();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getCardHash = function(card) {

    var entry = zatoPortal.state.entriesById[card.id];
    var query = zatoPortal.links.getRequestQuery(card);

    var out = zatoPortal.links.getHash(entry);

    if(query !== '') {
        out += zatoPortal.links.config.requestSeparator + query;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getAddressHash = function(hash) {

    // The address keeps any characters outside of ASCII percent-encoded, e.g. those of a path in Greek
    var out = new URL(hash, window.location.href).hash;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getUrl = function(card) {

    var address = window.location;
    var hash = zatoPortal.links.getCardHash(card);

    var out = address.origin + address.pathname + address.search + hash;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.splitHash = function(hash) {

    var config = zatoPortal.links.config;
    var separatorIndex = hash.indexOf(config.requestSeparator);

    // The operation comes first, and the request, if any, follows the separator
    if(separatorIndex === -1) {
        var plain = {operation: hash, query: ''};
        return plain;
    }

    var out = {operation: hash.slice(0, separatorIndex), query: hash.slice(separatorIndex + 1)};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.applyRequest = function(entryId, query) {

    var config = zatoPortal.links.config;
    var card = document.getElementById(entryId);
    var params = new URLSearchParams(query);

    // A card that already holds the request linked to is left as it is, with the caret where it was ..
    if(zatoPortal.links.getRequestQuery(card) === params.toString()) {
        return;
    }

    // .. otherwise, what the link leaves out is what the card starts with, and the request is shown
    // the way the editor formats it ..
    var defaults = zatoPortal.links.getDefaults(zatoPortal.state.entriesById[entryId]);
    var text = defaults.requestText;

    if(params.has(config.requestKey)) {
        text = params.get(config.requestKey);
    }

    var parsed = zatoPortal.invoke.parse(text);

    if(parsed !== undefined) {
        text = zatoPortal.highlight.format(parsed);
    }

    zatoPortal.invoke.setRequestText(card, text);

    // .. the path parameters it names replace the ones the operation has ..
    var pathValues = defaults.pathValues;
    var headers = [];
    var pairs = Array.from(params.entries());

    for(var pairIndex = 0; pairIndex < pairs.length; pairIndex++) {
        var key = pairs[pairIndex][0];
        var value = pairs[pairIndex][1];

        if(key.startsWith(config.pathPrefix)) {
            var pathName = key.slice(config.pathPrefix.length);

            if(pathName in pathValues) {
                pathValues[pathName] = value;
            }
        }

        if(key.startsWith(config.headerPrefix)) {
            headers.push({name: key.slice(config.headerPrefix.length), value: value});
        }
    }

    zatoPortal.invoke.setPathValues(card, pathValues);

    // .. and its headers replace the ones on the card.
    zatoPortal.state.exchanges[card.id].headers = headers;
    zatoPortal.options.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.init = function() {

    var entriesById = zatoPortal.state.entriesById;
    var entryIds = Object.keys(entriesById);

    for(var entryIndex = 0; entryIndex < entryIds.length; entryIndex++) {
        var entryId = entryIds[entryIndex];
        var operation = zatoPortal.links.getOperation(entriesById[entryId]);

        zatoPortal.links.state.entryIdsByOperation[operation] = entryId;
    }

    window.addEventListener('hashchange', zatoPortal.links.onHashChange);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.remember = function() {

    var hash = window.location.hash;

    // A link opened before signing in is followed once the portal is shown again
    if(hash !== '') {
        sessionStorage.setItem(zatoPortal.links.config.storageKey, hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.getEntryId = function(hash) {

    var entryIdsByOperation = zatoPortal.links.state.entryIdsByOperation;
    var operation = zatoPortal.links.splitHash(hash).operation;
    var decoded = '';

    // A link comes from outside the portal, and its escapes can be malformed
    try {
        decoded = decodeURIComponent(operation);
    }
    catch(error) {
        return '';
    }

    if(Object.hasOwn(entryIdsByOperation, decoded)) {
        return entryIdsByOperation[decoded];
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.showInitial = function(firstGroup) {

    var config = zatoPortal.links.config;
    var hash = window.location.hash;

    // A link that led to the sign-in page is the one followed, unless the address has a link of its own ..
    var remembered = sessionStorage.getItem(config.storageKey);
    sessionStorage.removeItem(config.storageKey);

    if(hash === '') {
        if(remembered !== null) {
            hash = remembered;
        }
    }

    var entryId = zatoPortal.links.getEntryId(hash);

    // .. an operation linked to is shown as it would be when chosen in the navigation, with the request linked to ..
    if(entryId !== '') {
        zatoPortal.links.showEntry(entryId);
        zatoPortal.links.applyRequest(entryId, zatoPortal.links.splitHash(hash).query);
        return;
    }

    // .. and without one the first group is shown.
    zatoPortal.render.selectGroup(firstGroup.name);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.showEntry = function(entryId) {

    var entry = zatoPortal.state.entriesById[entryId];

    zatoPortal.render.selectGroup(entry.group);
    zatoPortal.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.update = function(entryId) {

    var state = zatoPortal.links.state;
    state.pendingEntryId = entryId;

    // A group and then a card in it can be shown in one step, which is a single entry in the browser's history,
    // so the address is updated once, for the card shown last
    if(state.isUpdatePending) {
        return;
    }

    state.isUpdatePending = true;
    queueMicrotask(zatoPortal.links.flushUpdate);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.flushUpdate = function() {

    var state = zatoPortal.links.state;
    var entryId = state.pendingEntryId;
    var current = window.location.hash;

    state.isUpdatePending = false;

    var card = document.getElementById(entryId);
    var hash = zatoPortal.links.getCardHash(card);

    if(current === zatoPortal.links.getAddressHash(hash)) {
        return;
    }

    // Going to another operation is an entry in the browser's history, while the first operation shown,
    // an address that names no operation and a change to the operation's own request replace the entry ..
    var currentEntryId = zatoPortal.links.getEntryId(current);

    if(currentEntryId === '') {
        history.replaceState(null, '', hash);
        return;
    }

    if(currentEntryId === entryId) {
        history.replaceState(null, '', hash);
        return;
    }

    // .. and the entry left behind keeps the request it had.
    history.pushState(null, '', hash);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.refresh = function(card) {

    // The address follows the request as it is edited, but only on the card it names
    if(zatoPortal.links.getEntryId(window.location.hash) !== card.id) {
        return;
    }

    var hash = zatoPortal.links.getCardHash(card);

    if(window.location.hash !== zatoPortal.links.getAddressHash(hash)) {
        history.replaceState(null, '', hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.onCardInput = function(event) {
    zatoPortal.links.refresh(event.currentTarget);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.links.onHashChange = function() {

    var hash = window.location.hash;
    var entryId = zatoPortal.links.getEntryId(hash);

    if(entryId !== '') {
        zatoPortal.links.showEntry(entryId);
        zatoPortal.links.applyRequest(entryId, zatoPortal.links.splitHash(hash).query);
    }
};
