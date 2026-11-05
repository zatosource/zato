zatoApp.render = {};

zatoApp.render.config = {
    methodOrder: ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'],
    entryIdPrefix: 'app-operation-',
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
    filteringClass: 'app-navigation-filtering',
    collapsedClass: 'app-navigation-collapsed',
    entryAttribute: 'data-entry',
    selectedClass: 'app-selected',
    responseEditableMode: 'plaintext-only',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildGroups = function(apiDocument) {

    var config = zatoApp.render.config;
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
                groupsByName[groupName] = zatoApp.render.buildGroup(groupName);
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
            zatoApp.state.entriesById[entry.id] = entry;
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

zatoApp.render.buildGroup = function(name) {

    var config = zatoApp.render.config;
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

zatoApp.render.createElement = function(tagName, className, text) {
    var out = zatoApp.panels.createElement(tagName, className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.createMethodChip = function(method) {

    var text = method.toUpperCase();
    var className = 'app-chip app-method app-method-' + method;

    var out = zatoApp.render.createElement('span', className, text);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildNavigationGroup = function(group) {

    var config = zatoApp.render.config;

    var container = zatoApp.render.createElement('div', 'app-navigation-group');
    container.setAttribute(config.groupAttribute, group.name);

    var heading = zatoApp.render.createElement('button', 'app-navigation-heading');
    heading.type = 'button';
    heading.addEventListener('click', zatoApp.render.onGroupClick);

    var chevron = zatoApp.panels.createSvgElement('svg', {'class': 'app-navigation-chevron', 'viewBox': zatoApp.panels.config.iconViewBox});
    var chevronShape = zatoApp.panels.createSvgElement('path', {'d': config.chevronPath});
    chevron.appendChild(chevronShape);

    var name = zatoApp.render.createElement('span', 'app-navigation-name', group.label);
    var count = zatoApp.render.createElement('span', 'app-navigation-count', String(group.entries.length));

    heading.appendChild(chevron);
    heading.appendChild(name);
    heading.appendChild(count);
    container.appendChild(heading);

    var list = zatoApp.render.createElement('ul', 'app-navigation-list');

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];

        var item = zatoApp.render.createElement('li', 'app-navigation-item');
        item.setAttribute(config.entryAttribute, entry.id);

        var link = zatoApp.render.createElement('a', 'app-navigation-link');
        link.href = zatoApp.links.getHash(entry);
        link.addEventListener('click', zatoApp.render.onEntryClick);

        var chip = zatoApp.render.createMethodChip(entry.method);
        var label = zatoApp.render.buildPath(entry.path, 'app-navigation-label');

        link.appendChild(chip);
        link.appendChild(label);
        item.appendChild(link);
        list.appendChild(item);
    }

    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildNavigationSection = function(name) {

    var out = zatoApp.render.createElement('div', 'app-navigation-section', name);
    out.setAttribute(zatoApp.render.config.sectionAttribute, name);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildSection = function(group) {

    var config = zatoApp.render.config;

    var section = zatoApp.render.createElement('section', 'app-group');
    section.setAttribute(config.groupAttribute, group.name);
    section.hidden = true;

    var header = zatoApp.render.createElement('header', 'app-group-header');
    var name = zatoApp.render.createElement('h2', 'app-group-name', group.label);

    var entryCount = group.entries.length;
    var noun = entryCount === 1 ? config.operationSingular : config.operationPlural;
    var count = zatoApp.render.createElement('span', 'app-group-count', entryCount + ' ' + noun);

    if(group.section !== '') {
        var sectionName = zatoApp.render.createElement('span', 'app-chip app-group-section', group.section);
        header.appendChild(sectionName);
    }

    header.appendChild(name);
    header.appendChild(count);
    section.appendChild(header);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var card = zatoApp.render.buildCard(entry);
        section.appendChild(card);
    }

    return section;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildPath = function(path, className) {

    var config = zatoApp.render.config;
    var element = zatoApp.render.createElement('span', className);

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. and they stand out from the literal segments around them.
        if(isPlaceholder) {
            var placeholder = zatoApp.render.createElement('span', 'app-operation-path-parameter', part);
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

zatoApp.render.buildHeader = function(entry) {

    var config = zatoApp.render.config;
    var operation = entry.operation;

    var header = zatoApp.render.createElement('header', 'app-operation-header');

    // The method and the path wrap within their own part of the header ..
    var heading = zatoApp.render.createElement('div', 'app-operation-heading');

    var chip = zatoApp.render.createMethodChip(entry.method);
    var path = zatoApp.render.buildPath(entry.path, 'app-operation-path');

    heading.appendChild(chip);
    heading.appendChild(path);

    // .. deprecated operations say so, with their sunset date and successor when known ..
    if(operation.deprecated === true) {
        var deprecated = zatoApp.render.createElement('span', 'app-chip app-chip-warning', config.deprecatedText);
        heading.appendChild(deprecated);

        if(config.sunsetKey in operation) {
            var sunsetText = config.sunsetPrefix + operation[config.sunsetKey];
            var sunset = zatoApp.render.createElement('span', 'app-chip app-chip-neutral', sunsetText);
            heading.appendChild(sunset);
        }

        if(config.successorKey in operation) {
            var successorText = config.successorPrefix + operation[config.successorKey];
            var successor = zatoApp.render.createElement('span', 'app-chip app-chip-neutral', successorText);
            heading.appendChild(successor);
        }
    }

    // .. while the tools stay on the first line, however long the path is.
    var tools = zatoApp.panels.buildTools();
    tools.className = 'app-panel-tools app-operation-tools';

    var specification = zatoApp.panels.buildToolButton(config.specificationText, 'app-tool-specification', zatoApp.specification.onButtonClick);
    var link = zatoApp.panels.buildCopyButton(zatoApp.render.getLinkCopyText, config.linkText);

    tools.appendChild(specification);
    tools.appendChild(link);

    header.appendChild(heading);
    header.appendChild(tools);

    return header;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.getLinkCopyText = function(button) {

    var card = button.closest(zatoApp.invoke.config.cardSelector);

    var out = zatoApp.links.getUrl(card);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildCard = function(entry) {

    var operation = entry.operation;

    var card = zatoApp.render.createElement('article', 'app-operation');
    card.id = entry.id;
    card.addEventListener('keydown', zatoApp.invoke.onCardKeyDown);
    card.addEventListener('input', zatoApp.links.onCardInput);

    zatoApp.state.exchanges[entry.id] = {headers: [], result: null};

    var header = zatoApp.render.buildHeader(entry);
    card.appendChild(header);

    if('description' in operation) {
        var description = zatoApp.render.createElement('p', 'app-operation-description', operation.description);
        card.appendChild(description);
    }

    // The request, with the button that sends it, and the response below it, the handle between them dividing their height
    var exchange = zatoApp.render.createElement('div', 'app-operation-exchange');
    var request = zatoApp.render.buildRequest(entry);
    var resizer = zatoApp.exchange.buildResizer();
    var response = zatoApp.render.buildResponse();

    exchange.appendChild(request);
    exchange.appendChild(resizer);
    exchange.appendChild(response);
    card.appendChild(exchange);

    zatoApp.history.refresh(card);

    return card;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildRequest = function(entry) {

    var config = zatoApp.render.config;
    var panels = zatoApp.panels;

    var container = zatoApp.render.createElement('div', 'app-operation-request');

    var bar = panels.buildBar(config.requestTitle);
    bar.className = 'app-panel-bar app-request-bar';

    var play = panels.buildPlayButton(zatoApp.invoke.onPlayClick);
    var invoking = panels.buildInvoking();

    var tools = panels.buildTools();
    var example = panels.buildToolButton(config.exampleText, 'app-tool-example', zatoApp.invoke.onExampleClick);
    var prettyPrint = panels.buildToolButton(config.prettyPrintText, 'app-tool-pretty-print', zatoApp.invoke.onPrettyPrintClick);
    var history = panels.buildToolButton(config.historyText, 'app-tool-history', zatoApp.history.onButtonClick);
    var options = panels.buildToolButton(config.optionsText, 'app-tool-options', zatoApp.options.onButtonClick);
    var rawSwitch = panels.buildRawSwitch(zatoApp.raw.onRequestSwitchChange);
    var copy = panels.buildCopyButton(zatoApp.raw.getRequestCopyText, zatoApp.panels.config.copyText);

    tools.appendChild(example);
    tools.appendChild(prettyPrint);
    tools.appendChild(history);
    tools.appendChild(options);
    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(play);
    bar.appendChild(invoking);
    bar.appendChild(tools);

    var sample = zatoApp.invoke.buildSample(entry, false);
    var sampleText = zatoApp.highlight.format(sample);
    var editor = zatoApp.highlight.createEditor(sampleText);

    var input = editor.querySelector(zatoApp.invoke.config.inputSelector);
    input.addEventListener('input', zatoApp.invoke.onEditorInput);

    var raw = zatoApp.render.createElement('pre', 'app-code app-raw app-raw-request');
    raw.hidden = true;

    container.appendChild(bar);

    // Endpoints with parameters in their paths have an input for each of them, apart from the request itself
    if(config.placeholderPattern.test(entry.path)) {
        var pathEditor = zatoApp.render.buildPathEditor(entry);
        container.appendChild(pathEditor);
    }

    container.appendChild(editor);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildPathEditor = function(entry) {

    var config = zatoApp.render.config;
    var examples = zatoApp.invoke.getPathExamples(entry.operation);
    var container = zatoApp.render.createElement('div', 'app-path-editor');

    // Splitting on a capturing pattern keeps the placeholders, at every odd position ..
    var parts = entry.path.split(config.placeholderPattern);

    for(var partIndex = 0; partIndex < parts.length; partIndex++) {
        var part = parts[partIndex];
        var isPlaceholder = partIndex % 2 === 1;

        // .. each of which becomes an input with the parameter's sample value ..
        if(isPlaceholder) {
            var name = part.slice(1, -1);

            var input = zatoApp.render.createElement('input', 'app-path-input');
            input.type = 'text';
            input.spellcheck = false;
            input.autocomplete = 'off';
            input.placeholder = name;
            input.title = name;
            input.value = examples[name];
            input.setAttribute('aria-label', name);
            input.setAttribute(zatoApp.invoke.config.pathParameterAttribute, name);
            input.addEventListener('input', zatoApp.invoke.onPathInput);

            zatoApp.invoke.sizePathInput(input);
            container.appendChild(input);
        }

        // .. between the literal segments of the path.
        else {
            var literal = zatoApp.render.createElement('span', 'app-path-literal', part);
            container.appendChild(literal);
        }
    }

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.buildResponse = function() {

    var config = zatoApp.render.config;
    var panels = zatoApp.panels;

    var container = zatoApp.render.createElement('div', 'app-operation-response');
    container.hidden = true;

    var bar = panels.buildBar(config.responseTitle);
    bar.className = 'app-panel-bar app-response-bar';

    var status = zatoApp.render.createElement('span', 'app-chip app-response-status');
    var time = zatoApp.render.createElement('span', 'app-response-time');

    var tools = panels.buildTools();
    var rawSwitch = panels.buildRawSwitch(zatoApp.raw.onResponseSwitchChange);
    var copy = panels.buildCopyButton(zatoApp.raw.getResponseCopyText, zatoApp.panels.config.copyText);

    tools.appendChild(rawSwitch);
    tools.appendChild(copy);

    bar.appendChild(status);
    bar.appendChild(time);
    bar.appendChild(tools);

    // The response can be edited in place, both as it is formatted and in its raw form
    var body = zatoApp.render.createElement('pre', 'app-code app-response-body');
    body.contentEditable = config.responseEditableMode;
    body.spellcheck = false;

    var raw = zatoApp.render.createElement('pre', 'app-code app-raw app-raw-response');
    raw.contentEditable = config.responseEditableMode;
    raw.spellcheck = false;
    raw.hidden = true;

    container.appendChild(bar);
    container.appendChild(body);
    container.appendChild(raw);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.onGroupClick = function(event) {

    var config = zatoApp.render.config;
    var container = event.currentTarget.parentNode;
    var groupName = container.getAttribute(config.groupAttribute);

    // The group already shown is collapsed or expanded in the navigation ..
    if(groupName === zatoApp.state.selectedGroup) {
        container.classList.toggle(config.collapsedClass);
        return;
    }

    // .. and any other one is shown, expanded.
    zatoApp.render.selectGroup(groupName);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.onEntryClick = function(event) {

    event.preventDefault();

    var item = event.currentTarget.parentNode;
    var entryId = item.getAttribute(zatoApp.render.config.entryAttribute);
    var entry = zatoApp.state.entriesById[entryId];

    // The card can be shown only once its group is the one shown
    zatoApp.render.selectGroup(entry.group);
    zatoApp.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.selectGroup = function(groupName) {

    var config = zatoApp.render.config;
    var groupSelector = '[' + config.groupAttribute + ']';
    var elements = document.querySelectorAll(groupSelector);

    zatoApp.state.selectedGroup = groupName;

    // The navigation marks the group and the content shows its section only
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var isSelected = element.getAttribute(config.groupAttribute) === groupName;

        if(element.tagName === 'SECTION') {
            element.hidden = !isSelected;

            if(isSelected) {
                zatoApp.layouts.onGroupShown(element);
            }
        }
        else {
            element.classList.toggle(config.selectedClass, isSelected);
            element.classList.remove(config.collapsedClass);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.getSearchText = function(entry) {

    var text = entry.method + ' ' + entry.path;

    if('description' in entry.operation) {
        text += ' ' + entry.operation.description;
    }

    var out = text.toLowerCase();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.render.onFilterInput = function(event) {

    var config = zatoApp.render.config;
    var query = event.target.value.trim().toLowerCase();
    var groups = zatoApp.state.groups;
    var firstVisibleGroup = '';
    var isSelectedVisible = false;
    var visibleSections = {};

    // While a query is typed, every group with matches is expanded, not only the one shown
    var navigation = document.getElementById(zatoApp.config.navigationId);
    navigation.classList.toggle(config.filteringClass, query !== '');

    for(var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
        var group = groups[groupIndex];
        var visibleCount = 0;

        // An operation matches by its path or its description ..
        for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
            var entry = group.entries[entryIndex];
            var searchText = zatoApp.render.getSearchText(entry);
            var isMatch = searchText.includes(query);

            var itemSelector = '[' + config.entryAttribute + '="' + entry.id + '"]';
            var item = document.querySelector(itemSelector);
            var card = document.getElementById(entry.id);

            item.hidden = !isMatch;
            card.hidden = !isMatch;
            zatoApp.layouts.setEntryVisible(entry.id, isMatch);

            if(isMatch) {
                visibleCount += 1;
            }
        }

        // .. and a group with no matching operation is left out of the navigation.
        var groupName = CSS.escape(group.name);
        var navigationSelector = '.app-navigation-group[' + config.groupAttribute + '="' + groupName + '"]';
        var navigationGroup = document.querySelector(navigationSelector);
        var hasMatches = visibleCount > 0;

        navigationGroup.hidden = !hasMatches;

        if(hasMatches) {
            visibleSections[group.section] = true;

            if(firstVisibleGroup === '') {
                firstVisibleGroup = group.name;
            }
            if(group.name === zatoApp.state.selectedGroup) {
                isSelectedVisible = true;
            }
        }
    }

    // A section heading is shown only if any of its groups has matches ..
    var sectionSelector = '.app-navigation-section[' + config.sectionAttribute + ']';
    var sectionHeadings = document.querySelectorAll(sectionSelector);

    for(var headingIndex = 0; headingIndex < sectionHeadings.length; headingIndex++) {
        var heading = sectionHeadings[headingIndex];
        heading.hidden = !(heading.getAttribute(config.sectionAttribute) in visibleSections);
    }

    // .. and the group shown moves to the first one with matches when its own operations are all filtered out.
    if(!isSelectedVisible) {
        if(firstVisibleGroup !== '') {
            zatoApp.render.selectGroup(firstVisibleGroup);
        }
    }
};
