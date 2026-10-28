'use strict';

// The selection of a listing. A press on a row selects it and shows its details in the lower pane, which are read
// from the item's own address, and the line between the two panes is dragged to share the height between them.
// The actions of each item are kept in its row as hidden sources, which the links beside its state and the command
// palette are built from. The sources follow from the state of the item, so that a change of state offers the actions
// of the new state at once. The address names the selected item, its open tab and whether what is kept apart
// from the tab is open, so that it always leads back to what is shown.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var selection = {};

selection.config = {
    detailsParameter: 'details',
    selectedClass: 'listing-row-selected',
    removedClass: 'listing-row-removed',
    paneRemovedClass: 'detail-removed',
    draggingClass: 'split-dragging',
    minimumPaneHeight: 140,
    transitionsId: 'transitions-data'
};

// The actions an item can take, by the state it is in
selection.transitions = {};

// The details already read, by the ID of their item, so that what was changed in them stays changed
selection.panes = {};

// The item whose details are shown, and the item whose details were asked for last
selection.current = null;
selection.requested = null;

// ////////////////////////////////////////////////////////////////////////

selection.row = function(itemId) {
    var out = document.querySelector('#listing tbody tr[data-id="' + CSS.escape(itemId) + '"]');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The actions the item can still take, as kept in its row.
selection.sources = function(itemId) {
    var out = selection.row(itemId).querySelectorAll('.row-sources [data-action]');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

selection.mark = function(itemId) {

    var selected = document.querySelectorAll('#listing .' + selection.config.selectedClass);

    for (var rowIndex = 0; rowIndex < selected.length; rowIndex++) {
        selected[rowIndex].classList.remove(selection.config.selectedClass);
    }

    if (itemId === null) {
        return;
    }

    var row = selection.row(itemId);
    row.classList.add(selection.config.selectedClass);
};

// ////////////////////////////////////////////////////////////////////////

// The sources of the actions an item can take in the state it is in.
selection.fillSources = function(itemId, state) {

    var host = selection.row(itemId).querySelector('.row-sources');
    var list = selection.transitions[state];

    host.textContent = '';

    for (var actionIndex = 0; actionIndex < list.length; actionIndex++) {

        var action = list[actionIndex];
        var source = portal.create('button', '', action.label);

        source.type = 'button';
        source.setAttribute('data-action', action.kind);
        source.setAttribute('data-state', action.state);
        source.setAttribute('data-tone', action.tone);
        source.setAttribute('data-text', action.text);

        if (action.is_danger) {
            source.setAttribute('data-danger', '1');
        }

        if (action.is_primary) {
            source.setAttribute('data-primary', '1');
        }

        host.appendChild(source);
    }
};

// ////////////////////////////////////////////////////////////////////////

selection.activeTab = function(itemId) {
    var out = selection.panes[itemId].querySelector('.tab-active').getAttribute('data-tab');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

selection.address = function(itemId, isDetails) {

    var out = window.location.pathname;

    if (itemId !== null) {
        out += '?id=' + encodeURIComponent(itemId) + '&tab=' + encodeURIComponent(selection.activeTab(itemId));
    }

    if (isDetails) {
        out += '&' + selection.config.detailsParameter + '=1';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

selection.writeAddress = function(itemId, isDetails) {

    var address = selection.address(itemId, isDetails);

    window.history.replaceState(null, '', address);
};

// ////////////////////////////////////////////////////////////////////////

selection.setPaneShown = function(isShown) {
    document.getElementById('split-bottom').hidden = !isShown;
    document.getElementById('split-handle').hidden = !isShown;
};

// ////////////////////////////////////////////////////////////////////////

// Readies the details of an item - tooltips go first, so that a value which also opens a micro-form keeps its tip.
selection.prepare = function(itemId, pane) {
    portal.tooltips.attach(pane);
    portal.detail.init(pane);
    portal.edit.init(pane);
    portal.actions.onPane(itemId, pane);
    selection.panes[itemId] = pane;
};

// ////////////////////////////////////////////////////////////////////////

selection.show = function(itemId) {

    var bottom = document.getElementById('split-bottom');
    var pane = selection.panes[itemId];

    // The tab open for the item shown so far stays open for the next one, if that one has it too
    if (selection.current !== null) {

        var key = selection.activeTab(selection.current);

        if (pane.querySelector('.tab[data-tab="' + key + '"]')) {
            portal.detail.showTab(pane, key);
        }
    }

    bottom.textContent = '';
    bottom.appendChild(pane);

    selection.current = itemId;
    selection.setPaneShown(true);
    selection.writeAddress(itemId, false);
};

// ////////////////////////////////////////////////////////////////////////

selection.close = function() {
    selection.current = null;
    selection.requested = null;
    selection.mark(null);
    selection.setPaneShown(false);
    selection.writeAddress(null, false);
};

// ////////////////////////////////////////////////////////////////////////

// Reads the details of an item from the page of its own address, unless they were read before.
selection.load = function(itemId, address) {

    selection.requested = itemId;

    if (selection.panes[itemId]) {
        selection.show(itemId);
        return;
    }

    window.fetch(address).then(function(response) {
        return response.text();
    }).then(function(html) {

        var page = new DOMParser().parseFromString(html, 'text/html');
        var pane = document.importNode(page.getElementById('detail'), true);

        selection.prepare(itemId, pane);

        // Another row may have been selected while these details were being read
        if (selection.requested === itemId) {
            selection.show(itemId);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

selection.select = function(row) {

    var itemId = row.getAttribute('data-id');

    if (itemId === selection.current) {
        return;
    }

    selection.mark(itemId);
    selection.load(itemId, row.querySelector('.listing-link').getAttribute('href'));
};

// ////////////////////////////////////////////////////////////////////////

selection.onRowClick = function(event) {

    var row = event.target.closest('tr');

    if (row === null) {
        return;
    }

    // A control in the row acts on its own
    if (event.target.closest('.row-switch, .listing-select')) {
        return;
    }

    // A press with a modifier key opens the item's address the way the browser opens any link
    if (event.ctrlKey) {
        return;
    }

    if (event.metaKey) {
        return;
    }

    if (event.shiftKey) {
        return;
    }

    event.preventDefault();
    selection.select(row);
};

// ////////////////////////////////////////////////////////////////////////

selection.runAction = function(itemId, source) {

    var pane = selection.panes[itemId];
    var row = selection.row(itemId);

    // The item either moves to the state of the action, in its details and in its row alike ..
    if (source.getAttribute('data-action') === 'set-state') {

        var state = source.getAttribute('data-state');
        var tone = source.getAttribute('data-tone');
        var text = source.getAttribute('data-text');

        portal.detail.setState(row, text, tone);
        row.setAttribute('data-attribute-state', state);

        if (pane) {
            portal.detail.setState(pane, text, tone);
        }

        selection.fillSources(itemId, state);
        portal.actions.onChange(itemId, state);
    }

    // .. or it is deleted, and its row with it.
    else {

        row.classList.add(selection.config.removedClass);

        if (pane) {
            pane.classList.add(selection.config.paneRemovedClass);
        }

        if (itemId === selection.current) {
            selection.close();
        }

        portal.listing.apply();
    }

    portal.bulk.render();
};

// ////////////////////////////////////////////////////////////////////////

// Escape closes the details once nothing over them is open - a search being typed is cleared by the browser first.
selection.onKeyDown = function(event) {

    if (event.key !== 'Escape') {
        return;
    }

    if (selection.current === null) {
        return;
    }

    if (document.querySelector('.palette-backdrop')) {
        return;
    }

    if (event.target.matches('input[type="search"]')) {
        if (event.target.value !== '') {
            return;
        }
    }

    selection.close();
};

// ////////////////////////////////////////////////////////////////////////

// The line between the panes gives the lower pane the height from the pointer to the bottom of the split.
selection.startResize = function(event) {

    event.preventDefault();

    var split = document.getElementById('split');
    var bottom = document.getElementById('split-bottom');
    var minimum = selection.config.minimumPaneHeight;

    document.body.classList.add(selection.config.draggingClass);

    var onMove = function(moveEvent) {

        var rect = split.getBoundingClientRect();
        var height = rect.bottom - moveEvent.clientY;
        var maximum = rect.height - minimum;

        height = Math.max(minimum, Math.min(maximum, height));
        bottom.style.flexBasis = height + 'px';
    };

    var onUp = function() {
        document.body.classList.remove(selection.config.draggingClass);
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
};

// ////////////////////////////////////////////////////////////////////////

selection.init = function() {

    var listing = document.getElementById('listing');
    var pane = document.getElementById('detail');

    selection.transitions = portal.readData(selection.config.transitionsId);

    var rows = listing.querySelectorAll('tbody tr');

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        selection.fillSources(rows[rowIndex].getAttribute('data-id'), rows[rowIndex].getAttribute('data-attribute-state'));
    }

    listing.querySelector('tbody').addEventListener('click', selection.onRowClick);
    document.getElementById('split-handle').addEventListener('mousedown', selection.startResize);
    document.addEventListener('keydown', selection.onKeyDown);

    // The item the address names is already shown under the listing
    if (pane) {

        var itemId = pane.getAttribute('data-id');
        var isDetails = new URLSearchParams(window.location.search).has(selection.config.detailsParameter);

        selection.prepare(itemId, pane);
        selection.current = itemId;
        selection.requested = itemId;
        selection.writeAddress(itemId, false);
        selection.row(itemId).scrollIntoView({block: 'nearest'});

        // The address asked for what is kept apart from the open tab
        if (isDetails) {
            portal.detail.openDetails(pane);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

portal.selection = selection;

document.addEventListener('DOMContentLoaded', selection.init);

// ////////////////////////////////////////////////////////////////////////

})();
