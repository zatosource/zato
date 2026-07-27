// The wizard kit's collapsibles - what a step folds away when it has more
// to offer than it has room for.
//
// There are two of them. A section is folded behind one line reading like
// the rest of the step - a label, a link saying what is currently set and a
// soft hint offering the click. A group is folded behind its own heading
// with a chevron, and groups sit inside a section or a card, one heading
// after another, each opening on its own.
//
// Both hide with the hidden attribute rather than with a height that
// animates, since a body sliding out of something that is itself sliding
// open is what makes an opening jerk.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.collapse = {};

// ////////////////////////////////////////////////////////////////////////

kit.collapse.config = {

    // What the soft hint of a folded section offers
    openHint: 'Click to open',
    closeHint: 'Click to close',

    // A group's heading and the body it opens
    groupTitleSelector: '.wizard-collapse-group-title',
    groupBodySelector: '.wizard-collapse-group-body',
    chevronSelector: '.wizard-chevron',
    chevronOpenClass: 'wizard-chevron-open'
};

// ////////////////////////////////////////////////////////////////////////

// One section folded behind one line.
//
// spec:
//   toggleId - the line that opens and closes it
//   bodyId   - what it opens, hidden or not in the template as it should start
//   hintId   - optional, the soft hint whose words follow the state
//   openHint, closeHint - optional, the words themselves
//   onToggle - optional, run after each open and each close
kit.collapse.initSection = function(spec) {

    var body = $('#' + spec.bodyId);
    var hint = spec.hintId ? $('#' + spec.hintId) : null;

    var setHint = function() {

        if(!hint) {
            return;
        }

        var collapseConfig = kit.collapse.config;
        var openHint = spec.openHint ? spec.openHint : collapseConfig.openHint;
        var closeHint = spec.closeHint ? spec.closeHint : collapseConfig.closeHint;

        hint.text(body.prop('hidden') ? openHint : closeHint);
    };

    $('#' + spec.toggleId).on('click', function() {

        body.prop('hidden', !body.prop('hidden'));
        setHint();

        if(spec.onToggle) {
            spec.onToggle(!body.prop('hidden'));
        }
    });

    // The template decides what the section starts as, the hint follows it
    setHint();
};

// ////////////////////////////////////////////////////////////////////////

// Every group inside the given container - a heading opens the body right
// after it and turns its chevron, and the groups are independent of each
// other, so any number of them may be open at once.
kit.collapse.initGroups = function(containerSelector) {

    var collapseConfig = kit.collapse.config;

    $(containerSelector).find(collapseConfig.groupTitleSelector).on('click', function() {

        var title = $(this);
        var body = title.next(collapseConfig.groupBodySelector);
        var isOpening = body.prop('hidden');

        body.prop('hidden', !isOpening);
        title.find(collapseConfig.chevronSelector).toggleClass(collapseConfig.chevronOpenClass, isOpening);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The chevron every collapsible heading wears, pointing right while closed
// and down while open.
kit.collapse.buildChevron = function() {

    var chevron = document.createElement('span');

    chevron.innerHTML = '<svg class="wizard-chevron" width="11" height="11" viewBox="0 0 24 24" fill="none" ' +
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
        '<polyline points="9 18 15 12 9 6"></polyline></svg>';

    var out = chevron.firstChild;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
