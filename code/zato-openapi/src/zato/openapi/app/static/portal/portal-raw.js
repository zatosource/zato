zatoPortal.raw = {};

zatoPortal.raw.config = {
    protocol: 'HTTP/1.1',
    headerSeparator: ': ',
    lineSeparator: '\n',
    sectionSeparator: '\n\n',
    querySeparator: '?',
    cardSelector: '.portal-operation',
    editorSelector: '.portal-editor',
    inputSelector: '.portal-editor-input',
    requestRawSelector: '.portal-raw-request',
    requestSwitchSelector: '.portal-request-bar .portal-switch-input',
    responseBodySelector: '.portal-response-body',
    responseRawSelector: '.portal-raw-response',
    responseSwitchSelector: '.portal-response-bar .portal-switch-input',
    headClass: 'portal-raw-head',
    bodyClass: 'portal-raw-body',
    startSeparator: ' ',
    methodClassPrefix: 'portal-raw-method portal-raw-method-',
    targetClass: 'portal-raw-target',
    protocolClass: 'portal-raw-protocol',
    statusOkClass: 'portal-raw-status-ok',
    statusErrorClass: 'portal-raw-status-error',
    reasonClass: 'portal-raw-reason',
    headerNameClass: 'portal-raw-header-name',
    headerSeparatorClass: 'portal-raw-header-separator',
    headerValueClass: 'portal-raw-header-value',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.getHeaderObject = function(headers) {

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

zatoPortal.raw.buildRequest = function(entry, text, pathValues, headers) {

    var config = zatoPortal.raw.config;
    var request = zatoPortal.invoke.buildRequest(entry, text, pathValues);
    var target = request.path;

    if(request.query !== '') {
        target += config.querySeparator + request.query;
    }

    var lines = [entry.method.toUpperCase() + ' ' + target + ' ' + config.protocol];

    var headerObject = zatoPortal.invoke.getRequestHeaders(entry.operation, request, headers);
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

zatoPortal.raw.buildResponse = function(result) {

    var config = zatoPortal.raw.config;

    // A request that never reached the portal has no status line and no headers, only the reason
    if(result.status === zatoPortal.invoke.config.networkErrorStatusCode) {
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

zatoPortal.raw.getText = function(raw) {

    var config = zatoPortal.raw.config;

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

zatoPortal.raw.fillStartLine = function(head, line, startClasses) {

    var config = zatoPortal.raw.config;
    var rest = line;

    // The start line has as many parts as it has classes, and the last part keeps any spaces of its own,
    // as a reason phrase does
    for(var partIndex = 0; partIndex < startClasses.length; partIndex++) {

        var separatorIndex = rest.indexOf(config.startSeparator);
        var isLast = partIndex === startClasses.length - 1;

        if(isLast || separatorIndex === -1) {
            head.appendChild(zatoPortal.panels.createElement('span', startClasses[partIndex], rest));
            return;
        }

        head.appendChild(zatoPortal.panels.createElement('span', startClasses[partIndex], rest.slice(0, separatorIndex)));
        head.appendChild(document.createTextNode(config.startSeparator));

        rest = rest.slice(separatorIndex + config.startSeparator.length);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.fillHeaderLine = function(head, line) {

    var config = zatoPortal.raw.config;

    // A value can hold the separator itself, so only the first one ends the name
    var separatorIndex = line.indexOf(config.headerSeparator);
    var name = line.slice(0, separatorIndex);
    var value = line.slice(separatorIndex + config.headerSeparator.length);

    head.appendChild(zatoPortal.panels.createElement('span', config.headerNameClass, name));
    head.appendChild(zatoPortal.panels.createElement('span', config.headerSeparatorClass, config.headerSeparator));
    head.appendChild(zatoPortal.panels.createElement('span', config.headerValueClass, value));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.fillHead = function(head, raw) {

    var config = zatoPortal.raw.config;

    if(raw.head === '') {
        return;
    }

    var lines = raw.head.split(config.lineSeparator);

    zatoPortal.raw.fillStartLine(head, lines[0], raw.startClasses);

    for(var lineIndex = 1; lineIndex < lines.length; lineIndex++) {
        head.appendChild(document.createTextNode(config.lineSeparator));
        zatoPortal.raw.fillHeaderLine(head, lines[lineIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.fill = function(element, raw) {

    var config = zatoPortal.raw.config;

    element.textContent = '';

    var head = zatoPortal.panels.createElement('span', config.headClass);
    var body = zatoPortal.panels.createElement('span', config.bodyClass);

    // The head is colored part by part, and the body as the editor colors it, whether it is valid JSON or not
    zatoPortal.raw.fillHead(head, raw);
    zatoPortal.highlight.fill(body, raw.body);

    element.appendChild(head);

    if(raw.head !== '') {
        if(raw.body !== '') {
            element.appendChild(document.createTextNode(config.sectionSeparator));
        }
    }

    element.appendChild(body);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.getCardRequest = function(card) {

    var config = zatoPortal.raw.config;
    var entry = zatoPortal.state.entriesById[card.id];
    var exchange = zatoPortal.state.exchanges[card.id];
    var input = card.querySelector(config.inputSelector);

    var pathValues = zatoPortal.invoke.getPathValues(card);

    var out = zatoPortal.raw.buildRequest(entry, input.value, pathValues, exchange.headers);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.isRequestRaw = function(card) {
    var out = card.querySelector(zatoPortal.raw.config.requestSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.isResponseRaw = function(card) {
    var out = card.querySelector(zatoPortal.raw.config.responseSwitchSelector).checked;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.refreshRequest = function(card) {

    var config = zatoPortal.raw.config;
    var isRaw = zatoPortal.raw.isRequestRaw(card);

    var editor = card.querySelector(config.editorSelector);
    var rawElement = card.querySelector(config.requestRawSelector);

    // The raw request is read-only and is built anew from the editor and the headers each time it is shown
    if(isRaw) {
        var raw = zatoPortal.raw.getCardRequest(card);
        zatoPortal.raw.fill(rawElement, raw);
    }

    editor.hidden = isRaw;
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.refreshResponse = function(card) {

    var config = zatoPortal.raw.config;
    var isRaw = zatoPortal.raw.isResponseRaw(card);
    var result = zatoPortal.state.exchanges[card.id].result;

    var bodyElement = card.querySelector(config.responseBodySelector);
    var rawElement = card.querySelector(config.responseRawSelector);

    if(isRaw) {
        var raw = zatoPortal.raw.buildResponse(result);
        zatoPortal.raw.fill(rawElement, raw);
    }

    // An empty body has nothing to show, while its raw form still has the status line and the headers
    bodyElement.hidden = isRaw || result.text === '';
    rawElement.hidden = !isRaw;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.onRequestSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoPortal.raw.config.cardSelector);
    zatoPortal.raw.refreshRequest(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.onResponseSwitchChange = function(event) {
    var card = event.currentTarget.closest(zatoPortal.raw.config.cardSelector);
    zatoPortal.raw.refreshResponse(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.getRequestCopyText = function(button) {

    var card = button.closest(zatoPortal.raw.config.cardSelector);

    if(zatoPortal.raw.isRequestRaw(card)) {
        var raw = zatoPortal.raw.getCardRequest(card);
        var rawText = zatoPortal.raw.getText(raw);
        return rawText;
    }

    var out = card.querySelector(zatoPortal.raw.config.inputSelector).value;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.raw.getResponseCopyText = function(button) {

    var config = zatoPortal.raw.config;
    var card = button.closest(config.cardSelector);

    // The response is copied as it is shown, with any edits made to it
    var selector = config.responseBodySelector;

    if(zatoPortal.raw.isResponseRaw(card)) {
        selector = config.responseRawSelector;
    }

    var out = card.querySelector(selector).innerText;
    return out;
};
