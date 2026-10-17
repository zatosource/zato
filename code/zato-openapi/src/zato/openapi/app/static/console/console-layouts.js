zatoConsole.layouts = {};

zatoConsole.layouts.config = {
    layoutEntryAttribute: 'data-layout-entry',
    cardSelector: '.console-operation',
    sectionSelector: '.console-group',
    masterSelector: '.console-layout-master',
    detailSelector: '.console-layout-detail',
    activeCardSelector: '.console-operation.console-layout-active',
    activeClass: 'console-layout-active',
    rowScrollBlock: 'nearest',
    listSelector: '.console-layout-list',
    rowSelector: '.console-layout-row',
    excludedClass: 'console-layout-excluded',
    filterPlaceholder: 'Filter',
    clearLabel: 'Clear',
    filterIconCircle: {'cx': '11', 'cy': '11', 'r': '7'},
    filterIconHandle: 'm20 20-3.5-3.5',
    clearIconStrokes: ['M18 6 6 18', 'm6 6 12 12'],
    escapeKey: 'Escape',
    enterKey: 'Enter',
    resizerClass: 'console-layout-resizer',
    gripClass: 'console-layout-grip',
    resizeLabel: 'Resize',
    resizingClass: 'console-body console-resizing-layout',
    idleClass: 'console-body',
    storageKey: 'zato.openapi.console.master.width',
    widthVariable: '--console-layout-master-width',
    widthUnit: 'px',
    widthMinimum: 240,
    widthMaximumShare: 0.6,
    primaryButton: 0,
    masterTopClass: 'console-layout-master-top',
    toggleClass: 'console-sidebar-toggle console-layout-toggle',
    toggleSelector: '.console-layout-toggle',
    contentId: 'console-content',
    collapsedContentClass: 'console-content console-layout-master-collapsed',
    expandedContentClass: 'console-content',
    collapsedStorageKey: 'zato.openapi.console.master.collapsed',
    collapsedValue: '1',
    expandedValue: '0',
    collapseLabel: 'Collapse',
    expandLabel: 'Expand',
    iconCollapseClass: 'console-sidebar-icon console-layout-icon-collapse',
    iconExpandClass: 'console-sidebar-icon console-layout-icon-expand',
};

zatoConsole.layouts.collapse = {
    isCollapsed: false,
};

