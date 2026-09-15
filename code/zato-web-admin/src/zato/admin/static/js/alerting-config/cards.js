// Alert rules - the rows.
//
// The state badge of each row, the flip of a type through its badge, and
// the order the rows keep between visits.

(function($) {

var screen = $.fn.zato.alerting_config;
var config = screen.config;

// ////////////////////////////////////////////////////////////////////////

// The grid the rows sit in - found by init.js once the page is there
screen.grid = null;

// ////////////////////////////////////////////////////////////////////////
//
// The state badges
//
// ////////////////////////////////////////////////////////////////////////

screen.renderCard = function(setName) {

    var isOn = screen.field(setName).is(':checked');

    var cardElem = screen.card(setName);
    cardElem.classList.toggle('alert-rules-set-off', !isOn);

    // The badge after the name says plainly whether the type is active
    var status = document.getElementById(config.statusIdPrefix + setName);
    status.textContent = '';

    // The badge is the shared dashboard tag - the same face the role tags
    // of the message flow and audit log listings wear
    var statusBadge = document.createElement('span');

    if(isOn) {
        statusBadge.className = 'dashboard-tag alert-rules-state-on';
        statusBadge.textContent = config.statusOnLabel;
    }
    else {
        statusBadge.className = 'dashboard-tag alert-rules-state-off';
        statusBadge.textContent = config.statusOffLabel;
    }

    // The badge is also the way to flip the type - it sits in a link
    // whose hover offers the same soft hint the value cells give
    var toggle = document.createElement('a');
    toggle.href = 'javascript:void(0)';
    toggle.className = 'summary-link alert-rules-state-toggle';
    toggle.appendChild(statusBadge);

    var hint = document.createElement('span');
    hint.className = 'zato-soft-hint';
    hint.textContent = config.toggleHintLabel;
    toggle.appendChild(hint);

    status.appendChild(toggle);
};

// ////////////////////////////////////////////////////////////////////////

screen.renderAll = function() {

    $.each(config.types, function(setName) {
        screen.renderCard(setName);
    });
};

// ////////////////////////////////////////////////////////////////////////

// Clicking a row's badge flips its type on or off - the badge changes
// at once, the backend flips all the type's rules, and a refused flip
// puts the badge back where it was
screen.toggleCard = function(toggleElem) {

    var cardElem = toggleElem.closest('.alert-rules-set-card');
    var setName = screen.setNameOf(cardElem);

    var fieldInput = screen.field(setName);
    var isOn = !fieldInput.is(':checked');
    fieldInput.prop('checked', isOn);

    // A re-toggle back to active cancels any dimming still waiting
    cardElem.classList.remove('alert-rules-set-off-pending');

    screen.renderCard(setName);

    // Deactivating happens under the pointer - only the badge changes for
    // now, the row keeps its full face until the pointer moves elsewhere
    if(!isOn) {
        cardElem.classList.remove('alert-rules-set-off');
        cardElem.classList.add('alert-rules-set-off-pending');
    }

    var revert = function() {
        fieldInput.prop('checked', !isOn);
        cardElem.classList.remove('alert-rules-set-off-pending');
        screen.renderCard(setName);
    };

    screen.postChange(setName, config.saveUrl, {type: setName, is_active: isOn}, function() {}, revert);
};

// Once the pointer leaves a row whose dimming is waiting, it dims
screen.settleDimming = function(cardElem) {

    if(cardElem.classList.contains('alert-rules-set-off-pending')) {
        cardElem.classList.remove('alert-rules-set-off-pending');
        cardElem.classList.add('alert-rules-set-off');
    }
};

// ////////////////////////////////////////////////////////////////////////
//
// Reordering the rows
//
// ////////////////////////////////////////////////////////////////////////

// The rows keep whatever order they were last dragged into, per browser
screen.saveOrder = function() {

    var order = [];
    var cards = screen.grid.querySelectorAll('.alert-rules-set-card');

    for(var cardIdx = 0; cardIdx < cards.length; cardIdx++) {
        order.push(screen.setNameOf(cards[cardIdx]));
    }

    localStorage.setItem(config.orderStorageKey, JSON.stringify(order));
};

screen.restoreOrder = function() {

    var stored = localStorage.getItem(config.orderStorageKey);

    // A first visit has no order on record yet
    if(stored === null) {
        return;
    }

    var order = JSON.parse(stored);

    // Appending an element moves it, so walking the saved order rebuilds it -
    // a type the saved order does not know stays where the page put it
    for(var orderIdx = 0; orderIdx < order.length; orderIdx++) {

        var saved = screen.card(order[orderIdx]);

        if(saved) {
            screen.grid.appendChild(saved);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
