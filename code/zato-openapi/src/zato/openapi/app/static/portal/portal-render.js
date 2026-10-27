zatoPortal.render = {};

zatoPortal.render.config = {
    methodOrder: ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'],
    entryIdPrefix: 'portal-operation-',
    placeholderPattern: /(\{[^}]+\})/,
    groupSeparator: ' / ',
    chevronPath: 'M9 6l6 6-6 6',
    requestTitle: 'Request',
    responseTitle: 'Response',
    historyText: 'History',
    optionsText: 'Options',
    exampleText: 'Example',
    prettyPrintText: 'Pretty print',
    specificationText: 'Spec',
    linkText: 'Link',
    deprecatedText: 'Deprecated',
    sunsetPrefix: 'Sunset ',
    successorPrefix: 'Successor ',
    sunsetKey: 'x-sunset',
    successorKey: 'x-successor',
    operationSingular: 'operation',
    operationPlural: 'operations',
    groupAttribute: 'data-group',
    sectionAttribute: 'data-section',
    filteringClass: 'portal-navigation-filtering',
    collapsedClass: 'portal-navigation-collapsed',
    entryAttribute: 'data-entry',
    selectedClass: 'portal-selected',
    responseEditableMode: 'plaintext-only',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildGroups = function(apiDocument) {

    var config = zatoPortal.render.config;
    var groupsByName = {};
    var paths = apiDocument.paths;
    var pathNames = Object.keys(paths).sort();
    var entryCount = 0;

    // Operations are listed by path and, under one path, in the usual order of methods ..
    for(var pathIndex = 0; pathIndex < pathNames.length; pathIndex++) {
        var path = pathNames[pathIndex];
        var pathItem = paths[path];

        for(var methodIndex = 0; methodIndex < config.methodOrder.length; methodIndex++) {
            var method = config.methodOrder[methodIndex];

            if(!(method in pathItem)) {
                continue;
            }

            var operation = pathItem[method];
            var groupName = operation.tags[0];

            if(!(groupName in groupsByName)) {
                groupsByName[groupName] = zatoPortal.render.buildGroup(groupName);
            }

            entryCount += 1;

            var entryId = config.entryIdPrefix + entryCount;

            var entry = {
                id: entryId,
                group: groupName,
                method: method,
                path: path,
                operation: operation,
            };

            groupsByName[groupName].entries.push(entry);
            zatoPortal.state.entriesById[entry.id] = entry;
        }
    }

    // .. and groups are listed by name, which keeps the groups of a section together.
    var groupNames = Object.keys(groupsByName).sort();
    var out = [];

    for(var groupIndex = 0; groupIndex < groupNames.length; groupIndex++) {
        var name = groupNames[groupIndex];
        out.push(groupsByName[name]);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildGroup = function(name) {

    var config = zatoPortal.render.config;
    var separatorIndex = name.indexOf(config.groupSeparator);
    var section = '';
    var label = name;

    // A group of a large section is named after both, e.g. Healthcare / Patients,
    // while any other group stands on its own.
    if(separatorIndex > -1) {
        section = name.slice(0, separatorIndex);
        label = name.slice(separatorIndex + config.groupSeparator.length);
    }

    var out = {name: name, section: section, label: label, entries: []};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.createElement = function(tagName, className, text) {
    var out = zatoPortal.panels.createElement(tagName, className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.createMethodChip = function(method) {

    var text = method.toUpperCase();
    var className = 'portal-chip portal-method portal-method-' + method;

    var out = zatoPortal.render.createElement('span', className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildNavigationGroup = function(group) {

    var config = zatoPortal.render.config;

    var container = zatoPortal.render.createElement('div', 'portal-navigation-group');
    container.setAttribute(config.groupAttribute, group.name);

    var heading = zatoPortal.render.createElement('button', 'portal-navigation-heading');
    heading.type = 'button';
    heading.addEventListener('click', zatoPortal.render.onGroupClick);

    var chevron = zatoPortal.panels.createSvgElement('svg', {'class': 'portal-navigation-chevron', 'viewBox': zatoPortal.panels.config.iconViewBox});
    var chevronShape = zatoPortal.panels.createSvgElement('path', {'d': config.chevronPath});
    chevron.appendChild(chevronShape);

    var name = zatoPortal.render.createElement('span', 'portal-navigation-name', group.label);
    var count = zatoPortal.render.createElement('span', 'portal-navigation-count', String(group.entries.length));

    heading.appendChild(chevron);
    heading.appendChild(name);
    heading.appendChild(count);
    container.appendChild(heading);

    var list = zatoPortal.render.createElement('ul', 'portal-navigation-list');

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];

        var item = zatoPortal.render.createElement('li', 'portal-navigation-item');
        item.setAttribute(config.entryAttribute, entry.id);

        var link = zatoPortal.render.createElement('a', 'portal-navigation-link');
        link.href = zatoPortal.links.getHash(entry);
        link.addEventListener('click', zatoPortal.render.onEntryClick);

        var chip = zatoPortal.render.createMethodChip(entry.method);
        var label = zatoPortal.render.buildPath(entry.path, 'portal-navigation-label');

        link.appendChild(chip);
        link.appendChild(label);
        item.appendChild(link);
        list.appendChild(item);
    }

    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildNavigationSection = function(name) {

    var out = zatoPortal.render.createElement('div', 'portal-navigation-section', name);
    out.setAttribute(zatoPortal.render.config.sectionAttribute, name);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildSection = function(group) {

    var config = zatoPortal.render.config;

    var section = zatoPortal.render.createElement('section', 'portal-group');
    section.setAttribute(config.groupAttribute, group.name);
    section.hidden = true;

    var header = zatoPortal.render.createElement('header', 'portal-group-header');
    var name = zatoPortal.render.createElement('h2', 'portal-group-name', group.label);

    var entryCount = group.entries.length;
    var noun = entryCount === 1 ? config.operationSingular : config.operationPlural;
    var count = zatoPortal.render.createElement('span', 'portal-group-count', entryCount + ' ' + noun);

    if(group.section !== '') {
        var sectionName = zatoPortal.render.createElement('span', 'portal-chip portal-group-section', group.section);
        header.appendChild(sectionName);
    }

    header.appendChild(name);
    header.appendChild(count);
    section.appendChild(header);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var card = zatoPortal.render.buildCard(entry);
        section.appendChild(card);
    }

    return section;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildPath = function(path, className) {

    var config = zatoPortal.render.config;
    var element = zatoPortal.render.createElement('span', className);

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. and they stand out from the literal segments around them.
        if(isPlaceholder) {
            var placeholder = zatoPortal.render.createElement('span', 'portal-operation-path-parameter', part);
            element.appendChild(placeholder);
        }
        else {
            var literal = document.createTextNode(part);
            element.appendChild(literal);
        }
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildHeader = function(entry) {

    var config = zatoPortal.render.config;
    var operation = entry.operation;

    var header = zatoPortal.render.createElement('header', 'portal-operation-header');

    // The method and the path wrap within their own part of the header ..
    var heading = zatoPortal.render.createElement('div', 'portal-operation-heading');

    var chip = zatoPortal.render.createMethodChip(entry.method);
    var path = zatoPortal.render.buildPath(entry.path, 'portal-operation-path');

    heading.appendChild(chip);
    heading.appendChild(path);

    // .. deprecated operations say so, with their sunset date and successor when known ..
    if(operation.deprecated === true) {
        var deprecated = zatoPortal.render.createElement('span', 'portal-chip portal-chip-warning', config.deprecatedText);
        heading.appendChild(deprecated);

        if(config.sunsetKey in operation) {
            var sunsetText = config.sunsetPrefix + operation[config.sunsetKey];
            var sunset = zatoPortal.render.createElement('span', 'portal-chip portal-chip-neutral', sunsetText);
            heading.appendChild(sunset);
        }

        if(config.successorKey in operation) {
            var successorText = config.successorPrefix + operation[config.successorKey];
            var successor = zatoPortal.render.createElement('span', 'portal-chip portal-chip-neutral', successorText);
            heading.appendChild(successor);
        }
    }

    // .. while the tools stay on the first line, however long the path is.
    var tools = zatoPortal.panels.buildTools();
    tools.className = 'portal-panel-tools portal-operation-tools';

    var specification = zatoPortal.panels.buildToolButton(config.specificationText, 'portal-tool-specification', zatoPortal.specification.onButtonClick);
    var link = zatoPortal.panels.buildCopyButton(zatoPortal.render.getLinkCopyText, config.linkText);

    tools.appendChild(specification);
    tools.appendChild(link);

    header.appendChild(heading);
    header.appendChild(tools);

    return header;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.getLinkCopyText = function(button) {

    var card = button.closest(zatoPortal.invoke.config.cardSelector);

    var out = zatoPortal.links.getUrl(card);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildCard = function(entry) {

    var operation = entry.operation;

    var card = zatoPortal.render.createElement('article', 'portal-operation');
    card.id = entry.id;
    card.addEventListener('keydown', zatoPortal.invoke.onCardKeyDown);
    card.addEventListener('input', zatoPortal.links.onCardInput);

    zatoPortal.state.exchanges[entry.id] = {headers: [], result: null};

    var header = zatoPortal.render.buildHeader(entry);
    card.appendChild(header);

    if('description' in operation) {
        var description = zatoPortal.render.createElement('p', 'portal-operation-description', operation.description);
        card.appendChild(description);
    }

    // The request, with the button that sends it, and the response below it, the handle between them dividing their height
    var exchange = zatoPortal.render.createElement('div', 'portal-operation-exchange');
    var request = zatoPortal.render.buildRequest(entry);
    var resizer = zatoPortal.exchange.buildResizer();
    var response = zatoPortal.render.buildResponse();

    exchange.appendChild(request);
    exchange.appendChild(resizer);
    exchange.appendChild(response);
    card.appendChild(exchange);

    zatoPortal.history.refresh(card);

    return card;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildRequest = function(entry) {

    var config = zatoPortal.render.config;
    var panels = zatoPortal.panels;

    var container = zatoPortal.render.createElement('div', 'portal-operation-request');

    var bar = panels.buildBar(config.requestTitle);
    bar.className = 'portal-panel-bar portal-request-bar';

    var play = panels.buildPlayButton(zatoPortal.invoke.onPlayClick);
    var invoking = panels.buildInvoking();

    var tools = panels.buildTools();
    var example = panels.buildToolButton(config.exampleText, 'portal-tool-example', zatoPortal.invoke.onExampleClick);
    var prettyPrint = panels.buildToolButton(config.prettyPrintText, 'portal-tool-pretty-print', zatoPortal.invoke.onPrettyPrintClick);
    var history = panels.buildToolButton(config.historyText, 'portal-tool-history', zatoPortal.history.onButtonClick);
    var options = panels.buildToolButton(config.optionsText, 'portal-tool-options', zatoPortal.options.onButtonClick);
    var rawSwitch = panels.buildRawSwitch(zatoPortal.raw.onRequestSwitchChange);
    var copy = panels.buildCopyButton(zatoPortal.raw.getRequestCopyText, zatoPortal.panels.config.copyText);

    tools.appendChild(example);
    tools.appendChild(prettyPrint);
    tools.appendChild(history);
    tools.appendChild(options);
    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(play);
    bar.appendChild(invoking);
    bar.appendChild(tools);

    var sample = zatoPortal.invoke.buildSample(entry, false);
    var sampleText = zatoPortal.highlight.format(sample);
    var editor = zatoPortal.highlight.createEditor(sampleText);

    var input = editor.querySelector(zatoPortal.invoke.config.inputSelector);
    input.addEventListener('input', zatoPortal.invoke.onEditorInput);

    var raw = zatoPortal.render.createElement('pre', 'portal-code portal-raw portal-raw-request');
    raw.hidden = true;

    container.appendChild(bar);

    // Endpoints with parameters in their paths have an input for each of them, apart from the request itself
    if(config.placeholderPattern.test(entry.path)) {
        var pathEditor = zatoPortal.render.buildPathEditor(entry);
        container.appendChild(pathEditor);
    }

    container.appendChild(editor);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildPathEditor = function(entry) {

    var config = zatoPortal.render.config;
    var examples = zatoPortal.invoke.getPathExamples(entry.operation);
    var container = zatoPortal.render.createElement('div', 'portal-path-editor');

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = entry.path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. each of which becomes an input with the parameter's sample value ..
        if(isPlaceholder) {
            var name = part.slice(1, -1);

            var input = zatoPortal.render.createElement('input', 'portal-path-input');
            input.type = 'text';
            input.spellcheck = false;
            input.autocomplete = 'off';
            input.placeholder = name;
            input.title = name;
            input.value = examples[name];
            input.setAttribute('aria-label', name);
            input.setAttribute(zatoPortal.invoke.config.pathParameterAttribute, name);
            input.addEventListener('input', zatoPortal.invoke.onPathInput);

            zatoPortal.invoke.sizePathInput(input);
            container.appendChild(input);
        }

        // .. between the literal segments of the path.
        else {
            var literal = zatoPortal.render.createElement('span', 'portal-path-literal', part);
            container.appendChild(literal);
        }
    }

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.buildResponse = function() {

    var config = zatoPortal.render.config;
    var panels = zatoPortal.panels;

    var container = zatoPortal.render.createElement('div', 'portal-operation-response');
    container.hidden = true;

    var bar = panels.buildBar(config.responseTitle);
    bar.className = 'portal-panel-bar portal-response-bar';

    var status = zatoPortal.render.createElement('span', 'portal-chip portal-response-status');
    var time = zatoPortal.render.createElement('span', 'portal-response-time');

    var tools = panels.buildTools();
    var rawSwitch = panels.buildRawSwitch(zatoPortal.raw.onResponseSwitchChange);
    var copy = panels.buildCopyButton(zatoPortal.raw.getResponseCopyText, zatoPortal.panels.config.copyText);

    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(status);
    bar.appendChild(time);
    bar.appendChild(tools);

    // The response can be edited in place, both as it is formatted and in its raw form
    var body = zatoPortal.render.createElement('pre', 'portal-code portal-response-body');
    body.contentEditable = config.responseEditableMode;
    body.spellcheck = false;

    var raw = zatoPortal.render.createElement('pre', 'portal-code portal-raw portal-raw-response');
    raw.contentEditable = config.responseEditableMode;
    raw.spellcheck = false;
    raw.hidden = true;

    container.appendChild(bar);
    container.appendChild(body);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.onGroupClick = function(event) {

    var config = zatoPortal.render.config;
    var container = event.currentTarget.parentNode;
    var groupName = container.getAttribute(config.groupAttribute);

    // The group already shown is collapsed or expanded in the navigation ..
    if(groupName === zatoPortal.state.selectedGroup) {
        container.classList.toggle(config.collapsedClass);
        return;
    }

    // .. and any other one is shown, expanded.
    zatoPortal.render.selectGroup(groupName);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.onEntryClick = function(event) {

    event.preventDefault();

    var item = event.currentTarget.parentNode;
    var entryId = item.getAttribute(zatoPortal.render.config.entryAttribute);
    var entry = zatoPortal.state.entriesById[entryId];

    // The card can be shown only once its group is the one shown
    zatoPortal.render.selectGroup(entry.group);
    zatoPortal.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.selectGroup = function(groupName) {

    var config = zatoPortal.render.config;
    var groupSelector = '[' + config.groupAttribute + ']';
    var elements = document.querySelectorAll(groupSelector);

    zatoPortal.state.selectedGroup = groupName;

    // The navigation marks the group and the content shows its section only
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var isSelected = element.getAttribute(config.groupAttribute) === groupName;

        if(element.tagName === 'SECTION') {
            element.hidden = !isSelected;

            if(isSelected) {
                zatoPortal.layouts.onGroupShown(element);
            }
        }
        else {
            element.classList.toggle(config.selectedClass, isSelected);
            element.classList.remove(config.collapsedClass);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.getSearchText = function(entry) {

    var text = entry.method + ' ' + entry.path;

    if('description' in entry.operation) {
        text += ' ' + entry.operation.description;
    }

    var out = text.toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.render.onFilterInput = function(event) {

    var config = zatoPortal.render.config;
    var query = event.target.value.trim().toLowerCase();
    var groups = zatoPortal.state.groups;
    var firstVisibleGroup = '';
    var isSelectedVisible = false;
    var visibleSections = {};

    // While a query is typed, every group with matches is expanded, not only the one shown
    var navigation = document.getElementById(zatoPortal.config.navigationId);
    navigation.classList.toggle(config.filteringClass, query !== '');

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];
        var visibleCount = 0;

        // An operation matches by its path or its description ..
        for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
            var entry = group.entries[entryIndex];
            var searchText = zatoPortal.render.getSearchText(entry);
            var isMatch = searchText.includes(query);

            var itemSelector = '[' + config.entryAttribute + '="' + entry.id + '"]';
            var item = document.querySelector(itemSelector);
            var card = document.getElementById(entry.id);

            item.hidden = !isMatch;
            card.hidden = !isMatch;
            zatoPortal.layouts.setEntryVisible(entry.id, isMatch);

            if(isMatch) {
                visibleCount += 1;
            }
        }

        // .. and a group with no matching operation is left out of the navigation.
        var groupName = CSS.escape(group.name);
        var navigationSelector = '.portal-navigation-group[' + config.groupAttribute + '="' + groupName + '"]';
        var navigationGroup = document.querySelector(navigationSelector);
        var hasMatches = visibleCount > 0;

        navigationGroup.hidden = !hasMatches;

        if(hasMatches) {
            visibleSections[group.section] = true;

            if(firstVisibleGroup === '') {
                firstVisibleGroup = group.name;
            }
            if(group.name === zatoPortal.state.selectedGroup) {
                isSelectedVisible = true;
            }
        }
    }

    // A section heading is shown only if any of its groups has matches ..
    var sectionSelector = '.portal-navigation-section[' + config.sectionAttribute + ']';
    var sectionHeadings = document.querySelectorAll(sectionSelector);

    for(var headingIndex = 0; headingIndex < sectionHeadings.length; headingIndex++) {
        var heading = sectionHeadings[headingIndex];
        heading.hidden = !(heading.getAttribute(config.sectionAttribute) in visibleSections);
    }

    // .. and the group shown moves to the first one with matches when its own operations are all filtered out.
    if(!isSelectedVisible) {
        if(firstVisibleGroup !== '') {
            zatoPortal.render.selectGroup(firstVisibleGroup);
        }
    }
};
