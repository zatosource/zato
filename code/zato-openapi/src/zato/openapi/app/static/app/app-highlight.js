var zatoApp = {};

zatoApp.state = {
    relayBase: '',
    components: {},
    groups: [],
    entriesById: {},
    exchanges: {},
    selectedGroup: '',
};

zatoApp.highlight = {};

zatoApp.highlight.config = {
    indent: 2,

    // Strings, with the colon that makes a string a key, then literals, numbers and punctuation
    tokenPattern: /("(?:\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*")(\s*:)?|\b(true|false)\b|\b(null)\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],])/g,

    keyClass: 'app-code-key',
    stringClass: 'app-code-string',
    booleanClass: 'app-code-boolean',
    nullClass: 'app-code-null',
    numberClass: 'app-code-number',
    punctuationClass: 'app-code-punctuation',

    editorClass: 'app-editor',
    editorHighlightClass: 'app-code app-editor-highlight',
    editorInputClass: 'app-editor-input',

    // A trailing newline in a textarea opens a line that a pre element only shows when another follows
    editorTrailer: '\n',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.highlight.format = function(value) {
    var out = JSON.stringify(value, null, zatoApp.highlight.config.indent);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.highlight.appendToken = function(fragment, text, className) {

    var span = document.createElement('span');
    span.className = className;
    span.textContent = text;

    fragment.appendChild(span);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.highlight.classify = function(match) {

    var config = zatoApp.highlight.config;

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

zatoApp.highlight.fill = function(element, text) {

    var config = zatoApp.highlight.config;
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
                zatoApp.highlight.appendToken(fragment, match[1], config.keyClass);
                zatoApp.highlight.appendToken(fragment, match[2], config.punctuationClass);
            }
            else {
                zatoApp.highlight.appendToken(fragment, match[1], config.stringClass);
            }
        }

        // .. and every other token is classified by the group it matched.
        else {
            var className = zatoApp.highlight.classify(match);
            zatoApp.highlight.appendToken(fragment, match[0], className);
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

zatoApp.highlight.createEditor = function(text) {

    var config = zatoApp.highlight.config;

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
    input.addEventListener('input', zatoApp.highlight.onEditorInput);

    container.appendChild(highlighted);
    container.appendChild(input);

    // .. and both start with the same text.
    zatoApp.highlight.refreshEditor(input);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.highlight.onEditorInput = function(event) {
    zatoApp.highlight.refreshEditor(event.target);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.highlight.refreshEditor = function(input) {

    var highlighted = input.previousSibling;
    var text = input.value + zatoApp.highlight.config.editorTrailer;

    if(zatoApp.keyValue.isKeyValue(input.value)) {
        zatoApp.keyValue.fill(highlighted, text);
        return;
    }

    zatoApp.highlight.fill(highlighted, text);
};
