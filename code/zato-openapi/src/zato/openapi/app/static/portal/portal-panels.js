zatoPortal.panels = {};

zatoPortal.panels.config = {
    svgNamespace: 'http://www.w3.org/2000/svg',
    iconViewBox: '0 0 24 24',
    playIconPath: 'M8 5v14l11-7z',
    spinnerViewBox: '0 0 50 50',
    spinnerCenter: '25',
    spinnerRadius: '20',
    playLabel: 'Invoke',
    invokingText: 'Invoking',
    rawText: 'Raw',
    copyText: 'Copy',
    copiedText: 'Copied',
    copiedPlacement: 'top',
    copiedLayer: 400,
    bareTheme: 'portal-bare',
    countClass: 'portal-chip portal-chip-neutral portal-tool-count',
    countEmptyClass: 'portal-tool-count-empty',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.createElement = function(tagName, className, text) {

    var element = document.createElement(tagName);
    element.className = className;

    if(text !== undefined) {
        element.textContent = text;
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.createSvgElement = function(tagName, attributes) {

    var element = document.createElementNS(zatoPortal.panels.config.svgNamespace, tagName);
    var names = Object.keys(attributes);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        element.setAttribute(name, attributes[name]);
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildBar = function(title) {

    var bar = zatoPortal.panels.createElement('div', 'portal-panel-bar');
    var titleElement = zatoPortal.panels.createElement('span', 'portal-panel-title', title);

    bar.appendChild(titleElement);

    return bar;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildTools = function() {
    var out = zatoPortal.panels.createElement('div', 'portal-panel-tools');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildPlayButton = function(onClick) {

    var config = zatoPortal.panels.config;

    var button = zatoPortal.panels.createElement('button', 'portal-play');
    button.type = 'button';
    button.title = config.playLabel;
    button.setAttribute('aria-label', config.playLabel);
    button.addEventListener('click', onClick);

    var icon = zatoPortal.panels.createSvgElement('svg', {'class': 'portal-play-icon', 'viewBox': config.iconViewBox});
    var shape = zatoPortal.panels.createSvgElement('path', {'d': config.playIconPath});

    icon.appendChild(shape);
    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildInvoking = function() {

    var config = zatoPortal.panels.config;

    var container = zatoPortal.panels.createElement('span', 'portal-invoking');
    container.hidden = true;

    var text = zatoPortal.panels.createElement('span', 'portal-invoking-text', config.invokingText);

    var spinner = zatoPortal.panels.createSvgElement('svg', {'class': 'portal-spinner portal-invoking-spinner', 'viewBox': config.spinnerViewBox});
    var circleAttributes = {'cx': config.spinnerCenter, 'cy': config.spinnerCenter, 'r': config.spinnerRadius};

    var track = zatoPortal.panels.createSvgElement('circle', circleAttributes);
    track.setAttribute('class', 'portal-spinner-track');

    var arc = zatoPortal.panels.createSvgElement('circle', circleAttributes);
    arc.setAttribute('class', 'portal-spinner-arc');

    spinner.appendChild(track);
    spinner.appendChild(arc);

    container.appendChild(text);
    container.appendChild(spinner);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildToolButton = function(text, className, onClick) {

    var button = zatoPortal.panels.createElement('button', 'portal-tool ' + className, text);
    button.type = 'button';
    button.addEventListener('click', onClick);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.setCount = function(button, count) {

    var config = zatoPortal.panels.config;
    var chip = button.querySelector('.portal-tool-count');

    if(chip === null) {
        chip = zatoPortal.panels.createElement('span', config.countClass);
        button.appendChild(chip);
    }

    // A count is shown only when there is something to count, and it keeps its place either way,
    // so the button never changes its width
    chip.textContent = String(count);
    chip.classList.toggle(config.countEmptyClass, count === 0);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildRawSwitch = function(onChange) {

    var config = zatoPortal.panels.config;

    var label = zatoPortal.panels.createElement('label', 'portal-switch');

    var input = zatoPortal.panels.createElement('input', 'portal-switch-input');
    input.type = 'checkbox';
    input.addEventListener('change', onChange);

    var track = zatoPortal.panels.createElement('span', 'portal-switch-track');
    var text = zatoPortal.panels.createElement('span', 'portal-switch-text', config.rawText);

    label.appendChild(input);
    label.appendChild(track);
    label.appendChild(text);

    return label;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.buildCopyButton = function(getText, text) {

    var button = zatoPortal.panels.createElement('button', 'portal-copy', text);
    button.type = 'button';

    button.addEventListener('click', zatoPortal.panels.onCopyClick.bind(null, getText));

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.onCopyClick = function(getText, event) {

    var button = event.currentTarget;
    var text = getText(button);

    navigator.clipboard.writeText(text).then(zatoPortal.panels.showCopied.bind(null, button));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.panels.showCopied = function(button) {

    var config = zatoPortal.panels.config;

    // The tooltip is placed on the page itself, above the button it confirms, so no panel that scrolls
    // or clips its content cuts it off, and its anchor is an element of its own, which leaves the button
    // free for a menu ..
    var anchor = document.createElement('span');
    var tooltip = zatoPortal.panels.createElement('span', 'portal-copy-tooltip', config.copiedText);

    var instance = tippy(anchor, {
        content: tooltip,
        trigger: 'manual',
        placement: config.copiedPlacement,
        arrow: false,
        duration: 0,
        appendTo: document.body,
        theme: config.bareTheme,
        zIndex: config.copiedLayer,
        getReferenceClientRect: button.getBoundingClientRect.bind(button),
    });

    // .. and it removes itself once it has faded.
    tooltip.addEventListener('animationend', instance.destroy.bind(instance));
    instance.show();
};
