
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.config = {
    sortTypeText: 'text',
    sortTypeNumber: 'number',

    // The filter selects of the usage page - what each one is called, what its
    // everything entry says, what several picks at once are counted in, where each
    // one is rendered and the face its trigger wears, the same the audit log uses
    sourceSelectLabel: 'Type',
    objectSelectLabel: 'Name',
    allLabel: 'All',
    manySourcesLabel: 'types',
    manyObjectsLabel: 'names',

    // Short on purpose - it stands in the same badge All does, so swapping
    // the two must not resize the select
    noMatchesLabel: 'None',

    sourceSelectHost: '#report-filter-source',
    objectSelectHost: '#report-filter-object',
    sourcesInput: '#report-filter-sources',
    objectsInput: '#report-filter-objects',
    filterTriggerCls: 'dashboard-select-face'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.getCellValue = function(row, columnIndex) {
    var cell = $(row).children('td').eq(columnIndex);
    var out = cell.text().trim();
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.compareValues = function(first, second, sortType) {
    var config = $.fn.zato.b2b.reports.config;

    // Count columns compare numerically ..
    if(sortType === config.sortTypeNumber) {
        var firstNumber = parseFloat(first);
        var secondNumber = parseFloat(second);

        // .. cells without a number, e.g. the --- of an empty document type, sort last ..
        if(isNaN(firstNumber)) {
            firstNumber = -1;
        }
        if(isNaN(secondNumber)) {
            secondNumber = -1;
        }

        return firstNumber - secondNumber;
    }

    // .. and everything else compares as text.
    if(first < second) {
        return -1;
    }
    if(first > second) {
        return 1;
    }
    return 0;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.sortTable = function(table, columnIndex, sortType, isAscending) {
    var body = table.find('tbody');
    var rows = body.children('tr').get();

    rows.sort(function(firstRow, secondRow) {
        var firstValue = $.fn.zato.b2b.reports.getCellValue(firstRow, columnIndex);
        var secondValue = $.fn.zato.b2b.reports.getCellValue(secondRow, columnIndex);

        var out = $.fn.zato.b2b.reports.compareValues(firstValue, secondValue, sortType);

        if(!isAscending) {
            out = -out;
        }

        return out;
    });

    // Reattach the rows in their new order, restriping them as they go.
    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = $(rows[rowIndex]);
        row.removeClass('odd even');

        if(rowIndex % 2 === 0) {
            row.addClass('odd');
        }
        else {
            row.addClass('even');
        }

        body.append(row);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.onHeaderClick = function(header) {
    var table = header.closest('table');
    var columnIndex = header.index();
    var sortType = header.attr('data-sort-type');

    // Each click flips the direction of the clicked column.
    var isAscending = header.attr('data-sort-ascending') !== '1';

    table.find('th').removeAttr('data-sort-ascending');
    header.attr('data-sort-ascending', isAscending ? '1' : '0');

    $.fn.zato.b2b.reports.sortTable(table, columnIndex, sortType, isAscending);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.init = function() {
    $('table.b2b-report-table').on('click', 'th.b2b-report-sortable', function() {
        $.fn.zato.b2b.reports.onHeaderClick($(this));
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.init_filter_selects = function(formId, filterOptions, pickedSources, pickedObjects) {
    var config = $.fn.zato.b2b.reports.config;
    var kit = $.fn.zato.dashboard_kit;
    var form = $('#' + formId);

    // The type entries the source select offers, one per covered source
    var sourceItems = [];

    for (var optionIndex = 0; optionIndex < filterOptions.length; optionIndex++) {
        var option = filterOptions[optionIndex];
        sourceItems.push({value: option.source, label: option.label});
    }

    // The object groups the picked sources leave on offer - each name is listed once,
    // because the report filters events by name alone
    var objectGroups = function(sources) {
        var out = [];
        var seen = {};

        for (var groupIndex = 0; groupIndex < filterOptions.length; groupIndex++) {
            var option = filterOptions[groupIndex];

            if (sources.length && sources.indexOf(option.source) === -1) {
                continue;
            }

            var items = [];

            for (var objectIndex = 0; objectIndex < option.objects.length; objectIndex++) {
                var name = option.objects[objectIndex];

                if (seen[name]) {
                    continue;
                }

                seen[name] = true;
                items.push({value: name, label: name});
            }

            if (items.length) {
                out.push({group: option.label, items: items});
            }
        }

        return out;
    };

    // Whether an object is still on offer once the sources have changed underneath it
    var hasObject = function(groups, value) {
        for (var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
            var items = groups[groupIndex].items;

            for (var itemIndex = 0; itemIndex < items.length; itemIndex++) {
                if (items[itemIndex].value === value) {
                    return true;
                }
            }
        }

        return false;
    };

    // The picks reload the report - they land in the hidden inputs and the GET form
    // carries them, the same way the range tabs do. The reload waits until the menu
    // closes, so several values can be toggled in one visit.
    var submitWith = function(sources, objects) {
        $(config.sourcesInput).val(sources.join(','));
        $(config.objectsInput).val(objects.join(','));
        form.trigger('submit');
    };

    var sourcesChanged = false;
    var objectsChanged = false;

    var initialObjectGroups = objectGroups(pickedSources);

    var objectSelect = kit.select.create({
        host: config.objectSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.objectSelectLabel,
        groups: initialObjectGroups,
        multi: true,
        values: pickedObjects,
        empty_label: config.allLabel,
        many_label: config.manyObjectsLabel,
        disabled_label: config.noMatchesLabel,
        on_change: function() {
            objectsChanged = true;
        },
        on_close: function() {
            if (objectsChanged) {
                submitWith(sourceSelect.get_values(), objectSelect.get_values());
            }
        }
    });

    // With no objects on offer there is nothing to filter by and the select stands aside
    objectSelect.set_enabled(initialObjectGroups.length > 0);

    var sourceSelect = kit.select.create({
        host: config.sourceSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.sourceSelectLabel,
        groups: [{group: '', items: sourceItems}],
        multi: true,
        values: pickedSources,
        empty_label: config.allLabel,
        many_label: config.manySourcesLabel,
        on_change: function() {
            sourcesChanged = true;
        },
        on_close: function() {
            if (!sourcesChanged) {
                return;
            }

            // An object of some source no longer picked is no filter for these
            var values = sourceSelect.get_values();
            var newGroups = objectGroups(values);
            var currentObjects = objectSelect.get_values();
            var keptObjects = [];

            for (var pickedIndex = 0; pickedIndex < currentObjects.length; pickedIndex++) {
                if (hasObject(newGroups, currentObjects[pickedIndex])) {
                    keptObjects.push(currentObjects[pickedIndex]);
                }
            }

            submitWith(values, keptObjects);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.init_filter_tabs = function(formId, rangeInputId) {
    var form = $('#' + formId);
    var rangeInput = $('#' + rangeInputId);

    // Each tab carries its range value - clicking one applies it immediately
    // by writing it into the hidden input and submitting the GET form.
    form.on('click', '.dashboard-tab', function() {
        var tab = $(this);
        rangeInput.val(tab.attr('data-range'));
        form.trigger('submit');
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
