

// /////////////////////////////////////////////////////////////////////////////

// The steps of one file or one stored file, drawn with the journey kit.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.byTimeThenId = function(first, second) {
    if (first.event_time_iso < second.event_time_iso) {
        return -1;
    }

    if (first.event_time_iso > second.event_time_iso) {
        return 1;
    }

    return first.id - second.id;
};

// /////////////////////////////////////////////////////////////////////////////

// The rows of one cid, oldest first.
fileOutgoing.fetchJourney = function(cid, onDone) {
    $.ajax({
        url: fileOutgoing.config.journeyURL,
        type: 'POST',
        data: JSON.stringify({term: cid}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            var rows = [];

            for (var index = 0; index < data.rows.length; index++) {
                if (data.rows[index].cid === cid) {
                    rows.push(data.rows[index]);
                }
            }

            rows.sort(fileOutgoing.byTimeThenId);

            onDone(rows);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.stateOf = function(row) {
    if (row.outcome === fileOutgoing.config.errorOutcome) {
        return 'failed';
    }

    return 'done';
};

// /////////////////////////////////////////////////////////////////////////////

// A step standing for a row, a failed row's title is its error.
fileOutgoing.stepFor = function(label, row, title) {
    var durationText = '';

    if (row.duration_ms > 0) {
        durationText = kit.format_duration_ms(row.duration_ms);
    }

    if (row.outcome === fileOutgoing.config.errorOutcome) {
        if (row.error !== '') {
            title = fileOutgoing.errorSummary(row.error);
        }
    }

    return {label: label, state: fileOutgoing.stateOf(row), durationText: durationText,
        eventId: row.id, title: title, isFoldable: false, timeIso: row.event_time_iso, gapText: ''};
};

// /////////////////////////////////////////////////////////////////////////////

// A step with no row behind it.
fileOutgoing.pendingStep = function(label, state, title) {
    return {label: label, state: state, durationText: '', eventId: 0, title: title, isFoldable: false,
        timeIso: '', gapText: ''};
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.isFrame = function(row) {
    return fileOutgoing.config.frameSources[row.source] === true;
};

// /////////////////////////////////////////////////////////////////////////////

// The rows of a file sorted into the roles its steps are built from.
fileOutgoing.fileRoles = function(rows) {
    var config = fileOutgoing.config;

    var roles = {
        claimed: null,
        read: null,
        delivered: null,
        acked: null,
        quarantined: null,
        downstream: []
    };

    for (var index = 0; index < rows.length; index++) {
        var row = rows[index];

        if (!fileOutgoing.isOwn(row)) {
            if (!fileOutgoing.isFrame(row)) {
                roles.downstream.push(row);
            }

            continue;
        }

        if (row.event_type === config.connectionEvent) {
            fileOutgoing.noteConnectionRole(roles, row);
        }
        else if (row.event_type === config.claimedEvent) {
            roles.claimed = row;
        }
        else if (config.deliveryEvents[row.event_type]) {
            roles.delivered = row;
        }
        else if (row.event_type === config.ackedEvent) {
            roles.acked = row;
        }
        else if (row.event_type === config.quarantinedEvent) {
            roles.quarantined = row;
        }
    }

    return roles;
};

// /////////////////////////////////////////////////////////////////////////////

// A move before the delivery is the claim, the first read is the read.
fileOutgoing.noteConnectionRole = function(roles, row) {
    var config = fileOutgoing.config;

    if (row.operation === config.moveOperation) {
        if (roles.delivered === null) {
            if (roles.claimed === null) {
                roles.claimed = row;
            }
        }
    }
    else if (row.operation === config.readOperation) {
        if (roles.read === null) {
            roles.read = row;
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The step a role's row stands for, or a pending step in the given state when there is no row.
fileOutgoing.roleStep = function(label, row, pendingState) {
    if (row !== null) {
        return fileOutgoing.stepFor(label, row, '');
    }

    return fileOutgoing.pendingStep(label, pendingState, '');
};

// /////////////////////////////////////////////////////////////////////////////

// The last step of a file, quarantined, put away, or the put-away it never reached.
fileOutgoing.lastFileStep = function(roles) {
    var config = fileOutgoing.config;
    var labels = config.journeySteps;

    if (roles.quarantined !== null) {
        return fileOutgoing.stepFor(labels.quarantined, roles.quarantined, '');
    }

    if (roles.acked !== null) {
        return fileOutgoing.stepFor(labels.acked, roles.acked, '');
    }

    if (roles.delivered !== null) {
        if (roles.delivered.outcome === config.errorOutcome) {
            return fileOutgoing.pendingStep(labels.acked, 'skipped', '');
        }
    }

    return fileOutgoing.pendingStep(labels.acked, 'pending', '');
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.fileJourneySteps = function(rows, rowModel) {
    var labels = fileOutgoing.config.journeySteps;
    var roles = fileOutgoing.fileRoles(rows);
    var steps = [];

    steps.push(fileOutgoing.roleStep(labels.claimed, roles.claimed, 'skipped'));
    steps.push(fileOutgoing.roleStep(labels.read, roles.read, 'pending'));
    steps.push(fileOutgoing.roleStep(labels.delivered, roles.delivered, 'pending'));

    for (var downIndex = 0; downIndex < roles.downstream.length; downIndex++) {
        var downRow = roles.downstream[downIndex];
        var downStep = fileOutgoing.stepFor(downRow.object_name, downRow, downRow.source);
        downStep.isFoldable = true;
        steps.push(downStep);
    }

    steps.push(fileOutgoing.lastFileStep(roles));

    // A file sent out again by hand has that as its last step.
    for (var childIndex = 0; childIndex < rowModel.children.length; childIndex++) {
        var child = rowModel.children[childIndex];
        var reprocessed = fileOutgoing.pendingStep(labels.reprocessed, 'done', '');
        reprocessed.eventId = child.id;
        steps.push(reprocessed);
    }

    return steps;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.verifiedStep = function(storeRow) {
    var config = fileOutgoing.config;
    var labels = config.journeySteps;

    if (storeRow.status === config.verifiedStatus) {
        var verified = fileOutgoing.pendingStep(labels.verified, 'done', storeRow.verify_how);
        verified.durationText = kit.format_duration_ms(storeRow.verify_ms);
        verified.eventId = storeRow.id;
        return verified;
    }

    if (storeRow.status === config.verifyFailedStatus) {
        return fileOutgoing.pendingStep(labels.verified, 'failed', storeRow.mismatch);
    }

    return fileOutgoing.pendingStep(labels.verified, 'pending', '');
};

// /////////////////////////////////////////////////////////////////////////////

// Stored, Verified, then whatever moved or deleted the file under the same cid.
fileOutgoing.storeJourneySteps = function(rows, rowModel) {
    var config = fileOutgoing.config;
    var labels = config.journeySteps;
    var storeRow = rowModel.raw;
    var steps = [];

    steps.push(fileOutgoing.stepFor(labels.stored, storeRow, ''));
    steps.push(fileOutgoing.verifiedStep(storeRow));

    for (var index = 0; index < rows.length; index++) {
        var row = rows[index];

        if (row.event_time_iso <= storeRow.event_time_iso) {
            continue;
        }

        if (!fileOutgoing.isOwn(row)) {
            continue;
        }

        if (row.operation === config.moveOperation) {
            steps.push(fileOutgoing.stepFor(labels.moved, row, row.to_path));
        }
        else if (row.operation === config.deleteOperation) {
            steps.push(fileOutgoing.stepFor(labels.deleted, row, ''));
        }
    }

    return steps;
};

// /////////////////////////////////////////////////////////////////////////////

// The time between one step and the next, written on the connector before the latter.
fileOutgoing.addGaps = function(steps) {
    var previousIso = '';

    for (var index = 0; index < steps.length; index++) {
        var step = steps[index];

        if (step.timeIso === '') {
            continue;
        }

        if (previousIso !== '') {
            var gapMs = new Date(step.timeIso).getTime() - new Date(previousIso).getTime();

            if (gapMs > 0) {
                step.gapText = '+' + kit.format_duration_ms(gapMs);
            }
        }

        previousIso = step.timeIso;
    }

    return steps;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.renderJourney = function(rowModel, $host, variant) {
    var config = fileOutgoing.config;
    var row = rowModel.raw;

    $host.html('<div class="audit-log-journey-loading">' + config.journeyLoadingLabel + '</div>');

    fileOutgoing.fetchJourney(row.cid, function(rows) {
        if (!fileOutgoing.isHostAttached($host)) {
            return;
        }

        var steps;

        if (fileOutgoing.isStore(row)) {
            steps = fileOutgoing.storeJourneySteps(rows, rowModel);
        }
        else {
            steps = fileOutgoing.fileJourneySteps(rows, rowModel);
        }

        $host.html(kit.journey.render({steps: fileOutgoing.addGaps(steps), variant: variant}));
    });
};

// /////////////////////////////////////////////////////////////////////////////

// A clicked step opens its event on the list, on the drawing or on the flow page.
$(document).on('click', '.dashboard-journey-step-selectable', function(event) {
    event.stopPropagation();

    var config = fileOutgoing.config;
    var eventId = $(this).attr('data-event-id');
    var listing = $.fn.zato.audit_log.listing;

    if (listing.panes !== null) {
        if (listing.modelById(eventId) !== null) {
            listing.panes.select(eventId);
            return;
        }
    }

    if (config.selectOnDrawing) {
        var drawing = $.fn.zato.message_flow.drawing;

        if (drawing.selectEvent !== null) {
            if (drawing.selectEvent(eventId)) {
                return;
            }
        }
    }

    window.location.href = $.fn.zato.audit_log.flowPageURL(eventId);
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
