// The date and time picker - the format grammar and the calendar maths.
//
// The tokens are the ones the jQuery UI datepicker and the timepicker addon
// used, so the formats the backend hands out in js_date_format and
// js_time_format keep working unchanged. Loaded before datetime-picker.js,
// which fills the rest of the namespace this file opens.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.datetime_picker = {};

var picker = $.fn.zato.datetime_picker;

// ////////////////////////////////////////////////////////////////////////

picker.pad = function(value) {
    return value < 10 ? '0' + value : String(value);
};

// ////////////////////////////////////////////////////////////////////////

// The jQuery UI date tokens - d, dd, m, mm, y for two digits, yy for four
picker.formatDate = function(date, format) {
    var out = '';
    var position = 0;
    while(position < format.length) {
        if(format.substr(position, 2) === 'dd') { out += picker.pad(date.getDate()); position += 2; }
        else if(format[position] === 'd') { out += date.getDate(); position += 1; }
        else if(format.substr(position, 2) === 'mm') { out += picker.pad(date.getMonth() + 1); position += 2; }
        else if(format[position] === 'm') { out += (date.getMonth() + 1); position += 1; }
        else if(format.substr(position, 2) === 'yy') { out += date.getFullYear(); position += 2; }
        else if(format[position] === 'y') { out += picker.pad(date.getFullYear() % 100); position += 1; }
        else { out += format[position]; position += 1; }
    }
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The timepicker addon time tokens - h, hh, m, mm, s, ss, TT for AM/PM
picker.formatTime = function(date, format, ampm) {
    var hours = date.getHours();
    var suffix = '';
    if(ampm) {
        suffix = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        if(hours === 0) {
            hours = 12;
        }
    }
    var out = '';
    var position = 0;
    while(position < format.length) {
        if(format.substr(position, 2) === 'hh') { out += picker.pad(hours); position += 2; }
        else if(format[position] === 'h') { out += hours; position += 1; }
        else if(format.substr(position, 2) === 'mm') { out += picker.pad(date.getMinutes()); position += 2; }
        else if(format[position] === 'm') { out += date.getMinutes(); position += 1; }
        else if(format.substr(position, 2) === 'ss') { out += picker.pad(date.getSeconds()); position += 2; }
        else if(format[position] === 's') { out += date.getSeconds(); position += 1; }
        else if(format.substr(position, 2) === 'TT') { out += suffix; position += 2; }
        else if(format.substr(position, 2) === 'tt') { out += suffix.toLowerCase(); position += 2; }
        else { out += format[position]; position += 1; }
    }
    return out;
};

// ////////////////////////////////////////////////////////////////////////

picker.format = function(date, options) {
    return picker.formatDate(date, options.dateFormat) + ' ' + picker.formatTime(date, options.timeFormat, options.ampm);
};

// ////////////////////////////////////////////////////////////////////////

// Any run of digits is a field, in the order the format names them, so a
// hand-edited value still comes back as a date. Null when there is none.
picker.parse = function(text, options) {

    var numbers = text.match(/\d+/g);
    if(!numbers) {
        return null;
    }

    var dateOrder = options.dateFormat.match(/d+|m+|y+/g);
    var timeOrder = options.timeFormat.match(/h+|m+|s+/g);
    var now = new Date();

    var parts = {
        year: now.getFullYear(),
        month: now.getMonth() + 1,
        day: now.getDate(),
        hours: 0,
        minutes: 0,
        seconds: 0
    };
    var dateKeys = {d: 'day', m: 'month', y: 'year'};
    var timeKeys = ['hours', 'minutes', 'seconds'];

    var cursor = 0;

    for(var dateIdx = 0; dateIdx < dateOrder.length && cursor < numbers.length; dateIdx++) {
        var value = parseInt(numbers[cursor], 10);
        var token = dateOrder[dateIdx];
        if(token === 'y' && value < 100) {
            value += 2000;
        }
        parts[dateKeys[token[0]]] = value;
        cursor += 1;
    }

    for(var timeIdx = 0; timeIdx < timeOrder.length && cursor < numbers.length; timeIdx++) {
        parts[timeKeys[timeIdx]] = parseInt(numbers[cursor], 10);
        cursor += 1;
    }

    if(options.ampm) {
        var isPm = /pm/i.test(text);
        var isAm = /am/i.test(text);
        if(isPm && parts.hours < 12) { parts.hours += 12; }
        if(isAm && parts.hours === 12) { parts.hours = 0; }
    }

    var date = new Date(parts.year, parts.month - 1, parts.day, parts.hours, parts.minutes, parts.seconds);
    return isNaN(date.getTime()) ? null : date;
};

// ////////////////////////////////////////////////////////////////////////

// Six rows of seven cells - each cell a Date plus whether it belongs to the month shown
picker.monthMatrix = function(year, month) {
    var first = new Date(year, month, 1);
    var lead = (first.getDay() - picker.config.firstDay + 7) % 7;
    var start = new Date(year, month, 1 - lead);
    var rows = [];
    for(var rowIdx = 0; rowIdx < 6; rowIdx++) {
        var row = [];
        for(var columnIdx = 0; columnIdx < 7; columnIdx++) {
            var cell = new Date(start.getFullYear(), start.getMonth(), start.getDate() + rowIdx * 7 + columnIdx);
            row.push({date: cell, inMonth: cell.getMonth() === month});
        }
        rows.push(row);
    }
    return rows;
};

// ////////////////////////////////////////////////////////////////////////

picker.sameDay = function(first, second) {
    return first.getFullYear() === second.getFullYear() && first.getMonth() === second.getMonth() && first.getDate() === second.getDate();
};

// ////////////////////////////////////////////////////////////////////////

picker.range = function(from, to) {
    var out = [];
    for(var value = from; value <= to; value++) {
        out.push(value);
    }
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Today at the next full hour, seconds zeroed - what an empty field opens on
picker.defaultValue = function() {
    var now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1, 0, 0);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
