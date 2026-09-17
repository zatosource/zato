
// /////////////////////////////////////////////////////////////////////////////
//
// Time slots - a list of ranges of the day, each with values of its own, under an
// All day slot that answers whenever no range does. The host builds a slot's values.
//
// Works together with /static/css/shared/time-slots.css and needs the dashboard
// kit's select menu, /static/js/dashboard-kit/select.js, for the time suggestions,
// and /static/js/shared/time-slots-fields.js, which must load before this file.
//
// How to use:
//
//     var slots = $.fn.zato.time_slots.create({
//         container: someElement,
//         labels: {allDay: 'All day', add: '+ Add time range', delete: 'Delete', disable: 'Disable', enable: 'Enable'},
//         withDisable: true,
//         toggles: [{attr: 'disallowed', offLabel: 'Disallow traffic', onLabel: 'Allow traffic'}],
//         buildFields: function(slot, isDefault) { .. append the slot's inputs .. },
//         readFields: function(slot) { return {rate: ..}; },
//         writeFields: function(slot, entry) { .. },
//         onTimeChange: function(slot) { .. a range's times were edited .. }
//     });
//
//     slots.load(entries);           // [{is_all_day: true, ..}, {time_from: '09:00', time_to: '17:00', ..}]
//     var entries = slots.getEntries();
//
// An entry is the kit's own keys - is_all_day, time_from and time_to for a range,
// disabled with withDisable, one boolean per toggle under its attr - plus what
// readFields returned, and writeFields gets the very same shape back.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.time_slots');

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.config = {

    fromPlaceholder: 'from',
    toPlaceholder: 'to',

    // What a range reads as between its two times
    rangeSeparator: ' - ',

    // The times of a range are HH:MM, 24 hours
    timePattern: /^([01]\d|2[0-3]):([0-5]\d)$/,
    timeLength: 5,
    minutesPerHour: 60,
    minutesPerDay: 24 * 60,

    // What a time input lets through as it is typed into
    digitPattern: /^\d$/,
    passthroughKeys: ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Escape', 'Enter'],

    // The three lives of a slot - the one All day slot, a range, and a range still being typed in
    slotDefault: 'default',
    slotRange: 'range',
    slotPending: 'pending',

    disabledAttr: 'disabled',

    // The times offered under the from and to inputs
    timeSuggestions: [
        {group: 'Business hours', items: [
            {value: '06:00', label: '6 AM'},
            {value: '07:00', label: '7 AM'},
            {value: '08:00', label: '8 AM'},
            {value: '09:00', label: '9 AM'},
            {value: '10:00', label: '10 AM'},
            {value: '11:00', label: '11 AM'},
            {value: '12:00', label: 'noon'},
            {value: '13:00', label: '1 PM'},
            {value: '14:00', label: '2 PM'},
            {value: '15:00', label: '3 PM'},
            {value: '16:00', label: '4 PM'},
            {value: '17:00', label: '5 PM'},
            {value: '18:00', label: '6 PM'}
        ]},
        {group: 'Off hours', items: [
            {value: '19:00', label: '7 PM'},
            {value: '20:00', label: '8 PM'},
            {value: '21:00', label: '9 PM'},
            {value: '22:00', label: '10 PM'},
            {value: '23:00', label: '11 PM'},
            {value: '00:00', label: 'midnight'},
            {value: '01:00', label: '1 AM'},
            {value: '02:00', label: '2 AM'},
            {value: '03:00', label: '3 AM'},
            {value: '04:00', label: '4 AM'},
            {value: '05:00', label: '5 AM'}
        ]}
    ]
};

// The labels a host passes when it has none of its own
$.fn.zato.time_slots.config.labels = {
    allDay: 'All day',
    add: '+ Add time range',
    delete: 'Delete',
    disable: 'Disable',
    enable: 'Enable'
};

