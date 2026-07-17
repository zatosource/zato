
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.reports.config = {
    sortTypeText: 'text',
    sortTypeNumber: 'number',
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
