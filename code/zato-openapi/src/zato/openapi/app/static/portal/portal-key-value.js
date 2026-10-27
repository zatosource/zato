zatoPortal.keyValue = {};

zatoPortal.keyValue.config = {
    objectMarker: '{',
    separator: '=',
    commentMarker: '#',
    pairPattern: /^([A-Za-z_][\w.-]*)\s*=(?!=)\s*(\S.*)$/,
    linePattern: /\r?\n|;/,
    segmentPattern: /(\r?\n|;)/,
    numberPattern: /^-?\d+(?:\.\d+)?$/,
    quotedPattern: /^(?:'[^']*'|"[^"]*")$/,
    listMarker: '[',
    lineSeparator: '\n',
    alignedSeparator: ' = ',
    literals: {
        'True': true,
        'False': false,
        'None': null,
    },
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.isKeyValue = function(text) {

    var config = zatoPortal.keyValue.config;
    var trimmed = text.trim();

    // The text is a list of key=value lines when it is not an object and its first line assigns a value to a name,
    // which XML attributes and the padding of base64 do not
    if(trimmed === '') {
        return false;
    }

    if(trimmed.includes(config.objectMarker)) {
        return false;
    }

    var firstLine = trimmed.split(config.linePattern)[0];

    var out = config.pairPattern.test(firstLine.trim());
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.split = function(text) {

    var config = zatoPortal.keyValue.config;
    var lines = text.split(config.linePattern);
    var pairs = [];

    for(var lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        var line = lines[lineIndex].trim();

        // Empty lines and comments carry no value ..
        if(line === '') {
            continue;
        }

        if(line.startsWith(config.commentMarker)) {
            continue;
        }

        // .. and a line that does not assign a value to a name makes the whole text something other than key=value lines.
        var match = config.pairPattern.exec(line);

        if(match === null) {
            return null;
        }

        var key = match[1];
        var value = match[2].trim();

        pairs.push({key: key, value: value});
    }

    return pairs;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.parse = function(text) {

    var pairs = zatoPortal.keyValue.split(text);

    if(pairs === null) {
        return null;
    }

    var out = {};

    for(var pairIndex = 0; pairIndex < pairs.length; pairIndex++) {
        var pair = pairs[pairIndex];
        out[pair.key] = zatoPortal.keyValue.convert(pair.value);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.convert = function(value) {

    var config = zatoPortal.keyValue.config;

    // Values are read as the Dashboard reads them, numbers and literals first, everything else as a string
    if(config.numberPattern.test(value)) {
        var number = Number(value);
        return number;
    }

    if(value in config.literals) {
        return config.literals[value];
    }

    if(config.quotedPattern.test(value)) {
        var unquoted = value.slice(1, -1);
        return unquoted;
    }

    if(value.startsWith(config.listMarker)) {
        var list = zatoPortal.invoke.parse(value);

        if(list !== undefined) {
            return list;
        }
    }

    return value;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.format = function(text) {

    var config = zatoPortal.keyValue.config;
    var pairs = zatoPortal.keyValue.split(text);

    if(pairs === null) {
        return null;
    }

    var width = 0;

    for(var widthIndex = 0; widthIndex < pairs.length; widthIndex++) {
        width = Math.max(width, pairs[widthIndex].key.length);
    }

    // Every value starts in the same column
    var lines = [];

    for(var pairIndex = 0; pairIndex < pairs.length; pairIndex++) {
        var pair = pairs[pairIndex];
        var key = pair.key.padEnd(width);

        lines.push(key + config.alignedSeparator + pair.value);
    }

    var out = lines.join(config.lineSeparator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.classify = function(value) {

    var config = zatoPortal.keyValue.config;
    var classes = zatoPortal.highlight.config;
    var trimmed = value.trim();

    if(config.numberPattern.test(trimmed)) {
        return classes.numberClass;
    }

    if(trimmed in config.literals) {
        var literal = config.literals[trimmed];

        if(literal === null) {
            return classes.nullClass;
        }

        return classes.booleanClass;
    }

    return classes.stringClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.keyValue.fill = function(element, text) {

    var config = zatoPortal.keyValue.config;
    var classes = zatoPortal.highlight.config;
    var highlight = zatoPortal.highlight;

    // The separators are kept, so the highlighted copy has exactly the characters of the text
    var segments = text.split(config.segmentPattern);
    var fragment = document.createDocumentFragment();

    for(var segmentIndex = 0; segmentIndex < segments.length; segmentIndex++) {
        var segment = segments[segmentIndex];
        var separatorIndex = segment.indexOf(config.separator);

        // Odd segments are the separators between lines ..
        if(segmentIndex % 2 === 1) {
            highlight.appendToken(fragment, segment, classes.punctuationClass);
            continue;
        }

        // .. a comment is shown as a whole ..
        if(segment.trim().startsWith(config.commentMarker)) {
            highlight.appendToken(fragment, segment, classes.nullClass);
            continue;
        }

        // .. a line still being typed is shown as it is ..
        if(separatorIndex === -1) {
            var textNode = document.createTextNode(segment);
            fragment.appendChild(textNode);
            continue;
        }

        // .. and a complete line is its key, the separator and its value.
        var key = segment.slice(0, separatorIndex);
        var value = segment.slice(separatorIndex + 1);
        var valueClass = zatoPortal.keyValue.classify(value);

        highlight.appendToken(fragment, key, classes.keyClass);
        highlight.appendToken(fragment, config.separator, classes.punctuationClass);
        highlight.appendToken(fragment, value, valueClass);
    }

    element.textContent = '';
    element.appendChild(fragment);
};
