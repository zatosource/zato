zatoConsole.links = {};

zatoConsole.links.config = {
    hashPrefix: '#',
    storageKey: 'zato.openapi.console.link',
    inputSelector: '.console-editor-input',
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

zatoConsole.links.state = {
    entryIdsByOperation: {},
    pendingEntryId: '',
    isUpdatePending: false,
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getOperation = function(entry) {
    var out = zatoConsole.links.config.hashPrefix + entry.method + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.escapePath = function(path) {

    var escapes = zatoConsole.links.config.pathEscapes;

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

zatoConsole.links.getHash = function(entry) {

    var path = zatoConsole.links.escapePath(entry.path);

    var out = zatoConsole.links.config.hashPrefix + entry.method + path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getDefaults = function(entry) {

    var sample = zatoConsole.invoke.buildSample(entry, false);

    var out = {
        requestText: zatoConsole.highlight.format(sample),
        pathValues: zatoConsole.invoke.getPathExamples(entry.operation),
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getCompactText = function(text) {

    var parsed = zatoConsole.invoke.parse(text);

    // A JSON request is compared and linked to without its indentation, and any other one as it was typed
    if(parsed === undefined) {
        return text;
    }

    var out = JSON.stringify(parsed);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getRequestQuery = function(card) {

    var config = zatoConsole.links.config;
    var entry = zatoConsole.state.entriesById[card.id];
    var defaults = zatoConsole.links.getDefaults(entry);
    var params = new URLSearchParams();

    // A link carries only what differs from what the card starts with, beginning with the request ..
    var text = zatoConsole.links.getCompactText(card.querySelector(config.inputSelector).value);
    var defaultText = zatoConsole.links.getCompactText(defaults.requestText);

    if(text !== defaultText) {
        params.append(config.requestKey, text);
    }

    // .. followed by the path parameters ..
    var pathValues = zatoConsole.invoke.getPathValues(card);
    var pathNames = Object.keys(pathValues);

    for(var nameIndex = 0; nameIndex < pathNames.length; nameIndex++) {
        var pathName = pathNames[nameIndex];

        if(pathValues[pathName] !== defaults.pathValues[pathName]) {
            params.append(config.pathPrefix + pathName, pathValues[pathName]);
        }
    }

    // .. and the headers that have a name.
    var headers = zatoConsole.state.exchanges[card.id].headers;

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

zatoConsole.links.getCardHash = function(card) {

    var entry = zatoConsole.state.entriesById[card.id];
    var query = zatoConsole.links.getRequestQuery(card);

    var out = zatoConsole.links.getHash(entry);

    if(query !== '') {
        out += zatoConsole.links.config.requestSeparator + query;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getAddressHash = function(hash) {

    // The address keeps any characters outside of ASCII percent-encoded, e.g. those of a path in Greek
    var out = new URL(hash, window.location.href).hash;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getUrl = function(card) {

    var address = window.location;
    var hash = zatoConsole.links.getCardHash(card);

    var out = address.origin + address.pathname + address.search + hash;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.splitHash = function(hash) {

    var config = zatoConsole.links.config;
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

zatoConsole.links.applyRequest = function(entryId, query) {

    var config = zatoConsole.links.config;
    var card = document.getElementById(entryId);
    var params = new URLSearchParams(query);

    // A card that already holds the request linked to is left as it is, with the caret where it was ..
    if(zatoConsole.links.getRequestQuery(card) === params.toString()) {
        return;
    }

    // .. otherwise, what the link leaves out is what the card starts with, and the request is shown
    // the way the editor formats it ..
    var defaults = zatoConsole.links.getDefaults(zatoConsole.state.entriesById[entryId]);
    var text = defaults.requestText;

    if(params.has(config.requestKey)) {
        text = params.get(config.requestKey);
    }

    var parsed = zatoConsole.invoke.parse(text);

    if(parsed !== undefined) {
        text = zatoConsole.highlight.format(parsed);
    }

    zatoConsole.invoke.setRequestText(card, text);

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

    zatoConsole.invoke.setPathValues(card, pathValues);

    // .. and its headers replace the ones on the card.
    zatoConsole.state.exchanges[card.id].headers = headers;
    zatoConsole.options.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.init = function() {

    var entriesById = zatoConsole.state.entriesById;
    var entryIds = Object.keys(entriesById);

    for(var entryIndex = 0; entryIndex < entryIds.length; entryIndex++) {
        var entryId = entryIds[entryIndex];
        var operation = zatoConsole.links.getOperation(entriesById[entryId]);

        zatoConsole.links.state.entryIdsByOperation[operation] = entryId;
    }

    window.addEventListener('hashchange', zatoConsole.links.onHashChange);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.remember = function() {

    var hash = window.location.hash;

    // A link opened before signing in is followed once the console is shown again
    if(hash !== '') {
        sessionStorage.setItem(zatoConsole.links.config.storageKey, hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.getEntryId = function(hash) {

    var entryIdsByOperation = zatoConsole.links.state.entryIdsByOperation;
    var operation = zatoConsole.links.splitHash(hash).operation;
    var decoded = '';

    // A link comes from outside the console, and its escapes can be malformed
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

zatoConsole.links.showInitial = function(firstGroup) {

    var config = zatoConsole.links.config;
    var hash = window.location.hash;

    // A link that led to the sign-in page is the one followed, unless the address has a link of its own ..
    var remembered = sessionStorage.getItem(config.storageKey);
    sessionStorage.removeItem(config.storageKey);

    if(hash === '') {
        if(remembered !== null) {
            hash = remembered;
        }
    }

    var entryId = zatoConsole.links.getEntryId(hash);

    // .. an operation linked to is shown as it would be when chosen in the navigation, with the request linked to ..
    if(entryId !== '') {
        zatoConsole.links.showEntry(entryId);
        zatoConsole.links.applyRequest(entryId, zatoConsole.links.splitHash(hash).query);
        return;
    }

    // .. and without one the first group is shown.
    zatoConsole.render.selectGroup(firstGroup.name);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.showEntry = function(entryId) {

    var entry = zatoConsole.state.entriesById[entryId];

    zatoConsole.render.selectGroup(entry.group);
    zatoConsole.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.update = function(entryId) {

    var state = zatoConsole.links.state;
    state.pendingEntryId = entryId;

    // A group and then a card in it can be shown in one step, which is a single entry in the browser's history,
    // so the address is updated once, for the card shown last
    if(state.isUpdatePending) {
        return;
    }

    state.isUpdatePending = true;
    queueMicrotask(zatoConsole.links.flushUpdate);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.flushUpdate = function() {

    var state = zatoConsole.links.state;
    var entryId = state.pendingEntryId;
    var current = window.location.hash;

    state.isUpdatePending = false;

    var card = document.getElementById(entryId);
    var hash = zatoConsole.links.getCardHash(card);

    if(current === zatoConsole.links.getAddressHash(hash)) {
        return;
    }

    // Going to another operation is an entry in the browser's history, while the first operation shown,
    // an address that names no operation and a change to the operation's own request replace the entry ..
    var currentEntryId = zatoConsole.links.getEntryId(current);

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

zatoConsole.links.refresh = function(card) {

    // The address follows the request as it is edited, but only on the card it names
    if(zatoConsole.links.getEntryId(window.location.hash) !== card.id) {
        return;
    }

    var hash = zatoConsole.links.getCardHash(card);

    if(window.location.hash !== zatoConsole.links.getAddressHash(hash)) {
        history.replaceState(null, '', hash);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.onCardInput = function(event) {
    zatoConsole.links.refresh(event.currentTarget);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.links.onHashChange = function() {

    var hash = window.location.hash;
    var entryId = zatoConsole.links.getEntryId(hash);

    if(entryId !== '') {
        zatoConsole.links.showEntry(entryId);
        zatoConsole.links.applyRequest(entryId, zatoConsole.links.splitHash(hash).query);
    }
};