// /////////////////////////////////////////////////////////////////////////////
// The constructor
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.create = function(options) {

    var kit = $.fn.zato.time_slots;
    var config = kit.config;

    var labels = options.labels;
    var toggles = options.toggles;
    var withDisable = options.withDisable;

    var instance = {};

    var root = document.createElement('div');
    root.className = 'time-slots';
    options.container.appendChild(root);

    var addButton = document.createElement('span');
    addButton.className = 'time-slots-add';
    addButton.textContent = labels.add;
    addButton.onclick = function() {
        instance.beginAdd();
    };
    options.container.appendChild(addButton);

    instance.root = root;
    instance.addButton = addButton;

// /////////////////////////////////////////////////////////////////////////////

    // Flips one of a slot's flags - disabled or one of the host's toggles - and its link's text
    instance.setFlag = function(slot, attr, isOn, link) {

        if(isOn) {
            slot.setAttribute('data-' + attr, 'true');
            link.textContent = link.getAttribute('data-on-label');
        }
        else {
            slot.removeAttribute('data-' + attr);
            link.textContent = link.getAttribute('data-off-label');
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    // One link toggling one flag, in a cell of the actions area
    var addActionLink = function(actions, slot, className, attr, offLabel, onLabel) {

        var cell = document.createElement('div');
        cell.className = 'time-slot-action-cell';

        var link = document.createElement('a');
        link.href = 'javascript:void(0)';
        link.className = className;
        link.textContent = offLabel;
        link.setAttribute('data-toggle-attr', attr);
        link.setAttribute('data-on-label', onLabel);
        link.setAttribute('data-off-label', offLabel);
        link.onclick = function() {
            var isOn = slot.getAttribute('data-' + attr) === 'true';
            instance.setFlag(slot, attr, !isOn, link);
        };

        cell.appendChild(link);
        actions.appendChild(cell);

        var out = link;
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    // Builds one slot - the All day one or a range - with the host's fields in the middle
    var buildSlot = function(timeFrom, timeTo, isDefault) {

        var slot = document.createElement('div');
        slot.className = 'time-slot';

        if(isDefault) {
            slot.setAttribute('data-slot-type', config.slotDefault);
        }
        else {
            slot.setAttribute('data-slot-type', config.slotRange);
            slot.setAttribute('data-time-from', timeFrom);
            slot.setAttribute('data-time-to', timeTo);
        }

        var timeArea = document.createElement('div');
        timeArea.className = 'time-slot-time';

        var label = document.createElement('span');
        var labelText;

        if(isDefault) {
            label.className = 'time-slot-time-label';
            labelText = labels.allDay;
        }
        else {
            label.className = 'time-slot-time-label time-slot-time-label-editable';
            labelText = kit.rangeLabel(timeFrom, timeTo);
        }

        label.textContent = labelText;
        timeArea.appendChild(label);

        // A range's times are edited in place
        if(!isDefault) {
            label.onclick = function() {
                instance.editTime(slot, timeArea, label);
            };
        }

        slot.appendChild(timeArea);

        options.buildFields(slot, isDefault);

        var actions = document.createElement('div');
        actions.className = 'time-slot-actions';

        toggles.forEach(function(toggle) {
            addActionLink(actions, slot, 'time-slot-toggle', toggle.attr, toggle.offLabel, toggle.onLabel);
        });

        if(withDisable) {
            addActionLink(actions, slot, 'time-slot-disable', config.disabledAttr, labels.disable, labels.enable);
        }

        if(!isDefault) {
            var deleteCell = document.createElement('div');
            deleteCell.className = 'time-slot-action-cell';

            var deleteLink = document.createElement('a');
            deleteLink.href = 'javascript:void(0)';
            deleteLink.className = 'time-slot-delete';
            deleteLink.textContent = labels.delete;
            deleteLink.onclick = function() {
                root.removeChild(slot);
            };

            deleteCell.appendChild(deleteLink);
            actions.appendChild(deleteCell);
        }

        slot.appendChild(actions);
        root.appendChild(slot);

        // A slot built into a list already on screen locks its cells now, the All day slot
        // built before the list is attached waits for the host to call lockWidths
        if(root.isConnected) {
            kit.lockActionCells(slot);
        }

        var out = slot;
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.addSlot = function(timeFrom, timeTo) {
        var out = buildSlot(timeFrom, timeTo, false);
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.lockWidths = function() {
        kit.lockActionCells(instance.defaultSlot);
    };

// /////////////////////////////////////////////////////////////////////////////

    // Swaps a range's label for two inputs until both hold a time or the edit is left
    instance.editTime = function(slot, timeArea, label) {

        var openInput = timeArea.querySelector('.time-slot-time-input');

        if(openInput !== null) {
            return;
        }

        label.style.display = 'none';

        var fromInput = kit.buildTimeInput(config.fromPlaceholder, slot.getAttribute('data-time-from'));
        var toInput = kit.buildTimeInput(config.toPlaceholder, slot.getAttribute('data-time-to'));

        var dash = document.createElement('span');
        dash.className = 'time-slot-time-dash';
        dash.textContent = '-';

        timeArea.appendChild(fromInput);
        timeArea.appendChild(dash);
        timeArea.appendChild(toInput);

        var isFinished = false;

        var finish = function() {

            // Escape, a pick from the menu and focus leaving may each ask for this
            if(isFinished) {
                return;
            }

            isFinished = true;

            var newFrom = fromInput.value;
            var newTo = toInput.value;

            var hasNewFrom = config.timePattern.test(newFrom);
            var hasNewTo = config.timePattern.test(newTo);
            var hasNewTimes = false;

            if(hasNewFrom) {
                if(hasNewTo) {
                    hasNewTimes = true;
                }
            }

            if(hasNewTimes) {
                slot.setAttribute('data-time-from', newFrom);
                slot.setAttribute('data-time-to', newTo);
                label.textContent = kit.rangeLabel(newFrom, newTo);
            }

            timeArea.removeChild(fromInput);
            timeArea.removeChild(dash);
            timeArea.removeChild(toInput);

            label.style.display = '';
            kit.hideMenu();

            if(hasNewTimes) {
                if(options.onTimeChange !== null) {
                    options.onTimeChange(slot);
                }
            }
        };

        // Focus moving from one input to the other is not the end of the edit, focus
        // going anywhere else is
        var onBlur = function(input, otherInput, event) {
            kit.validateTimeInput(input);

            if(event.relatedTarget === otherInput) {
                return;
            }

            finish();
        };

        var showToMenu = function() {
            kit.showMenu(toInput, '', function(selectedValue) {
                toInput.value = selectedValue;
                finish();
            });
        };

        var showFromMenu = function() {
            kit.showMenu(fromInput, '', function(selectedValue) {
                fromInput.value = selectedValue;
                toInput.focus();
                showToMenu();
            });
        };

        fromInput.onkeydown = function(event) {
            kit.filterTimeKey(event);
            if(event.key === 'Escape') {
                finish();
            }
        };

        toInput.onkeydown = function(event) {
            kit.filterTimeKey(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                finish();
            }
            if(event.key === 'Escape') {
                finish();
            }
        };

        fromInput.onfocus = showFromMenu;
        toInput.onfocus = showToMenu;

        fromInput.onblur = function(event) {
            onBlur(fromInput, toInput, event);
        };

        toInput.onblur = function(event) {
            onBlur(toInput, fromInput, event);
        };

        fromInput.focus();
        fromInput.select();
    };

// /////////////////////////////////////////////////////////////////////////////

    // Adds a row of two time inputs that turns into a range once both hold a time
    instance.beginAdd = function() {

        var existingInput = root.querySelector('.time-slot-time-input');

        if(existingInput !== null) {
            existingInput.focus();
            return;
        }

        var pending = document.createElement('div');
        pending.className = 'time-slot';
        pending.setAttribute('data-slot-type', config.slotPending);

        var timeArea = document.createElement('div');
        timeArea.className = 'time-slot-time';

        var fromInput = kit.buildTimeInput(config.fromPlaceholder, '');
        var toInput = kit.buildTimeInput(config.toPlaceholder, '');

        var dash = document.createElement('span');
        dash.className = 'time-slot-time-dash';
        dash.textContent = '-';

        timeArea.appendChild(fromInput);
        timeArea.appendChild(dash);
        timeArea.appendChild(toInput);
        pending.appendChild(timeArea);
        root.appendChild(pending);

        var cancel = function() {
            kit.hideMenu();
            root.removeChild(pending);
        };

        var commit = function() {

            var fromValue = fromInput.value;
            var toValue = toInput.value;

            var hasFrom = config.timePattern.test(fromValue);
            var hasTo = config.timePattern.test(toValue);

            if(hasFrom) {
                if(hasTo) {
                    kit.hideMenu();
                    root.removeChild(pending);
                    instance.addSlot(fromValue, toValue);
                }
            }
        };

        var showToMenu = function() {
            kit.showMenu(toInput, toInput.value, function(selectedValue) {
                toInput.value = selectedValue;
                commit();
            });
        };

        var showFromMenu = function() {
            kit.showMenu(fromInput, fromInput.value, function(selectedValue) {
                fromInput.value = selectedValue;
                toInput.focus();
                showToMenu();
            });
        };

        fromInput.onfocus = showFromMenu;
        fromInput.oninput = showFromMenu;
        fromInput.onkeydown = function(event) {
            kit.filterTimeKey(event);
            if(event.key === 'Escape') {
                cancel();
            }
        };
        fromInput.onblur = function() {
            kit.validateTimeInput(fromInput);
        };

        toInput.onfocus = showToMenu;
        toInput.oninput = showToMenu;
        toInput.onkeydown = function(event) {
            kit.filterTimeKey(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                commit();
            }
            if(event.key === 'Escape') {
                cancel();
            }
        };
        toInput.onblur = function() {
            kit.validateTimeInput(toInput);
        };

        fromInput.focus();
    };

// /////////////////////////////////////////////////////////////////////////////

    // Every slot but a pending one, the All day slot first
    instance.slots = function() {
        var out = root.querySelectorAll('.time-slot:not([data-slot-type="' + config.slotPending + '"])');
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.getEntries = function() {

        var out = [];
        var slots = instance.slots();

        for(var idx = 0; idx < slots.length; idx++) {

            var slot = slots[idx];
            var isAllDay = slot.getAttribute('data-slot-type') === config.slotDefault;

            var entry = {is_all_day: isAllDay};

            if(withDisable) {
                entry[config.disabledAttr] = slot.getAttribute('data-' + config.disabledAttr) === 'true';
            }

            toggles.forEach(function(toggle) {
                entry[toggle.attr] = slot.getAttribute('data-' + toggle.attr) === 'true';
            });

            $.extend(entry, options.readFields(slot));

            if(!isAllDay) {
                entry.time_from = slot.getAttribute('data-time-from');
                entry.time_to = slot.getAttribute('data-time-to');
            }

            out.push(entry);
        }

        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    // Writes one entry's flags and fields into a slot
    var writeSlot = function(slot, entry) {

        options.writeFields(slot, entry);

        var links = slot.querySelectorAll('a[data-toggle-attr]');

        for(var idx = 0; idx < links.length; idx++) {
            var link = links[idx];
            var attr = link.getAttribute('data-toggle-attr');

            instance.setFlag(slot, attr, entry[attr], link);
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    // The All day entry goes into the All day slot, every other one adds a range
    instance.load = function(entries) {

        entries.forEach(function(entry) {

            var slot;

            if(entry.is_all_day) {
                slot = instance.defaultSlot;
            }
            else {
                slot = instance.addSlot(entry.time_from, entry.time_to);
            }

            writeSlot(slot, entry);
        });
    };

// /////////////////////////////////////////////////////////////////////////////

    // Every range added so far goes, the All day slot stays
    instance.clearRanges = function() {

        var ranges = root.querySelectorAll('.time-slot:not([data-slot-type="' + config.slotDefault + '"])');

        for(var idx = 0; idx < ranges.length; idx++) {
            root.removeChild(ranges[idx]);
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.defaultSlot = buildSlot('', '', true);

    var out = instance;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////
