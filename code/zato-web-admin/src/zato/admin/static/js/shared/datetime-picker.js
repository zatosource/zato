// The date and time picker - three months side by side in the shared popup
// chrome, the time as selects for the hour, the minute and the second.
//
// It is attached the way the jQuery UI timepicker addon used to be, through
// $(field).datetimepicker({dateFormat, timeFormat, ampm}), with the same
// option names and the same token grammar, so the value written back into
// the field is exactly what the backend parses. The look lives in
// css/shared/datetime-picker.css, the chrome and the dragging come from
// shared/popup.css and shared/popup.js, the format grammar and the calendar
// maths from shared/datetime-picker-format.js, which opens the namespace.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var picker = $.fn.zato.datetime_picker;

picker.config = {
    popupClass: 'zato-popup zato-datetime-picker',
    stateKey: 'zato-datetime-picker',
    popupOffset: 4,
    monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'],
    dayNames: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
    dayNamesLong: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    firstDay: 1,
    monthsShown: 3,
    holdDelay: 400,
    holdInterval: 70,
    wheelCooldown: 120,
    svgNamespace: 'http://www.w3.org/2000/svg',
    iconPaths: {
        'chevron-left': 'm15 18-6-6 6-6',
        'chevron-right': 'm9 18 6-6-6-6',
        'x': 'M18 6 6 18M6 6l12 12'
    },
    labels: {
        hour: 'Hour',
        minute: 'Minute',
        second: 'Second',
        meridiem: 'AM/PM',
        now: 'Now',
        cancel: 'Cancel',
        ok: 'OK'
    }
};

// ////////////////////////////////////////////////////////////////////////

picker.element = function(tag, className, text) {
    var node = document.createElement(tag);
    node.className = className;
    if(text !== undefined) {
        node.textContent = text;
    }
    return node;
};

// ////////////////////////////////////////////////////////////////////////

