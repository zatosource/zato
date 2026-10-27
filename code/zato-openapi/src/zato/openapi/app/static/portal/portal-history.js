zatoPortal.history = {};

zatoPortal.history.config = {
    storageKeyPrefix: 'zato.openapi.portal.history.',
    quotaErrorName: 'QuotaExceededError',
    maximumItems: 25,
    previewLength: 72,
    previewEllipsis: '...',
    whitespacePattern: /\s+/g,
    cardSelector: '.portal-operation',
    buttonSelector: '.portal-tool-history',
    inputSelector: '.portal-editor-input',
    title: 'History',
    clearText: 'Clear',
    removeLabel: 'Remove',
    removeIconPaths: ['M18 6 6 18', 'm6 6 12 12'],
    historySelector: '.portal-history',
    listSelector: '.portal-history-list',
    timeLocale: [],
    timeOptions: {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false},
    statusOkClass: 'portal-chip portal-chip-success',
    statusErrorClass: 'portal-chip portal-chip-error',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.getStorageKey = function(entry) {
    var out = zatoPortal.history.config.storageKeyPrefix + entry.method + ' ' + entry.path;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.load = function(entry) {

    var key = zatoPortal.history.getStorageKey(entry);
    var stored = sessionStorage.getItem(key);

    // sessionStorage returns null for an operation never invoked in this browser session
    if(stored === null) {
        return [];
    }

    var out = JSON.parse(stored);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.record = function(card, requestText, pathValues, headers, result) {

    var config = zatoPortal.history.config;
    var entry = zatoPortal.state.entriesById[card.id];
    var items = zatoPortal.history.load(entry);

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

    zatoPortal.history.save(card, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.save = function(card, items) {

    var entry = zatoPortal.state.entriesById[card.id];
    var key = zatoPortal.history.getStorageKey(entry);

    // The oldest invocations go when the browser's storage has no room for all of them ..
    while(items.length > 0 && !zatoPortal.history.store(key, items)) {
        items.pop();
    }

    // .. and an operation with no invocations left has no history kept for it at all.
    if(items.length === 0) {
        sessionStorage.removeItem(key);
    }

    zatoPortal.history.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.store = function(key, items) {

    try {
        sessionStorage.setItem(key, JSON.stringify(items));
    }
    catch(error) {
        if(error.name !== zatoPortal.history.config.quotaErrorName) {
            throw error;
        }
        return false;
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.refresh = function(card) {

    var entry = zatoPortal.state.entriesById[card.id];
    var items = zatoPortal.history.load(entry);
    var button = card.querySelector(zatoPortal.history.config.buttonSelector);

    button.disabled = items.length === 0;
    zatoPortal.panels.setCount(button, items.length);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.clear = function() {

    var prefix = zatoPortal.history.config.storageKeyPrefix;
    var keys = Object.keys(sessionStorage);

    for(var keyIndex = 0; keyIndex < keys.length; keyIndex++) {
        var key = keys[keyIndex];

        if(key.startsWith(prefix)) {
            sessionStorage.removeItem(key);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoPortal.history.config.cardSelector);

    var content = zatoPortal.history.buildContent(card);
    zatoPortal.popover.open(button, content, null);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.getPreview = function(text) {

    var config = zatoPortal.history.config;
    var compact = text.replace(config.whitespacePattern, ' ').trim();

    if(compact.length <= config.previewLength) {
        return compact;
    }

    var out = compact.slice(0, config.previewLength) + config.previewEllipsis;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.buildContent = function(card) {

    var config = zatoPortal.history.config;
    var entry = zatoPortal.state.entriesById[card.id];
    var items = zatoPortal.history.load(entry);

    var container = zatoPortal.panels.createElement('div', 'portal-history');

    // The title shares its line with the button that clears the whole history of the operation
    var heading = zatoPortal.panels.createElement('div', 'portal-history-heading');
    var title = zatoPortal.panels.createElement('div', 'portal-popover-title portal-history-title', config.title);
    var clear = zatoPortal.panels.buildToolButton(config.clearText, 'portal-history-clear', zatoPortal.history.onClearClick.bind(null, card));

    heading.appendChild(title);
    heading.appendChild(clear);

    var list = zatoPortal.panels.createElement('div', 'portal-history-list');
    zatoPortal.history.fillList(card, list, items);

    container.appendChild(heading);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.fillList = function(card, list, items) {

    list.textContent = '';

    for(var itemIndex = 0; itemIndex < items.length; itemIndex++) {
        var row = zatoPortal.history.buildRow(card, items[itemIndex], itemIndex);
        list.appendChild(row);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.onClearClick = function(card) {
    zatoPortal.popover.close();
    zatoPortal.history.save(card, []);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.onRemoveClick = function(card, itemIndex, event) {

    var config = zatoPortal.history.config;
    var entry = zatoPortal.state.entriesById[card.id];
    var items = zatoPortal.history.load(entry);
    var list = event.currentTarget.closest(config.historySelector).querySelector(config.listSelector);

    items.splice(itemIndex, 1);
    zatoPortal.history.save(card, items);

    // The popover closes with its last item, and otherwise the rows after the removed one move up an index,
    // so all of them are built anew
    if(items.length === 0) {
        zatoPortal.popover.close();
        return;
    }

    zatoPortal.history.fillList(card, list, items);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.buildRemoveButton = function(card, itemIndex) {

    var config = zatoPortal.history.config;

    var button = zatoPortal.panels.createElement('button', 'portal-history-remove');
    button.type = 'button';
    button.setAttribute('aria-label', config.removeLabel);
    button.addEventListener('click', zatoPortal.history.onRemoveClick.bind(null, card, itemIndex));

    var viewBox = zatoPortal.panels.config.iconViewBox;
    var icon = zatoPortal.panels.createSvgElement('svg', {'class': 'portal-history-remove-icon', 'viewBox': viewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoPortal.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.buildRow = function(card, item, itemIndex) {

    var config = zatoPortal.history.config;
    var result = item.result;

    // Each row is the invocation, which brings it back when clicked, and the button that removes it
    var container = zatoPortal.panels.createElement('div', 'portal-history-row');

    var row = zatoPortal.panels.createElement('button', 'portal-history-item');
    row.type = 'button';
    row.addEventListener('click', zatoPortal.history.onItemClick.bind(null, card, item));

    var date = new Date(item.time);
    var timeText = date.toLocaleTimeString(config.timeLocale, config.timeOptions);
    var statusClass = result.isOk ? config.statusOkClass : config.statusErrorClass;
    var durationText = result.durationMs + zatoPortal.invoke.config.timeSuffix;

    var time = zatoPortal.panels.createElement('span', 'portal-history-time', timeText);
    var status = zatoPortal.panels.createElement('span', statusClass, zatoPortal.invoke.getStatusText(result));
    var duration = zatoPortal.panels.createElement('span', 'portal-history-duration', durationText);
    var preview = zatoPortal.panels.createElement('span', 'portal-history-preview', zatoPortal.history.getPreview(item.requestText));

    row.appendChild(time);
    row.appendChild(status);
    row.appendChild(duration);
    row.appendChild(preview);

    var remove = zatoPortal.history.buildRemoveButton(card, itemIndex);

    container.appendChild(row);
    container.appendChild(remove);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.history.onItemClick = function(card, item) {

    var input = card.querySelector(zatoPortal.history.config.inputSelector);
    var exchange = zatoPortal.state.exchanges[card.id];

    // The request, its headers and its response all return to the card, ready to be sent again or copied
    input.value = item.requestText;
    zatoPortal.highlight.refreshEditor(input);
    zatoPortal.invoke.setPathValues(card, item.pathValues);

    exchange.headers = item.headers;

    zatoPortal.popover.close();
    zatoPortal.options.refresh(card);
    zatoPortal.invoke.showResult(card, item.result);
};
