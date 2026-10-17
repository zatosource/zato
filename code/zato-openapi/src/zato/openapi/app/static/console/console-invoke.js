zatoConsole.invoke = {};

zatoConsole.invoke.config = {
    contentType: 'application/json',
    contentTypeHeader: 'Content-Type',
    acceptHeader: 'Accept',
    queryStringMethods: ['get', 'head', 'delete'],
    placeholderPattern: /\{([^}]+)\}/g,
    cardSelector: '.console-operation',
    relayMethod: 'POST',
    csrfTokenSelector: 'meta[name="csrf-token"]',
    csrfTokenHeader: 'X-CSRFToken',
    serverHeadersName: 'X-Zato-Console-Response-Headers',
    pathParameterLocation: 'path',
    pathInputSelector: '.console-path-input',
    pathParameterAttribute: 'data-parameter',
    pathInputMinimumSize: 4,
    inputSelector: '.console-editor-input',
    editorSelector: '.console-editor',
    playSelector: '.console-play',
    invalidClass: 'console-editor-invalid',
    exampleKey: 'example',
    completeExampleKey: 'x-complete-example',
    invokeKey: 'Enter',
    indicatorMinimumMs: 60,
    invokingSelector: '.console-invoking',
    responseSelector: '.console-operation-response',
    statusSelector: '.console-response-status',
    timeSelector: '.console-response-time',
    bodySelector: '.console-response-body',
    statusOkClass: 'console-chip console-response-status console-chip-success',
    statusErrorClass: 'console-chip console-response-status console-chip-error',
    statusOkMinimum: 200,
    statusOkMaximum: 299,
    statusUnauthorized: 401,
    networkErrorText: 'The console could not be reached',
    networkErrorStatus: 'Error',
    networkErrorStatusCode: 0,
    timeSuffix: ' ms',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.isObject = function(value) {

    if(value === null) {
        return false;
    }

    var out = typeof value === 'object' && !Array.isArray(value);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getExample = function(holder, isComplete) {

    var config = zatoConsole.invoke.config;

    // The complete example, with every optional property, is there only in documents that the console's own generator builds ..
    if(isComplete) {
        if(config.completeExampleKey in holder) {
            return holder[config.completeExampleKey];
        }
    }

    // .. and any document can have the standard one.
    if(config.exampleKey in holder) {
        return holder[config.exampleKey];
    }

    return undefined;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getBodyExample = function(operation, isComplete) {

    if(!('requestBody' in operation)) {
        return undefined;
    }

    var content = operation.requestBody.content[zatoConsole.invoke.config.contentType];

    var out = zatoConsole.invoke.getExample(content, isComplete);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.buildSample = function(entry, isComplete) {

    var config = zatoConsole.invoke.config;
    var operation = entry.operation;
    var sample = {};

    // Query string parameters with a sample value of their own come first, while path parameters
    // have inputs of their own in the path ..
    if('parameters' in operation) {
        for(var parameterIndex = 0; parameterIndex < operation.parameters.length; parameterIndex++) {
            var parameter = operation.parameters[parameterIndex];

            if(parameter.in === config.pathParameterLocation) {
                continue;
            }

            var parameterExample = zatoConsole.invoke.getExample(parameter, isComplete);

            if(parameterExample !== undefined) {
                sample[parameter.name] = parameterExample;
            }
        }
    }

    var bodyExample = zatoConsole.invoke.getBodyExample(operation, isComplete);

    if(bodyExample === undefined) {
        return sample;
    }

    // .. followed by the body's own properties ..
    if(zatoConsole.invoke.isObject(bodyExample)) {
        Object.assign(sample, bodyExample);
        return sample;
    }

    // .. unless the body is not an object, in which case it is the whole request.
    return bodyExample;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.setRequestText = function(card, text) {

    var input = card.querySelector(zatoConsole.invoke.config.inputSelector);

    input.value = text;
    zatoConsole.highlight.refreshEditor(input);
    zatoConsole.invoke.markInvalid(card, false);
    zatoConsole.raw.refreshRequest(card);
    zatoConsole.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.markInvalid = function(card, isInvalid) {
    var editor = card.querySelector(zatoConsole.invoke.config.editorSelector);
    editor.classList.toggle(zatoConsole.invoke.config.invalidClass, isInvalid);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onExampleClick = function(event) {

    var card = event.currentTarget.closest(zatoConsole.invoke.config.cardSelector);
    var entry = zatoConsole.state.entriesById[card.id];

    // The example has every property of the request, and the path parameters return to their sample values
    var sample = zatoConsole.invoke.buildSample(entry, true);
    var text = zatoConsole.highlight.format(sample);

    var pathExamples = zatoConsole.invoke.getPathExamples(entry.operation);
    zatoConsole.invoke.setPathValues(card, pathExamples);

    zatoConsole.invoke.setRequestText(card, text);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onPrettyPrintClick = function(event) {

    var card = event.currentTarget.closest(zatoConsole.invoke.config.cardSelector);
    var input = card.querySelector(zatoConsole.invoke.config.inputSelector);

    // Key=value lines are aligned on their separators ..
    if(zatoConsole.keyValue.isKeyValue(input.value)) {
        var aligned = zatoConsole.keyValue.format(input.value);

        if(aligned === null) {
            zatoConsole.invoke.markInvalid(card, true);
            return;
        }

        zatoConsole.invoke.setRequestText(card, aligned);
        return;
    }

    // .. and any other request is JSON, which stays as it was typed when it does not parse, with the editor showing it
    var parsed = zatoConsole.invoke.parse(input.value);

    if(parsed === undefined) {
        zatoConsole.invoke.markInvalid(card, true);
        return;
    }

    var text = zatoConsole.highlight.format(parsed);
    zatoConsole.invoke.setRequestText(card, text);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onEditorInput = function(event) {
    var card = event.target.closest(zatoConsole.invoke.config.cardSelector);
    zatoConsole.invoke.markInvalid(card, false);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onCardKeyDown = function(event) {

    var config = zatoConsole.invoke.config;

    // Only Enter sends a request ..
    if(event.key !== config.invokeKey) {
        return;
    }

    // .. a path parameter is a single line, so Enter alone sends the request from it ..
    var isPathInput = event.target.matches(config.pathInputSelector);

    if(!isPathInput && !event.ctrlKey && !event.metaKey) {
        return;
    }

    // .. and the request is sent from wherever it is being edited, unless one is already under way.
    event.preventDefault();

    var play = event.currentTarget.querySelector(config.playSelector);

    if(!play.disabled) {
        play.click();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.parse = function(text) {

    try {
        var out = JSON.parse(text);
        return out;
    }
    catch(error) {
        return undefined;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.parseRequest = function(text) {

    // A request is JSON or key=value lines, the same as in the Dashboard
    var parsed = zatoConsole.invoke.parse(text);

    if(parsed !== undefined) {
        return parsed;
    }

    if(!zatoConsole.keyValue.isKeyValue(text)) {
        return undefined;
    }

    var pairs = zatoConsole.keyValue.parse(text);

    if(pairs === null) {
        return undefined;
    }

    return pairs;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.fillPath = function(path, values) {

    var pattern = new RegExp(zatoConsole.invoke.config.placeholderPattern.source, 'g');
    var out = path;
    var match = pattern.exec(path);

    while(match !== null) {
        var placeholder = match[0];
        var name = match[1];

        if(name in values) {
            var value = String(values[name]);
            var encoded = encodeURIComponent(value);
            out = out.replace(placeholder, encoded);
        }

        match = pattern.exec(path);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getPathExamples = function(operation) {

    var config = zatoConsole.invoke.config;

    // Our response to produce
    var out = {};

    if(!('parameters' in operation)) {
        return out;
    }

    for(var parameterIndex = 0; parameterIndex < operation.parameters.length; parameterIndex++) {
        var parameter = operation.parameters[parameterIndex];

        if(parameter.in === config.pathParameterLocation) {
            out[parameter.name] = String(parameter.example);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getPathValues = function(card) {

    var config = zatoConsole.invoke.config;
    var inputs = card.querySelectorAll(config.pathInputSelector);

    // Our response to produce
    var out = {};

    for(var inputIndex = 0; inputIndex < inputs.length; inputIndex++) {
        var input = inputs[inputIndex];
        var name = input.getAttribute(config.pathParameterAttribute);

        out[name] = input.value;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.setPathValues = function(card, values) {

    var config = zatoConsole.invoke.config;
    var inputs = card.querySelectorAll(config.pathInputSelector);

    for(var inputIndex = 0; inputIndex < inputs.length; inputIndex++) {
        var input = inputs[inputIndex];
        var name = input.getAttribute(config.pathParameterAttribute);

        input.value = values[name];
        zatoConsole.invoke.sizePathInput(input);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.sizePathInput = function(input) {

    // An input is as wide as its value, or as its parameter's name while it is empty
    var length = Math.max(input.value.length, input.placeholder.length);
    input.size = Math.max(length, zatoConsole.invoke.config.pathInputMinimumSize);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onPathInput = function(event) {

    var input = event.target;
    var card = input.closest(zatoConsole.invoke.config.cardSelector);

    zatoConsole.invoke.sizePathInput(input);
    zatoConsole.raw.refreshRequest(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.buildQueryString = function(values) {

    var search = new URLSearchParams();
    var names = Object.keys(values);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        var value = values[name];

        // Nested values travel as JSON and everything else as its text
        if(typeof value === 'object') {
            value = JSON.stringify(value);
        }

        search.append(name, value);
    }

    var out = search.toString();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.buildRequest = function(entry, text, pathValues) {

    var config = zatoConsole.invoke.config;
    var usesQueryString = config.queryStringMethods.includes(entry.method);
    var parsed = zatoConsole.invoke.parseRequest(text);

    // Our response to produce, with the path parameters from their own inputs
    var out = {path: zatoConsole.invoke.fillPath(entry.path, pathValues), query: '', body: null};

    // An empty editor sends neither a query string nor a body ..
    if(text.trim() === '') {
        return out;
    }

    // .. an object of plain values is the query string of the methods that have one ..
    if(zatoConsole.invoke.isObject(parsed)) {
        if(usesQueryString && zatoConsole.invoke.hasPlainValues(parsed)) {
            out.query = zatoConsole.invoke.buildQueryString(parsed);
        }
        else {
            out.body = JSON.stringify(parsed);
        }

        return out;
    }

    // .. while anything else is the body as it was typed, whatever the method.
    out.body = text;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.hasPlainValues = function(values) {

    var names = Object.keys(values);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var value = values[names[nameIndex]];

        if(typeof value === 'object' && value !== null) {
            return false;
        }
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getRequestHeaders = function(operation, request, headers) {

    var config = zatoConsole.invoke.config;
    var callerHeaders = zatoConsole.raw.getHeaderObject(headers);
    var contentTypeName = config.contentTypeHeader.toLowerCase();
    var acceptName = config.acceptHeader.toLowerCase();
    var mediaType = zatoConsole.fields.getResponseMediaType(operation);

    // Our response to produce
    var out = {};

    // A body is JSON and a response is expected in the media type that the operation documents,
    // unless the caller names a content type or an Accept value of their own ..
    if(request.body !== null) {
        out[config.contentTypeHeader] = config.contentType;
    }

    if(mediaType !== null) {
        out[config.acceptHeader] = mediaType;
    }

    var names = Object.keys(callerHeaders);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        var lowerName = name.toLowerCase();

        // .. which replaces the default one, whatever the case its name is typed in.
        if(lowerName === contentTypeName) {
            delete out[config.contentTypeHeader];
        }

        if(lowerName === acceptName) {
            delete out[config.acceptHeader];
        }

        out[name] = callerHeaders[name];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onPlayClick = function(event) {

    var config = zatoConsole.invoke.config;
    var button = event.currentTarget;
    var card = button.closest(config.cardSelector);
    var entry = zatoConsole.state.entriesById[card.id];
    var exchange = zatoConsole.state.exchanges[card.id];
    var input = card.querySelector(config.inputSelector);
    var invoking = card.querySelector(config.invokingSelector);

    var requestText = input.value;
    var pathValues = zatoConsole.invoke.getPathValues(card);
    var request = zatoConsole.invoke.buildRequest(entry, requestText, pathValues);

    var url = zatoConsole.state.relayBase + request.path;

    // The method, the query string, the caller's own headers and the body travel to the endpoint as one JSON document,
    // apart from the headers the browser adds on its own and clear of the size limits that proxies put on headers ..
    var envelope = {
        method: entry.method.toUpperCase(),
        query: request.query,
        headers: zatoConsole.invoke.getRequestHeaders(entry.operation, request, exchange.headers),
        body: request.body,
    };

    var csrfToken = document.querySelector(config.csrfTokenSelector).content;

    var headers = {};
    headers[config.contentTypeHeader] = config.contentType;
    headers[config.csrfTokenHeader] = csrfToken;

    var options = {method: config.relayMethod, headers: headers, body: JSON.stringify(envelope), cache: 'no-store'};

    // .. the button stays disabled and the indicator next to it stays shown until the response arrives ..
    button.disabled = true;
    invoking.hidden = false;

    // .. and the history keeps the request with the headers as they were when it was sent.
    var pending = {
        card: card,
        button: button,
        invoking: invoking,
        startedAt: performance.now(),
        requestText: requestText,
        pathValues: pathValues,
        headers: JSON.parse(JSON.stringify(exchange.headers)),
    };

    var onResponse = zatoConsole.invoke.onResponse.bind(null, pending);
    var onNetworkError = zatoConsole.invoke.onNetworkError.bind(null, pending);

    fetch(url, options).then(onResponse, onNetworkError);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getServerHeaders = function(response) {

    var value = response.headers.get(zatoConsole.invoke.config.serverHeadersName);

    // The relay sends the endpoint's own headers only when the endpoint was invoked, and not when the console rejected the request
    if(value === null) {
        return [];
    }

    var text = decodeURIComponent(value);

    var out = JSON.parse(text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onResponse = function(pending, response) {

    var config = zatoConsole.invoke.config;
    var hasServerHeaders = response.headers.has(config.serverHeadersName);

    // A session that has ended signs in again, which a 401 from the endpoint itself does not mean
    if(response.status === config.statusUnauthorized) {
        if(!hasServerHeaders) {
            zatoConsole.signOut();
            return;
        }
    }

    var isOk = response.status >= config.statusOkMinimum;

    if(isOk) {
        isOk = response.status <= config.statusOkMaximum;
    }

    var headers = zatoConsole.invoke.getServerHeaders(response);

    var finish = zatoConsole.invoke.finish.bind(null, pending, response.status, response.statusText, isOk, headers);
    response.text().then(finish);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.onNetworkError = function(pending) {

    var config = zatoConsole.invoke.config;
    zatoConsole.invoke.finish(pending, config.networkErrorStatusCode, '', false, [], config.networkErrorText);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.finish = function(pending, status, statusText, isOk, headers, text) {

    var elapsed = performance.now() - pending.startedAt;

    var result = {
        status: status,
        statusText: statusText,
        isOk: isOk,
        durationMs: Math.round(elapsed),
        headers: headers,
        text: text,
    };

    // The indicator stays on screen a moment past the response, as in the Dashboard's IDE,
    // so that a fast call does not make it a barely visible blip
    var complete = zatoConsole.invoke.complete.bind(null, pending, result);
    setTimeout(complete, zatoConsole.invoke.config.indicatorMinimumMs);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.complete = function(pending, result) {

    pending.button.disabled = false;
    pending.invoking.hidden = true;

    zatoConsole.invoke.showResult(pending.card, result);
    zatoConsole.history.record(pending.card, pending.requestText, pending.pathValues, pending.headers, result);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getStatusText = function(result) {

    var config = zatoConsole.invoke.config;

    if(result.status === config.networkErrorStatusCode) {
        return config.networkErrorStatus;
    }

    var statusText = result.status + ' ' + result.statusText;

    var out = statusText.trim();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.getDisplayText = function(text) {

    var parsed = zatoConsole.invoke.parse(text);

    // A JSON body is shown formatted and anything else as it arrived
    if(parsed === undefined) {
        return text;
    }

    var out = zatoConsole.highlight.format(parsed);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.invoke.showResult = function(card, result) {

    var config = zatoConsole.invoke.config;

    var response = card.querySelector(config.responseSelector);
    var statusElement = card.querySelector(config.statusSelector);
    var timeElement = card.querySelector(config.timeSelector);
    var bodyElement = card.querySelector(config.bodySelector);

    zatoConsole.state.exchanges[card.id].result = result;

    statusElement.textContent = zatoConsole.invoke.getStatusText(result);
    statusElement.className = result.isOk ? config.statusOkClass : config.statusErrorClass;
    timeElement.textContent = result.durationMs + config.timeSuffix;

    var displayText = zatoConsole.invoke.getDisplayText(result.text);

    if(zatoConsole.invoke.parse(result.text) === undefined) {
        bodyElement.textContent = displayText;
    }
    else {
        zatoConsole.highlight.fill(bodyElement, displayText);
    }

    response.hidden = false;
    zatoConsole.raw.refreshResponse(card);
};
