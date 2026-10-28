'use strict';

// The actions of an item stand as links beside its state in its details, a switch in a row moves its item between
// two states, and Ctrl and the comma open a command palette with the actions of the selected item, the one adding
// a new item and the other sections.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var actions = {};

actions.config = {
    paletteKey: ',',
    goToPrefix: 'Go to ',
    activeCommandClass: 'palette-item-active'
};

// ////////////////////////////////////////////////////////////////////////

actions.selection = function() {
    var out = portal.selection;
    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Command palette
// ////////////////////////////////////////////////////////////////////////

// The commands of the palette - the actions of the selected item, adding a new item, and the other sections.
actions.commands = function() {

    var out = [];
    var selection = actions.selection();

    if (selection.current !== null) {

        var itemId = selection.current;
        var sources = selection.sources(itemId);
        var title = selection.panes[itemId].querySelector('.detail-title').textContent;

        for (var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {
            out.push({
                label: sources[sourceIndex].textContent,
                note: title,
                run: selection.runAction.bind(null, itemId, sources[sourceIndex])
            });
        }
    }

    var split = document.getElementById('split');

    if (split.hasAttribute('data-new-href')) {
        out.push({label: split.getAttribute('data-new-label'), note: '', href: split.getAttribute('data-new-href')});
    }

    var entries = portal.readData('navigation-data');

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        if (!entries[entryIndex].is_active) {
            out.push({label: actions.config.goToPrefix + entries[entryIndex].label, note: '', href: entries[entryIndex].href});
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

actions.runCommand = function(command) {

    actions.closePalette();

    if (command.href) {
        window.location.href = command.href;
        return;
    }

    command.run();
};

// ////////////////////////////////////////////////////////////////////////

actions.closePalette = function() {

    var backdrop = document.querySelector('.palette-backdrop');

    if (backdrop) {
        backdrop.remove();
    }
};

// ////////////////////////////////////////////////////////////////////////

actions.openPalette = function() {

    actions.closePalette();

    var commands = actions.commands();
    var shown = [];
    var active = 0;

    var backdrop = portal.create('div', 'palette-backdrop', '');
    var palette = portal.create('div', 'palette', '');
    var input = portal.create('input', 'palette-input', '');
    var list = portal.create('div', 'palette-list', '');

    input.type = 'text';
    input.autocomplete = 'off';
    input.spellcheck = false;

    var render = function() {

        var text = input.value.trim().toLowerCase();

        shown = [];
        list.textContent = '';

        for (var commandIndex = 0; commandIndex < commands.length; commandIndex++) {
            if (commands[commandIndex].label.toLowerCase().indexOf(text) !== -1) {
                shown.push(commands[commandIndex]);
            }
        }

        active = Math.min(active, shown.length - 1);

        for (var shownIndex = 0; shownIndex < shown.length; shownIndex++) {

            var className = shownIndex === active ? 'palette-item ' + actions.config.activeCommandClass : 'palette-item';
            var item = portal.create('button', className, '');

            item.type = 'button';
            item.appendChild(portal.create('span', 'palette-label', shown[shownIndex].label));
            item.appendChild(portal.create('span', 'palette-note portal-mono', shown[shownIndex].note));
            item.addEventListener('click', actions.runCommand.bind(null, shown[shownIndex]));

            list.appendChild(item);
        }
    };

    input.addEventListener('input', function() {
        active = 0;
        render();
    });

    input.addEventListener('keydown', function(event) {

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            active = Math.min(active + 1, shown.length - 1);
            render();
        }
        else if (event.key === 'ArrowUp') {
            event.preventDefault();
            active = Math.max(active - 1, 0);
            render();
        }
        else if (event.key === 'Enter') {
            if (shown.length) {
                actions.runCommand(shown[active]);
            }
        }
        else if (event.key === 'Escape') {
            event.stopPropagation();
            actions.closePalette();
        }
    });

    // A press on the backdrop around the palette closes it
    backdrop.addEventListener('mousedown', function(event) {
        if (event.target === backdrop) {
            actions.closePalette();
        }
    });

    palette.appendChild(input);
    palette.appendChild(list);
    backdrop.appendChild(palette);
    document.body.appendChild(backdrop);

    render();
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

actions.initPalette = function() {

    document.addEventListener('keydown', function(event) {

        if (event.key !== actions.config.paletteKey) {
            return;
        }

        if (event.ctrlKey) {
            event.preventDefault();
            actions.openPalette();
            return;
        }

        if (event.metaKey) {
            event.preventDefault();
            actions.openPalette();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////
// Links beside the state
// ////////////////////////////////////////////////////////////////////////

actions.addInline = function(itemId, pane) {

    var pill = pane.querySelector('.fields [data-role="state"]');
    var sources = actions.selection().sources(itemId);
    var host = portal.create('span', 'inline-actions', '');

    for (var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {

        var source = sources[sourceIndex];
        var className = source.hasAttribute('data-danger') ? 'link link-danger' : 'link';
        var link = portal.create('button', className, source.textContent);

        link.type = 'button';
        link.setAttribute('data-action', source.getAttribute('data-action'));
        link.addEventListener('click', actions.selection().runAction.bind(null, itemId, source));

        host.appendChild(link);
    }

    pill.closest('dd').appendChild(host);
};

// ////////////////////////////////////////////////////////////////////////
// The box tinted in the color of the state
// ////////////////////////////////////////////////////////////////////////

actions.fillBox = function(itemId, pane) {

    var host = pane.querySelector('.status-box-buttons');
    var sources = actions.selection().sources(itemId);

    host.textContent = '';

    for (var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {
        host.appendChild(actions.createButton(itemId, sources[sourceIndex]));
    }
};

// ////////////////////////////////////////////////////////////////////////
// The toolbar over the selected row
// ////////////////////////////////////////////////////////////////////////

actions.closeContextual = function() {
    if (actions.contextual) {
        actions.contextual.destroy();
        actions.contextual = null;
    }
};

// ////////////////////////////////////////////////////////////////////////

actions.openContextual = function(itemId) {

    actions.closeContextual();

    var sources = actions.selection().sources(itemId);

    if (sources.length === 0) {
        return;
    }

    var toolbar = portal.create('div', 'contextual-toolbar', '');

    for (var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {
        toolbar.appendChild(actions.createButton(itemId, sources[sourceIndex]));
    }

    actions.contextual = window.tippy(actions.selection().row(itemId), {
        content: toolbar,
        trigger: 'manual',
        interactive: true,
        hideOnClick: false,
        arrow: false,
        animation: false,
        theme: actions.config.menuTheme,
        placement: actions.config.contextualPlacement,
        offset: actions.config.contextualOffset,
        maxWidth: 'none',
        appendTo: document.body
    });

    actions.contextual.show();
};

// ////////////////////////////////////////////////////////////////////////
// Switches in the rows
// ////////////////////////////////////////////////////////////////////////

actions.initToggle = function() {

    var switches = document.querySelectorAll('.row-switch');

    var onChange = function(event) {

        var input = event.currentTarget;
        var row = input.closest('tr');
        var prefix = input.checked ? 'data-on-' : 'data-off-';

        // The switch runs the change of state as any other source of an action would
        var source = portal.create('button', '', '');
        source.setAttribute('data-action', 'set-state');
        source.setAttribute('data-state', input.getAttribute(prefix + 'state'));
        source.setAttribute('data-tone', input.getAttribute(prefix + 'tone'));
        source.setAttribute('data-text', input.getAttribute(prefix + 'state'));

        actions.selection().runAction(row.getAttribute('data-id'), source);
    };

    for (var switchIndex = 0; switchIndex < switches.length; switchIndex++) {
        switches[switchIndex].addEventListener('change', onChange);
    }
};

// The switch of a row stands as the state of its item says, whatever moved the item to that state.
actions.syncSwitch = function(itemId, state) {

    var input = actions.selection().row(itemId).querySelector('.row-switch');

    if (input === null) {
        return;
    }

    input.checked = state === input.getAttribute('data-on-state');
};

// ////////////////////////////////////////////////////////////////////////
// What the selection tells the actions
// ////////////////////////////////////////////////////////////////////////

// The details of an item were read.
actions.onPane = function(itemId, pane) {
    actions.addInline(itemId, pane);
};

// ////////////////////////////////////////////////////////////////////////

// An item moved to another state, which offers actions of its own.
actions.onChange = function(itemId, state) {

    var pane = actions.selection().panes[itemId];

    actions.syncSwitch(itemId, state);

    if (pane) {
        pane.querySelector('.inline-actions').remove();
        actions.addInline(itemId, pane);
    }
};

// ////////////////////////////////////////////////////////////////////////

actions.init = function() {
    actions.initPalette();
    actions.initToggle();
};

// ////////////////////////////////////////////////////////////////////////

portal.actions = actions;

document.addEventListener('DOMContentLoaded', actions.init);

// ////////////////////////////////////////////////////////////////////////

})();
