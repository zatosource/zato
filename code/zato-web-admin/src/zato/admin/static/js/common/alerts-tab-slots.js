
// /////////////////////////////////////////////////////////////////////////////
//
// Alerts tab - the time slots kind of its popovers. Loads before common/alerts-tab.js.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.alerts_tab');

// The relabel function of each slot's unit select, run again when its options are rebuilt
$.fn.zato.alerts_tab.slotRelabels = new WeakMap();

// /////////////////////////////////////////////////////////////////////////////

// The duration field of a slots line
$.fn.zato.alerts_tab.slotsDurationField = function(line) {

    var settings = $.fn.zato.alerts_tab.settings;
    var out = null;

    line.fields.forEach(function(fieldName) {
        if(settings.field_kinds[fieldName] === settings.duration_kind) {
            out = fieldName;
        }
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// A number of seconds as a count and the largest unit dividing it evenly
$.fn.zato.alerts_tab.splitDuration = function(seconds) {

    var units = $.fn.zato.alerts_tab.settings.duration_units;
    var smallest = units[0];
    var out = {count: seconds / smallest.seconds, unit: smallest.name};

    units.forEach(function(unit) {
        if(seconds % unit.seconds === 0) {
            out = {count: seconds / unit.seconds, unit: unit.name};
        }
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The seconds a count of a unit stands for
$.fn.zato.alerts_tab.joinDuration = function(count, unitName) {
    var unitSeconds = $.fn.zato.alerts_tab.settings.unit_seconds;
    var out = count * unitSeconds[unitName];
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The ranges kept in a line's hidden slots field
$.fn.zato.alerts_tab.readSlots = function(line) {
    var out = JSON.parse($.fn.zato.alerts_tab.field(line.slots_field).val());
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The units a slot's duration may be in - the All day slot has them all, a range only those
// shorter than the range itself
$.fn.zato.alerts_tab.slotUnitOptions = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var isDefault = slot.getAttribute('data-slot-type') === kit.config.slotDefault;
    var unitSeconds = tab.settings.unit_seconds;

    var rangeSeconds = 0;

    if(!isDefault) {
        var rangeMinutes = kit.rangeMinutes(slot.getAttribute('data-time-from'), slot.getAttribute('data-time-to'));
        rangeSeconds = rangeMinutes * tab.config.secondsPerMinute;
    }

    var out = [];

    tab.field(line.unit_field).find('option').each(function() {

        var isOffered = isDefault;

        if(!isOffered) {
            if(unitSeconds[this.value] < rangeSeconds) {
                isOffered = true;
            }
        }

        if(isOffered) {
            out.push({value: this.value, label: this.textContent});
        }
    });

    // The smallest unit stays whatever the range
    if(out.length === 0) {
        var first = tab.field(line.unit_field).find('option').first();
        out.push({value: first.val(), label: first.text()});
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Fills a slot's unit select with the units its range can hold, keeping the picked unit when it may
$.fn.zato.alerts_tab.fillUnitOptions = function(line, slot, unitSelect, unitName) {

    var options = $.fn.zato.alerts_tab.slotUnitOptions(line, slot);

    unitSelect.textContent = '';
    options.forEach(function(item) {
        var option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.label;
        unitSelect.appendChild(option);
    });

    var hasUnit = false;
    options.forEach(function(item) {
        if(item.value === unitName) {
            hasUnit = true;
        }
    });

    // A unit longer than the range gives way to the largest one the range holds
    if(hasUnit) {
        unitSelect.value = unitName;
    }
    else {
        var last = options[options.length - 1];
        unitSelect.value = last.value;
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Builds the switch and the duration of one slot
$.fn.zato.alerts_tab.buildSlotFields = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var settings = tab.settings;
    var durationField = tab.slotsDurationField(line);

    var switchGroup = kit.addGroup(slot);
    kit.addSwitch(switchGroup, tab.config.slotIsOn, true, settings.field_labels[line.off_field]);

    var durationGroup = kit.addGroup(slot);
    kit.addText(durationGroup, settings.field_labels[durationField], 'label');
    var countInput = kit.addInput(durationGroup, durationField, tab.field(durationField).val());
    var unitSelect = kit.addSelect(durationGroup, line.unit_field, []);

    tab.fillUnitOptions(line, slot, unitSelect, tab.field(line.unit_field).val());

    var relabel = tab.forms.bindUnitLabels(countInput, unitSelect);
    tab.slotRelabels.set(slot, relabel);
}

// /////////////////////////////////////////////////////////////////////////////

// A range's times were edited - its unit select offers what the new length can hold
$.fn.zato.alerts_tab.onSlotTimeChange = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var unitSelect = kit.field(slot, line.unit_field);

    tab.fillUnitOptions(line, slot, unitSelect, unitSelect.value);
    tab.slotRelabels.get(slot)();
}

// /////////////////////////////////////////////////////////////////////////////

// The switch, the count and the unit of one slot, as the kit's readFields
$.fn.zato.alerts_tab.readSlotFields = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var durationField = tab.slotsDurationField(line);

    var out = {
        is_on: kit.field(slot, tab.config.slotIsOn).checked,
        count: parseInt(kit.field(slot, durationField).value),
        unit: kit.field(slot, line.unit_field).value
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes one entry's switch, count and unit into a slot, as the kit's writeFields
$.fn.zato.alerts_tab.writeSlotFields = function(line, slot, entry) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var durationField = tab.slotsDurationField(line);

    kit.field(slot, tab.config.slotIsOn).checked = entry.is_on;
    tab.fillUnitOptions(line, slot, kit.field(slot, line.unit_field), entry.unit);

    // The unit select relabels itself on input, which a value set by hand does not fire
    var countInput = kit.field(slot, durationField);
    countInput.value = entry.count;

    var inputEvent = new Event('input');
    countInput.dispatchEvent(inputEvent);
}

// /////////////////////////////////////////////////////////////////////////////

// The entries the kit loads - the All day one from the line's own fields, the ranges from the slots field
$.fn.zato.alerts_tab.slotEntries = function(line) {

    var tab = $.fn.zato.alerts_tab;
    var durationField = tab.slotsDurationField(line);

    var out = [{
        is_all_day: true,
        is_on: tab.field(line.off_field).is(':checked'),
        count: parseInt(tab.field(durationField).val()),
        unit: tab.field(line.unit_field).val()
    }];

    tab.readSlots(line).forEach(function(range) {
        var duration = tab.splitDuration(range[tab.config.slotSeconds]);

        out.push({
            is_all_day: false,
            time_from: range[tab.config.slotTimeFrom],
            time_to: range[tab.config.slotTimeTo],
            is_on: range[tab.config.slotIsOn],
            count: duration.count,
            unit: duration.unit
        });
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes the slots kit of a line's popover back - the All day slot into the line's own fields, the ranges into the slots field
$.fn.zato.alerts_tab.saveSlots = function(line, slots) {

    var tab = $.fn.zato.alerts_tab;
    var durationField = tab.slotsDurationField(line);
    var ranges = [];

    slots.getEntries().forEach(function(entry) {

        if(entry.is_all_day) {
            tab.field(line.off_field).prop('checked', entry.is_on);
            tab.field(durationField).val(entry.count);
            tab.field(line.unit_field).val(entry.unit);
        }
        else {
            var range = {};
            range[tab.config.slotTimeFrom] = entry.time_from;
            range[tab.config.slotTimeTo] = entry.time_to;
            range[tab.config.slotIsOn] = entry.is_on;
            range[tab.config.slotSeconds] = tab.joinDuration(entry.count, entry.unit);
            ranges.push(range);
        }
    });

    tab.field(line.slots_field).val(JSON.stringify(ranges));
}

// /////////////////////////////////////////////////////////////////////////////

// Registers the time slots kind with the micro-forms kit
$.fn.zato.alerts_tab.registerSlotsKind = function() {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;

    tab.forms.registerKind(tab.settings.slots_kind, {

        build: function(fieldSpec, row) {

            var line = fieldSpec.line;

            // The kit dresses its own controls, the popover's input styles stay off them
            row.classList.add(tab.config.slotsFieldClass);

            var slots = kit.create({
                container: row,
                labels: kit.config.labels,
                toggles: [],
                withDisable: false,
                buildFields: function(slot) {
                    tab.buildSlotFields(line, slot);
                },
                readFields: function(slot) {
                    var out = tab.readSlotFields(line, slot);
                    return out;
                },
                writeFields: function(slot, entry) {
                    tab.writeSlotFields(line, slot, entry);
                },
                onTimeChange: function(slot) {
                    tab.onSlotTimeChange(line, slot);
                }
            });

            var entries = tab.slotEntries(line);
            slots.load(entries);

            tab.state.slotsKits[line.name] = slots;
        },

        save: function(popper, fieldSpec) {
            var line = fieldSpec.line;
            tab.saveSlots(line, tab.state.slotsKits[line.name]);
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////
