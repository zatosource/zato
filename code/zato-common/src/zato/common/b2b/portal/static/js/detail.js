'use strict';

// The details of one item, shown in the lower pane of a listing - its tabs, the state its chips show,
// the syntax colors of its XML blocks, the copying of these blocks and the tippy of what is kept apart from the tabs.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var detail = {};

detail.config = {
    copiedLabel: 'Copied to clipboard',
    copiedDuration: 600,

    // The confirmation of a copy opens away from what was copied - to the left of a document's button,
    // to the right of a value's chip
    copyButtonPlacement: 'left',
    copyChipPlacement: 'right',
    copyChipLabel: 'Copy',
    copiedTheme: 'copied',

    // The values of these blocks of the details tippy offer a chip that copies them
    copyChipCells: '.table td, .fields dd',

    // What is kept apart from the tabs opens over the listing, clear of the pane that is being read.
    // The theme only names the tippy for Escape, its look is the default one.
    detailsTheme: 'details',
    detailsPlacement: 'top-start',
    detailsModifiers: [
        {name: 'flip', enabled: false},
        {name: 'preventOverflow', options: {altAxis: true, padding: 8}}
    ]
};

// ////////////////////////////////////////////////////////////////////////

detail.showTab = function(pane, key) {

    var tabs = pane.querySelectorAll('.tab');
    var panels = pane.querySelectorAll('.tab-panel');

    for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
        var tab = tabs[tabIndex];
        tab.classList.toggle('tab-active', tab.getAttribute('data-tab') === key);
    }

    // The link to what is kept apart from the tabs leads back to the tab that is open
    var link = pane.querySelector('.details-open');

    if (link !== null) {
        link.href = portal.selection.address(pane.getAttribute('data-id'), true);
    }

    for (var panelIndex = 0; panelIndex < panels.length; panelIndex++) {
        var panel = panels[panelIndex];
        panel.hidden = panel.getAttribute('data-tab-panel') !== key;
    }
};

// ////////////////////////////////////////////////////////////////////////

