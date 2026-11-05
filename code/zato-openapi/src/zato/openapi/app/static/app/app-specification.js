zatoApp.specification = {};

zatoApp.specification.config = {
    storageKey: 'zato.openapi.app.specification.size',
    positionStorageKey: 'zato.openapi.app.specification.window',
    cardSelector: '.app-operation',
    sidebarSelector: '.app-sidebar',
    buttonSelector: '.app-tool-specification',
    activeClass: 'app-tool-active',
    placement: 'bottom-start',
    animation: 'fade',
    strategy: 'fixed',
    layer: 200,
    defaultWidth: 560,
    defaultHeight: 520,
    edgeMargin: 16,
    cascadeOffset: 32,
    minimumVisible: 64,
    escapeKey: 'Escape',
    closeText: 'Close',
    copyAsText: 'Copy as',
    copyFormats: [
        {name: 'text', label: 'Text'},
        {name: 'json', label: 'JSON'},
    ],
    jsonFormat: 'json',
    formatAttribute: 'data-format',
    menuPlacement: 'top-end',
    menuOffset: [0, 4],
    menuLayer: 300,
    unit: 'px',
    primaryButton: 0,
};

zatoApp.specification.state = {

    // The windows in the order they were opened, which is the order Escape closes them in reverse ..
    windows: [],

    // .. and the same windows from the bottom one to the top one on the page.
    stacking: [],
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.loadSize = function() {

    var config = zatoApp.specification.config;

    // localStorage returns null for a key that was never stored, and the window then opens with its default size
    var stored = localStorage.getItem(config.storageKey);

    if(stored === null) {
        var defaultSize = {width: config.defaultWidth, height: config.defaultHeight};
        return defaultSize;
    }

    var out = JSON.parse(stored);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.saveSize = function(specWindow) {

    var size = {width: specWindow.width, height: specWindow.height};
    localStorage.setItem(zatoApp.specification.config.storageKey, JSON.stringify(size));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.savePosition = function(specWindow) {

    var position = {left: specWindow.left, top: specWindow.top};
    localStorage.setItem(zatoApp.specification.config.positionStorageKey, JSON.stringify(position));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.clampPosition = function(left, top, width) {

    var config = zatoApp.specification.config;

    // The bar never leaves the page, so the window can always be dragged back
    var leftMinimum = config.minimumVisible - width;
    var leftMaximum = window.innerWidth - config.minimumVisible;
    var topMaximum = window.innerHeight - config.minimumVisible;

    var out = {
        left: Math.min(leftMaximum, Math.max(leftMinimum, left)),
        top: Math.min(topMaximum, Math.max(0, top)),
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.getStartPosition = function(card, size) {

    var config = zatoApp.specification.config;

    // localStorage returns null until the first window is moved, and the window then opens at its default place ..
    var stored = localStorage.getItem(config.positionStorageKey);

    // .. while a place it was moved to is kept, within a page that may have become smaller since.
    if(stored !== null) {
        var position = JSON.parse(stored);
        var kept = zatoApp.specification.clampPosition(position.left, position.top, size.width);
        return kept;
    }

    // The default place starts at the middle of the sidebar and a margin below the top of the operations list
    var sidebarRect = document.querySelector(config.sidebarSelector).getBoundingClientRect();
    var cardRect = card.getBoundingClientRect();
    var sidebarMiddle = sidebarRect.left + sidebarRect.width / 2;

    var out = {left: sidebarMiddle, top: cardRect.top + config.edgeMargin};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.getNextPosition = function(card, size) {

    var config = zatoApp.specification.config;
    var windows = zatoApp.specification.state.windows;
    var start = zatoApp.specification.getStartPosition(card, size);

    // The first window opens at its start position ..
    if(windows.length === 0) {
        return start;
    }

    // .. each next one opens to the right of and below the one opened before it ..
    var previous = windows[windows.length - 1];
    var left = previous.left + config.cascadeOffset;
    var top = previous.top + config.cascadeOffset;

    // .. and a window that would reach past the page starts again from the edge it would cross.
    if(left + size.width > window.innerWidth - config.edgeMargin) {
        left = start.left;
    }

    if(top + size.height > window.innerHeight - config.edgeMargin) {
        top = start.top;
    }

    var out = {left: left, top: top};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.getReferenceRect = function(specWindow) {

    // The window hangs from a point of its own, which moves with every drag
    var out = {
        x: specWindow.left,
        y: specWindow.top,
        left: specWindow.left,
        right: specWindow.left,
        top: specWindow.top,
        bottom: specWindow.top,
        width: 0,
        height: 0,
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.build = function(specWindow) {

    var config = zatoApp.specification.config;
    var render = zatoApp.render;

    var element = render.createElement('div', 'app-specification');
    element.style.width = specWindow.width + config.unit;
    element.style.height = specWindow.height + config.unit;
    element.addEventListener('pointerdown', zatoApp.specification.raise.bind(null, specWindow), true);

    // The bar moves the window, with the operation's method and path in it ..
    var bar = render.createElement('div', 'app-specification-bar');
    bar.addEventListener('pointerdown', zatoApp.specification.onPointerDown.bind(null, specWindow));
    bar.addEventListener('pointermove', zatoApp.specification.onPointerMove.bind(null, specWindow));
    bar.addEventListener('pointerup', zatoApp.specification.onPointerUp.bind(null, specWindow));
    bar.addEventListener('pointercancel', zatoApp.specification.onPointerUp.bind(null, specWindow));

    var title = render.createElement('span', 'app-specification-title');

    var tools = zatoApp.panels.buildTools();
    var copyAs = render.createElement('button', 'app-tool app-specification-copy', config.copyAsText);
    copyAs.type = 'button';

    var onCloseClick = zatoApp.specification.close.bind(null, specWindow);
    var close = zatoApp.panels.buildToolButton(config.closeText, 'app-specification-close', onCloseClick);

    tools.appendChild(copyAs);
    tools.appendChild(close);

    bar.appendChild(title);
    bar.appendChild(tools);

    // .. and what goes in and what comes out below it.
    var body = render.createElement('div', 'app-specification-body');

    element.appendChild(bar);
    element.appendChild(body);

    specWindow.element = element;
    specWindow.title = title;
    specWindow.body = body;
    specWindow.copyAs = copyAs;
    specWindow.menu = zatoApp.specification.buildMenu(specWindow);

    // A size changed with the corner of the window is the size the next window opens with
    specWindow.observer = new ResizeObserver(zatoApp.specification.onResize.bind(null, specWindow));
    specWindow.observer.observe(element);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.open = function(card) {

    var config = zatoApp.specification.config;
    var state = zatoApp.specification.state;

    var size = zatoApp.specification.loadSize();
    var position = zatoApp.specification.getNextPosition(card, size);

    var specWindow = {
        entryId: card.id,
        left: position.left,
        top: position.top,
        width: size.width,
        height: size.height,
        isDragging: false,
        startX: 0,
        startY: 0,
        startLeft: 0,
        startTop: 0,
    };

    zatoApp.specification.build(specWindow);
    zatoApp.specification.fill(specWindow);

    // Each window hangs from an anchor of its own, outside the page, and is placed by its own point,
    // so neither flipping nor keeping it in view applies ..
    var anchor = document.createElement('span');

    specWindow.instance = tippy(anchor, {
        content: specWindow.element,
        trigger: 'manual',
        interactive: true,
        hideOnClick: false,
        arrow: false,
        placement: config.placement,
        offset: [0, 0],
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoApp.panels.config.bareTheme,
        zIndex: config.layer,
        animation: config.animation,
        getReferenceClientRect: zatoApp.specification.getReferenceRect.bind(null, specWindow),
        onHidden: zatoApp.specification.onHidden.bind(null, specWindow),
        popperOptions: {
            strategy: config.strategy,
            modifiers: [
                {name: 'flip', enabled: false},
                {name: 'preventOverflow', enabled: false},
            ],
        },
    });

    state.windows.push(specWindow);
    state.stacking.push(specWindow);

    // .. and a new window always opens above the ones already open.
    specWindow.instance.show();
    zatoApp.specification.restack();
    zatoApp.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.getWindow = function(entryId) {

    var windows = zatoApp.specification.state.windows;

    for(var windowIndex = 0; windowIndex < windows.length; windowIndex++) {
        var specWindow = windows[windowIndex];

        if(specWindow.entryId === entryId) {
            return specWindow;
        }
    }

    return null;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onButtonClick = function(event) {

    var card = event.currentTarget.closest(zatoApp.specification.config.cardSelector);
    var specWindow = zatoApp.specification.getWindow(card.id);

    // The button of an operation with a window open closes that window, and otherwise it opens one more
    if(specWindow === null) {
        zatoApp.specification.open(card);
    }
    else {
        zatoApp.specification.close(specWindow);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.close = function(specWindow) {

    var state = zatoApp.specification.state;

    state.windows.splice(state.windows.indexOf(specWindow), 1);
    state.stacking.splice(state.stacking.indexOf(specWindow), 1);

    specWindow.menu.hide();
    specWindow.instance.hide();

    zatoApp.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onHidden = function(specWindow) {

    // A closed window is never shown again, so nothing of it is kept once it fades out
    specWindow.observer.disconnect();
    specWindow.menu.destroy();
    specWindow.instance.destroy();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.raise = function(specWindow) {

    var stacking = zatoApp.specification.state.stacking;

    stacking.splice(stacking.indexOf(specWindow), 1);
    stacking.push(specWindow);

    zatoApp.specification.restack();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.restack = function() {

    var config = zatoApp.specification.config;
    var stacking = zatoApp.specification.state.stacking;

    // The layers are counted from the bottom window up, so they stay below the menus whatever the number of clicks
    for(var stackIndex = 0; stackIndex < stacking.length; stackIndex++) {
        var specWindow = stacking[stackIndex];
        specWindow.instance.popper.style.zIndex = config.layer + stackIndex;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onDocumentKeyDown = function(event) {

    var config = zatoApp.specification.config;
    var windows = zatoApp.specification.state.windows;

    if(event.key !== config.escapeKey) {
        return;
    }

    // Escape already used by a filter, or meant for the popover, leaves the windows as they are ..
    if(event.defaultPrevented) {
        return;
    }

    if(zatoApp.popover.state.anchor !== null) {
        return;
    }

    if(windows.length === 0) {
        return;
    }

    // .. an open menu closes before any window ..
    for(var windowIndex = 0; windowIndex < windows.length; windowIndex++) {
        var menu = windows[windowIndex].menu;

        if(menu.state.isVisible) {
            menu.hide();
            return;
        }
    }

    // .. and the windows close from the most recently opened one back to the first.
    var latest = windows[windows.length - 1];
    zatoApp.specification.close(latest);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.fill = function(specWindow) {

    var entry = zatoApp.state.entriesById[specWindow.entryId];

    var chip = zatoApp.render.createMethodChip(entry.method);
    var path = zatoApp.render.buildPath(entry.path, 'app-specification-path');

    specWindow.title.appendChild(chip);
    specWindow.title.appendChild(path);

    var fields = zatoApp.fields.build(entry.operation);
    specWindow.body.appendChild(fields);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.markButtons = function() {

    var config = zatoApp.specification.config;
    var buttons = document.querySelectorAll(config.buttonSelector);

    for(var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        var button = buttons[buttonIndex];
        var card = button.closest(config.cardSelector);
        var isOpen = zatoApp.specification.getWindow(card.id) !== null;

        button.classList.toggle(config.activeClass, isOpen);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.buildMenu = function(specWindow) {

    var config = zatoApp.specification.config;
    var menu = zatoApp.render.createElement('div', 'app-menu');

    for(var formatIndex = 0; formatIndex < config.copyFormats.length; formatIndex++) {
        var format = config.copyFormats[formatIndex];
        var item = zatoApp.render.createElement('button', 'app-menu-item', format.label);

        item.type = 'button';
        item.setAttribute(config.formatAttribute, format.name);
        item.addEventListener('click', zatoApp.specification.onCopyFormatClick.bind(null, specWindow));

        menu.appendChild(item);
    }

    // The menu is placed on the page itself, above every window, so no window's edges cut it off,
    // and its button opens and closes it
    var out = tippy(specWindow.copyAs, {
        content: menu,
        trigger: 'click',
        interactive: true,
        arrow: false,
        placement: config.menuPlacement,
        offset: config.menuOffset,
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoApp.panels.config.bareTheme,
        zIndex: config.menuLayer,
        animation: config.animation,
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onCopyFormatClick = function(specWindow, event) {

    var config = zatoApp.specification.config;

    var format = event.currentTarget.getAttribute(config.formatAttribute);
    var operation = zatoApp.state.entriesById[specWindow.entryId].operation;
    var text = '';

    if(format === config.jsonFormat) {
        text = zatoApp.fields.toJson(operation);
    }
    else {
        text = zatoApp.fields.toText(operation);
    }

    specWindow.menu.hide();
    navigator.clipboard.writeText(text).then(zatoApp.panels.showCopied.bind(null, specWindow.copyAs));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onResize = function(specWindow) {

    // A window fading out is taken out of the page and has no size of its own to keep
    if(!specWindow.element.isConnected) {
        return;
    }

    specWindow.width = specWindow.element.offsetWidth;
    specWindow.height = specWindow.element.offsetHeight;

    zatoApp.specification.saveSize(specWindow);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onPointerDown = function(specWindow, event) {

    var config = zatoApp.specification.config;

    // Only the primary button starts a drag, and the buttons in the bar keep their own clicks ..
    if(event.button !== config.primaryButton) {
        return;
    }

    if(event.target.closest('button') !== null) {
        return;
    }

    // .. no text is selected while the pointer crosses the page, and a menu open in the bar would be left behind ..
    event.preventDefault();
    specWindow.menu.hide();

    specWindow.isDragging = true;
    specWindow.startX = event.clientX;
    specWindow.startY = event.clientY;
    specWindow.startLeft = specWindow.left;
    specWindow.startTop = specWindow.top;

    // .. and capturing the pointer keeps the drag going when it leaves the bar.
    event.currentTarget.setPointerCapture(event.pointerId);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onPointerMove = function(specWindow, event) {

    if(!specWindow.isDragging) {
        return;
    }

    var requestedLeft = specWindow.startLeft + event.clientX - specWindow.startX;
    var requestedTop = specWindow.startTop + event.clientY - specWindow.startY;
    var position = zatoApp.specification.clampPosition(requestedLeft, requestedTop, specWindow.width);

    specWindow.left = position.left;
    specWindow.top = position.top;

    specWindow.instance.popperInstance.update();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.specification.onPointerUp = function(specWindow, event) {

    if(!specWindow.isDragging) {
        return;
    }

    specWindow.isDragging = false;
    event.currentTarget.releasePointerCapture(event.pointerId);

    // Only the first window open sets where the first window opens the next time, the others step off from it
    if(zatoApp.specification.state.windows[0] === specWindow) {
        zatoApp.specification.savePosition(specWindow);
    }
};

// ////////////////////////////////////////////////////////////////////////

document.addEventListener('keydown', zatoApp.specification.onDocumentKeyDown);