picker.icon = function(name) {
    var svg = document.createElementNS(picker.config.svgNamespace, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('class', 'zato-datetime-picker-icon');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS(picker.config.svgNamespace, 'path');
    path.setAttribute('d', picker.config.iconPaths[name]);
    svg.appendChild(path);
    return svg;
};

// ////////////////////////////////////////////////////////////////////////

picker.iconButton = function(className, iconName) {
    var button = picker.element('button', className);
    button.type = 'button';
    button.appendChild(picker.icon(iconName));
    return button;
};

// ////////////////////////////////////////////////////////////////////////

// A button that fires once on press and then keeps firing while held
picker.holdable = function(button, action) {

    var timer = null;

    var stop = function() {
        clearTimeout(timer);
        clearInterval(timer);
        timer = null;
        document.removeEventListener('mouseup', stop);
    };

    button.addEventListener('mousedown', function(event) {
        if(event.button !== 0) {
            return;
        }
        event.preventDefault();
        action();
        timer = setTimeout(function() {
            timer = setInterval(action, picker.config.holdInterval);
        }, picker.config.holdDelay);
        document.addEventListener('mouseup', stop);
    });

    button.addEventListener('mouseleave', stop);

    button.addEventListener('keydown', function(event) {
        if(event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            action();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// Under the field, or above it when there is no room below, never off the right edge
picker.position = function(popup, input) {
    var box = input.getBoundingClientRect();
    var top = box.bottom + window.scrollY + picker.config.popupOffset;
    var left = box.left + window.scrollX;
    var popupBox = popup.getBoundingClientRect();
    if(box.bottom + popupBox.height + picker.config.popupOffset > window.innerHeight && box.top > popupBox.height) {
        top = box.top + window.scrollY - popupBox.height - picker.config.popupOffset;
    }
    if(left + popupBox.width > window.scrollX + window.innerWidth) {
        left = Math.max(window.scrollX, box.right + window.scrollX - popupBox.width);
    }
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
};

// ////////////////////////////////////////////////////////////////////////

// A select bound to one part of the time
picker.boundSelect = function(api, values, labels, read, write) {

    var select = picker.element('select', 'zato-datetime-picker-select');

    for(var valueIdx = 0; valueIdx < values.length; valueIdx++) {
        var option = picker.element('option', '', labels[valueIdx]);
        option.value = values[valueIdx];
        select.appendChild(option);
    }

    var refresh = function() {
        select.value = read(api.state.value);
    };

    select.onchange = function() {
        write(parseInt(select.value, 10));
    };

    refresh();
    api.onChange(refresh);
    return select;
};

// ////////////////////////////////////////////////////////////////////////

picker.field = function(label, control) {
    var wrapper = picker.element('label', 'zato-datetime-picker-field');
    wrapper.appendChild(picker.element('span', 'zato-datetime-picker-label', label));
    wrapper.appendChild(control);
    return wrapper;
};

// ////////////////////////////////////////////////////////////////////////

picker.renderMonth = function(api, year, month) {

    var today = new Date();
    var isCurrentMonth = year === today.getFullYear() && month === today.getMonth();

    var block = picker.element('div', 'zato-datetime-picker-month');

    var titleClass = 'zato-datetime-picker-month-title';
    if(isCurrentMonth) {
        titleClass += ' zato-datetime-picker-month-title-current';
    }
    block.appendChild(picker.element('div', titleClass, picker.config.monthNames[month] + ' ' + year));

    var names = picker.element('div', 'zato-datetime-picker-grid zato-datetime-picker-grid-names');
    for(var dayIdx = 0; dayIdx < 7; dayIdx++) {
        names.appendChild(picker.element('span', '', picker.config.dayNames[dayIdx]));
    }
    block.appendChild(names);

    var grid = picker.element('div', 'zato-datetime-picker-grid');
    var matrix = picker.monthMatrix(year, month);

    for(var rowIdx = 0; rowIdx < matrix.length; rowIdx++) {
        for(var columnIdx = 0; columnIdx < 7; columnIdx++) {
            grid.appendChild(picker.renderDay(api, matrix[rowIdx][columnIdx], today));
        }
    }

    block.appendChild(grid);
    return block;
};

// ////////////////////////////////////////////////////////////////////////

picker.renderDay = function(api, cell, today) {

    // Days of the neighbouring months are blank - they have their own block
    if(!cell.inMonth) {
        return picker.element('span', 'zato-datetime-picker-day-blank');
    }

    var className = 'zato-datetime-picker-day';
    if(picker.sameDay(cell.date, today)) {
        className += ' zato-datetime-picker-day-today';
    }
    if(picker.sameDay(cell.date, api.state.value)) {
        className += ' zato-datetime-picker-day-selected';
    }

    var day = picker.element('button', className, cell.date.getDate());
    day.type = 'button';
    day.onclick = function() {
        api.setDate(cell.date.getFullYear(), cell.date.getMonth(), cell.date.getDate());
    };
    return day;
};

// ////////////////////////////////////////////////////////////////////////

picker.renderTime = function(api) {

    var row = picker.element('div', 'zato-datetime-picker-time');
    var labels = picker.config.labels;
    var sixty = picker.range(0, 59);
    var sixtyLabels = sixty.map(picker.pad);

    var hourValues;
    var hourLabels;
    var readHour;
    var writeHour;

    if(api.options.ampm) {
        hourValues = picker.range(1, 12);
        hourLabels = hourValues.map(String);
        readHour = function(value) {
            var shown = value.getHours() % 12;
            return shown === 0 ? 12 : shown;
        };
        writeHour = function(pickedHour) {
            var isPm = api.state.value.getHours() >= 12;
            api.setTime((pickedHour % 12) + (isPm ? 12 : 0), api.state.value.getMinutes(), api.state.value.getSeconds());
        };
    }
    else {
        hourValues = picker.range(0, 23);
        hourLabels = hourValues.map(picker.pad);
        readHour = function(value) {
            return value.getHours();
        };
        writeHour = function(pickedHour) {
            api.setTime(pickedHour, api.state.value.getMinutes(), api.state.value.getSeconds());
        };
    }

    row.appendChild(picker.field(labels.hour, picker.boundSelect(api, hourValues, hourLabels, readHour, writeHour)));

    row.appendChild(picker.field(labels.minute, picker.boundSelect(api, sixty, sixtyLabels,
        function(value) { return value.getMinutes(); },
        function(pickedMinute) { api.setTime(api.state.value.getHours(), pickedMinute, api.state.value.getSeconds()); })));

    row.appendChild(picker.field(labels.second, picker.boundSelect(api, sixty, sixtyLabels,
        function(value) { return value.getSeconds(); },
        function(pickedSecond) { api.setTime(api.state.value.getHours(), api.state.value.getMinutes(), pickedSecond); })));

    if(api.options.ampm) {
        row.appendChild(picker.field(labels.meridiem, picker.boundSelect(api, [0, 12], ['AM', 'PM'],
            function(value) { return value.getHours() >= 12 ? 12 : 0; },
            function(pickedHalf) {
                var value = api.state.value;
                api.setTime((value.getHours() % 12) + pickedHalf, value.getMinutes(), value.getSeconds());
            })));
    }

    return row;
};

// ////////////////////////////////////////////////////////////////////////

picker.renderButtons = function(api) {

    var labels = picker.config.labels;
    var buttons = picker.element('div', 'zato-datetime-picker-buttons');

    var nowButton = picker.element('button', 'zato-datetime-picker-button', labels.now);
    var cancelButton = picker.element('button', 'zato-datetime-picker-button', labels.cancel);
    var okButton = picker.element('button', 'zato-datetime-picker-button zato-datetime-picker-button-primary', labels.ok);

    nowButton.type = 'button';
    cancelButton.type = 'button';
    okButton.type = 'button';

    nowButton.onclick = function() { api.setValue(new Date()); };
    cancelButton.onclick = api.close;
    okButton.onclick = api.commit;

    buttons.appendChild(nowButton);
    buttons.appendChild(cancelButton);
    buttons.appendChild(okButton);
    return buttons;
};

// ////////////////////////////////////////////////////////////////////////

picker.render = function(popup, api) {

    // The header - the pick so far, the drag handle, the close mark ..
    var header = picker.element('div', 'zato-popup-header zato-datetime-picker-header');
    var title = picker.element('span', 'zato-datetime-picker-title');
    var closeMark = picker.iconButton('zato-datetime-picker-close', 'x');
    closeMark.onclick = api.close;
    header.appendChild(title);
    header.appendChild(closeMark);
    popup.appendChild(header);

    $.fn.zato.popup.install_drag(header, {
        dragging_elem: popup,
        should_ignore: function(target) { return !!target.closest('button'); },
        on_start: function() {
            api.pinned = true;
            return {x: popup.offsetLeft, y: popup.offsetTop};
        },
        on_move: function(x, y) {
            popup.style.left = x + 'px';
            popup.style.top = y + 'px';
        }
    });

    // .. the months, with the wheel over them turning the pages ..
    var body = picker.element('div', 'zato-datetime-picker-body');
    popup.appendChild(body);

    var months = picker.element('div', 'zato-datetime-picker-months');
    var previous = picker.iconButton('zato-datetime-picker-arrow', 'chevron-left');
    var next = picker.iconButton('zato-datetime-picker-arrow', 'chevron-right');
    var pages = picker.element('div', 'zato-datetime-picker-pages');
    picker.holdable(previous, function() { api.moveMonth(-1); });
    picker.holdable(next, function() { api.moveMonth(1); });
    months.appendChild(previous);
    months.appendChild(pages);
    months.appendChild(next);
    body.appendChild(months);

    var lastWheel = 0;
    months.addEventListener('wheel', function(event) {
        event.preventDefault();
        var now = Date.now();
        if(now - lastWheel < picker.config.wheelCooldown) {
            return;
        }
        lastWheel = now;
        api.moveMonth(event.deltaY > 0 ? 1 : -1);
    }, {passive: false});

    // .. the time and the buttons.
    body.appendChild(picker.renderTime(api));
    body.appendChild(picker.renderButtons(api));

    var draw = function() {
        pages.innerHTML = '';
        var sideMonths = Math.floor(picker.config.monthsShown / 2);
        for(var offset = -sideMonths; offset <= sideMonths; offset++) {
            var shifted = new Date(api.state.viewYear, api.state.viewMonth + offset, 1);
            pages.appendChild(picker.renderMonth(api, shifted.getFullYear(), shifted.getMonth()));
        }

        var value = api.state.value;
        var weekday = picker.config.dayNamesLong[(value.getDay() + 6) % 7];
        title.textContent = weekday + ', ' + value.getDate() + ' ' + picker.config.monthNames[value.getMonth()] + ' ' +
            value.getFullYear() + ', ' + picker.formatTime(value, api.options.timeFormat, api.options.ampm);
    };

    draw();
    api.onChange(draw);
};

// ////////////////////////////////////////////////////////////////////////

picker.attach = function(input, options) {

    var popup = picker.element('div', picker.config.popupClass);
    popup.hidden = true;
    document.body.appendChild(popup);

    var listeners = [];

    var api = {
        input: input,
        popup: popup,
        options: options,
        pinned: false,
        state: {
            value: null,
            viewYear: 0,
            viewMonth: 0
        },
        onChange: function(listener) {
            listeners.push(listener);
        },
        notify: function() {
            for(var listenerIdx = 0; listenerIdx < listeners.length; listenerIdx++) {
                listeners[listenerIdx]();
            }
        }
    };

    var readInput = function() {
        var parsed = null;
        if(input.value) {
            parsed = picker.parse(input.value, options);
        }
        if(parsed === null) {
            parsed = picker.defaultValue();
        }
        api.state.value = parsed;
        api.state.viewYear = parsed.getFullYear();
        api.state.viewMonth = parsed.getMonth();
    };

    api.write = function() {
        input.value = picker.format(api.state.value, options);
        $(input).trigger('change');
    };

    // The months shown stay where they are when a day in a side month is picked
    api.setDate = function(year, month, day) {
        var value = api.state.value;
        api.state.value = new Date(year, month, day, value.getHours(), value.getMinutes(), value.getSeconds());
        api.write();
        api.notify();
    };

    api.setTime = function(hours, minutes, seconds) {
        var value = api.state.value;
        api.state.value = new Date(value.getFullYear(), value.getMonth(), value.getDate(), hours, minutes, seconds);
        api.write();
        api.notify();
    };

    api.setValue = function(date) {
        api.state.value = new Date(date.getTime());
        api.state.viewYear = date.getFullYear();
        api.state.viewMonth = date.getMonth();
        api.write();
        api.notify();
    };

    api.moveMonth = function(delta) {
        var shifted = new Date(api.state.viewYear, api.state.viewMonth + delta, 1);
        api.state.viewYear = shifted.getFullYear();
        api.state.viewMonth = shifted.getMonth();
        api.notify();
    };

    api.commit = function() {
        api.write();
        api.close();
    };

    // A popup the user has dragged stays where it was put
    var reposition = function() {
        if(!api.pinned) {
            picker.position(popup, input);
        }
    };

    var onOutside = function(event) {
        if(popup.contains(event.target) || event.target === input) {
            return;
        }
        api.close();
    };

    // Escape closes the popup alone, the dialog under it stays open
    var onKey = function(event) {
        if(event.key === 'Escape') {
            event.stopPropagation();
            api.close();
            input.focus();
        }
    };

    api.open = function() {
        if(!popup.hidden) {
            return;
        }
        readInput();
        listeners = [];
        api.pinned = false;
        popup.innerHTML = '';
        picker.render(popup, api);
        popup.hidden = false;
        picker.position(popup, input);
        document.addEventListener('mousedown', onOutside, true);
        document.addEventListener('keydown', onKey, true);
        window.addEventListener('resize', reposition);
        window.addEventListener('scroll', reposition, true);
    };

    api.close = function() {
        if(popup.hidden) {
            return;
        }
        popup.hidden = true;
        document.removeEventListener('mousedown', onOutside, true);
        document.removeEventListener('keydown', onKey, true);
        window.removeEventListener('resize', reposition);
        window.removeEventListener('scroll', reposition, true);
    };

    input.addEventListener('focus', api.open);
    input.addEventListener('click', api.open);
    input.addEventListener('keydown', function(event) {
        if(event.key === 'ArrowDown' && popup.hidden) {
            api.open();
        }
    });

    // A value typed straight into the field while the popup is open moves the popup to it
    input.addEventListener('change', function() {
        if(popup.hidden) {
            return;
        }
        readInput();
        api.notify();
    });

    $(input).data(picker.config.stateKey, api);
    return api;
};

// ////////////////////////////////////////////////////////////////////////

// The entry point every page calls, with the options the timepicker addon took
$.fn.datetimepicker = function(options) {
    return this.each(function() {
        if($(this).data(picker.config.stateKey)) {
            return;
        }
        picker.attach(this, {
            dateFormat: options.dateFormat,
            timeFormat: options.timeFormat,
            ampm: options.ampm
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