zatoConsole.layouts.drag = {
    isDragging: false,
    startX: 0,
    startWidth: 0,
    maximumWidth: 0,
    width: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.init = function() {

    var config = zatoConsole.layouts.config;

    // The width of an earlier visit applies to every group, localStorage returning null for a key never stored
    var stored = localStorage.getItem(config.storageKey);

    if(stored !== null) {
        document.documentElement.style.setProperty(config.widthVariable, stored + config.widthUnit);
    }

    // The list is collapsed or not in every group alike, as it was left on an earlier visit
    var storedCollapsed = localStorage.getItem(config.collapsedStorageKey);
    zatoConsole.layouts.collapse.isCollapsed = storedCollapsed === config.collapsedValue;

    zatoConsole.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.applyCollapsed = function() {

    var config = zatoConsole.layouts.config;
    var isCollapsed = zatoConsole.layouts.collapse.isCollapsed;

    var content = document.getElementById(config.contentId);
    content.className = isCollapsed ? config.collapsedContentClass : config.expandedContentClass;

    var toggles = document.querySelectorAll(config.toggleSelector);

    for(var toggleIndex = 0; toggleIndex < toggles.length; toggleIndex++) {
        zatoConsole.layouts.markToggle(toggles[toggleIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.markToggle = function(toggle) {

    var config = zatoConsole.layouts.config;
    var isCollapsed = zatoConsole.layouts.collapse.isCollapsed;
    var label = isCollapsed ? config.expandLabel : config.collapseLabel;

    toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.buildToggle = function() {

    var config = zatoConsole.layouts.config;

    var toggle = zatoConsole.render.createElement('button', config.toggleClass);
    toggle.type = 'button';
    toggle.addEventListener('click', zatoConsole.layouts.onToggleClick);

    var collapseIcon = zatoConsole.sidebar.buildIcon(zatoConsole.sidebar.config.iconCollapseChevron, config.iconCollapseClass);
    var expandIcon = zatoConsole.sidebar.buildIcon(zatoConsole.sidebar.config.iconExpandChevron, config.iconExpandClass);

    toggle.appendChild(collapseIcon);
    toggle.appendChild(expandIcon);

    zatoConsole.layouts.markToggle(toggle);

    return toggle;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onToggleClick = function() {

    var config = zatoConsole.layouts.config;
    var collapse = zatoConsole.layouts.collapse;

    collapse.isCollapsed = !collapse.isCollapsed;
    localStorage.setItem(config.collapsedStorageKey, collapse.isCollapsed ? config.collapsedValue : config.expandedValue);

    zatoConsole.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.apply = function(section, group) {

    var frame = zatoConsole.render.createElement('div', 'console-layout-frame');
    var master = zatoConsole.layouts.buildEntryButtons(group);
    var resizer = zatoConsole.layouts.buildResizer();
    var detail = zatoConsole.render.createElement('div', 'console-layout-detail');

    // The list of operations stands next to the detail column that holds the cards ..
    var cards = zatoConsole.layouts.getCards(section);
    zatoConsole.layouts.moveCards(cards, detail);

    frame.appendChild(master);
    frame.appendChild(resizer);
    frame.appendChild(detail);
    section.appendChild(frame);

    // .. of which the first one is shown.
    zatoConsole.layouts.showOnly(section, cards[0]);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.activate = function(entryId) {

    var config = zatoConsole.layouts.config;
    var card = document.getElementById(entryId);
    var section = card.closest(config.sectionSelector);

    zatoConsole.layouts.showOnly(section, card);

    // A card shown anew starts at its top ..
    var detail = section.querySelector(config.detailSelector);
    detail.scrollTop = 0;

    // .. its row is brought into view in the list, which matters when the card is chosen from the navigation ..
    var row = section.querySelector('[' + config.layoutEntryAttribute + '="' + entryId + '"]');
    row.scrollIntoView({block: config.rowScrollBlock});

    // .. and the address and the specification window follow it.
    zatoConsole.layouts.onCardShown(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onGroupShown = function(section) {

    var card = section.querySelector(zatoConsole.layouts.config.activeCardSelector);
    zatoConsole.layouts.onCardShown(card.id);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onCardShown = function(entryId) {
    zatoConsole.links.update(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.getCards = function(section) {

    var config = zatoConsole.layouts.config;
    var found = section.querySelectorAll(config.cardSelector);
    var out = [];

    for(var cardIndex = 0; cardIndex < found.length; cardIndex++) {
        out.push(found[cardIndex]);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.setEntryVisible = function(entryId, isVisible) {

    var config = zatoConsole.layouts.config;
    var selector = '[' + config.layoutEntryAttribute + '="' + entryId + '"]';
    var elements = document.querySelectorAll(selector);

    // The navigation's filter excludes rows apart from the list's own filter, which hides them
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        elements[elementIndex].classList.toggle(config.excludedClass, !isVisible);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.buildEntryButton = function(entry) {

    var config = zatoConsole.layouts.config;

    var button = zatoConsole.render.createElement('button', 'console-layout-row');
    button.type = 'button';
    button.setAttribute(config.layoutEntryAttribute, entry.id);
    button.addEventListener('click', zatoConsole.layouts.onEntryButtonClick);

    var chip = zatoConsole.render.createMethodChip(entry.method);
    var path = zatoConsole.render.buildPath(entry.path, 'console-layout-entry-path');

    button.appendChild(chip);
    button.appendChild(path);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.buildEntryButtons = function(group) {

    var config = zatoConsole.layouts.config;
    var container = zatoConsole.render.createElement('div', 'console-layout-master');

    // The filter and the button that collapses the list stay above the rows while they scroll
    var masterTop = zatoConsole.render.createElement('div', config.masterTopClass);
    var filter = zatoConsole.layouts.buildFilter();
    var toggle = zatoConsole.layouts.buildToggle();
    var list = zatoConsole.render.createElement('div', 'console-layout-list');

    masterTop.appendChild(filter);
    masterTop.appendChild(toggle);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var button = zatoConsole.layouts.buildEntryButton(entry);
        list.appendChild(button);
    }

    container.appendChild(masterTop);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.buildFilter = function() {

    var config = zatoConsole.layouts.config;
    var panels = zatoConsole.panels;
    var viewBox = panels.config.iconViewBox;

    var box = zatoConsole.render.createElement('div', 'console-filter-box console-layout-filter');

    var icon = panels.createSvgElement('svg', {'class': 'console-filter-icon', 'viewBox': viewBox});
    var circle = panels.createSvgElement('circle', config.filterIconCircle);
    var handle = panels.createSvgElement('path', {'d': config.filterIconHandle});

    icon.appendChild(circle);
    icon.appendChild(handle);

    var input = zatoConsole.render.createElement('input', 'console-filter');
    input.type = 'text';
    input.placeholder = config.filterPlaceholder;
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.addEventListener('input', zatoConsole.layouts.onFilterInput);
    input.addEventListener('keydown', zatoConsole.layouts.onFilterKeyDown);

    var clear = zatoConsole.render.createElement('button', 'console-filter-clear');
    clear.type = 'button';
    clear.hidden = true;
    clear.setAttribute('aria-label', config.clearLabel);
    clear.addEventListener('click', zatoConsole.layouts.onFilterClearClick);

    var clearIcon = panels.createSvgElement('svg', {'class': 'console-filter-clear-icon', 'viewBox': viewBox});

    for(var strokeIndex = 0; strokeIndex < config.clearIconStrokes.length; strokeIndex++) {
        var stroke = panels.createSvgElement('path', {'d': config.clearIconStrokes[strokeIndex]});
        clearIcon.appendChild(stroke);
    }

    clear.appendChild(clearIcon);

    box.appendChild(icon);
    box.appendChild(input);
    box.appendChild(clear);

    return box;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onFilterInput = function(event) {

    var config = zatoConsole.layouts.config;
    var input = event.target;
    var box = input.parentNode;
    var master = input.closest(config.masterSelector);

    var query = input.value.trim().toLowerCase();
    var rows = master.querySelectorAll(config.rowSelector);

    var clear = box.querySelector('button');
    clear.hidden = input.value === '';

    // A row stays when its operation matches the way it matches in the navigation's filter
    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var entryId = row.getAttribute(config.layoutEntryAttribute);
        var entry = zatoConsole.state.entriesById[entryId];
        var searchText = zatoConsole.render.getSearchText(entry);

        row.hidden = !searchText.includes(query);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onFilterKeyDown = function(event) {

    var config = zatoConsole.layouts.config;
    var input = event.target;

    // Escape empties the filter ..
    if(event.key === config.escapeKey) {
        input.value = '';
        input.dispatchEvent(new Event('input'));
        return;
    }

    if(event.key !== config.enterKey) {
        return;
    }

    // .. and Enter shows the first operation that is still listed.
    var master = input.closest(config.masterSelector);
    var rows = master.querySelectorAll(config.rowSelector);

    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];

        if(row.hidden) {
            continue;
        }

        if(row.classList.contains(config.excludedClass)) {
            continue;
        }

        row.click();
        return;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onFilterClearClick = function(event) {

    var input = event.currentTarget.parentNode.querySelector('input');

    // The filter is cleared the same way typing changes it, so the rows and the clear button both follow
    input.value = '';
    input.dispatchEvent(new Event('input'));
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onEntryButtonClick = function(event) {

    var config = zatoConsole.layouts.config;
    var entryId = event.currentTarget.getAttribute(config.layoutEntryAttribute);

    zatoConsole.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.showOnly = function(section, card) {

    var config = zatoConsole.layouts.config;
    var cards = zatoConsole.layouts.getCards(section);
    var buttonSelector = '[' + config.layoutEntryAttribute + ']';
    var buttons = section.querySelectorAll(buttonSelector);

    // The card shown and the button that stands for it are marked, all the other ones are not
    for(var cardIndex = 0; cardIndex < cards.length; cardIndex++) {
        cards[cardIndex].classList.toggle(config.activeClass, cards[cardIndex] === card);
    }

    for(var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        var button = buttons[buttonIndex];
        var isActive = button.getAttribute(config.layoutEntryAttribute) === card.id;
        button.classList.toggle(config.activeClass, isActive);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.moveCards = function(cards, target) {

    for(var cardIndex = 0; cardIndex < cards.length; cardIndex++) {
        target.appendChild(cards[cardIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.buildResizer = function() {

    var config = zatoConsole.layouts.config;

    var resizer = zatoConsole.render.createElement('div', config.resizerClass);
    var grip = zatoConsole.render.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'vertical');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoConsole.layouts.onPointerDown);
    resizer.addEventListener('pointermove', zatoConsole.layouts.onPointerMove);
    resizer.addEventListener('pointerup', zatoConsole.layouts.onPointerUp);
    resizer.addEventListener('pointercancel', zatoConsole.layouts.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onPointerDown = function(event) {

    var config = zatoConsole.layouts.config;
    var drag = zatoConsole.layouts.drag;

    // Only the primary button starts a drag ..
    if(event.button !== config.primaryButton) {
        return;
    }

    // .. no text is selected while the pointer crosses the page ..
    event.preventDefault();

    var resizer = event.currentTarget;
    var frame = resizer.parentNode;
    var master = frame.querySelector(config.masterSelector);

    var frameWidth = frame.getBoundingClientRect().width;

    drag.isDragging = true;
    drag.startX = event.clientX;
    drag.startWidth = master.getBoundingClientRect().width;
    drag.maximumWidth = frameWidth * config.widthMaximumShare;
    drag.width = drag.startWidth;

    // .. and capturing the pointer keeps the drag going when it leaves the handle.
    resizer.setPointerCapture(event.pointerId);
    document.body.className = config.resizingClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onPointerMove = function(event) {

    var config = zatoConsole.layouts.config;
    var drag = zatoConsole.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedWidth = drag.startWidth + event.clientX - drag.startX;
    var atLeastMinimum = Math.max(config.widthMinimum, requestedWidth);

    drag.width = Math.min(drag.maximumWidth, atLeastMinimum);
    document.documentElement.style.setProperty(config.widthVariable, drag.width + config.widthUnit);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.onPointerUp = function(event) {

    var config = zatoConsole.layouts.config;
    var drag = zatoConsole.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, Math.round(drag.width));
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.layouts.init();
