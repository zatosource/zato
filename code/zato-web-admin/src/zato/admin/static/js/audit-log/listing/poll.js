

// /////////////////////////////////////////////////////////////////////////////

// Drawing the page and what each poll brings.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

// The newest rows carry a fading tint, and a row that arrived on a live refresh puffs once.
// A page the reader asked for - a search, a page turned, a filter - puffs nothing, because
// everything on it is new and a whole list blinking says nothing about any of it.
listing.markNewRows = function() {
    var config = listing.config;
    var $itemsHost = listing.panes.items_host();
    var seenIds = {};
    var progressWords = {};

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        var rowModel = listing.visible[rowIndex];
        seenIds[rowModel.id] = true;

        if (listing.isLive && !listing.seenIds[rowModel.id]) {
            $itemsHost.find('[data-item-id="' + rowModel.id + '"]').addClass('kit-puff');
        }

        // The progress chip of a running row pulses when its words changed since the last poll.
        if (rowModel.outcome === config.runningOutcome) {
            var words = listing.sentenceOf(rowModel);
            progressWords[rowModel.id] = words;

            var wordsBefore = listing.progressWords[rowModel.id];

            if (wordsBefore !== undefined) {
                if (wordsBefore !== words) {
                    $itemsHost.find('[data-item-id="' + rowModel.id + '"] .' + config.progressChipClass)
                        .addClass('kit-pulse');
                }
            }
        }
    }

    listing.seenIds = seenIds;
    listing.progressWords = progressWords;

    // The list is drawn newest first, so the tint goes by where a row stands. It is laid on
    // without animating unless the page came in by itself - the rows are drawn afresh every
    // time, and fading each of them in would blink the whole list at every draw.
    kit.recency.apply_by_position({
        container: listing.config.itemsHost,
        item_selector: listing.config.itemSelector,
        rgb: listing.config.recencyRGB,
        animate: listing.isLive
    });
};

// /////////////////////////////////////////////////////////////////////////////

// A row keeps every column it has room for and gives up the next one at the moment it has not.
// Which moment that is, is measured rather than guessed - the columns are as wide as the data
// makes them, and a width written down here could only ever be a guess at what that comes to.
listing.fitColumns = function() {
    var config = listing.config;
    var $host = $(config.host);
    var tableElement = listing.panes.items_host().closest('table')[0];
    var listElement = tableElement.parentElement;

    // Everything is put back before the row is measured, so a pane being widened takes its
    // columns back in the reverse of the order it gave them up
    for (var index = 0; index < config.dropOrder.length; index++) {
        $host.removeClass(config.dropClassPrefix + config.dropOrder[index]);
    }

    for (var dropIndex = 0; dropIndex < config.dropOrder.length; dropIndex++) {

        // Reading the width is what settles the layout, so the row that is measured next is the
        // row as it stands with the column just given up already gone. It is the table that is
        // measured and not what the list scrolls over - a row that has just arrived puffs up for
        // a moment, and a puffed row reaches past the list without the table being any wider,
        // so a list measured by its scroll width while a drag happens mid-puff would give up
        // every column it has and get none of them back.
        if (tableElement.offsetWidth <= listElement.clientWidth) {
            break;
        }

        $host.addClass(config.dropClassPrefix + config.dropOrder[dropIndex]);
    }
};

// A list scrolls, and a scrolling box shows nothing painted outside it, so a mark that is to stand
// outside the rows cannot be part of one. The marks for the failed rows are drawn in a rail of their
// own beside the list, in the room the page already leaves at its edge, and each is held level with
// the row it belongs to. Nothing is added to the table, so no row moves and no column changes.
listing.rail = {};

listing.rail.parts = function() {
    var config = listing.config;
    var $list = listing.panes.items_host().closest('table').parent();

    // The rail stands next to the list rather than inside it, so it is a child of the pair
    var $pair = $list.parent();
    var $rail = $pair.children('.' + config.railClass);

    if ($rail.length === 0) {
        $rail = $('<div class="' + config.railClass + '"></div>');
        $pair.append($rail);
    }

    return {list: $list[0], pair: $pair[0], $rail: $rail};
};

