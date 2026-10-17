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
    startSeparator: ' ',
    methodClassPrefix: 'console-raw-method console-raw-method-',
    targetClass: 'console-raw-target',
    protocolClass: 'console-raw-protocol',
    statusOkClass: 'console-raw-status-ok',
    statusErrorClass: 'console-raw-status-error',
    reasonClass: 'console-raw-reason',
    headerNameClass: 'console-raw-header-name',
    headerSeparatorClass: 'console-raw-header-separator',
    headerValueClass: 'console-raw-header-value',
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

    var headerObject = zatoConsole.invoke.getRequestHeaders(entry.operation, request, headers);
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

zatoConsole.raw.buildResponse = function(result) {

    var config = zatoConsole.raw.config;

    // A request that never reached the console has no status line and no headers, only the reason
    if(result.status === zatoConsole.invoke.config.networkErrorStatusCode) {
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

zatoConsole.raw.fillStartLine = function(head, line, startClasses) {

    var config = zatoConsole.raw.config;
    var rest = line;

    // The start line has as many parts as it has classes, and the last part keeps any spaces of its own,
    // as a reason phrase does
    for(var partIndex = 0; partIndex < startClasses.length; partIndex++) {

        var separatorIndex = rest.indexOf(config.startSeparator);
        var isLast = partIndex === startClasses.length - 1;

        if(isLast || separatorIndex === -1) {
            head.appendChild(zatoConsole.panels.createElement('span', startClasses[partIndex], rest));
            return;
        }

        head.appendChild(zatoConsole.panels.createElement('span', startClasses[partIndex], rest.slice(0, separatorIndex)));
        head.appendChild(document.createTextNode(config.startSeparator));

        rest = rest.slice(separatorIndex + config.startSeparator.length);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.fillHeaderLine = function(head, line) {

    var config = zatoConsole.raw.config;

    // A value can hold the separator itself, so only the first one ends the name
    var separatorIndex = line.indexOf(config.headerSeparator);
    var name = line.slice(0, separatorIndex);
    var value = line.slice(separatorIndex + config.headerSeparator.length);

    head.appendChild(zatoConsole.panels.createElement('span', config.headerNameClass, name));
    head.appendChild(zatoConsole.panels.createElement('span', config.headerSeparatorClass, config.headerSeparator));
    head.appendChild(zatoConsole.panels.createElement('span', config.headerValueClass, value));
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.fillHead = function(head, raw) {

    var config = zatoConsole.raw.config;

    if(raw.head === '') {
        return;
    }

    var lines = raw.head.split(config.lineSeparator);

    zatoConsole.raw.fillStartLine(head, lines[0], raw.startClasses);

    for(var lineIndex = 1; lineIndex < lines.length; lineIndex++) {
        head.appendChild(document.createTextNode(config.lineSeparator));
        zatoConsole.raw.fillHeaderLine(head, lines[lineIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.raw.fill = function(element, raw) {

    var config = zatoConsole.raw.config;

    element.textContent = '';

    var head = zatoConsole.panels.createElement('span', config.headClass);
    var body = zatoConsole.panels.createElement('span', config.bodyClass);

    // The head is colored part by part, and the body as the editor colors it, whether it is valid JSON or not
    zatoConsole.raw.fillHead(head, raw);
    zatoConsole.highlight.fill(body, raw.body);

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

    var config = zatoConsole.raw.config;
    var card = button.closest(config.cardSelector);

    // The response is copied as it is shown, with any edits made to it
    var selector = config.responseBodySelector;

    if(zatoConsole.raw.isResponseRaw(card)) {
        selector = config.responseRawSelector;
    }

    var out = card.querySelector(selector).innerText;
    return out;
};
