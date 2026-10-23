'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

var b2bConsole = {};

b2bConsole.config = {
    detailMinWidth: 320,
    masterMinWidth: 420,
    splitStorageKey: 'zato.b2b-console.split.detail',
    splitActiveClass: 'pane-split-active',
    hiddenRowClass: 'b2b-console-row-hidden',
};

// ////////////////////////////////////////////////////////////////////////

b2bConsole.initSplit = function() {

    var frame = document.getElementById('b2b-console-frame');
    var bar = document.getElementById('b2b-console-split-bar');
    var detail = document.getElementById('b2b-console-detail');

    paneSplit.init({
        bar: bar,
        pane: detail,
        container: frame,
        axis: 'x',
        minSize: b2bConsole.config.detailMinWidth,
        minOther: b2bConsole.config.masterMinWidth,
        activeClass: b2bConsole.config.splitActiveClass,
        storageKey: b2bConsole.config.splitStorageKey,
    });
};

// ////////////////////////////////////////////////////////////////////////

b2bConsole.initFilter = function() {

    var input = document.getElementById('b2b-console-filter');
    var rows = document.querySelectorAll('#b2b-console-master tbody tr');

    input.addEventListener('input', function() {
        var term = input.value.toLowerCase();

        rows.forEach(function(row) {
            var isMatch = row.textContent.toLowerCase().indexOf(term) !== -1;
            row.classList.toggle(b2bConsole.config.hiddenRowClass, !isMatch);
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

b2bConsole.init = function() {
    b2bConsole.initSplit();
    b2bConsole.initFilter();
};

// ////////////////////////////////////////////////////////////////////////

window.b2bConsole = b2bConsole;

document.addEventListener('DOMContentLoaded', b2bConsole.init);

// ////////////////////////////////////////////////////////////////////////

})();
