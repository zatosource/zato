zatoApp.raw = {};

zatoApp.raw.config = {
    protocol: 'HTTP/1.1',
    headerSeparator: ': ',
    lineSeparator: '\n',
    sectionSeparator: '\n\n',
    querySeparator: '?',
    cardSelector: '.app-operation',
    editorSelector: '.app-editor',
    inputSelector: '.app-editor-input',
    requestRawSelector: '.app-raw-request',
    requestSwitchSelector: '.app-request-bar .app-switch-input',
    responseBodySelector: '.app-response-body',
    responseRawSelector: '.app-raw-response',
    responseSwitchSelector: '.app-response-bar .app-switch-input',
    headClass: 'app-raw-head',
    bodyClass: 'app-raw-body',
    startSeparator: ' ',
    methodClassPrefix: 'app-raw-method app-raw-method-',
    targetClass: 'app-raw-target',
    protocolClass: 'app-raw-protocol',
    statusOkClass: 'app-raw-status-ok',
    statusErrorClass: 'app-raw-status-error',
    reasonClass: 'app-raw-reason',
    headerNameClass: 'app-raw-header-name',
    headerSeparatorClass: 'app-raw-header-separator',
    headerValueClass: 'app-raw-header-value',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.getHeaderObject = function(headers) {

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

zatoApp.raw.buildRequest = function(entry, text, pathValues, headers) {

    var config = zatoApp.raw.config;
    var request = zatoApp.invoke.buildRequest(entry, text, pathValues);
    var target = request.path;

    if(request.query !== '') {
        target += config.querySeparator + request.query;
    }

    var lines = [entry.method.toUpperCase() + ' ' + target + ' ' + config.protocol];

    var headerObject = zatoApp.invoke.getRequestHeaders(entry.operation, request, headers);
    var names = Object.keys(headerObject);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        lines.push(name + config.headerSeparator + headerObject[name]);
    }

    var body = request.body;

    if(body === null) {
        body = '';
    }

    var startClasses = [config.methodClassPrefix + entry.method, config.targetClass, config.protocolClass];

    var out = {head: lines.join(config.lineSeparator), body: body, startClasses: startClasses};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.buildResponse = function(result) {

    var config = zatoApp.raw.config;

    // A request that never reached the app has no status line and no headers, only the reason
    if(result.status === zatoApp.invoke.config.networkErrorStatusCode) {
        var failure = {head: '', body: result.text, startClasses: []};
        return failure;
    }

    var statusLine = config.protocol + ' ' + result.status + ' ' + result.statusText;
    var lines = [statusLine.trim()];

    for(var headerIndex = 0; headerIndex < result.headers.length; headerIndex++) {
        var header = result.headers[headerIndex];
        lines.push(header[0] + config.headerSeparator + header[1]);
    }

    var statusClass = result.isOk ? config.statusOkClass : config.statusErrorClass;
    var startClasses = [config.protocolClass, statusClass, config.reasonClass];

    var out = {head: lines.join(config.lineSeparator), body: result.text, startClasses: startClasses};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.getText = function(raw) {

    var config = zatoApp.raw.config;

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

zatoApp.raw.fillStartLine = function(head, line, startClasses) {

    var config = zatoApp.raw.config;
    var rest = line;

    // The start line has as many parts as it has classes, and the last part keeps any spaces of its own,
    // as a reason phrase does
    for(var partIndex = 0; partIndex < startClasses.length; partIndex++) {

        var separatorIndex = rest.indexOf(config.startSeparator);
        var isLast = partIndex === startClasses.length - 1;

        if(isLast || separatorIndex === -1) {
            head.appendChild(zatoApp.panels.createElement('span', startClasses[partIndex], rest));
            return;
        }

        head.appendChild(zatoApp.panels.createElement('span', startClasses[partIndex], rest.slice(0, separatorIndex)));
        head.appendChild(document.createTextNode(config.startSeparator));

        rest = rest.slice(separatorIndex + config.startSeparator.length);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.fillHeaderLine = function(head, line) {

    var config = zatoApp.raw.config;

    // A value can hold the separator itself, so only the first one ends the name
    var separatorIndex = line.indexOf(config.headerSeparator);
    var name = line.slice(0, separatorIndex);
    var value = line.slice(separatorIndex + config.headerSeparator.length);

    head.appendChild(zatoApp.panels.createElement('span', config.headerNameClass, name));
    head.appendChild(zatoApp.panels.createElement('span', config.headerSeparatorClass, config.headerSeparator));
    head.appendChild(zatoApp.panels.createElement('span', config.headerValueClass, value));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.fillHead = function(head, raw) {

    var config = zatoApp.raw.config;

    if(raw.head === '') {
        return;
    }

    var lines = raw.head.split(config.lineSeparator);

    zatoApp.raw.fillStartLine(head, lines[0], raw.startClasses);

    for(var lineIndex = 1; lineIndex < lines.length; lineIndex++) {
        head.appendChild(document.createTextNode(config.lineSeparator));
        zatoApp.raw.fillHeaderLine(head, lines[lineIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.fill = function(element, raw) {

    var config = zatoApp.raw.config;

    element.textContent = '';

    var head = zatoApp.panels.createElement('span', config.headClass);
    var body = zatoApp.panels.createElement('span', config.bodyClass);

    // The head is colored part by part, and the body as the editor colors it, whether it is valid JSON or not
    zatoApp.raw.fillHead(head, raw);
    zatoApp.highlight.fill(body, raw.body);

    element.appendChild(head);

    if(raw.head !== '') {
        if(raw.body !== '') {
            element.appendChild(document.createTextNode(config.sectionSeparator));
        }
    }

    element.appendChild(body);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.getCardRequest = function(card) {

    var config = zatoApp.raw.config;
    var entry = zatoApp.state.entriesById[card.id];
    var exchange = zatoApp.state.exchanges[card.id];
    var input = card.querySelector(config.inputSelector);

    var pathValues = zatoApp.invoke.getPathValues(card);

    var out = zatoApp.raw.buildRequest(entry, input.value, pathValues, exchange.headers);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.isRequestRaw = function(card) {
    var out = card.querySelector(zatoApp.raw.config.requestSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.isResponseRaw = function(card) {
    var out = card.querySelector(zatoApp.raw.config.responseSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.refreshRequest = function(card) {

    var config = zatoApp.raw.config;
    var isRaw = zatoApp.raw.isRequestRaw(card);

    var editor = card.querySelector(config.editorSelector);
    var rawElement = card.querySelector(config.requestRawSelector);

    // The raw request is read-only and is built anew from the editor and the headers each time it is shown
    if(isRaw) {
        var raw = zatoApp.raw.getCardRequest(card);
        zatoApp.raw.fill(rawElement, raw);
    }

    editor.hidden = isRaw;
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.refreshResponse = function(card) {

    var config = zatoApp.raw.config;
    var isRaw = zatoApp.raw.isResponseRaw(card);
    var result = zatoApp.state.exchanges[card.id].result;

    var bodyElement = card.querySelector(config.responseBodySelector);
    var rawElement = card.querySelector(config.responseRawSelector);

    if(isRaw) {
        var raw = zatoApp.raw.buildResponse(result);
        zatoApp.raw.fill(rawElement, raw);
    }

    // An empty body has nothing to show, while its raw form still has the status line and the headers
    bodyElement.hidden = isRaw || result.text === '';
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.onRequestSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoApp.raw.config.cardSelector);
    zatoApp.raw.refreshRequest(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.onResponseSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoApp.raw.config.cardSelector);
    zatoApp.raw.refreshResponse(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.getRequestCopyText = function(button) {

    var card = button.closest(zatoApp.raw.config.cardSelector);

    if(zatoApp.raw.isRequestRaw(card)) {
        var raw = zatoApp.raw.getCardRequest(card);
        var rawText = zatoApp.raw.getText(raw);
        return rawText;
    }

    var out = card.querySelector(zatoApp.raw.config.inputSelector).value;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.raw.getResponseCopyText = function(button) {

    var config = zatoApp.raw.config;
    var card = button.closest(config.cardSelector);

    // The response is copied as it is shown, with any edits made to it
    var selector = config.responseBodySelector;

    if(zatoApp.raw.isResponseRaw(card)) {
        selector = config.responseRawSelector;
    }

    var out = card.querySelector(selector).innerText;
    return out;
};