// /////////////////////////////////////////////////////////////////////////////

listing.rail.sync = function() {
    var config = listing.config;
    var parts = listing.rail.parts();
    var listRect = parts.list.getBoundingClientRect();
    var pairRect = parts.pair.getBoundingClientRect();

    // The rail stands level with the list and no taller than it, which is what cuts a mark off as
    // the row it belongs to is scrolled out of sight rather than leaving it above the list
    parts.$rail.css({
        top: (listRect.top - pairRect.top) + 'px',
        height: listRect.height + 'px'
    });

    var rows = listing.panes.items_host().find('.' + config.errorRowClass);
    var marks = parts.$rail.children();

    // One mark per failed row. They are drawn again only when their number changes - a scroll
    // moves the ones already there rather than making them afresh.
    if (marks.length !== rows.length) {
        var html = '';

        for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
            html += '<div class="' + config.railMarkClass + '"></div>';
        }

        parts.$rail.html(html);
        marks = parts.$rail.children();
    }

    for (var markIndex = 0; markIndex < rows.length; markIndex++) {
        var rowRect = rows[markIndex].getBoundingClientRect();

        // Where the middle of the row falls inside the list, the mark being centred on that point
        marks[markIndex].style.top = (rowRect.top + rowRect.height / 2 - listRect.top) + 'px';
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A scroll asks for the marks to be moved far oftener than they can be drawn, so what it asks for
// is one move on the next frame and nothing more until that frame has been drawn.
listing.rail.pending = false;

listing.rail.schedule = function() {
    if (listing.rail.pending) {
        return;
    }

    listing.rail.pending = true;

    window.requestAnimationFrame(function() {
        listing.rail.pending = false;
        listing.rail.sync();
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.draw = function() {

    // Every row of the page is drawn - what the legend switches off never reaches
    // the page at all, the poll filters it out in the database
    listing.visible = listing.rowModels;

    // Which cells a row holds is settled before a single one of them is drawn.
    listing.updateColumns();

    listing.panes.set_items(listing.visible, listing.detached);
    listing.markNewRows();

    // What the rows just drawn are holding is what settles how much room the row needs, so which
    // columns fit is worked out after they are on the page rather than before
    listing.fitColumns();

    // Where the failed rows now stand is where their marks stand beside them
    listing.rail.sync();
};

// /////////////////////////////////////////////////////////////////////////////

// The ids of the rows the page keeps hearing about whether or not the next page still holds
// them - the running rows, whose words are still changing, and the selected row, so that new
// rows pushing it off the page never take the pane away from what is being read.
listing.watchedIds = function() {
    var config = listing.config;
    var out = [];

    for (var rowIndex = 0; rowIndex < listing.rowModels.length; rowIndex++) {
        var rowModel = listing.rowModels[rowIndex];

        if (rowModel.outcome === config.runningOutcome) {
            out.push(rowModel.id);
        }
    }

    if (listing.selected !== null) {
        if (out.indexOf(listing.selected.id) === -1) {
            out.push(listing.selected.id);
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The selected row among the updated ones, null when it is not among them.
listing.detachedModel = function(updated) {
    if (listing.selected === null) {
        return null;
    }

    for (var rowIndex = 0; rowIndex < updated.length; rowIndex++) {
        if (String(updated[rowIndex].id) === String(listing.selected.id)) {
            return listing.buildRow(updated[rowIndex]);
        }
    }

    return null;
};

// /////////////////////////////////////////////////////////////////////////////

listing.renderPage = function(_$body, rows, _total, updated) {
    listing.rowModels = listing.buildRows(rows);
    listing.detached = listing.detachedModel(updated);
    listing.draw();

    // Whatever brought the next page, it will have to say for itself that it came by
    // the clock rather than by the reader.
    listing.isLive = false;

    // A deep link may have asked for the resubmit confirmation on one of these rows
    listing.runPendingAction();
};

})(jQuery);
