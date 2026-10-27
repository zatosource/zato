zatoApp.panels = {};

zatoApp.panels.config = {
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
    bareTheme: 'app-bare',
    countClass: 'app-chip app-chip-neutral app-tool-count',
    countEmptyClass: 'app-tool-count-empty',
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.createElement = function(tagName, className, text) {

    var element = document.createElement(tagName);
    element.className = className;

    if(text !== undefined) {
        element.textContent = text;
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.createSvgElement = function(tagName, attributes) {

    var element = document.createElementNS(zatoApp.panels.config.svgNamespace, tagName);
    var names = Object.keys(attributes);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];
        element.setAttribute(name, attributes[name]);
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildBar = function(title) {

    var bar = zatoApp.panels.createElement('div', 'app-panel-bar');
    var titleElement = zatoApp.panels.createElement('span', 'app-panel-title', title);

    bar.appendChild(titleElement);

    return bar;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildTools = function() {
    var out = zatoApp.panels.createElement('div', 'app-panel-tools');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildPlayButton = function(onClick) {

    var config = zatoApp.panels.config;

    var button = zatoApp.panels.createElement('button', 'app-play');
    button.type = 'button';
    button.title = config.playLabel;
    button.setAttribute('aria-label', config.playLabel);
    button.addEventListener('click', onClick);

    var icon = zatoApp.panels.createSvgElement('svg', {'class': 'app-play-icon', 'viewBox': config.iconViewBox});
    var shape = zatoApp.panels.createSvgElement('path', {'d': config.playIconPath});

    icon.appendChild(shape);
    button.appendChild(icon);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildInvoking = function() {

    var config = zatoApp.panels.config;

    var container = zatoApp.panels.createElement('span', 'app-invoking');
    container.hidden = true;

    var text = zatoApp.panels.createElement('span', 'app-invoking-text', config.invokingText);

    var spinner = zatoApp.panels.createSvgElement('svg', {'class': 'app-spinner app-invoking-spinner', 'viewBox': config.spinnerViewBox});
    var circleAttributes = {'cx': config.spinnerCenter, 'cy': config.spinnerCenter, 'r': config.spinnerRadius};

    var track = zatoApp.panels.createSvgElement('circle', circleAttributes);
    track.setAttribute('class', 'app-spinner-track');

    var arc = zatoApp.panels.createSvgElement('circle', circleAttributes);
    arc.setAttribute('class', 'app-spinner-arc');

    spinner.appendChild(track);
    spinner.appendChild(arc);

    container.appendChild(text);
    container.appendChild(spinner);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildToolButton = function(text, className, onClick) {

    var button = zatoApp.panels.createElement('button', 'app-tool ' + className, text);
    button.type = 'button';
    button.addEventListener('click', onClick);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.setCount = function(button, count) {

    var config = zatoApp.panels.config;
    var chip = button.querySelector('.app-tool-count');

    if(chip === null) {
        chip = zatoApp.panels.createElement('span', config.countClass);
        button.appendChild(chip);
    }

    // A count is shown only when there is something to count, and it keeps its place either way,
    // so the button never changes its width
    chip.textContent = String(count);
    chip.classList.toggle(config.countEmptyClass, count === 0);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildRawSwitch = function(onChange) {

    var config = zatoApp.panels.config;

    var label = zatoApp.panels.createElement('label', 'app-switch');

    var input = zatoApp.panels.createElement('input', 'app-switch-input');
    input.type = 'checkbox';
    input.addEventListener('change', onChange);

    var track = zatoApp.panels.createElement('span', 'app-switch-track');
    var text = zatoApp.panels.createElement('span', 'app-switch-text', config.rawText);

    label.appendChild(input);
    label.appendChild(track);
    label.appendChild(text);

    return label;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.buildCopyButton = function(getText, text) {

    var button = zatoApp.panels.createElement('button', 'app-copy', text);
    button.type = 'button';

    button.addEventListener('click', zatoApp.panels.onCopyClick.bind(null, getText));

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.onCopyClick = function(getText, event) {

    var button = event.currentTarget;
    var text = getText(button);

    navigator.clipboard.writeText(text).then(zatoApp.panels.showCopied.bind(null, button));
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.panels.showCopied = function(button) {

    var config = zatoApp.panels.config;

    // The tooltip is placed on the page itself, above the button it confirms, so no panel that scrolls
    // or clips its content cuts it off, and its anchor is an element of its own, which leaves the button
    // free for a menu ..
    var anchor = document.createElement('span');
    var tooltip = zatoApp.panels.createElement('span', 'app-copy-tooltip', config.copiedText);

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
