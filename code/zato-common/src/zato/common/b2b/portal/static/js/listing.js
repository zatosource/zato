'use strict';

// The listing of a section - the rows are narrowed down by the text of the filter and by the criteria of a search.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var listing = {};

listing.state = {
    text: '',
    criteria: []
};

// ////////////////////////////////////////////////////////////////////////

listing.matchesCriterion = function(row, criterion) {

    var value = row.getAttribute('data-attribute-' + criterion.name);
    var out;

    if (criterion.match === 'contains') {
        out = value.toLowerCase().indexOf(criterion.value.toLowerCase()) !== -1;
    }
    else if (criterion.match === 'at-most') {
        out = parseInt(value, 10) <= parseInt(criterion.value, 10);
    }
    else {
        out = value === criterion.value;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

listing.matches = function(row) {

    var state = listing.state;

    // A row of a deleted item is never shown again ..
    if (row.classList.contains('listing-row-removed')) {
        return false;
    }

    // .. a row has to have the text of the filter ..
    if (state.text) {
        if (row.getAttribute('data-search').indexOf(state.text) === -1) {
            return false;
        }
    }

    // .. and it has to meet each criterion of the search.
    for (var criterionIndex = 0; criterionIndex < state.criteria.length; criterionIndex++) {
        if (!listing.matchesCriterion(row, state.criteria[criterionIndex])) {
            return false;
        }
    }

    return true;
};

// ////////////////////////////////////////////////////////////////////////

// Shows the rows that match, every second one of them on a stripe.
listing.apply = function() {

    var rows = document.querySelectorAll('#listing tbody tr');
    var shownCount = 0;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {

        var row = rows[rowIndex];
        var isShown = listing.matches(row);
        var isStripe = false;

        row.hidden = !isShown;

        if (isShown) {
            shownCount += 1;
            isStripe = shownCount % 2 === 0;
        }

        row.classList.toggle('table-stripe', isStripe);
    }

    document.getElementById('listing-empty').hidden = shownCount !== 0;
    portal.bulk.render();
};

// ////////////////////////////////////////////////////////////////////////

listing.init = function() {

    var input = document.getElementById('listing-filter');

    input.addEventListener('input', function() {
        listing.state.text = input.value.trim().toLowerCase();
        listing.apply();
    });

    listing.apply();
};

// ////////////////////////////////////////////////////////////////////////

portal.listing = listing;

document.addEventListener('DOMContentLoaded', listing.init);

// ////////////////////////////////////////////////////////////////////////

})();
