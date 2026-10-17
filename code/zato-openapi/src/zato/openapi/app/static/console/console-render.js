zatoConsole.render = {};

zatoConsole.render.config = {
    methodOrder: ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'],
    entryIdPrefix: 'console-operation-',
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
    filteringClass: 'console-navigation-filtering',
    collapsedClass: 'console-navigation-collapsed',
    entryAttribute: 'data-entry',
    selectedClass: 'console-selected',
    responseEditableMode: 'plaintext-only',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildGroups = function(apiDocument) {

    var config = zatoConsole.render.config;
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
                groupsByName[groupName] = zatoConsole.render.buildGroup(groupName);
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
            zatoConsole.state.entriesById[entry.id] = entry;
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

zatoConsole.render.buildGroup = function(name) {

    var config = zatoConsole.render.config;
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

zatoConsole.render.createElement = function(tagName, className, text) {
    var out = zatoConsole.panels.createElement(tagName, className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.createMethodChip = function(method) {

    var text = method.toUpperCase();
    var className = 'console-chip console-method console-method-' + method;

    var out = zatoConsole.render.createElement('span', className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildNavigationGroup = function(group) {

    var config = zatoConsole.render.config;

    var container = zatoConsole.render.createElement('div', 'console-navigation-group');
    container.setAttribute(config.groupAttribute, group.name);

    var heading = zatoConsole.render.createElement('button', 'console-navigation-heading');
    heading.type = 'button';
    heading.addEventListener('click', zatoConsole.render.onGroupClick);

    var chevron = zatoConsole.panels.createSvgElement('svg', {'class': 'console-navigation-chevron', 'viewBox': zatoConsole.panels.config.iconViewBox});
    var chevronShape = zatoConsole.panels.createSvgElement('path', {'d': config.chevronPath});
    chevron.appendChild(chevronShape);

    var name = zatoConsole.render.createElement('span', 'console-navigation-name', group.label);
    var count = zatoConsole.render.createElement('span', 'console-navigation-count', String(group.entries.length));

    heading.appendChild(chevron);
    heading.appendChild(name);
    heading.appendChild(count);
    container.appendChild(heading);

    var list = zatoConsole.render.createElement('ul', 'console-navigation-list');

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];

        var item = zatoConsole.render.createElement('li', 'console-navigation-item');
        item.setAttribute(config.entryAttribute, entry.id);

        var link = zatoConsole.render.createElement('a', 'console-navigation-link');
        link.href = zatoConsole.links.getHash(entry);
        link.addEventListener('click', zatoConsole.render.onEntryClick);

        var chip = zatoConsole.render.createMethodChip(entry.method);
        var label = zatoConsole.render.buildPath(entry.path, 'console-navigation-label');

        link.appendChild(chip);
        link.appendChild(label);
        item.appendChild(link);
        list.appendChild(item);
    }

    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildNavigationSection = function(name) {

    var out = zatoConsole.render.createElement('div', 'console-navigation-section', name);
    out.setAttribute(zatoConsole.render.config.sectionAttribute, name);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildSection = function(group) {

    var config = zatoConsole.render.config;

    var section = zatoConsole.render.createElement('section', 'console-group');
    section.setAttribute(config.groupAttribute, group.name);
    section.hidden = true;

    var header = zatoConsole.render.createElement('header', 'console-group-header');
    var name = zatoConsole.render.createElement('h2', 'console-group-name', group.label);

    var entryCount = group.entries.length;
    var noun = entryCount === 1 ? config.operationSingular : config.operationPlural;
    var count = zatoConsole.render.createElement('span', 'console-group-count', entryCount + ' ' + noun);

    if(group.section !== '') {
        var sectionName = zatoConsole.render.createElement('span', 'console-chip console-group-section', group.section);
        header.appendChild(sectionName);
    }

    header.appendChild(name);
    header.appendChild(count);
    section.appendChild(header);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var card = zatoConsole.render.buildCard(entry);
        section.appendChild(card);
    }

    return section;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildPath = function(path, className) {

    var config = zatoConsole.render.config;
    var element = zatoConsole.render.createElement('span', className);

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. and they stand out from the literal segments around them.
        if(isPlaceholder) {
            var placeholder = zatoConsole.render.createElement('span', 'console-operation-path-parameter', part);
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

zatoConsole.render.buildHeader = function(entry) {

    var config = zatoConsole.render.config;
    var operation = entry.operation;

    var header = zatoConsole.render.createElement('header', 'console-operation-header');

    // The method and the path wrap within their own part of the header ..
    var heading = zatoConsole.render.createElement('div', 'console-operation-heading');

    var chip = zatoConsole.render.createMethodChip(entry.method);
    var path = zatoConsole.render.buildPath(entry.path, 'console-operation-path');

    heading.appendChild(chip);
    heading.appendChild(path);

    // .. deprecated operations say so, with their sunset date and successor when known ..
    if(operation.deprecated === true) {
        var deprecated = zatoConsole.render.createElement('span', 'console-chip console-chip-warning', config.deprecatedText);
        heading.appendChild(deprecated);

        if(config.sunsetKey in operation) {
            var sunsetText = config.sunsetPrefix + operation[config.sunsetKey];
            var sunset = zatoConsole.render.createElement('span', 'console-chip console-chip-neutral', sunsetText);
            heading.appendChild(sunset);
        }

        if(config.successorKey in operation) {
            var successorText = config.successorPrefix + operation[config.successorKey];
            var successor = zatoConsole.render.createElement('span', 'console-chip console-chip-neutral', successorText);
            heading.appendChild(successor);
        }
    }

    // .. while the tools stay on the first line, however long the path is.
    var tools = zatoConsole.panels.buildTools();
    tools.className = 'console-panel-tools console-operation-tools';

    var specification = zatoConsole.panels.buildToolButton(config.specificationText, 'console-tool-specification', zatoConsole.specification.onButtonClick);
    var link = zatoConsole.panels.buildCopyButton(zatoConsole.render.getLinkCopyText, config.linkText);

    tools.appendChild(specification);
    tools.appendChild(link);

    header.appendChild(heading);
    header.appendChild(tools);

    return header;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.getLinkCopyText = function(button) {

    var card = button.closest(zatoConsole.invoke.config.cardSelector);

    var out = zatoConsole.links.getUrl(card);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildCard = function(entry) {

    var operation = entry.operation;

    var card = zatoConsole.render.createElement('article', 'console-operation');
    card.id = entry.id;
    card.addEventListener('keydown', zatoConsole.invoke.onCardKeyDown);
    card.addEventListener('input', zatoConsole.links.onCardInput);

    zatoConsole.state.exchanges[entry.id] = {headers: [], result: null};

    var header = zatoConsole.render.buildHeader(entry);
    card.appendChild(header);

    if('description' in operation) {
        var description = zatoConsole.render.createElement('p', 'console-operation-description', operation.description);
        card.appendChild(description);
    }

    // The request, with the button that sends it, and the response below it, the handle between them dividing their height
    var exchange = zatoConsole.render.createElement('div', 'console-operation-exchange');
    var request = zatoConsole.render.buildRequest(entry);
    var resizer = zatoConsole.exchange.buildResizer();
    var response = zatoConsole.render.buildResponse();

    exchange.appendChild(request);
    exchange.appendChild(resizer);
    exchange.appendChild(response);
    card.appendChild(exchange);

    zatoConsole.history.refresh(card);

    return card;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildRequest = function(entry) {

    var config = zatoConsole.render.config;
    var panels = zatoConsole.panels;

    var container = zatoConsole.render.createElement('div', 'console-operation-request');

    var bar = panels.buildBar(config.requestTitle);
    bar.className = 'console-panel-bar console-request-bar';

    var play = panels.buildPlayButton(zatoConsole.invoke.onPlayClick);
    var invoking = panels.buildInvoking();

    var tools = panels.buildTools();
    var example = panels.buildToolButton(config.exampleText, 'console-tool-example', zatoConsole.invoke.onExampleClick);
    var prettyPrint = panels.buildToolButton(config.prettyPrintText, 'console-tool-pretty-print', zatoConsole.invoke.onPrettyPrintClick);
    var history = panels.buildToolButton(config.historyText, 'console-tool-history', zatoConsole.history.onButtonClick);
    var options = panels.buildToolButton(config.optionsText, 'console-tool-options', zatoConsole.options.onButtonClick);
    var rawSwitch = panels.buildRawSwitch(zatoConsole.raw.onRequestSwitchChange);
    var copy = panels.buildCopyButton(zatoConsole.raw.getRequestCopyText, zatoConsole.panels.config.copyText);

    tools.appendChild(example);
    tools.appendChild(prettyPrint);
    tools.appendChild(history);
    tools.appendChild(options);
    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(play);
    bar.appendChild(invoking);
    bar.appendChild(tools);

    var sample = zatoConsole.invoke.buildSample(entry, false);
    var sampleText = zatoConsole.highlight.format(sample);
    var editor = zatoConsole.highlight.createEditor(sampleText);

    var input = editor.querySelector(zatoConsole.invoke.config.inputSelector);
    input.addEventListener('input', zatoConsole.invoke.onEditorInput);

    var raw = zatoConsole.render.createElement('pre', 'console-code console-raw console-raw-request');
    raw.hidden = true;

    container.appendChild(bar);

    // Endpoints with parameters in their paths have an input for each of them, apart from the request itself
    if(config.placeholderPattern.test(entry.path)) {
        var pathEditor = zatoConsole.render.buildPathEditor(entry);
        container.appendChild(pathEditor);
    }

    container.appendChild(editor);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildPathEditor = function(entry) {

    var config = zatoConsole.render.config;
    var examples = zatoConsole.invoke.getPathExamples(entry.operation);
    var container = zatoConsole.render.createElement('div', 'console-path-editor');

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = entry.path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. each of which becomes an input with the parameter's sample value ..
        if(isPlaceholder) {
            var name = part.slice(1, -1);

            var input = zatoConsole.render.createElement('input', 'console-path-input');
            input.type = 'text';
            input.spellcheck = false;
            input.autocomplete = 'off';
            input.placeholder = name;
            input.title = name;
            input.value = examples[name];
            input.setAttribute('aria-label', name);
            input.setAttribute(zatoConsole.invoke.config.pathParameterAttribute, name);
            input.addEventListener('input', zatoConsole.invoke.onPathInput);

            zatoConsole.invoke.sizePathInput(input);
            container.appendChild(input);
        }

        // .. between the literal segments of the path.
        else {
            var literal = zatoConsole.render.createElement('span', 'console-path-literal', part);
            container.appendChild(literal);
        }
    }

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.buildResponse = function() {

    var config = zatoConsole.render.config;
    var panels = zatoConsole.panels;

    var container = zatoConsole.render.createElement('div', 'console-operation-response');
    container.hidden = true;

    var bar = panels.buildBar(config.responseTitle);
    bar.className = 'console-panel-bar console-response-bar';

    var status = zatoConsole.render.createElement('span', 'console-chip console-response-status');
    var time = zatoConsole.render.createElement('span', 'console-response-time');

    var tools = panels.buildTools();
    var rawSwitch = panels.buildRawSwitch(zatoConsole.raw.onResponseSwitchChange);
    var copy = panels.buildCopyButton(zatoConsole.raw.getResponseCopyText, zatoConsole.panels.config.copyText);

    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(status);
    bar.appendChild(time);
    bar.appendChild(tools);

    // The response can be edited in place, both as it is formatted and in its raw form
    var body = zatoConsole.render.createElement('pre', 'console-code console-response-body');
    body.contentEditable = config.responseEditableMode;
    body.spellcheck = false;

    var raw = zatoConsole.render.createElement('pre', 'console-code console-raw console-raw-response');
    raw.contentEditable = config.responseEditableMode;
    raw.spellcheck = false;
    raw.hidden = true;

    container.appendChild(bar);
    container.appendChild(body);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.onGroupClick = function(event) {

    var config = zatoConsole.render.config;
    var container = event.currentTarget.parentNode;
    var groupName = container.getAttribute(config.groupAttribute);

    // The group already shown is collapsed or expanded in the navigation ..
    if(groupName === zatoConsole.state.selectedGroup) {
        container.classList.toggle(config.collapsedClass);
        return;
    }

    // .. and any other one is shown, expanded.
    zatoConsole.render.selectGroup(groupName);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.onEntryClick = function(event) {

    event.preventDefault();

    var item = event.currentTarget.parentNode;
    var entryId = item.getAttribute(zatoConsole.render.config.entryAttribute);
    var entry = zatoConsole.state.entriesById[entryId];

    // The card can be shown only once its group is the one shown
    zatoConsole.render.selectGroup(entry.group);
    zatoConsole.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.selectGroup = function(groupName) {

    var config = zatoConsole.render.config;
    var groupSelector = '[' + config.groupAttribute + ']';
    var elements = document.querySelectorAll(groupSelector);

    zatoConsole.state.selectedGroup = groupName;

    // The navigation marks the group and the content shows its section only
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var isSelected = element.getAttribute(config.groupAttribute) === groupName;

        if(element.tagName === 'SECTION') {
            element.hidden = !isSelected;

            if(isSelected) {
                zatoConsole.layouts.onGroupShown(element);
            }
        }
        else {
            element.classList.toggle(config.selectedClass, isSelected);
            element.classList.remove(config.collapsedClass);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.getSearchText = function(entry) {

    var text = entry.method + ' ' + entry.path;

    if('description' in entry.operation) {
        text += ' ' + entry.operation.description;
    }

    var out = text.toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.render.onFilterInput = function(event) {

    var config = zatoConsole.render.config;
    var query = event.target.value.trim().toLowerCase();
    var groups = zatoConsole.state.groups;
    var firstVisibleGroup = '';
    var isSelectedVisible = false;
    var visibleSections = {};

    // While a query is typed, every group with matches is expanded, not only the one shown
    var navigation = document.getElementById(zatoConsole.config.navigationId);
    navigation.classList.toggle(config.filteringClass, query !== '');

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];
        var visibleCount = 0;

        // An operation matches by its path or its description ..
        for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
            var entry = group.entries[entryIndex];
            var searchText = zatoConsole.render.getSearchText(entry);
            var isMatch = searchText.includes(query);

            var itemSelector = '[' + config.entryAttribute + '="' + entry.id + '"]';
            var item = document.querySelector(itemSelector);
            var card = document.getElementById(entry.id);

            item.hidden = !isMatch;
            card.hidden = !isMatch;
            zatoConsole.layouts.setEntryVisible(entry.id, isMatch);

            if(isMatch) {
                visibleCount += 1;
            }
        }

        // .. and a group with no matching operation is left out of the navigation.
        var groupName = CSS.escape(group.name);
        var navigationSelector = '.console-navigation-group[' + config.groupAttribute + '="' + groupName + '"]';
        var navigationGroup = document.querySelector(navigationSelector);
        var hasMatches = visibleCount > 0;

        navigationGroup.hidden = !hasMatches;

        if(hasMatches) {
            visibleSections[group.section] = true;

            if(firstVisibleGroup === '') {
                firstVisibleGroup = group.name;
            }
            if(group.name === zatoConsole.state.selectedGroup) {
                isSelectedVisible = true;
            }
        }
    }

    // A section heading is shown only if any of its groups has matches ..
    var sectionSelector = '.console-navigation-section[' + config.sectionAttribute + ']';
    var sectionHeadings = document.querySelectorAll(sectionSelector);

    for(var headingIndex = 0; headingIndex < sectionHeadings.length; headingIndex++) {
        var heading = sectionHeadings[headingIndex];
        heading.hidden = !(heading.getAttribute(config.sectionAttribute) in visibleSections);
    }

    // .. and the group shown moves to the first one with matches when its own operations are all filtered out.
    if(!isSelectedVisible) {
        if(firstVisibleGroup !== '') {
            zatoConsole.render.selectGroup(firstVisibleGroup);
        }
    }
};
