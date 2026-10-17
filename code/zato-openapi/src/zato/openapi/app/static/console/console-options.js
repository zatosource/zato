zatoConsole.options = {};

zatoConsole.options.config = {
    cardSelector: '.console-operation',
    buttonSelector: '.console-tool-options',
    headersTitle: 'Headers',
    namePlaceholder: 'Name',
    valuePlaceholder: 'Value',
    addText: 'Add header',
    removeLabel: 'Remove',
    rowAttribute: 'data-row',
    svgNamespace: 'http://www.w3.org/2000/svg',
    iconViewBox: '0 0 24 24',
    removeIconPaths: ['M18 6 6 18', 'm6 6 12 12'],
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoConsole.options.config.cardSelector);
    var headers = zatoConsole.state.exchanges[card.id].headers;

    // With no headers yet, the popover opens with an empty row ready for the first one ..
    var isFirst = headers.length === 0;

    if(isFirst) {
        headers.push({name: '', value: ''});
    }

    var content = zatoConsole.options.buildContent(card);
    var onClose = zatoConsole.options.onClose.bind(null, card);

    zatoConsole.popover.open(button, content, onClose);

    // .. and its name is typed in at once, unless the click closed the popover instead.
    if(isFirst && content.isConnected) {
        content.querySelector('.console-options-input').focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.buildContent = function(card) {

    var config = zatoConsole.options.config;
    var exchange = zatoConsole.state.exchanges[card.id];

    var container = zatoConsole.panels.createElement('div', 'console-options');
    var title = zatoConsole.panels.createElement('div', 'console-popover-title', config.headersTitle);
    var rows = zatoConsole.panels.createElement('div', 'console-options-rows');

    for(var headerIndex = 0; headerIndex < exchange.headers.length; headerIndex++) {
        var row = zatoConsole.options.buildRow(card, headerIndex);
        rows.appendChild(row);
    }

    var addButton = zatoConsole.panels.createElement('button', 'console-tool console-options-add', config.addText);
    addButton.type = 'button';
    addButton.addEventListener('click', zatoConsole.options.onAddClick.bind(null, card, rows));

    container.appendChild(title);
    container.appendChild(rows);
    container.appendChild(addButton);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.buildRow = function(card, headerIndex) {

    var config = zatoConsole.options.config;
    var header = zatoConsole.state.exchanges[card.id].headers[headerIndex];

    var row = zatoConsole.panels.createElement('div', 'console-options-row');
    row.setAttribute(config.rowAttribute, headerIndex);

    var nameInput = zatoConsole.options.buildInput(config.namePlaceholder, header.name);
    nameInput.addEventListener('input', zatoConsole.options.onNameInput.bind(null, card, headerIndex));

    var valueInput = zatoConsole.options.buildInput(config.valuePlaceholder, header.value);
    valueInput.addEventListener('input', zatoConsole.options.onValueInput.bind(null, card, headerIndex));

    var removeButton = zatoConsole.panels.createElement('button', 'console-options-remove');
    removeButton.type = 'button';
    removeButton.title = config.removeLabel;
    removeButton.setAttribute('aria-label', config.removeLabel);
    removeButton.addEventListener('click', zatoConsole.options.onRemoveClick.bind(null, card, headerIndex));

    var icon = zatoConsole.panels.createSvgElement('svg', {'class': 'console-options-remove-icon', 'viewBox': config.iconViewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoConsole.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    removeButton.appendChild(icon);

    row.appendChild(nameInput);
    row.appendChild(valueInput);
    row.appendChild(removeButton);

    return row;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.buildInput = function(placeholder, value) {

    var input = zatoConsole.panels.createElement('input', 'console-options-input');
    input.type = 'text';
    input.placeholder = placeholder;
    input.value = value;
    input.spellcheck = false;
    input.autocomplete = 'off';

    return input;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onNameInput = function(card, headerIndex, event) {
    zatoConsole.state.exchanges[card.id].headers[headerIndex].name = event.target.value;
    zatoConsole.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onValueInput = function(card, headerIndex, event) {
    zatoConsole.state.exchanges[card.id].headers[headerIndex].value = event.target.value;
    zatoConsole.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onAddClick = function(card, rows) {

    var headers = zatoConsole.state.exchanges[card.id].headers;
    headers.push({name: '', value: ''});

    var headerIndex = headers.length - 1;
    var row = zatoConsole.options.buildRow(card, headerIndex);

    rows.appendChild(row);
    row.firstChild.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onRemoveClick = function(card, headerIndex, event) {

    var headers = zatoConsole.state.exchanges[card.id].headers;
    headers.splice(headerIndex, 1);

    // The rows after the removed one move up an index, so all of them are built anew
    var rows = event.currentTarget.closest('.console-options-rows');
    rows.textContent = '';

    for(var rowIndex = 0; rowIndex < headers.length; rowIndex++) {
        var row = zatoConsole.options.buildRow(card, rowIndex);
        rows.appendChild(row);
    }

    zatoConsole.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.onClose = function(card) {

    var headers = zatoConsole.state.exchanges[card.id].headers;
    var kept = [];

    // Rows left without a name are dropped once the popover closes ..
    for(var headerIndex = 0; headerIndex < headers.length; headerIndex++) {
        var header = headers[headerIndex];

        if(header.name.trim() !== '') {
            kept.push(header);
        }
    }

    zatoConsole.state.exchanges[card.id].headers = kept;

    // .. and the button and the raw request reflect the headers that remain.
    zatoConsole.options.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.options.refresh = function(card) {

    var button = card.querySelector(zatoConsole.options.config.buttonSelector);
    var headers = zatoConsole.state.exchanges[card.id].headers;

    zatoConsole.panels.setCount(button, headers.length);
    zatoConsole.raw.refreshRequest(card);
    zatoConsole.links.refresh(card);
};
