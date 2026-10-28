'use strict';

// The rows checked in a listing. The box in the header checks or clears every row shown, and a tippy to its left
// counts the rows checked and offers the actions that every checked item has, which run on all of them at once.
// A listing whose items are not acted on together has no boxes to check.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var bulk = {};

bulk.config = {
    countSuffix: ' selected',
    placement: 'left',
    offset: [0, 10]
};

// Whether the listing has boxes to check, the tippy beside the box in the header, and what the tippy shows
bulk.isEnabled = false;
bulk.instance = null;
bulk.count = null;
bulk.actions = null;

// ////////////////////////////////////////////////////////////////////////

// The rows the filter, the criteria and the deletions leave in the listing.
bulk.shownRows = function() {

    var rows = document.querySelectorAll('#listing tbody tr');
    var out = [];

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        if (!rows[rowIndex].hidden) {
            out.push(rows[rowIndex]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

bulk.checkedRows = function() {

    var rows = bulk.shownRows();
    var out = [];

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        if (rows[rowIndex].querySelector('.row-check').checked) {
            out.push(rows[rowIndex]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The source of the action of the given label among those of an item, or null if the item does not have it.
bulk.sourceOf = function(itemId, label) {

    var sources = portal.selection.sources(itemId);

    for (var sourceIndex = 0; sourceIndex < sources.length; sourceIndex++) {
        if (sources[sourceIndex].textContent === label) {
            return sources[sourceIndex];
        }
    }

    return null;
};

// ////////////////////////////////////////////////////////////////////////

// The actions every one of the rows has, each with the source of the action in each row.
bulk.common = function(rows) {

    var out = [];
    var first = portal.selection.sources(rows[0].getAttribute('data-id'));

    for (var sourceIndex = 0; sourceIndex < first.length; sourceIndex++) {

        var label = first[sourceIndex].textContent;
        var pairs = [];

        for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {

            var itemId = rows[rowIndex].getAttribute('data-id');
            var source = bulk.sourceOf(itemId, label);

            if (source === null) {
                break;
            }

            pairs.push({itemId: itemId, source: source});
        }

        if (pairs.length === rows.length) {
            out.push({label: label, isDanger: first[sourceIndex].hasAttribute('data-danger'), pairs: pairs});
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

bulk.run = function(entry) {
    for (var pairIndex = 0; pairIndex < entry.pairs.length; pairIndex++) {
        portal.selection.runAction(entry.pairs[pairIndex].itemId, entry.pairs[pairIndex].source);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The box in the header shows whether all, some or none of the rows shown are checked.
bulk.renderAll = function(shownCount, checkedCount) {

    var all = document.getElementById('check-all');

    all.checked = false;
    all.indeterminate = false;

    if (checkedCount === 0) {
        return;
    }

    if (checkedCount === shownCount) {
        all.checked = true;
        return;
    }

    all.indeterminate = true;
};

// ////////////////////////////////////////////////////////////////////////

bulk.render = function() {

    if (!bulk.isEnabled) {
        return;
    }

    var checked = bulk.checkedRows();

    bulk.renderAll(bulk.shownRows().length, checked.length);
    bulk.actions.textContent = '';

    if (checked.length === 0) {
        bulk.instance.hide();
        return;
    }

    bulk.count.textContent = checked.length + bulk.config.countSuffix;

    var entries = bulk.common(checked);

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {

        var entry = entries[entryIndex];
        var link = portal.create('button', entry.isDanger ? 'link link-danger' : 'link', entry.label);

        link.type = 'button';
        link.addEventListener('click', bulk.run.bind(null, entry));

        bulk.actions.appendChild(link);
    }

    bulk.instance.show();
    bulk.instance.popperInstance.update();
};

// ////////////////////////////////////////////////////////////////////////

// The tippy stays open while any row is checked, whatever else closes the tippies of the page.
bulk.onHide = function() {
    if (bulk.checkedRows().length > 0) {
        return false;
    }
};

// ////////////////////////////////////////////////////////////////////////

bulk.toggleAll = function(event) {

    var rows = bulk.shownRows();
    var isChecked = event.currentTarget.checked;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        rows[rowIndex].querySelector('.row-check').checked = isChecked;
    }

    bulk.render();
};

// ////////////////////////////////////////////////////////////////////////

bulk.init = function() {

    var all = document.getElementById('check-all');

    if (all === null) {
        return;
    }

    bulk.isEnabled = true;

    var host = portal.create('div', 'bulk', '');

    bulk.count = portal.create('span', 'bulk-count', '');
    bulk.actions = portal.create('span', 'bulk-actions', '');

    host.appendChild(bulk.count);
    host.appendChild(bulk.actions);

    bulk.instance = window.tippy(all, {
        content: host,
        trigger: 'manual',
        interactive: true,
        hideOnClick: false,
        placement: bulk.config.placement,
        offset: bulk.config.offset,
        maxWidth: 'none',
        appendTo: document.body,
        onHide: bulk.onHide
    });

    all.addEventListener('change', bulk.toggleAll);

    document.querySelector('#listing tbody').addEventListener('change', function(event) {
        if (event.target.classList.contains('row-check')) {
            bulk.render();
        }
    });

    bulk.render();
};

// ////////////////////////////////////////////////////////////////////////

portal.bulk = bulk;

document.addEventListener('DOMContentLoaded', bulk.init);

// ////////////////////////////////////////////////////////////////////////

})();
