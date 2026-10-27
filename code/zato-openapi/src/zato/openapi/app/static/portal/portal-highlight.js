var zatoPortal = {};

zatoPortal.state = {
    relayBase: '',
    components: {},
    groups: [],
    entriesById: {},
    exchanges: {},
    selectedGroup: '',
};

zatoPortal.highlight = {};

zatoPortal.highlight.config = {
    indent: 2,

    // Strings, with the colon that makes a string a key, then literals, numbers and punctuation
    tokenPattern: /("(?:\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*")(\s*:)?|\b(true|false)\b|\b(null)\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],])/g,

    keyClass: 'portal-code-key',
    stringClass: 'portal-code-string',
    booleanClass: 'portal-code-boolean',
    nullClass: 'portal-code-null',
    numberClass: 'portal-code-number',
    punctuationClass: 'portal-code-punctuation',

    editorClass: 'portal-editor',
    editorHighlightClass: 'portal-code portal-editor-highlight',
    editorInputClass: 'portal-editor-input',

    // A trailing newline in a textarea opens a line that a pre element only shows when another follows
    editorTrailer: '\n',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.format = function(value) {
    var out = JSON.stringify(value, null, zatoPortal.highlight.config.indent);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.appendToken = function(fragment, text, className) {

    var span = document.createElement('span');
    span.className = className;
    span.textContent = text;

    fragment.appendChild(span);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.classify = function(match) {

    var config = zatoPortal.highlight.config;

    if(match[3] !== undefined) {
        return config.booleanClass;
    }

    if(match[4] !== undefined) {
        return config.nullClass;
    }

    if(match[5] !== undefined) {
        return config.numberClass;
    }

    return config.punctuationClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.fill = function(element, text) {

    var config = zatoPortal.highlight.config;
    var pattern = new RegExp(config.tokenPattern.source, 'g');
    var fragment = document.createDocumentFragment();
    var position = 0;
    var match = pattern.exec(text);

    while(match !== null) {

        // Whatever lies between two tokens is kept as it is ..
        if(match.index > position) {
            var between = text.slice(position, match.index);
            var betweenNode = document.createTextNode(between);
            fragment.appendChild(betweenNode);
        }

        // .. a string followed by a colon is a key, and the colon itself is punctuation ..
        if(match[1] !== undefined) {
            if(match[2] !== undefined) {
                zatoPortal.highlight.appendToken(fragment, match[1], config.keyClass);
                zatoPortal.highlight.appendToken(fragment, match[2], config.punctuationClass);
            }
            else {
                zatoPortal.highlight.appendToken(fragment, match[1], config.stringClass);
            }
        }

        // .. and every other token is classified by the group it matched.
        else {
            var className = zatoPortal.highlight.classify(match);
            zatoPortal.highlight.appendToken(fragment, match[0], className);
        }

        position = pattern.lastIndex;
        match = pattern.exec(text);
    }

    var rest = text.slice(position);
    var restNode = document.createTextNode(rest);
    fragment.appendChild(restNode);

    element.textContent = '';
    element.appendChild(fragment);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.createEditor = function(text) {

    var config = zatoPortal.highlight.config;

    var container = document.createElement('div');
    container.className = config.editorClass;

    // The highlighted copy sizes the editor and the transparent textarea above it takes the typing ..
    var highlighted = document.createElement('pre');
    highlighted.className = config.editorHighlightClass;
    highlighted.setAttribute('aria-hidden', 'true');

    var input = document.createElement('textarea');
    input.className = config.editorInputClass;
    input.spellcheck = false;
    input.value = text;
    input.addEventListener('input', zatoPortal.highlight.onEditorInput);

    container.appendChild(highlighted);
    container.appendChild(input);

    // .. and both start with the same text.
    zatoPortal.highlight.refreshEditor(input);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.onEditorInput = function(event) {
    zatoPortal.highlight.refreshEditor(event.target);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.highlight.refreshEditor = function(input) {

    var highlighted = input.previousSibling;
    var text = input.value + zatoPortal.highlight.config.editorTrailer;

    if(zatoPortal.keyValue.isKeyValue(input.value)) {
        zatoPortal.keyValue.fill(highlighted, text);
        return;
    }

    zatoPortal.highlight.fill(highlighted, text);
};
