zatoConsole.raw = {};

zatoConsole.raw.config = {
    protocol: 'HTTP/1.1',
    headerSeparator: ': ',
    lineSeparator: '\n',
    sectionSeparator: '\n\n',
    querySeparator: '?',
    cardSelector: '.console-operation',
    editorSelector: '.console-editor',
    inputSelector: '.console-editor-input',
    requestRawSelector: '.console-raw-request',
    requestSwitchSelector: '.console-request-bar .console-switch-input',
    responseBodySelector: '.console-response-body',
    responseRawSelector: '.console-raw-response',
    responseSwitchSelector: '.console-response-bar .console-switch-input',
    headClass: 'console-raw-head',
    bodyClass: 'console-raw-body',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.getHeaderObject = function(headers) {

    // Our response to produce
    var out = {};

    // Rows whose name is still empty are being typed in and are not sent
    for(var headerIndex = 0; headerIndex < headers.length; headerIndex++) {
        var header = headers[headerIndex];
        var name = header.name.trim();

        if(name !== '') {
            out[name] = header.value;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.buildRequest = function(entry, text, pathValues, headers) {

    var config = zatoConsole.raw.config;
    var request = zatoConsole.invoke.buildRequest(entry, text, pathValues);
    var target = request.path;

    if(request.query !== '') {
        target += config.querySeparator + request.query;
    }

    var lines = [entry.method.toUpperCase() + ' ' + target + ' ' + config.protocol];

    if(request.body !== null) {
        lines.push(zatoConsole.invoke.config.contentTypeHeader + config.headerSeparator + zatoConsole.invoke.config.contentType);
    }

    var headerObject = zatoConsole.raw.getHeaderObject(headers);
    var names = Object.keys(headerObject);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        lines.push(name + config.headerSeparator + headerObject[name]);
    }

    var body = request.body;

    if(body === null) {
        body = '';
    }

    var out = {head: lines.join(config.lineSeparator), body: body};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.buildResponse = function(result) {

    var config = zatoConsole.raw.config;

    // A request that never reached the console has no status line and no headers, only the reason
    if(result.status === zatoConsole.invoke.config.networkErrorStatusCode) {
        var failure = {head: '', body: result.text};
        return failure;
    }

    var statusLine = config.protocol + ' ' + result.status + ' ' + result.statusText;
    var lines = [statusLine.trim()];

    for(var headerIndex = 0; headerIndex < result.headers.length; headerIndex++) {
        var header = result.headers[headerIndex];
        lines.push(header[0] + config.headerSeparator + header[1]);
    }

    var out = {head: lines.join(config.lineSeparator), body: result.text};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.getText = function(raw) {

    var config = zatoConsole.raw.config;

    if(raw.head === '') {
        return raw.body;
    }

    if(raw.body === '') {
        return raw.head;
    }

    var out = raw.head + config.sectionSeparator + raw.body;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.fill = function(element, raw) {

    var config = zatoConsole.raw.config;

    element.textContent = '';

    var head = zatoConsole.panels.createElement('span', config.headClass, raw.head);
    var body = zatoConsole.panels.createElement('span', config.bodyClass);

    // A JSON body keeps its colors, as it was sent or received, and any other body is shown as it is
    if(zatoConsole.invoke.parse(raw.body) === undefined) {
        body.textContent = raw.body;
    }
    else {
        zatoConsole.highlight.fill(body, raw.body);
    }

    element.appendChild(head);

    if(raw.head !== '') {
        if(raw.body !== '') {
            element.appendChild(document.createTextNode(config.sectionSeparator));
        }
    }

    element.appendChild(body);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.getCardRequest = function(card) {

    var config = zatoConsole.raw.config;
    var entry = zatoConsole.state.entriesById[card.id];
    var exchange = zatoConsole.state.exchanges[card.id];
    var input = card.querySelector(config.inputSelector);

    var pathValues = zatoConsole.invoke.getPathValues(card);

    var out = zatoConsole.raw.buildRequest(entry, input.value, pathValues, exchange.headers);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.isRequestRaw = function(card) {
    var out = card.querySelector(zatoConsole.raw.config.requestSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.isResponseRaw = function(card) {
    var out = card.querySelector(zatoConsole.raw.config.responseSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.refreshRequest = function(card) {

    var config = zatoConsole.raw.config;
    var isRaw = zatoConsole.raw.isRequestRaw(card);

    var editor = card.querySelector(config.editorSelector);
    var rawElement = card.querySelector(config.requestRawSelector);

    // The raw request is read-only and is built anew from the editor and the headers each time it is shown
    if(isRaw) {
        var raw = zatoConsole.raw.getCardRequest(card);
        zatoConsole.raw.fill(rawElement, raw);
    }

    editor.hidden = isRaw;
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.refreshResponse = function(card) {

    var config = zatoConsole.raw.config;
    var isRaw = zatoConsole.raw.isResponseRaw(card);
    var result = zatoConsole.state.exchanges[card.id].result;

    var bodyElement = card.querySelector(config.responseBodySelector);
    var rawElement = card.querySelector(config.responseRawSelector);

    if(isRaw) {
        var raw = zatoConsole.raw.buildResponse(result);
        zatoConsole.raw.fill(rawElement, raw);
    }

    // An empty body has nothing to show, while its raw form still has the status line and the headers
    bodyElement.hidden = isRaw || result.text === '';
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.onRequestSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoConsole.raw.config.cardSelector);
    zatoConsole.raw.refreshRequest(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.onResponseSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoConsole.raw.config.cardSelector);
    zatoConsole.raw.refreshResponse(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.getRequestCopyText = function(button) {

    var card = button.closest(zatoConsole.raw.config.cardSelector);

    if(zatoConsole.raw.isRequestRaw(card)) {
        var raw = zatoConsole.raw.getCardRequest(card);
        var rawText = zatoConsole.raw.getText(raw);
        return rawText;
    }

    var out = card.querySelector(zatoConsole.raw.config.inputSelector).value;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.getResponseCopyText = function(button) {

    var card = button.closest(zatoConsole.raw.config.cardSelector);
    var result = zatoConsole.state.exchanges[card.id].result;

    if(zatoConsole.raw.isResponseRaw(card)) {
        var raw = zatoConsole.raw.buildResponse(result);
        var rawText = zatoConsole.raw.getText(raw);
        return rawText;
    }

    var out = zatoConsole.invoke.getDisplayText(result.text);
    return out;
};
