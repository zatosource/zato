'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

// The behaviour of a Clear control standing inside a search box - it shows only while
// there is a term in the box to be cleared, and clicking it empties the box and hands
// control back to the host through onClear. Returns the toggle so a host that fills
// the box programmatically can refresh the badge itself.

window.searchClear = {

    init: function(config) {

        var toggle = function() {
            config.button.style.display = config.input.value === '' ? 'none' : '';
        };

        // The box may come up with a term already in it, so the badge starts from that
        toggle();

        config.input.addEventListener('input', toggle);

        config.button.addEventListener('click', function() {
            config.input.value = '';
            toggle();
            config.onClear();
        });

        return toggle;
    },
};

// ////////////////////////////////////////////////////////////////////////

})();
