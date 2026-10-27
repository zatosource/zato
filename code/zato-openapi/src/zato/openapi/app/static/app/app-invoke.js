zatoApp.invoke = {};

zatoApp.invoke.config = {
    contentType: 'application/json',
    xmlContentType: 'application/xml',
    textContentType: 'text/plain',
    xmlMarker: '<',
    contentTypeHeader: 'Content-Type',
    acceptHeader: 'Accept',
    placeholderPattern: /\{([^}]+)\}/g,
    cardSelector: '.app-operation',
    relayMethod: 'POST',
    csrfTokenSelector: 'meta[name="csrf-token"]',
    csrfTokenHeader: 'X-CSRFToken',
    serverHeadersName: 'X-Zato-Response-Headers',
    pathParameterLocation: 'path',
    pathInputSelector: '.app-path-input',
    pathParameterAttribute: 'data-parameter',
    pathInputMinimumSize: 4,
    inputSelector: '.app-editor-input',
    editorSelector: '.app-editor',
    playSelector: '.app-play',
    invalidClass: 'app-editor-invalid',
    exampleKey: 'example',
    completeExampleKey: 'x-complete-example',
    invokeKey: 'Enter',
    indicatorMinimumMs: 60,
    invokingSelector: '.app-invoking',
    responseSelector: '.app-operation-response',
    statusSelector: '.app-response-status',
    timeSelector: '.app-response-time',
    bodySelector: '.app-response-body',
    statusOkClass: 'app-chip app-response-status app-chip-success',
    statusErrorClass: 'app-chip app-response-status app-chip-error',
    statusOkMinimum: 200,
    statusOkMaximum: 299,
    statusUnauthorized: 401,
    networkErrorText: 'The server could not be reached',
    networkErrorStatus: 'Error',
    networkErrorStatusCode: 0,
    timeSuffix: ' ms',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.isObject = function(value) {

    if(value === null) {
        return false;
    }

    var out = typeof value === 'object' && !Array.isArray(value);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getExample = function(holder, isComplete) {

    var config = zatoApp.invoke.config;

    // The complete example, with every optional property, is there only in documents that the app's own generator builds ..
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

zatoApp.invoke.getBodyExample = function(operation, isComplete) {

    if(!('requestBody' in operation)) {
        return undefined;
    }

    var content = operation.requestBody.content[zatoApp.invoke.config.contentType];

    var out = zatoApp.invoke.getExample(content, isComplete);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.buildSample = function(entry, isComplete) {

    var config = zatoApp.invoke.config;
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

            var parameterExample = zatoApp.invoke.getExample(parameter, isComplete);

            if(parameterExample !== undefined) {
                sample[parameter.name] = parameterExample;
            }
        }
    }

    var bodyExample = zatoApp.invoke.getBodyExample(operation, isComplete);

    if(bodyExample === undefined) {
        return sample;
    }

    // .. followed by the body's own properties ..
    if(zatoApp.invoke.isObject(bodyExample)) {
        Object.assign(sample, bodyExample);
        return sample;
    }

    // .. unless the body is not an object, in which case it is the whole request.
    return bodyExample;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.setRequestText = function(card, text) {

    var input = card.querySelector(zatoApp.invoke.config.inputSelector);

    input.value = text;
    zatoApp.highlight.refreshEditor(input);
    zatoApp.invoke.markInvalid(card, false);
    zatoApp.raw.refreshRequest(card);
    zatoApp.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.markInvalid = function(card, isInvalid) {
    var editor = card.querySelector(zatoApp.invoke.config.editorSelector);
    editor.classList.toggle(zatoApp.invoke.config.invalidClass, isInvalid);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onExampleClick = function(event) {

    var card = event.currentTarget.closest(zatoApp.invoke.config.cardSelector);
    var entry = zatoApp.state.entriesById[card.id];

    // The example has every property of the request, and the path parameters return to their sample values
    var sample = zatoApp.invoke.buildSample(entry, true);
    var text = zatoApp.highlight.format(sample);

    var pathExamples = zatoApp.invoke.getPathExamples(entry.operation);
    zatoApp.invoke.setPathValues(card, pathExamples);

    zatoApp.invoke.setRequestText(card, text);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onPrettyPrintClick = function(event) {

    var card = event.currentTarget.closest(zatoApp.invoke.config.cardSelector);
    var input = card.querySelector(zatoApp.invoke.config.inputSelector);

    // Key=value lines are aligned on their separators ..
    if(zatoApp.keyValue.isKeyValue(input.value)) {
        var aligned = zatoApp.keyValue.format(input.value);

        if(aligned === null) {
            zatoApp.invoke.markInvalid(card, true);
            return;
        }

        zatoApp.invoke.setRequestText(card, aligned);
        return;
    }

    // .. and any other request is JSON, which stays as it was typed when it does not parse, with the editor showing it
    var parsed = zatoApp.invoke.parse(input.value);

    if(parsed === undefined) {
        zatoApp.invoke.markInvalid(card, true);
        return;
    }

    var text = zatoApp.highlight.format(parsed);
    zatoApp.invoke.setRequestText(card, text);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onEditorInput = function(event) {
    var card = event.target.closest(zatoApp.invoke.config.cardSelector);
    zatoApp.invoke.markInvalid(card, false);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onCardKeyDown = function(event) {

    var config = zatoApp.invoke.config;

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

zatoApp.invoke.parse = function(text) {

    try {
        var out = JSON.parse(text);
        return out;
    }
    catch(error) {
        return undefined;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.parseRequest = function(text) {

    // A request is JSON or key=value lines, the same as in the Dashboard
    var parsed = zatoApp.invoke.parse(text);

    if(parsed !== undefined) {
        return parsed;
    }

    if(!zatoApp.keyValue.isKeyValue(text)) {
        return undefined;
    }

    var pairs = zatoApp.keyValue.parse(text);

    if(pairs === null) {
        return undefined;
    }

    return pairs;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.fillPath = function(path, values) {

    var pattern = new RegExp(zatoApp.invoke.config.placeholderPattern.source, 'g');
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

zatoApp.invoke.getPathExamples = function(operation) {

    var config = zatoApp.invoke.config;

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

zatoApp.invoke.getPathValues = function(card) {

    var config = zatoApp.invoke.config;
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

zatoApp.invoke.setPathValues = function(card, values) {

    var config = zatoApp.invoke.config;
    var inputs = card.querySelectorAll(config.pathInputSelector);

    for(var inputIndex = 0; inputIndex < inputs.length; inputIndex++) {
        var input = inputs[inputIndex];
        var name = input.getAttribute(config.pathParameterAttribute);

        input.value = values[name];
        zatoApp.invoke.sizePathInput(input);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.sizePathInput = function(input) {

    // An input is as wide as its value, or as its parameter's name while it is empty
    var length = Math.max(input.value.length, input.placeholder.length);
    input.size = Math.max(length, zatoApp.invoke.config.pathInputMinimumSize);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onPathInput = function(event) {

    var input = event.target;
    var card = input.closest(zatoApp.invoke.config.cardSelector);

    zatoApp.invoke.sizePathInput(input);
    zatoApp.raw.refreshRequest(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.buildRequest = function(entry, text, pathValues) {

    var config = zatoApp.invoke.config;
    var parsed = zatoApp.invoke.parseRequest(text);

    // Our response to produce, with the path parameters from their own inputs
    var out = {path: zatoApp.invoke.fillPath(entry.path, pathValues), query: '', body: null, contentType: null};

    // An empty editor sends no body ..
    if(text.trim() === '') {
        return out;
    }

    // .. an object is sent as the JSON body it is in the editor, whatever the method ..
    if(zatoApp.invoke.isObject(parsed)) {
        out.body = JSON.stringify(parsed);
        out.contentType = config.contentType;
        return out;
    }

    // .. while anything else is the body as it was typed, whatever the method, in the content type its text has.
    out.body = text;
    out.contentType = zatoApp.invoke.getTextContentType(text, parsed);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getTextContentType = function(text, parsed) {

    var config = zatoApp.invoke.config;

    if(parsed !== undefined) {
        return config.contentType;
    }

    if(text.trim().startsWith(config.xmlMarker)) {
        return config.xmlContentType;
    }

    return config.textContentType;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getRequestHeaders = function(operation, request, headers) {

    var config = zatoApp.invoke.config;
    var callerHeaders = zatoApp.raw.getHeaderObject(headers);
    var contentTypeName = config.contentTypeHeader.toLowerCase();
    var acceptName = config.acceptHeader.toLowerCase();
    var mediaType = zatoApp.fields.getResponseMediaType(operation);

    // Our response to produce
    var out = {};

    // A body is sent in the content type of its text and a response is expected in the media type that the operation documents,
    // unless the caller names a content type or an Accept value of their own ..
    if(request.body !== null) {
        out[config.contentTypeHeader] = request.contentType;
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

zatoApp.invoke.onPlayClick = function(event) {

    var config = zatoApp.invoke.config;
    var button = event.currentTarget;
    var card = button.closest(config.cardSelector);
    var entry = zatoApp.state.entriesById[card.id];
    var exchange = zatoApp.state.exchanges[card.id];
    var input = card.querySelector(config.inputSelector);
    var invoking = card.querySelector(config.invokingSelector);

    var requestText = input.value;
    var pathValues = zatoApp.invoke.getPathValues(card);
    var request = zatoApp.invoke.buildRequest(entry, requestText, pathValues);

    // The method, the path, the query string, the caller's own headers and the body travel to the endpoint as one JSON document,
    // apart from the headers the browser adds on its own, clear of the size limits that proxies put on headers
    // and with the path exactly as typed, which a URL would have decoded ..
    var envelope = {
        method: entry.method.toUpperCase(),
        path: request.path,
        query: request.query,
        headers: zatoApp.invoke.getRequestHeaders(entry.operation, request, exchange.headers),
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

    var onResponse = zatoApp.invoke.onResponse.bind(null, pending);
    var onNetworkError = zatoApp.invoke.onNetworkError.bind(null, pending);

    fetch(zatoApp.state.relayBase, options).then(onResponse, onNetworkError);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getServerHeaders = function(response) {

    var value = response.headers.get(zatoApp.invoke.config.serverHeadersName);

    // The relay sends the endpoint's own headers only when the endpoint was invoked, and not when the app rejected the request
    if(value === null) {
        return [];
    }

    var text = decodeURIComponent(value);

    var out = JSON.parse(text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onResponse = function(pending, response) {

    var config = zatoApp.invoke.config;
    var hasServerHeaders = response.headers.has(config.serverHeadersName);

    // A session that has ended signs in again, which a 401 from the endpoint itself does not mean
    if(response.status === config.statusUnauthorized) {
        if(!hasServerHeaders) {
            zatoApp.signOut();
            return;
        }
    }

    var isOk = response.status >= config.statusOkMinimum;

    if(isOk) {
        isOk = response.status <= config.statusOkMaximum;
    }

    var headers = zatoApp.invoke.getServerHeaders(response);

    var finish = zatoApp.invoke.finish.bind(null, pending, response.status, response.statusText, isOk, headers);
    response.text().then(finish);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.onNetworkError = function(pending) {

    var config = zatoApp.invoke.config;
    zatoApp.invoke.finish(pending, config.networkErrorStatusCode, '', false, [], config.networkErrorText);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.finish = function(pending, status, statusText, isOk, headers, text) {

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
    var complete = zatoApp.invoke.complete.bind(null, pending, result);
    setTimeout(complete, zatoApp.invoke.config.indicatorMinimumMs);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.complete = function(pending, result) {

    pending.button.disabled = false;
    pending.invoking.hidden = true;

    zatoApp.invoke.showResult(pending.card, result);
    zatoApp.history.record(pending.card, pending.requestText, pending.pathValues, pending.headers, result);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getStatusText = function(result) {

    var config = zatoApp.invoke.config;

    if(result.status === config.networkErrorStatusCode) {
        return config.networkErrorStatus;
    }

    var statusText = result.status + ' ' + result.statusText;

    var out = statusText.trim();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.getDisplayText = function(text) {

    var parsed = zatoApp.invoke.parse(text);

    // A JSON body is shown formatted and anything else as it arrived
    if(parsed === undefined) {
        return text;
    }

    var out = zatoApp.highlight.format(parsed);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.invoke.showResult = function(card, result) {

    var config = zatoApp.invoke.config;

    var response = card.querySelector(config.responseSelector);
    var statusElement = card.querySelector(config.statusSelector);
    var timeElement = card.querySelector(config.timeSelector);
    var bodyElement = card.querySelector(config.bodySelector);

    zatoApp.state.exchanges[card.id].result = result;

    statusElement.textContent = zatoApp.invoke.getStatusText(result);
    statusElement.className = result.isOk ? config.statusOkClass : config.statusErrorClass;
    timeElement.textContent = result.durationMs + config.timeSuffix;

    var displayText = zatoApp.invoke.getDisplayText(result.text);

    if(zatoApp.invoke.parse(result.text) === undefined) {
        bodyElement.textContent = displayText;
    }
    else {
        zatoApp.highlight.fill(bodyElement, displayText);
    }

    response.hidden = false;
    zatoApp.raw.refreshResponse(card);
};
