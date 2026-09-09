

// /////////////////////////////////////////////////////////////////////////////

// Resubmitting an event from the listing.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

// The confirmation a resubmit deep link opens - an alert notification points here
listing.openResubmitConfirm = function(rowModel, $row, warning) {
    var config = listing.config;

    // The row's own action link is the anchor - a narrow list may have dropped the
    // action cell, in which case the pane head carries the same link, the pane
    // already holding this event by now
    var $link = $row.find('.audit-log-resubmit-link');

    if ($link.length === 0) {
        $link = $(config.host).find('.audit-log-pane-actions .audit-log-resubmit-link');
    }

    // An event its source never declared resubmittable has no link and no confirmation -
    // a hand-edited address cannot resubmit what the page itself does not offer to
    if ($link.length === 0) {
        return;
    }

    var linkElement = $link[0];

    var content = document.createElement('div');
    content.className = 'audit-log-resubmit-confirm';

    var title = document.createElement('div');
    title.className = 'audit-log-resubmit-confirm-title';
    title.textContent = config.resubmitConfirmTitle;
    content.appendChild(title);

    var buttons = document.createElement('div');
    buttons.className = 'audit-log-resubmit-confirm-buttons';

    var instance = tippy(linkElement, {
        content: content,
        placement: 'left',
        trigger: 'manual',
        arrow: true,
        animation: 'fade',
        duration: [50, 50],
        hideOnClick: false,
        interactive: true,
        appendTo: document.body,
        zIndex: config.resubmitPopoverZIndex,

        // The instance is one-shot - once its hide animation finishes, it goes away
        onHidden: function(hiddenInstance) {
            hiddenInstance.destroy();
        }
    });

    var close = function() {
        instance.hide();
    };

    if (rowModel.isResubmitted) {
        var doneText = document.createElement('div');
        doneText.className = 'audit-log-resubmit-confirm-text';
        doneText.textContent = config.resubmitAlreadyDoneText;
        content.appendChild(doneText);

        var closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'audit-log-resubmit-confirm-cancel';
        closeButton.textContent = config.resubmitAlreadyDoneCloseLabel;
        closeButton.addEventListener('click', close);

        buttons.appendChild(closeButton);
        content.appendChild(buttons);

        instance.show();
        return;
    }

    // Which connection the message goes through again and what it is known by,
    // named in full before anything is sent
    var addFact = function(label, value) {
        var line = document.createElement('div');
        line.className = 'audit-log-resubmit-confirm-text';

        var labelPart = document.createElement('span');
        labelPart.className = 'audit-log-resubmit-confirm-label';
        labelPart.textContent = label;

        var valuePart = document.createElement('span');
        valuePart.textContent = value;

        line.appendChild(labelPart);
        line.appendChild(valuePart);
        content.appendChild(line);
    };

    addFact(config.resubmitConfirmConnectionLabel, rowModel.raw.object_name);
    addFact(config.resubmitConfirmMessageLabel, rowModel.identity);

    // The source's warning, if any, changes what the button says.
    var yesLabel = config.resubmitConfirmYesLabel;

    if (warning !== '') {
        var warningText = document.createElement('div');
        warningText.className = 'audit-log-resubmit-confirm-text audit-log-resubmit-confirm-warning';
        warningText.textContent = warning;
        content.appendChild(warningText);

        yesLabel = config.resubmitAnywayLabel;
    }

    var cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'audit-log-resubmit-confirm-cancel';
    cancelButton.textContent = config.resubmitConfirmCancelLabel;
    cancelButton.addEventListener('click', close);

    var yesButton = document.createElement('button');
    yesButton.type = 'button';
    yesButton.className = 'audit-log-resubmit-confirm-yes';
    yesButton.textContent = yesLabel;

    // Only confirming runs the POST - the same one the row's own link runs,
    // through the same per-source service registration
    yesButton.addEventListener('click', function() {
        close();
        $.fn.zato.audit_log.resubmit(linkElement);
    });

    buttons.appendChild(cancelButton);
    buttons.appendChild(yesButton);
    content.appendChild(buttons);

    instance.show();
};

// /////////////////////////////////////////////////////////////////////////////

// The action a deep link asked for, run once the page holding its event has arrived -
// the row is brought into view and marked, and the confirmation opens anchored on it
listing.runPendingAction = function() {
    if (listing.pendingAction === null) {
        return;
    }

    var rowModel = listing.modelById(listing.pendingAction);

    // The event may sit on a later page or outside the current window -
    // the action keeps waiting for a page that holds it
    if (rowModel === null) {
        return;
    }

    listing.pendingAction = null;

    // A refresh of the page is not asked to open the confirmation all over again
    kit.url_state.replace({action: ''});

    var $row = listing.panes.items_host().find('[data-item-id="' + rowModel.id + '"]');

    $row[0].scrollIntoView({block: 'center'});
    $row.addClass('kit-puff');

    listing.openResubmitConfirm(rowModel, $row, '');
};

})(jQuery);
