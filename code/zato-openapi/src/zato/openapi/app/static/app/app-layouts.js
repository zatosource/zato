zatoApp.layouts = {};

zatoApp.layouts.config = {
    layoutEntryAttribute: 'data-layout-entry',
    cardSelector: '.app-operation',
    sectionSelector: '.app-group',
    masterSelector: '.app-layout-master',
    detailSelector: '.app-layout-detail',
    activeCardSelector: '.app-operation.app-layout-active',
    activeClass: 'app-layout-active',
    rowScrollBlock: 'nearest',
    listSelector: '.app-layout-list',
    rowSelector: '.app-layout-row',
    excludedClass: 'app-layout-excluded',
    filterPlaceholder: 'Filter',
    clearLabel: 'Clear',
    filterIconCircle: {'cx': '11', 'cy': '11', 'r': '7'},
    filterIconHandle: 'm20 20-3.5-3.5',
    clearIconStrokes: ['M18 6 6 18', 'm6 6 12 12'],
    escapeKey: 'Escape',
    enterKey: 'Enter',
    resizerClass: 'app-layout-resizer',
    gripClass: 'app-layout-grip',
    resizeLabel: 'Resize',
    resizingClass: 'app-body app-resizing-layout',
    idleClass: 'app-body',
    storageKey: 'zato.openapi.app.master.width',
    widthVariable: '--app-layout-master-width',
    widthUnit: 'px',
    widthMinimum: 240,
    widthMaximumShare: 0.6,
    primaryButton: 0,
    masterTopClass: 'app-layout-master-top',
    toggleClass: 'app-sidebar-toggle app-layout-toggle',
    toggleSelector: '.app-layout-toggle',
    contentId: 'app-content',
    collapsedContentClass: 'app-content app-layout-master-collapsed',
    expandedContentClass: 'app-content',
    collapsedStorageKey: 'zato.openapi.app.master.collapsed',
    collapsedValue: '1',
    expandedValue: '0',
    collapseLabel: 'Collapse',
    expandLabel: 'Expand',
    iconCollapseClass: 'app-sidebar-icon app-layout-icon-collapse',
    iconExpandClass: 'app-sidebar-icon app-layout-icon-expand',
};

zatoApp.layouts.collapse = {
    isCollapsed: false,
};

