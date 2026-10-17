var zatoConsole = {};

zatoConsole.state = {
    relayBase: '',
    components: {},
    groups: [],
    entriesById: {},
    exchanges: {},
    selectedGroup: '',
};

zatoConsole.highlight = {};

zatoConsole.highlight.config = {
    indent: 2,

    // Strings, with the colon that makes a string a key, then literals, numbers and punctuation
    tokenPattern: /("(?:\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*")(\s*:)?|\b(true|false)\b|\b(null)\b|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],])/g,

    keyClass: 'console-code-key',
    stringClass: 'console-code-string',
    booleanClass: 'console-code-boolean',
    nullClass: 'console-code-null',
    numberClass: 'console-code-number',
    punctuationClass: 'console-code-punctuation',

    editorClass: 'console-editor',
    editorHighlightClass: 'console-code console-editor-highlight',
    editorInputClass: 'console-editor-input',

    // A trailing newline in a textarea opens a line that a pre element only shows when another follows
    editorTrailer: '\n',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.highlight.format = function(value) {
    var out = JSON.stringify(value, null, zatoConsole.highlight.config.indent);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.highlight.appendToken = function(fragment, text, className) {

    var span = document.createElement('span');
    span.className = className;
    span.textContent = text;

    fragment.appendChild(span);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.highlight.classify = function(match) {

    var config = zatoConsole.highlight.config;

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

zatoConsole.highlight.fill = function(element, text) {

    var config = zatoConsole.highlight.config;
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
                zatoConsole.highlight.appendToken(fragment, match[1], config.keyClass);
                zatoConsole.highlight.appendToken(fragment, match[2], config.punctuationClass);
            }
            else {
                zatoConsole.highlight.appendToken(fragment, match[1], config.stringClass);
            }
        }

        // .. and every other token is classified by the group it matched.
        else {
            var className = zatoConsole.highlight.classify(match);
            zatoConsole.highlight.appendToken(fragment, match[0], className);
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

zatoConsole.highlight.createEditor = function(text) {

    var config = zatoConsole.highlight.config;

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
    input.addEventListener('input', zatoConsole.highlight.onEditorInput);

    container.appendChild(highlighted);
    container.appendChild(input);

    // .. and both start with the same text.
    zatoConsole.highlight.refreshEditor(input);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.highlight.onEditorInput = function(event) {
    zatoConsole.highlight.refreshEditor(event.target);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.highlight.refreshEditor = function(input) {

    var highlighted = input.previousSibling;
    var text = input.value + zatoConsole.highlight.config.editorTrailer;

    if(zatoConsole.keyValue.isKeyValue(input.value)) {
        zatoConsole.keyValue.fill(highlighted, text);
        return;
    }

    zatoConsole.highlight.fill(highlighted, text);
};
