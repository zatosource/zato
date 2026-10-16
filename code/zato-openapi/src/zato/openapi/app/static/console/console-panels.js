zatoConsole.panels = {};

zatoConsole.panels.config = {
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
    bareTheme: 'console-bare',
    countClass: 'console-chip console-chip-neutral console-tool-count',
    countEmptyClass: 'console-tool-count-empty',
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.createElement = function(tagName, className, text) {

    var element = document.createElement(tagName);
    element.className = className;

    if(text !== undefined) {
        element.textContent = text;
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.createSvgElement = function(tagName, attributes) {

    var element = document.createElementNS(zatoConsole.panels.config.svgNamespace, tagName);
    var names = Object.keys(attributes);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        element.setAttribute(name, attributes[name]);
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildBar = function(title) {

    var bar = zatoConsole.panels.createElement('div', 'console-panel-bar');
    var titleElement = zatoConsole.panels.createElement('span', 'console-panel-title', title);

    bar.appendChild(titleElement);

    return bar;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildTools = function() {
    var out = zatoConsole.panels.createElement('div', 'console-panel-tools');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildPlayButton = function(onClick) {

    var config = zatoConsole.panels.config;

    var button = zatoConsole.panels.createElement('button', 'console-play');
    button.type = 'button';
    button.title = config.playLabel;
    button.setAttribute('aria-label', config.playLabel);
    button.addEventListener('click', onClick);

    var icon = zatoConsole.panels.createSvgElement('svg', {'class': 'console-play-icon', 'viewBox': config.iconViewBox});
    var shape = zatoConsole.panels.createSvgElement('path', {'d': config.playIconPath});

    icon.appendChild(shape);
    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildInvoking = function() {

    var config = zatoConsole.panels.config;

    var container = zatoConsole.panels.createElement('span', 'console-invoking');
    container.hidden = true;

    var text = zatoConsole.panels.createElement('span', 'console-invoking-text', config.invokingText);

    var spinner = zatoConsole.panels.createSvgElement('svg', {'class': 'console-spinner console-invoking-spinner', 'viewBox': config.spinnerViewBox});
    var circleAttributes = {'cx': config.spinnerCenter, 'cy': config.spinnerCenter, 'r': config.spinnerRadius};

    var track = zatoConsole.panels.createSvgElement('circle', circleAttributes);
    track.setAttribute('class', 'console-spinner-track');

    var arc = zatoConsole.panels.createSvgElement('circle', circleAttributes);
    arc.setAttribute('class', 'console-spinner-arc');

    spinner.appendChild(track);
    spinner.appendChild(arc);

    container.appendChild(text);
    container.appendChild(spinner);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildToolButton = function(text, className, onClick) {

    var button = zatoConsole.panels.createElement('button', 'console-tool ' + className, text);
    button.type = 'button';
    button.addEventListener('click', onClick);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.setCount = function(button, count) {

    var config = zatoConsole.panels.config;
    var chip = button.querySelector('.console-tool-count');

    if(chip === null) {
        chip = zatoConsole.panels.createElement('span', config.countClass);
        button.appendChild(chip);
    }

    // A count is shown only when there is something to count, and it keeps its place either way,
    // so the button never changes its width
    chip.textContent = String(count);
    chip.classList.toggle(config.countEmptyClass, count === 0);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildRawSwitch = function(onChange) {

    var config = zatoConsole.panels.config;

    var label = zatoConsole.panels.createElement('label', 'console-switch');

    var input = zatoConsole.panels.createElement('input', 'console-switch-input');
    input.type = 'checkbox';
    input.addEventListener('change', onChange);

    var track = zatoConsole.panels.createElement('span', 'console-switch-track');
    var text = zatoConsole.panels.createElement('span', 'console-switch-text', config.rawText);

    label.appendChild(input);
    label.appendChild(track);
    label.appendChild(text);

    return label;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.buildCopyButton = function(getText, text) {

    var button = zatoConsole.panels.createElement('button', 'console-copy', text);
    button.type = 'button';

    button.addEventListener('click', zatoConsole.panels.onCopyClick.bind(null, getText));

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.onCopyClick = function(getText, event) {

    var button = event.currentTarget;
    var text = getText(button);

    navigator.clipboard.writeText(text).then(zatoConsole.panels.showCopied.bind(null, button));
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.panels.showCopied = function(button) {

    var config = zatoConsole.panels.config;

    // The tooltip is placed on the page itself, above the button it confirms, so no panel that scrolls
    // or clips its content cuts it off, and its anchor is an element of its own, which leaves the button
    // free for a menu ..
    var anchor = document.createElement('span');
    var tooltip = zatoConsole.panels.createElement('span', 'console-copy-tooltip', config.copiedText);

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