zatoApp.layouts.drag = {
    isDragging: false,
    startX: 0,
    startWidth: 0,
    maximumWidth: 0,
    width: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.init = function() {

    var config = zatoApp.layouts.config;

    // The width of an earlier visit applies to every group, localStorage returning null for a key never stored
    var stored = localStorage.getItem(config.storageKey);

    if(stored !== null) {
        document.documentElement.style.setProperty(config.widthVariable, stored + config.widthUnit);
    }

    // The list is collapsed or not in every group alike, as it was left on an earlier visit
    var storedCollapsed = localStorage.getItem(config.collapsedStorageKey);
    zatoApp.layouts.collapse.isCollapsed = storedCollapsed === config.collapsedValue;

    zatoApp.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.applyCollapsed = function() {

    var config = zatoApp.layouts.config;
    var isCollapsed = zatoApp.layouts.collapse.isCollapsed;

    var content = document.getElementById(config.contentId);
    content.className = isCollapsed ? config.collapsedContentClass : config.expandedContentClass;

    var toggles = document.querySelectorAll(config.toggleSelector);

    for(var toggleIndex = 0; toggleIndex < toggles.length; toggleIndex++) {
        zatoApp.layouts.markToggle(toggles[toggleIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.markToggle = function(toggle) {

    var config = zatoApp.layouts.config;
    var isCollapsed = zatoApp.layouts.collapse.isCollapsed;
    var label = isCollapsed ? config.expandLabel : config.collapseLabel;

    toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.buildToggle = function() {

    var config = zatoApp.layouts.config;

    var toggle = zatoApp.render.createElement('button', config.toggleClass);
    toggle.type = 'button';
    toggle.addEventListener('click', zatoApp.layouts.onToggleClick);

    var collapseIcon = zatoApp.sidebar.buildIcon(zatoApp.sidebar.config.iconCollapseChevron, config.iconCollapseClass);
    var expandIcon = zatoApp.sidebar.buildIcon(zatoApp.sidebar.config.iconExpandChevron, config.iconExpandClass);

    toggle.appendChild(collapseIcon);
    toggle.appendChild(expandIcon);

    zatoApp.layouts.markToggle(toggle);

    return toggle;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onToggleClick = function() {

    var config = zatoApp.layouts.config;
    var collapse = zatoApp.layouts.collapse;

    collapse.isCollapsed = !collapse.isCollapsed;
    localStorage.setItem(config.collapsedStorageKey, collapse.isCollapsed ? config.collapsedValue : config.expandedValue);

    zatoApp.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.apply = function(section, group) {

    var frame = zatoApp.render.createElement('div', 'app-layout-frame');
    var master = zatoApp.layouts.buildEntryButtons(group);
    var resizer = zatoApp.layouts.buildResizer();
    var detail = zatoApp.render.createElement('div', 'app-layout-detail');

    // The list of operations stands next to the detail column that holds the cards ..
    var cards = zatoApp.layouts.getCards(section);
    zatoApp.layouts.moveCards(cards, detail);

    frame.appendChild(master);
    frame.appendChild(resizer);
    frame.appendChild(detail);
    section.appendChild(frame);

    // .. of which the first one is shown.
    zatoApp.layouts.showOnly(section, cards[0]);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.activate = function(entryId) {

    var config = zatoApp.layouts.config;
    var card = document.getElementById(entryId);
    var section = card.closest(config.sectionSelector);

    zatoApp.layouts.showOnly(section, card);

    // A card shown anew starts at its top ..
    var detail = section.querySelector(config.detailSelector);
    detail.scrollTop = 0;

    // .. its row is brought into view in the list, which matters when the card is chosen from the navigation ..
    var row = section.querySelector('[' + config.layoutEntryAttribute + '="' + entryId + '"]');
    row.scrollIntoView({block: config.rowScrollBlock});

    // .. and the address and the specification window follow it.
    zatoApp.layouts.onCardShown(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onGroupShown = function(section) {

    var card = section.querySelector(zatoApp.layouts.config.activeCardSelector);
    zatoApp.layouts.onCardShown(card.id);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onCardShown = function(entryId) {
    zatoApp.links.update(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.getCards = function(section) {

    var config = zatoApp.layouts.config;
    var found = section.querySelectorAll(config.cardSelector);
    var out = [];

    for(var cardIndex = 0; cardIndex < found.length; cardIndex++) {
        out.push(found[cardIndex]);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.setEntryVisible = function(entryId, isVisible) {

    var config = zatoApp.layouts.config;
    var selector = '[' + config.layoutEntryAttribute + '="' + entryId + '"]';
    var elements = document.querySelectorAll(selector);

    // The navigation's filter excludes rows apart from the list's own filter, which hides them
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        elements[elementIndex].classList.toggle(config.excludedClass, !isVisible);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.buildEntryButton = function(entry) {

    var config = zatoApp.layouts.config;

    var button = zatoApp.render.createElement('button', 'app-layout-row');
    button.type = 'button';
    button.setAttribute(config.layoutEntryAttribute, entry.id);
    button.addEventListener('click', zatoApp.layouts.onEntryButtonClick);

    var chip = zatoApp.render.createMethodChip(entry.method);
    var path = zatoApp.render.buildPath(entry.path, 'app-layout-entry-path');

    button.appendChild(chip);
    button.appendChild(path);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.buildEntryButtons = function(group) {

    var config = zatoApp.layouts.config;
    var container = zatoApp.render.createElement('div', 'app-layout-master');

    // The filter and the button that collapses the list stay above the rows while they scroll
    var masterTop = zatoApp.render.createElement('div', config.masterTopClass);
    var filter = zatoApp.layouts.buildFilter();
    var toggle = zatoApp.layouts.buildToggle();
    var list = zatoApp.render.createElement('div', 'app-layout-list');

    masterTop.appendChild(filter);
    masterTop.appendChild(toggle);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var button = zatoApp.layouts.buildEntryButton(entry);
        list.appendChild(button);
    }

    container.appendChild(masterTop);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.buildFilter = function() {

    var config = zatoApp.layouts.config;
    var panels = zatoApp.panels;
    var viewBox = panels.config.iconViewBox;

    var box = zatoApp.render.createElement('div', 'app-filter-box app-layout-filter');

    var icon = panels.createSvgElement('svg', {'class': 'app-filter-icon', 'viewBox': viewBox});
    var circle = panels.createSvgElement('circle', config.filterIconCircle);
    var handle = panels.createSvgElement('path', {'d': config.filterIconHandle});

    icon.appendChild(circle);
    icon.appendChild(handle);

    var input = zatoApp.render.createElement('input', 'app-filter');
    input.type = 'text';
    input.placeholder = config.filterPlaceholder;
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.addEventListener('input', zatoApp.layouts.onFilterInput);
    input.addEventListener('keydown', zatoApp.layouts.onFilterKeyDown);

    var clear = zatoApp.render.createElement('button', 'app-filter-clear');
    clear.type = 'button';
    clear.hidden = true;
    clear.setAttribute('aria-label', config.clearLabel);
    clear.addEventListener('click', zatoApp.layouts.onFilterClearClick);

    var clearIcon = panels.createSvgElement('svg', {'class': 'app-filter-clear-icon', 'viewBox': viewBox});

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

zatoApp.layouts.onFilterInput = function(event) {

    var config = zatoApp.layouts.config;
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
        var entry = zatoApp.state.entriesById[entryId];
        var searchText = zatoApp.render.getSearchText(entry);

        row.hidden = !searchText.includes(query);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onFilterKeyDown = function(event) {

    var config = zatoApp.layouts.config;
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

zatoApp.layouts.onFilterClearClick = function(event) {

    var input = event.currentTarget.parentNode.querySelector('input');

    // The filter is cleared the same way typing changes it, so the rows and the clear button both follow
    input.value = '';
    input.dispatchEvent(new Event('input'));
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onEntryButtonClick = function(event) {

    var config = zatoApp.layouts.config;
    var entryId = event.currentTarget.getAttribute(config.layoutEntryAttribute);

    zatoApp.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.showOnly = function(section, card) {

    var config = zatoApp.layouts.config;
    var cards = zatoApp.layouts.getCards(section);
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

zatoApp.layouts.moveCards = function(cards, target) {

    for(var cardIndex = 0; cardIndex < cards.length; cardIndex++) {
        target.appendChild(cards[cardIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.buildResizer = function() {

    var config = zatoApp.layouts.config;

    var resizer = zatoApp.render.createElement('div', config.resizerClass);
    var grip = zatoApp.render.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'vertical');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoApp.layouts.onPointerDown);
    resizer.addEventListener('pointermove', zatoApp.layouts.onPointerMove);
    resizer.addEventListener('pointerup', zatoApp.layouts.onPointerUp);
    resizer.addEventListener('pointercancel', zatoApp.layouts.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onPointerDown = function(event) {

    var config = zatoApp.layouts.config;
    var drag = zatoApp.layouts.drag;

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

zatoApp.layouts.onPointerMove = function(event) {

    var config = zatoApp.layouts.config;
    var drag = zatoApp.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedWidth = drag.startWidth + event.clientX - drag.startX;
    var atLeastMinimum = Math.max(config.widthMinimum, requestedWidth);

    drag.width = Math.min(drag.maximumWidth, atLeastMinimum);
    document.documentElement.style.setProperty(config.widthVariable, drag.width + config.widthUnit);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.onPointerUp = function(event) {

    var config = zatoApp.layouts.config;
    var drag = zatoApp.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, Math.round(drag.width));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.layouts.init();
