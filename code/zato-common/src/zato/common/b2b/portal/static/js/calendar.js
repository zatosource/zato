'use strict';

// A calendar opens under a date field when the field is pressed. Its header has a select of the month
// and a select of the year, its grid has the days of that month, and a press on a day puts the day
// in the field in the ISO form and closes the calendar.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var calendar = {};

calendar.config = {
    theme: 'popup',
    placement: 'bottom-start',
    weekdays: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
    months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
        'November', 'December'],
    firstWeekday: 1,
    daysPerWeek: 7,
    yearsBefore: 5,
    yearsAfter: 10,
    isoPattern: /^(\d{4})-(\d{2})-(\d{2})$/
};

// ////////////////////////////////////////////////////////////////////////

calendar.pad = function(number) {
    var out = number < 10 ? '0' + number : String(number);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The month counts from zero, as it does in a Date.
calendar.isoDate = function(year, month, day) {
    var out = year + '-' + calendar.pad(month + 1) + '-' + calendar.pad(day);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

calendar.today = function() {
    var now = new Date();
    var out = calendar.isoDate(now.getFullYear(), now.getMonth(), now.getDate());
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The month a calendar opens at - the one of the date in the field, or the current one when the field is empty.
calendar.openingMonth = function(value) {

    var match = calendar.config.isoPattern.exec(value);

    if (match === null) {
        var now = new Date();
        return {year: now.getFullYear(), month: now.getMonth()};
    }

    var out = {year: parseInt(match[1], 10), month: parseInt(match[2], 10) - 1};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Inside a popover the calendar belongs to the popover, so a press on a day does not close the popover.
calendar.host = function(reference) {

    var root = reference.closest('[data-tippy-root]');
    var out = root === null ? document.body : root;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

calendar.attach = function(input) {

    input.type = 'text';
    input.readOnly = true;
    input.classList.add('calendar-field');

    var view = {year: 0, month: 0};

    var out = window.tippy(input, {
        content: '',
        trigger: 'click',
        interactive: true,
        hideOnClick: true,
        arrow: false,
        animation: false,
        theme: calendar.config.theme,
        placement: calendar.config.placement,
        offset: portal.config.popoverOffset,
        maxWidth: 'none',
        appendTo: calendar.host,
        onShow: function(instance) {
            var opening = calendar.openingMonth(input.value);
            view.year = opening.year;
            view.month = opening.month;
            instance.setContent(calendar.build(input, view, instance));
        },
        onHidden: function(instance) {
            instance.setContent('');
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

calendar.buildSelect = function(labels, values, value) {

    var select = portal.create('select', '', '');

    for (var index = 0; index < values.length; index++) {
        var option = portal.create('option', '', labels[index]);
        option.value = String(values[index]);
        select.appendChild(option);
    }

    select.value = String(value);

    return select;
};

// ////////////////////////////////////////////////////////////////////////

calendar.yearValues = function(shownYear) {

    var currentYear = new Date().getFullYear();
    var first = Math.min(currentYear - calendar.config.yearsBefore, shownYear);
    var last = Math.max(currentYear + calendar.config.yearsAfter, shownYear);
    var out = [];

    for (var year = first; year <= last; year++) {
        out.push(year);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

calendar.build = function(input, view, instance) {

    var container = portal.create('div', 'popup calendar', '');
    var header = portal.create('div', 'calendar-header', '');
    var grid = portal.create('div', 'calendar-grid', '');

    var monthValues = [];
    for (var month = 0; month < calendar.config.months.length; month++) {
        monthValues.push(month);
    }

    var years = calendar.yearValues(view.year);
    var monthSelect = calendar.buildSelect(calendar.config.months, monthValues, view.month);
    var yearSelect = calendar.buildSelect(years, years, view.year);

    var onChange = function() {
        view.month = parseInt(monthSelect.value, 10);
        view.year = parseInt(yearSelect.value, 10);
        calendar.fillGrid(grid, input, view, instance);
    };

    monthSelect.addEventListener('change', onChange);
    yearSelect.addEventListener('change', onChange);

    header.appendChild(monthSelect);
    header.appendChild(yearSelect);

    container.appendChild(header);
    container.appendChild(grid);

    calendar.fillGrid(grid, input, view, instance);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

calendar.fillGrid = function(grid, input, view, instance) {

    var config = calendar.config;
    grid.textContent = '';

    for (var weekdayIndex = 0; weekdayIndex < config.weekdays.length; weekdayIndex++) {
        grid.appendChild(portal.create('span', 'calendar-weekday', config.weekdays[weekdayIndex]));
    }

    // .. the first day of the month stands under its own weekday ..
    var firstWeekday = new Date(view.year, view.month, 1).getDay();
    var blanks = (firstWeekday - config.firstWeekday + config.daysPerWeek) % config.daysPerWeek;

    // .. and day zero of the next month is the last day of this one ..
    var dayCount = new Date(view.year, view.month + 1, 0).getDate();

    for (var blankIndex = 0; blankIndex < blanks; blankIndex++) {
        grid.appendChild(portal.create('span', '', ''));
    }

    var today = calendar.today();

    for (var day = 1; day <= dayCount; day++) {

        var iso = calendar.isoDate(view.year, view.month, day);

        var button = portal.create('button', 'calendar-day', String(day));
        button.type = 'button';
        button.classList.toggle('calendar-day-today', iso === today);
        button.classList.toggle('calendar-day-on', iso === input.value);
        button.addEventListener('click', calendar.pick.bind(null, input, iso, instance));

        grid.appendChild(button);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The field tells its listeners of the new day the way typing into it would.
calendar.pick = function(input, iso, instance) {

    input.value = iso;
    input.dispatchEvent(new Event('input', {bubbles: true}));

    instance.hide();
};

// ////////////////////////////////////////////////////////////////////////

portal.calendar = calendar;

// ////////////////////////////////////////////////////////////////////////

})();
