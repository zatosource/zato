zatoApp.options = {};

zatoApp.options.config = {
    cardSelector: '.app-operation',
    buttonSelector: '.app-tool-options',
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

zatoApp.options.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoApp.options.config.cardSelector);
    var headers = zatoApp.state.exchanges[card.id].headers;

    // With no headers yet, the popover opens with an empty row ready for the first one ..
    var isFirst = headers.length === 0;

    if(isFirst) {
        headers.push({name: '', value: ''});
    }

    var content = zatoApp.options.buildContent(card);
    var onClose = zatoApp.options.onClose.bind(null, card);

    zatoApp.popover.open(button, content, onClose);

    // .. and its name is typed in at once, unless the click closed the popover instead.
    if(isFirst && content.isConnected) {
        content.querySelector('.app-options-input').focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.buildContent = function(card) {

    var config = zatoApp.options.config;
    var exchange = zatoApp.state.exchanges[card.id];

    var container = zatoApp.panels.createElement('div', 'app-options');
    var title = zatoApp.panels.createElement('div', 'app-popover-title', config.headersTitle);
    var rows = zatoApp.panels.createElement('div', 'app-options-rows');

    for(var headerIndex = 0; headerIndex < exchange.headers.length; headerIndex++) {
        var row = zatoApp.options.buildRow(card, headerIndex);
        rows.appendChild(row);
    }

    var addButton = zatoApp.panels.createElement('button', 'app-tool app-options-add', config.addText);
    addButton.type = 'button';
    addButton.addEventListener('click', zatoApp.options.onAddClick.bind(null, card, rows));

    container.appendChild(title);
    container.appendChild(rows);
    container.appendChild(addButton);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.buildRow = function(card, headerIndex) {

    var config = zatoApp.options.config;
    var header = zatoApp.state.exchanges[card.id].headers[headerIndex];

    var row = zatoApp.panels.createElement('div', 'app-options-row');
    row.setAttribute(config.rowAttribute, headerIndex);

    var nameInput = zatoApp.options.buildInput(config.namePlaceholder, header.name);
    nameInput.addEventListener('input', zatoApp.options.onNameInput.bind(null, card, headerIndex));

    var valueInput = zatoApp.options.buildInput(config.valuePlaceholder, header.value);
    valueInput.addEventListener('input', zatoApp.options.onValueInput.bind(null, card, headerIndex));

    var removeButton = zatoApp.panels.createElement('button', 'app-options-remove');
    removeButton.type = 'button';
    removeButton.title = config.removeLabel;
    removeButton.setAttribute('aria-label', config.removeLabel);
    removeButton.addEventListener('click', zatoApp.options.onRemoveClick.bind(null, card, headerIndex));

    var icon = zatoApp.panels.createSvgElement('svg', {'class': 'app-options-remove-icon', 'viewBox': config.iconViewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoApp.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    removeButton.appendChild(icon);

    row.appendChild(nameInput);
    row.appendChild(valueInput);
    row.appendChild(removeButton);

    return row;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.buildInput = function(placeholder, value) {

    var input = zatoApp.panels.createElement('input', 'app-options-input');
    input.type = 'text';
    input.placeholder = placeholder;
    input.value = value;
    input.spellcheck = false;
    input.autocomplete = 'off';

    return input;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.onNameInput = function(card, headerIndex, event) {
    zatoApp.state.exchanges[card.id].headers[headerIndex].name = event.target.value;
    zatoApp.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.onValueInput = function(card, headerIndex, event) {
    zatoApp.state.exchanges[card.id].headers[headerIndex].value = event.target.value;
    zatoApp.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.onAddClick = function(card, rows) {

    var headers = zatoApp.state.exchanges[card.id].headers;
    headers.push({name: '', value: ''});

    var headerIndex = headers.length - 1;
    var row = zatoApp.options.buildRow(card, headerIndex);

    rows.appendChild(row);
    row.firstChild.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.onRemoveClick = function(card, headerIndex, event) {

    var headers = zatoApp.state.exchanges[card.id].headers;
    headers.splice(headerIndex, 1);

    // The rows after the removed one move up an index, so all of them are built anew
    var rows = event.currentTarget.closest('.app-options-rows');
    rows.textContent = '';

    for(var rowIndex = 0; rowIndex < headers.length; rowIndex++) {
        var row = zatoApp.options.buildRow(card, rowIndex);
        rows.appendChild(row);
    }

    zatoApp.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.onClose = function(card) {

    var headers = zatoApp.state.exchanges[card.id].headers;
    var kept = [];

    // Rows left without a name are dropped once the popover closes ..
    for(var headerIndex = 0; headerIndex < headers.length; headerIndex++) {
        var header = headers[headerIndex];

        if(header.name.trim() !== '') {
            kept.push(header);
        }
    }

    zatoApp.state.exchanges[card.id].headers = kept;

    // .. and the button and the raw request reflect the headers that remain.
    zatoApp.options.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.options.refresh = function(card) {

    var button = card.querySelector(zatoApp.options.config.buttonSelector);
    var headers = zatoApp.state.exchanges[card.id].headers;

    zatoApp.panels.setCount(button, headers.length);
    zatoApp.raw.refreshRequest(card);
    zatoApp.links.refresh(card);
};
