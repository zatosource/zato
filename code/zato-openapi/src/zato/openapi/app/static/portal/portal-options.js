zatoPortal.options = {};

zatoPortal.options.config = {
    cardSelector: '.portal-operation',
    buttonSelector: '.portal-tool-options',
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

zatoPortal.options.onButtonClick = function(event) {

    var button = event.currentTarget;
    var card = button.closest(zatoPortal.options.config.cardSelector);
    var headers = zatoPortal.state.exchanges[card.id].headers;

    // With no headers yet, the popover opens with an empty row ready for the first one ..
    var isFirst = headers.length === 0;

    if(isFirst) {
        headers.push({name: '', value: ''});
    }

    var content = zatoPortal.options.buildContent(card);
    var onClose = zatoPortal.options.onClose.bind(null, card);

    zatoPortal.popover.open(button, content, onClose);

    // .. and its name is typed in at once, unless the click closed the popover instead.
    if(isFirst && content.isConnected) {
        content.querySelector('.portal-options-input').focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.buildContent = function(card) {

    var config = zatoPortal.options.config;
    var exchange = zatoPortal.state.exchanges[card.id];

    var container = zatoPortal.panels.createElement('div', 'portal-options');
    var title = zatoPortal.panels.createElement('div', 'portal-popover-title', config.headersTitle);
    var rows = zatoPortal.panels.createElement('div', 'portal-options-rows');

    for(var headerIndex = 0; headerIndex < exchange.headers.length; headerIndex++) {
        var row = zatoPortal.options.buildRow(card, headerIndex);
        rows.appendChild(row);
    }

    var addButton = zatoPortal.panels.createElement('button', 'portal-tool portal-options-add', config.addText);
    addButton.type = 'button';
    addButton.addEventListener('click', zatoPortal.options.onAddClick.bind(null, card, rows));

    container.appendChild(title);
    container.appendChild(rows);
    container.appendChild(addButton);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.buildRow = function(card, headerIndex) {

    var config = zatoPortal.options.config;
    var header = zatoPortal.state.exchanges[card.id].headers[headerIndex];

    var row = zatoPortal.panels.createElement('div', 'portal-options-row');
    row.setAttribute(config.rowAttribute, headerIndex);

    var nameInput = zatoPortal.options.buildInput(config.namePlaceholder, header.name);
    nameInput.addEventListener('input', zatoPortal.options.onNameInput.bind(null, card, headerIndex));

    var valueInput = zatoPortal.options.buildInput(config.valuePlaceholder, header.value);
    valueInput.addEventListener('input', zatoPortal.options.onValueInput.bind(null, card, headerIndex));

    var removeButton = zatoPortal.panels.createElement('button', 'portal-options-remove');
    removeButton.type = 'button';
    removeButton.title = config.removeLabel;
    removeButton.setAttribute('aria-label', config.removeLabel);
    removeButton.addEventListener('click', zatoPortal.options.onRemoveClick.bind(null, card, headerIndex));

    var icon = zatoPortal.panels.createSvgElement('svg', {'class': 'portal-options-remove-icon', 'viewBox': config.iconViewBox});

    for(var pathIndex = 0; pathIndex < config.removeIconPaths.length; pathIndex++) {
        var path = zatoPortal.panels.createSvgElement('path', {'d': config.removeIconPaths[pathIndex]});
        icon.appendChild(path);
    }

    removeButton.appendChild(icon);

    row.appendChild(nameInput);
    row.appendChild(valueInput);
    row.appendChild(removeButton);

    return row;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.buildInput = function(placeholder, value) {

    var input = zatoPortal.panels.createElement('input', 'portal-options-input');
    input.type = 'text';
    input.placeholder = placeholder;
    input.value = value;
    input.spellcheck = false;
    input.autocomplete = 'off';

    return input;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.onNameInput = function(card, headerIndex, event) {
    zatoPortal.state.exchanges[card.id].headers[headerIndex].name = event.target.value;
    zatoPortal.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.onValueInput = function(card, headerIndex, event) {
    zatoPortal.state.exchanges[card.id].headers[headerIndex].value = event.target.value;
    zatoPortal.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.onAddClick = function(card, rows) {

    var headers = zatoPortal.state.exchanges[card.id].headers;
    headers.push({name: '', value: ''});

    var headerIndex = headers.length - 1;
    var row = zatoPortal.options.buildRow(card, headerIndex);

    rows.appendChild(row);
    row.firstChild.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.onRemoveClick = function(card, headerIndex, event) {

    var headers = zatoPortal.state.exchanges[card.id].headers;
    headers.splice(headerIndex, 1);

    // The rows after the removed one move up an index, so all of them are built anew
    var rows = event.currentTarget.closest('.portal-options-rows');
    rows.textContent = '';

    for(var rowIndex = 0; rowIndex < headers.length; rowIndex++) {
        var row = zatoPortal.options.buildRow(card, rowIndex);
        rows.appendChild(row);
    }

    zatoPortal.links.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.onClose = function(card) {

    var headers = zatoPortal.state.exchanges[card.id].headers;
    var kept = [];

    // Rows left without a name are dropped once the popover closes ..
    for(var headerIndex = 0; headerIndex < headers.length; headerIndex++) {
        var header = headers[headerIndex];

        if(header.name.trim() !== '') {
            kept.push(header);
        }
    }

    zatoPortal.state.exchanges[card.id].headers = kept;

    // .. and the button and the raw request reflect the headers that remain.
    zatoPortal.options.refresh(card);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.options.refresh = function(card) {

    var button = card.querySelector(zatoPortal.options.config.buttonSelector);
    var headers = zatoPortal.state.exchanges[card.id].headers;

    zatoPortal.panels.setCount(button, headers.length);
    zatoPortal.raw.refreshRequest(card);
    zatoPortal.links.refresh(card);
};