detail.initTabs = function(pane) {

    var tabs = pane.querySelectorAll('.tab');

    var onClick = function(event) {
        detail.showTab(pane, event.currentTarget.getAttribute('data-tab'));
        portal.selection.writeAddress(pane.getAttribute('data-id'), false);
    };

    for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
        tabs[tabIndex].addEventListener('click', onClick);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The chips of the state say the text the action gives, which names the state in words of its own.
detail.setState = function(pane, text, tone) {

    var pills = pane.querySelectorAll('[data-role="state"]');

    for (var pillIndex = 0; pillIndex < pills.length; pillIndex++) {

        var pill = pills[pillIndex];

        pill.textContent = text;
        pill.className = 'pill portal-tone-' + tone;
        pill.removeAttribute('data-tip');

        // A tip described the state the pill had before
        if (pill._tippy) {
            pill._tippy.destroy();
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

detail.appendToken = function(parent, className, text) {
    parent.appendChild(portal.create('span', className, text));
};

// ////////////////////////////////////////////////////////////////////////

// Colors one tag - its name, the names and the values of its attributes, and its angle brackets.
detail.highlightTag = function(parent, tag) {

    var parts = /^(<\/?)([^\s/>]+)([\s\S]*?)(\/?>)$/.exec(tag);
    var attributePattern = /([^\s=]+)(=)("[^"]*")/g;

    detail.appendToken(parent, 'code-punctuation', parts[1]);
    detail.appendToken(parent, 'code-tag', parts[2]);

    var attributes = parts[3];
    var position = 0;
    var match = attributePattern.exec(attributes);

    while (match !== null) {
        parent.appendChild(document.createTextNode(attributes.slice(position, match.index)));
        detail.appendToken(parent, 'code-attribute', match[1]);
        detail.appendToken(parent, 'code-punctuation', match[2]);
        detail.appendToken(parent, 'code-value', match[3]);
        position = match.index + match[0].length;
        match = attributePattern.exec(attributes);
    }

    parent.appendChild(document.createTextNode(attributes.slice(position)));
    detail.appendToken(parent, 'code-punctuation', parts[4]);
};

// ////////////////////////////////////////////////////////////////////////

detail.appendXml = function(parent, text) {

    var pieces = text.split(/(<[^>]+>)/);

    for (var pieceIndex = 0; pieceIndex < pieces.length; pieceIndex++) {

        var piece = pieces[pieceIndex];

        if (piece.charAt(0) === '<') {
            detail.highlightTag(parent, piece);
        }
        else {
            parent.appendChild(document.createTextNode(piece));
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

detail.highlight = function(block) {

    var fragment = document.createDocumentFragment();
    detail.appendXml(fragment, block.textContent);

    block.textContent = '';
    block.appendChild(fragment);
};

// ////////////////////////////////////////////////////////////////////////

detail.initCode = function(pane) {

    var blocks = pane.querySelectorAll('.code');

    for (var blockIndex = 0; blockIndex < blocks.length; blockIndex++) {
        detail.highlight(blocks[blockIndex]);
    }

    var buttons = pane.querySelectorAll('.copy-button');

    for (var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        buttons[buttonIndex].addEventListener('click', detail.onCopy);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The value under a mouse pointer takes a chip right after its text, which copies the value.
detail.initCopyChips = function(root) {

    var chip = portal.create('button', 'copy-chip', '');
    var holder = portal.create('span', 'copy-chip-holder', '');
    var current = null;

    chip.type = 'button';
    chip.setAttribute('data-label', detail.config.copyChipLabel);
    holder.appendChild(chip);

    chip.addEventListener('click', function(event) {

        event.stopPropagation();

        var text = current.innerText.trim();

        window.navigator.clipboard.writeText(text).then(function() {
            detail.confirmCopy(chip, detail.config.copyChipPlacement);
        });
    });

    root.addEventListener('pointerover', function(event) {

        if (event.pointerType !== 'mouse') {
            return;
        }

        var cell = event.target.closest(detail.config.copyChipCells);

        if (cell === null) {
            return;
        }

        if (cell === current) {
            return;
        }

        current = cell;
        cell.appendChild(holder);
    });

    root.addEventListener('pointerleave', function() {
        current = null;
        holder.remove();
    });
};

// ////////////////////////////////////////////////////////////////////////

detail.onCopy = function(event) {

    var button = event.currentTarget;
    var text = button.parentElement.querySelector('.code').textContent;

    window.navigator.clipboard.writeText(text).then(function() {
        detail.confirmCopy(button, detail.config.copyButtonPlacement);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The control confirms the copy in a default tippy of its own for a moment, then the tippy is gone.
detail.confirmCopy = function(control, placement) {

    var instance = window.tippy(control, {
        content: detail.config.copiedLabel,
        trigger: 'manual',
        theme: detail.config.copiedTheme,
        placement: placement,
        appendTo: document.body
    });

    instance.show();

    window.setTimeout(function() {
        instance.destroy();
    }, detail.config.copiedDuration);
};

// ////////////////////////////////////////////////////////////////////////

// The tabs of the popover only switch what it shows, the address stays with the tabs of the pane.
detail.initDetailsTabs = function(root) {

    var tabs = root.querySelectorAll('.tab');

    var onClick = function(event) {
        detail.showTab(root, event.currentTarget.getAttribute('data-tab'));
    };

    for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
        tabs[tabIndex].addEventListener('click', onClick);
    }
};

// ////////////////////////////////////////////////////////////////////////

// What is kept apart from the tabs opens in a tippy of tabs of its own, built anew each time it opens.
// The link to it has an address of its own, and the address names the tippy for as long as it is open.
detail.initDetails = function(pane) {

    var link = pane.querySelector('.details-open');

    if (link === null) {
        return;
    }

    var itemId = pane.getAttribute('data-id');
    var source = pane.querySelector('.details-source');

    link.addEventListener('click', function(event) {
        event.preventDefault();
    });

    window.tippy(link, {
        content: '',
        trigger: 'click',
        interactive: true,
        hideOnClick: true,
        arrow: false,
        theme: detail.config.detailsTheme,
        placement: detail.config.detailsPlacement,
        maxWidth: 'none',
        appendTo: document.body,
        popperOptions: {modifiers: detail.config.detailsModifiers},
        onShow: function(instance) {
            instance.setContent(detail.buildDetails(source, instance));
        },
        onShown: function() {
            portal.selection.writeAddress(itemId, true);
        },
        onHidden: function(instance) {
            instance.setContent('');
            if (portal.selection.current === itemId) {
                portal.selection.writeAddress(itemId, false);
            }
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

detail.buildDetails = function(source, instance) {

    var root = source.content.firstElementChild.cloneNode(true);
    var close = portal.create('button', 'details-close', '');

    close.type = 'button';
    close.addEventListener('click', function() {
        instance.hide();
    });
    root.appendChild(close);

    detail.initDetailsTabs(root);
    detail.initCode(root);
    detail.initCopyChips(root);
    portal.tooltips.attach(root);

    return root;
};

// ////////////////////////////////////////////////////////////////////////

// Opens what is kept apart from the tabs, as an address that names it asks for.
detail.openDetails = function(pane) {

    var link = pane.querySelector('.details-open');

    // An address may name details for an item that keeps nothing apart
    if (link === null) {
        return;
    }

    link._tippy.show();
};

// ////////////////////////////////////////////////////////////////////////

detail.init = function(pane) {
    detail.initTabs(pane);
    detail.initCode(pane);
    detail.initDetails(pane);
};

// ////////////////////////////////////////////////////////////////////////

portal.detail = detail;

// ////////////////////////////////////////////////////////////////////////

})();
