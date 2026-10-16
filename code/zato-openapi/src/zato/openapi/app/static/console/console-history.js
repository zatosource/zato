zatoConsole.history = {};

zatoConsole.history.config = {
    storageKeyPrefix: 'zato.openapi.console.history.',
    maximumItems: 25,
    previewLength: 72,
    previewEllipsis: '...',
    whitespacePattern: /\s+/g,
    cardSelector: '.console-operation',
    buttonSelector: '.console-tool-history',
    inputSelector: '.console-editor-input',
    title: 'History',
    clearText: 'Clear',
    removeLabel: 'Remove',
    removeIconPaths: ['M18 6 6 18', 'm6 6 12 12'],
    historySelector: '.console-history',
    listSelector: '.console-history-list',
    timeLocale: [],
    timeOptions: {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false},
    statusOkClass: 'console-chip console-chip-success',
    statusErrorClass: 'console-chip console-chip-error',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.getStorageKey = function(entry) {
    var out = zatoConsole.history.config.storageKeyPrefix + entry.method + ' ' + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.load = function(entry) {

    var key = zatoConsole.history.getStorageKey(entry);
    var stored = sessionStorage.getItem(key);

    // sessionStorage returns null for an operation never invoked in this browser session
    if(stored === null) {
        return [];
    }

    var out = JSON.parse(stored);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.record = function(card, requestText, pathValues, headers, result) {

    var config = zatoConsole.history.config;
    var entry = zatoConsole.state.entriesById[card.id];
    var items = zatoConsole.history.load(entry);

    var item = {
        time: new Date().toISOString(),
        requestText: requestText,
        pathValues: pathValues,
        headers: headers,
        result: result,
    };

    // The latest invocation comes first and the oldest ones go once the history is full
    items.unshift(item);
    items = items.slice(0, config.maximumItems);

    zatoConsole.history.save(card, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.save = function(card, items) {

    var entry = zatoConsole.state.entriesById[card.id];
    var key = zatoConsole.history.getStorageKey(entry);

    // An operation with no invocations left has no history kept for it at all
    if(items.length === 0) {
        sessionStorage.removeItem(key);
    }
    else {
        sessionStorage.setItem(key, JSON.stringify(items));
    }

    zatoConsole.history.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.refresh = function(card) {

    var entry = zatoConsole.state.entriesById[card.id];
    var items = zatoConsole.history.load(entry);
    var button = card.querySelector(zatoConsole.history.config.buttonSelector);

    button.disabled = items.length === 0;
    zatoConsole.panels.setCount(button, items.length);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.clear = function() {

    var prefix = zatoConsole.history.config.storageKeyPrefix;
    var keys = Object.keys(sessionStorage);

    for(var keyIndex = 0; keyIndex < keys.length; keyIndex++) {
        var key = keys[keyIndex];

        if(key.startsWith(prefix)) {
            sessionStorage.removeItem(key);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoConsole.history.config.cardSelector);

    var content = zatoConsole.history.buildContent(card);
    zatoConsole.popover.open(button, content, null);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.getPreview = function(text) {

    var config = zatoConsole.history.config;
    var compact = text.replace(config.whitespacePattern, ' ').trim();

    if(compact.length <= config.previewLength) {
        return compact;
    }

    var out = compact.slice(0, config.previewLength) + config.previewEllipsis;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.buildContent = function(card) {

    var config = zatoConsole.history.config;
    var entry = zatoConsole.state.entriesById[card.id];
    var items = zatoConsole.history.load(entry);

    var container = zatoConsole.panels.createElement('div', 'console-history');

    // The title shares its line with the button that clears the whole history of the operation
    var heading = zatoConsole.panels.createElement('div', 'console-history-heading');
    var title = zatoConsole.panels.createElement('div', 'console-popover-title console-history-title', config.title);
    var clear = zatoConsole.panels.buildToolButton(config.clearText, 'console-history-clear', zatoConsole.history.onClearClick.bind(null, card));

    heading.appendChild(title);
    heading.appendChild(clear);

    var list = zatoConsole.panels.createElement('div', 'console-history-list');
    zatoConsole.history.fillList(card, list, items);

    container.appendChild(heading);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.fillList = function(card, list, items) {

    list.textContent = '';

    for(var itemIndex = 0; itemIndex < items.length; itemIndex++) {
        var row = zatoConsole.history.buildRow(card, items[itemIndex], itemIndex);
        list.appendChild(row);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.onClearClick = function(card) {
    zatoConsole.popover.close();
    zatoConsole.history.save(card, []);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.onRemoveClick = function(card, itemIndex, event) {

    var config = zatoConsole.history.config;
    var entry = zatoConsole.state.entriesById[card.id];
    var items = zatoConsole.history.load(entry);
    var list = event.currentTarget.closest(config.historySelector).querySelector(config.listSelector);

    items.splice(itemIndex, 1);
    zatoConsole.history.save(card, items);

    // The popover closes with its last item, and otherwise the rows after the removed one move up an index,
    // so all of them are built anew
    if(items.length === 0) {
        zatoConsole.popover.close();
        return;
    }

    zatoConsole.history.fillList(card, list, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.buildRemoveButton = function(card, itemIndex) {

    var config = zatoConsole.history.config;

    var button = zatoConsole.panels.createElement('button', 'console-history-remove');
    button.type = 'button';
    button.setAttribute('aria-label', config.removeLabel);
    button.addEventListener('click', zatoConsole.history.onRemoveClick.bind(null, card, itemIndex));

    var viewBox = zatoConsole.panels.config.iconViewBox;
    var icon = zatoConsole.panels.createSvgElement('svg', {'class': 'console-history-remove-icon', 'viewBox': viewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoConsole.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.buildRow = function(card, item, itemIndex) {

    var config = zatoConsole.history.config;
    var result = item.result;

    // Each row is the invocation, which brings it back when clicked, and the button that removes it
    var container = zatoConsole.panels.createElement('div', 'console-history-row');

    var row = zatoConsole.panels.createElement('button', 'console-history-item');
    row.type = 'button';
    row.addEventListener('click', zatoConsole.history.onItemClick.bind(null, card, item));

    var date = new Date(item.time);
    var timeText = date.toLocaleTimeString(config.timeLocale, config.timeOptions);
    var statusClass = result.isOk ? config.statusOkClass : config.statusErrorClass;
    var durationText = result.durationMs + zatoConsole.invoke.config.timeSuffix;

    var time = zatoConsole.panels.createElement('span', 'console-history-time', timeText);
    var status = zatoConsole.panels.createElement('span', statusClass, zatoConsole.invoke.getStatusText(result));
    var duration = zatoConsole.panels.createElement('span', 'console-history-duration', durationText);
    var preview = zatoConsole.panels.createElement('span', 'console-history-preview', zatoConsole.history.getPreview(item.requestText));

    row.appendChild(time);
    row.appendChild(status);
    row.appendChild(duration);
    row.appendChild(preview);

    var remove = zatoConsole.history.buildRemoveButton(card, itemIndex);

    container.appendChild(row);
    container.appendChild(remove);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.history.onItemClick = function(card, item) {

    var input = card.querySelector(zatoConsole.history.config.inputSelector);
    var exchange = zatoConsole.state.exchanges[card.id];

    // The request, its headers and its response all return to the card, ready to be sent again or copied
    input.value = item.requestText;
    zatoConsole.highlight.refreshEditor(input);
    zatoConsole.invoke.setPathValues(card, item.pathValues);

    exchange.headers = item.headers;

    zatoConsole.popover.close();
    zatoConsole.options.refresh(card);
    zatoConsole.invoke.showResult(card, item.result);
};
