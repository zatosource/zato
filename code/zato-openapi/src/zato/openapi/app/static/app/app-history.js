zatoApp.history = {};

zatoApp.history.config = {
    storageKeyPrefix: 'zato.openapi.history.',
    quotaErrorName: 'QuotaExceededError',
    maximumItems: 25,
    previewLength: 72,
    previewEllipsis: '...',
    whitespacePattern: /\s+/g,
    cardSelector: '.app-operation',
    buttonSelector: '.app-tool-history',
    inputSelector: '.app-editor-input',
    title: 'History',
    clearText: 'Clear',
    removeLabel: 'Remove',
    removeIconPaths: ['M18 6 6 18', 'm6 6 12 12'],
    historySelector: '.app-history',
    listSelector: '.app-history-list',
    timeLocale: [],
    timeOptions: {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false},
    statusOkClass: 'app-chip app-chip-success',
    statusErrorClass: 'app-chip app-chip-error',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.getStorageKey = function(entry) {
    var out = zatoApp.history.config.storageKeyPrefix + entry.method + ' ' + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.load = function(entry) {

    var key = zatoApp.history.getStorageKey(entry);
    var stored = sessionStorage.getItem(key);

    // sessionStorage returns null for an operation never invoked in this browser session
    if(stored === null) {
        return [];
    }

    var out = JSON.parse(stored);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.record = function(card, requestText, pathValues, headers, result) {

    var config = zatoApp.history.config;
    var entry = zatoApp.state.entriesById[card.id];
    var items = zatoApp.history.load(entry);

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

    zatoApp.history.save(card, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.save = function(card, items) {

    var entry = zatoApp.state.entriesById[card.id];
    var key = zatoApp.history.getStorageKey(entry);

    // The oldest invocations go when the browser's storage has no room for all of them ..
    while(items.length > 0 && !zatoApp.history.store(key, items)) {
        items.pop();
    }

    // .. and an operation with no invocations left has no history kept for it at all.
    if(items.length === 0) {
        sessionStorage.removeItem(key);
    }

    zatoApp.history.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.store = function(key, items) {

    try {
        sessionStorage.setItem(key, JSON.stringify(items));
    }
    catch(error) {
        if(error.name !== zatoApp.history.config.quotaErrorName) {
            throw error;
        }
        return false;
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.refresh = function(card) {

    var entry = zatoApp.state.entriesById[card.id];
    var items = zatoApp.history.load(entry);
    var button = card.querySelector(zatoApp.history.config.buttonSelector);

    button.disabled = items.length === 0;
    zatoApp.panels.setCount(button, items.length);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.clear = function() {

    var prefix = zatoApp.history.config.storageKeyPrefix;
    var keys = Object.keys(sessionStorage);

    for(var keyIndex = 0; keyIndex < keys.length; keyIndex++) {
        var key = keys[keyIndex];

        if(key.startsWith(prefix)) {
            sessionStorage.removeItem(key);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoApp.history.config.cardSelector);

    var content = zatoApp.history.buildContent(card);
    zatoApp.popover.open(button, content, null);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.getPreview = function(text) {

    var config = zatoApp.history.config;
    var compact = text.replace(config.whitespacePattern, ' ').trim();

    if(compact.length <= config.previewLength) {
        return compact;
    }

    var out = compact.slice(0, config.previewLength) + config.previewEllipsis;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.buildContent = function(card) {

    var config = zatoApp.history.config;
    var entry = zatoApp.state.entriesById[card.id];
    var items = zatoApp.history.load(entry);

    var container = zatoApp.panels.createElement('div', 'app-history');

    // The title shares its line with the button that clears the whole history of the operation
    var heading = zatoApp.panels.createElement('div', 'app-history-heading');
    var title = zatoApp.panels.createElement('div', 'app-popover-title app-history-title', config.title);
    var clear = zatoApp.panels.buildToolButton(config.clearText, 'app-history-clear', zatoApp.history.onClearClick.bind(null, card));

    heading.appendChild(title);
    heading.appendChild(clear);

    var list = zatoApp.panels.createElement('div', 'app-history-list');
    zatoApp.history.fillList(card, list, items);

    container.appendChild(heading);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.fillList = function(card, list, items) {

    list.textContent = '';

    for(var itemIndex = 0; itemIndex < items.length; itemIndex++) {
        var row = zatoApp.history.buildRow(card, items[itemIndex], itemIndex);
        list.appendChild(row);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.onClearClick = function(card) {
    zatoApp.popover.close();
    zatoApp.history.save(card, []);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.onRemoveClick = function(card, itemIndex, event) {

    var config = zatoApp.history.config;
    var entry = zatoApp.state.entriesById[card.id];
    var items = zatoApp.history.load(entry);
    var list = event.currentTarget.closest(config.historySelector).querySelector(config.listSelector);

    items.splice(itemIndex, 1);
    zatoApp.history.save(card, items);

    // The popover closes with its last item, and otherwise the rows after the removed one move up an index,
    // so all of them are built anew
    if(items.length === 0) {
        zatoApp.popover.close();
        return;
    }

    zatoApp.history.fillList(card, list, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.buildRemoveButton = function(card, itemIndex) {

    var config = zatoApp.history.config;

    var button = zatoApp.panels.createElement('button', 'app-history-remove');
    button.type = 'button';
    button.setAttribute('aria-label', config.removeLabel);
    button.addEventListener('click', zatoApp.history.onRemoveClick.bind(null, card, itemIndex));

    var viewBox = zatoApp.panels.config.iconViewBox;
    var icon = zatoApp.panels.createSvgElement('svg', {'class': 'app-history-remove-icon', 'viewBox': viewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoApp.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.buildRow = function(card, item, itemIndex) {

    var config = zatoApp.history.config;
    var result = item.result;

    // Each row is the invocation, which brings it back when clicked, and the button that removes it
    var container = zatoApp.panels.createElement('div', 'app-history-row');

    var row = zatoApp.panels.createElement('button', 'app-history-item');
    row.type = 'button';
    row.addEventListener('click', zatoApp.history.onItemClick.bind(null, card, item));

    var date = new Date(item.time);
    var timeText = date.toLocaleTimeString(config.timeLocale, config.timeOptions);
    var statusClass = result.isOk ? config.statusOkClass : config.statusErrorClass;
    var durationText = result.durationMs + zatoApp.invoke.config.timeSuffix;

    var time = zatoApp.panels.createElement('span', 'app-history-time', timeText);
    var status = zatoApp.panels.createElement('span', statusClass, zatoApp.invoke.getStatusText(result));
    var duration = zatoApp.panels.createElement('span', 'app-history-duration', durationText);
    var preview = zatoApp.panels.createElement('span', 'app-history-preview', zatoApp.history.getPreview(item.requestText));

    row.appendChild(time);
    row.appendChild(status);
    row.appendChild(duration);
    row.appendChild(preview);

    var remove = zatoApp.history.buildRemoveButton(card, itemIndex);

    container.appendChild(row);
    container.appendChild(remove);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.history.onItemClick = function(card, item) {

    var input = card.querySelector(zatoApp.history.config.inputSelector);
    var exchange = zatoApp.state.exchanges[card.id];

    // The request, its headers and its response all return to the card, ready to be sent again or copied
    input.value = item.requestText;
    zatoApp.highlight.refreshEditor(input);
    zatoApp.invoke.setPathValues(card, item.pathValues);

    exchange.headers = item.headers;

    zatoApp.popover.close();
    zatoApp.options.refresh(card);
    zatoApp.invoke.showResult(card, item.result);
};
