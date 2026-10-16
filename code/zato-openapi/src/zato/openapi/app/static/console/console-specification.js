zatoConsole.specification = {};

zatoConsole.specification.config = {
    storageKey: 'zato.openapi.console.specification.window',
    cardSelector: '.console-operation',
    headerSelector: '.console-header',
    buttonSelector: '.console-tool-specification',
    activeClass: 'console-tool-active',
    placement: 'bottom-start',
    animation: 'fade',
    strategy: 'fixed',
    layer: 200,
    defaultWidth: 560,
    defaultHeight: 520,
    edgeMargin: 16,
    minimumVisible: 64,
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

zatoConsole.specification.state = {
    instance: null,
    menu: null,
    element: null,
    title: null,
    body: null,
    copyAs: null,
    entryId: '',
    left: 0,
    top: 0,
    width: 0,
    height: 0,
    isDragging: false,
    startX: 0,
    startY: 0,
    startLeft: 0,
    startTop: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.load = function() {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;

    // localStorage returns null for a key that was never stored, and the window then opens at the top right of the page
    var stored = localStorage.getItem(config.storageKey);

    if(stored !== null) {
        var geometry = JSON.parse(stored);

        state.left = geometry.left;
        state.top = geometry.top;
        state.width = geometry.width;
        state.height = geometry.height;
        return;
    }

    var header = document.querySelector(config.headerSelector);
    var headerBottom = header.getBoundingClientRect().bottom;

    state.width = config.defaultWidth;
    state.height = config.defaultHeight;
    state.left = window.innerWidth - config.defaultWidth - config.edgeMargin;
    state.top = headerBottom + config.edgeMargin;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.save = function() {

    var state = zatoConsole.specification.state;
    var geometry = {left: state.left, top: state.top, width: state.width, height: state.height};

    localStorage.setItem(zatoConsole.specification.config.storageKey, JSON.stringify(geometry));
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.getReferenceRect = function() {

    var state = zatoConsole.specification.state;

    // The window hangs from a point of its own, which moves with every drag
    var out = {
        x: state.left,
        y: state.top,
        left: state.left,
        right: state.left,
        top: state.top,
        bottom: state.top,
        width: 0,
        height: 0,
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.build = function() {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;
    var render = zatoConsole.render;

    var element = render.createElement('div', 'console-specification');
    element.style.width = state.width + config.unit;
    element.style.height = state.height + config.unit;

    // The bar moves the window, with the operation's method and path in it ..
    var bar = render.createElement('div', 'console-specification-bar');
    bar.addEventListener('pointerdown', zatoConsole.specification.onPointerDown);
    bar.addEventListener('pointermove', zatoConsole.specification.onPointerMove);
    bar.addEventListener('pointerup', zatoConsole.specification.onPointerUp);
    bar.addEventListener('pointercancel', zatoConsole.specification.onPointerUp);

    var title = render.createElement('span', 'console-specification-title');

    var tools = zatoConsole.panels.buildTools();
    var copyAs = render.createElement('button', 'console-tool console-specification-copy', config.copyAsText);
    copyAs.type = 'button';

    var close = zatoConsole.panels.buildToolButton(config.closeText, 'console-specification-close', zatoConsole.specification.hide);

    tools.appendChild(copyAs);
    tools.appendChild(close);

    bar.appendChild(title);
    bar.appendChild(tools);

    // .. and what goes in and what comes out below it.
    var body = render.createElement('div', 'console-specification-body');

    element.appendChild(bar);
    element.appendChild(body);

    state.element = element;
    state.title = title;
    state.body = body;
    state.copyAs = copyAs;
    state.menu = zatoConsole.specification.buildMenu(copyAs);

    // A size changed with the corner of the window is the size it opens with the next time
    var observer = new ResizeObserver(zatoConsole.specification.onResize);
    observer.observe(element);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.create = function() {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;

    zatoConsole.specification.load();
    zatoConsole.specification.build();

    // The window is placed by its own point rather than next to a button, so neither flipping nor keeping it in view applies
    state.instance = tippy(document.body, {
        content: state.element,
        trigger: 'manual',
        interactive: true,
        hideOnClick: false,
        arrow: false,
        placement: config.placement,
        offset: [0, 0],
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoConsole.panels.config.bareTheme,
        zIndex: config.layer,
        animation: config.animation,
        getReferenceClientRect: zatoConsole.specification.getReferenceRect,
        popperOptions: {
            strategy: config.strategy,
            modifiers: [
                {name: 'flip', enabled: false},
                {name: 'preventOverflow', enabled: false},
            ],
        },
    });
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.isVisible = function() {

    var instance = zatoConsole.specification.state.instance;

    if(instance === null) {
        return false;
    }

    var out = instance.state.isVisible;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onButtonClick = function(event) {

    var state = zatoConsole.specification.state;
    var card = event.currentTarget.closest(zatoConsole.specification.config.cardSelector);

    // The button of the operation already shown closes the window, and any other one opens it with its own operation
    if(zatoConsole.specification.isVisible()) {
        if(state.entryId === card.id) {
            zatoConsole.specification.hide();
            return;
        }
    }

    if(state.instance === null) {
        zatoConsole.specification.create();
    }

    state.instance.show();
    zatoConsole.specification.fill(card.id);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.hide = function() {

    var state = zatoConsole.specification.state;

    state.menu.hide();
    state.instance.hide();

    zatoConsole.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.follow = function(entryId) {

    // An open window always shows the operation shown in the console
    if(zatoConsole.specification.isVisible()) {
        zatoConsole.specification.fill(entryId);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.fill = function(entryId) {

    var state = zatoConsole.specification.state;
    var entry = zatoConsole.state.entriesById[entryId];

    var chip = zatoConsole.render.createMethodChip(entry.method);
    var path = zatoConsole.render.buildPath(entry.path, 'console-specification-path');

    state.title.textContent = '';
    state.title.appendChild(chip);
    state.title.appendChild(path);

    var fields = zatoConsole.fields.build(entry.operation);

    state.entryId = entryId;
    state.body.textContent = '';
    state.body.appendChild(fields);
    state.body.scrollTop = 0;

    zatoConsole.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.markButtons = function() {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;
    var isVisible = zatoConsole.specification.isVisible();
    var buttons = document.querySelectorAll(config.buttonSelector);

    for(var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        var button = buttons[buttonIndex];
        var card = button.closest(config.cardSelector);

        button.classList.toggle(config.activeClass, isVisible && card.id === state.entryId);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.buildMenu = function(button) {

    var config = zatoConsole.specification.config;
    var menu = zatoConsole.render.createElement('div', 'console-menu');

    for(var formatIndex = 0; formatIndex < config.copyFormats.length; formatIndex++) {
        var format = config.copyFormats[formatIndex];
        var item = zatoConsole.render.createElement('button', 'console-menu-item', format.label);

        item.type = 'button';
        item.setAttribute(config.formatAttribute, format.name);
        item.addEventListener('click', zatoConsole.specification.onCopyFormatClick);

        menu.appendChild(item);
    }

    // The menu is placed on the page itself, above the window, so the window's edges never cut it off,
    // and its button opens and closes it
    var out = tippy(button, {
        content: menu,
        trigger: 'click',
        interactive: true,
        arrow: false,
        placement: config.menuPlacement,
        offset: config.menuOffset,
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoConsole.panels.config.bareTheme,
        zIndex: config.menuLayer,
        animation: config.animation,
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onCopyFormatClick = function(event) {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;

    var format = event.currentTarget.getAttribute(config.formatAttribute);
    var operation = zatoConsole.state.entriesById[state.entryId].operation;
    var text = '';

    if(format === config.jsonFormat) {
        text = zatoConsole.fields.toJson(operation);
    }
    else {
        text = zatoConsole.fields.toText(operation);
    }

    state.menu.hide();
    navigator.clipboard.writeText(text).then(zatoConsole.panels.showCopied.bind(null, state.copyAs));
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onResize = function() {

    var state = zatoConsole.specification.state;

    // A hidden window is taken out of the page and has no size of its own to keep
    if(!state.element.isConnected) {
        return;
    }

    state.width = state.element.offsetWidth;
    state.height = state.element.offsetHeight;

    zatoConsole.specification.save();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onPointerDown = function(event) {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;

    // Only the primary button starts a drag, and the buttons in the bar keep their own clicks ..
    if(event.button !== config.primaryButton) {
        return;
    }

    if(event.target.closest('button') !== null) {
        return;
    }

    // .. no text is selected while the pointer crosses the page, and a menu open in the bar would be left behind ..
    event.preventDefault();
    state.menu.hide();

    state.isDragging = true;
    state.startX = event.clientX;
    state.startY = event.clientY;
    state.startLeft = state.left;
    state.startTop = state.top;

    // .. and capturing the pointer keeps the drag going when it leaves the bar.
    event.currentTarget.setPointerCapture(event.pointerId);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onPointerMove = function(event) {

    var config = zatoConsole.specification.config;
    var state = zatoConsole.specification.state;

    if(!state.isDragging) {
        return;
    }

    var requestedLeft = state.startLeft + event.clientX - state.startX;
    var requestedTop = state.startTop + event.clientY - state.startY;

    // The bar never leaves the page, so the window can always be dragged back
    var leftMinimum = config.minimumVisible - state.width;
    var leftMaximum = window.innerWidth - config.minimumVisible;
    var topMaximum = window.innerHeight - config.minimumVisible;

    state.left = Math.min(leftMaximum, Math.max(leftMinimum, requestedLeft));
    state.top = Math.min(topMaximum, Math.max(0, requestedTop));

    state.instance.popperInstance.update();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.specification.onPointerUp = function(event) {

    var state = zatoConsole.specification.state;

    if(!state.isDragging) {
        return;
    }

    state.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    zatoConsole.specification.save();
};
