// Alert rules - durations and amounts.
//
// A duration is a number of seconds the screen shows as a count with a
// unit, an amount a count in ones shown as a fractional count with a
// unit. Both are edited the same way - a number with a hidden unit select
// next to it - and both go back to the backend as the plain number.

(function($) {

var screen = $.fn.zato.alerting_config;
var config = screen.config;

// ////////////////////////////////////////////////////////////////////////
//
// Durations
//
// ////////////////////////////////////////////////////////////////////////

// The hidden select a duration field's unit is edited through
screen.unitFieldName = function(fieldName) {
    var out = fieldName + config.unitFieldSuffix;
    return out;
};

// The unit a select value stands for
screen.durationUnit = function(unitValue) {

    var out = config.durationUnits[0];

    config.durationUnits.forEach(function(unit) {
        if(unit.value === unitValue) {
            out = unit;
        }
    });

    return out;
};

// A number of seconds as a count and the largest unit dividing it evenly -
// seconds no unit divides evenly are a fraction of the smallest one
screen.splitDuration = function(seconds) {

    var out = {count: seconds / config.durationUnits[0].seconds, unit: config.durationUnits[0]};

    config.durationUnits.forEach(function(unit) {
        if(seconds % unit.seconds === 0) {
            out = {count: seconds / unit.seconds, unit: unit};
        }
    });

    return out;
};

// A count of one unit back as seconds
screen.joinDuration = function(count, unitValue) {
    var out = Math.round(count * screen.durationUnit(unitValue).seconds);
    return out;
};

// What a duration cell reads as - 1 day, 10 minutes
screen.formatDuration = function(seconds) {
    var parts = screen.splitDuration(seconds);
    var out = $.fn.zato.count_text(parts.count, parts.unit.singular, parts.unit.plural);
    return out;
};

// ////////////////////////////////////////////////////////////////////////
//
// Amounts
//
// ////////////////////////////////////////////////////////////////////////

// The unit a select value stands for
screen.amountUnit = function(unitValue) {

    var out = config.amountUnits[0];

    config.amountUnits.forEach(function(unit) {
        if(unit.value === unitValue) {
            out = unit;
        }
    });

    return out;
};

// An amount as a count and the largest unit it reaches - an amount below
// the smallest unit is a fraction of it
screen.splitAmount = function(count) {

    var out = {count: count / config.amountUnits[0].size, unit: config.amountUnits[0]};

    config.amountUnits.forEach(function(unit) {
        if(count >= unit.size) {
            out = {count: count / unit.size, unit: unit};
        }
    });

    return out;
};

// A count of one unit back as whole ones
screen.joinAmount = function(count, unitValue) {
    var out = Math.round(count * screen.amountUnit(unitValue).size);
    return out;
};

// What an amount cell reads as - 10 millions, 1.5 millions
screen.formatAmount = function(count) {
    var parts = screen.splitAmount(count);
    var out = $.fn.zato.count_text(parts.count, parts.unit.singular, parts.unit.plural);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The hidden unit selects offer the same units, in the same words, as the cells show
screen.fillUnitSelect = function(select, units) {

    units.forEach(function(unit) {
        var option = document.createElement('option');
        option.value = unit.value;
        option.textContent = unit.plural;
        select.appendChild(option);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
