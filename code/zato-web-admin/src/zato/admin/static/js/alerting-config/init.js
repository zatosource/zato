// Alert rules - the wiring once the page is there.
//
// The endpoints and the elements the other files reach for are read off
// the page, the popover is set up on its descriptors, the clicks are
// delegated, the rows get their order and their badges, and the page is
// shown once it is fully filled in.

(function($) {

var screen = $.fn.zato.alerting_config;
var config = screen.config;

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    var root = document.getElementById('alert-rules');

    // Where a change is posted - the endpoints the template names
    config.saveUrl = root.dataset.saveUrl;
    config.notificationsSaveUrl = root.dataset.notificationsSaveUrl;

    // Where a failed change explains itself, and the grid the rows sit in
    screen.errorElement = document.getElementById('alert-rules-error');
    screen.grid = document.querySelector('.alert-rules-grid');

    // The hidden unit selects offer the same units, in the same words, as the cells show
    document.querySelectorAll('#alert-rules-row-fields select.alert-rules-unit').forEach(function(select) {
        screen.fillUnitSelect(select, config.durationUnits);
    });

    document.querySelectorAll('#alert-rules-row-fields select.alert-rules-amount-unit').forEach(function(select) {
        screen.fillUnitSelect(select, config.amountUnits);
    });

    document.querySelectorAll('#alert-rules-row-fields select.alert-rules-size-unit').forEach(function(select) {
        screen.fillUnitSelect(select, config.sizeUnits);
    });

    // The popover editor, one micro-form per row
    $.fn.zato.micro_forms.setup(screen.editor, {
        descriptors: screen.descriptors(),
        popupClass: config.popupClass,
        showCancel: true,
        doneLabel: 'OK',
        labelsLeft: true,
        onDone: screen.saveRow
    });

    $.fn.zato.micro_forms.registerChipsKind(screen.editor);

    // The value cells of every row, the notifications row included - it sits
    // outside the sortable grid, so the delegation runs from the screen's root
    $('#alert-rules').on('click', '.alert-rules-param-edit', function() {
        screen.openEditor(this);
    });

    // The badge flips its type, and a row whose dimming is waiting dims once the pointer leaves it
    $('.alert-rules-grid').on('click', '.alert-rules-state-toggle', function() {
        screen.toggleCard(this);
    });

    $('.alert-rules-grid').on('mouseleave', '.alert-rules-set-card', function() {
        screen.settleDimming(this);
    });

    // Reordering runs through Sortable, the way the rate limiting rules do -
    // rows are picked up by their handle, the ghost marks the drop spot
    // and the order that comes out is what the next visit restores.
    Sortable.create(screen.grid, {
        handle: '.alert-rules-drag-handle',
        animation: 150,
        ghostClass: 'alert-rules-dragging',
        onEnd: function() {
            screen.saveOrder();
        }
    });

    // Every row shows its type's state from the moment the page opens,
    // in the order the rows were last dragged into ..
    screen.restoreOrder();
    screen.renderAll();

    // .. the help explains each type at its own row header ..
    $.fn.zato.how_it_works.init({
        badgeId: 'alert-rules-how-it-works',
        divId: '#alert-rules',
        fieldSelector: '.alert-rules-set-header',

        // The tooltips go below their anchors, each one's left edge lining
        // up with the left edge of the thing it describes
        placement: 'bottom-start',
        descriptions: screen.helpDescriptions()
    });

    // .. and the page is shown once it is fully filled in.
    $.fn.zato.dashboard_kit.reveal();
});

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
