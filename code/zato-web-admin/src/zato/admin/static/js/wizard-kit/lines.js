// The wizard kit's decision lines - a step body written as sentences, one
// decision per line. A line is a label and one control: either a chip that
// opens a panel, or a strip of options with the picked one in the accent.
//
// A panel wears the shared popup chrome - the dark header with the grip,
// the sandy body, the buttons row - so it is the same popup the micro-forms
// and the IDE menus open, and it is dragged by its header just like them.
// What goes inside a panel is the instance's own, usually two columns.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.lines = {};

// ////////////////////////////////////////////////////////////////////////

kit.lines.config = {

    // The button that closes a panel
    doneLabel: 'OK',

    // Where a panel opens in relation to the chip it belongs to
    panelGap: 5,
    panelMargin: 16,

    // How short a panel may be dragged by its corners - below this the
    // lists inside would have no room left to show a row. How narrow it may
    // be is the panel's own, since that is what a row of it decides.
    panelMinHeight: 240,

    // The panel currently open, one at a time for the whole page
    openPanel: null
};

// ////////////////////////////////////////////////////////////////////////

// Fills the value slot of a line with a chip. A chip reads as a value with
// a caret after it and opens the panel it was given when clicked.
//
// spec:
//   text    - what the chip says
//   note    - optional, a quieter word after the text, e.g. how many are paused
//   isBlank - nothing has been picked on this line yet, so the chip is dashed
//   panel   - {title, width, build} handed over to openPanel
kit.lines.setChip = function(slotId, spec) {

    var slot = document.getElementById(slotId);
    slot.textContent = '';

    var chip = document.createElement('button');
    chip.type = 'button';
    chip.className = spec.isBlank ? 'wizard-chip wizard-chip-blank' : 'wizard-chip';
    chip.id = slotId + '-chip';

    var value = document.createElement('span');
    value.className = 'wizard-chip-value';
    value.textContent = spec.text;
    chip.appendChild(value);

    if(spec.note) {
        var note = document.createElement('span');
        note.className = 'wizard-chip-note';
        note.textContent = spec.note;
        chip.appendChild(note);
    }

    chip.appendChild(kit.lines._buildCaret());

    // The press on a chip must not reach the document, whose own press is
    // what closes an open panel - the click below is where a chip toggles
    chip.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    chip.addEventListener('click', function(event) {

        event.stopPropagation();

        // A second click on the same chip is how a panel is closed again
        var linesConfig = kit.lines.config;
        var wasOpen = linesConfig.openPanel;

        kit.lines.closePanel();

        if(wasOpen) {
            if(wasOpen.chipId === chip.id) {
                return;
            }
        }

        kit.lines.openPanel(chip, spec.panel);
    });

    slot.appendChild(chip);

    var out = chip;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Fills the value slot of a line with a strip of options, the picked one in
// the accent color. Every option is one word the reader chooses between,
// so the whole answer is visible without opening anything.
//
// optionList - [{name, label}], currentName - which one is picked
kit.lines.setSegments = function(slotId, optionList, currentName, onPick) {

    var slot = document.getElementById(slotId);
    slot.textContent = '';

    // The strip is the shared tab component, recolored by wizard-lines.css
    var strip = document.createElement('div');
    strip.className = 'wizard-segments dashboard-tabs';

    for(var optionIdx = 0; optionIdx < optionList.length; optionIdx++) {
        strip.appendChild(kit.lines._buildSegment(optionList[optionIdx], currentName, onPick));
    }

    slot.appendChild(strip);

    var out = strip;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

kit.lines._buildSegment = function(option, currentName, onPick) {

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'wizard-segment dashboard-tab';
    button.textContent = option.label;

    if(option.name === currentName) {
        button.className = button.className + ' wizard-segment-active dashboard-tab-active';
    }

    button.addEventListener('click', function() {
        onPick(option.name);
    });

    var out = button;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

kit.lines._buildCaret = function() {

    var caret = document.createElement('span');
    caret.className = 'wizard-chip-caret';
    caret.innerHTML = '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';

    var out = caret;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Opens a panel under a chip. The caller's build function fills the body and
// may return a function to run when the panel closes, which is where a panel
// that edits the DOM directly writes its answers back into the state.
//
// spec: {title, width, minWidth, build(body, panel)}
kit.lines.openPanel = function(chip, spec) {

    var linesConfig = kit.lines.config;

    var panel = document.createElement('div');
    panel.className = 'zato-popup wizard-panel';
    panel.id = 'wizard-panel';
    panel.style.width = spec.width + 'px';

    var header = document.createElement('div');
    header.className = 'zato-popup-header';
    header.appendChild($.fn.zato.popup.build_grip());
    header.appendChild(document.createTextNode(spec.title));
    panel.appendChild(header);

    var body = document.createElement('div');
    body.className = 'wizard-tippy-body';
    panel.appendChild(body);

    // Clicks inside the panel are the panel's own, only the ones outside close it
    panel.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    var content = document.createElement('div');
    content.className = 'wizard-panel-content';
    body.appendChild(content);
    body.appendChild(kit.lines._buildButtons());

    document.body.appendChild(panel);

    var onClose = spec.build(content, panel);

    // A panel the user has already moved or resized opens the way it was
    // left, the rest hang under their chip
    var isRestored = $.fn.zato.popup.restore_geometry(chip.id, panel);

    if(!isRestored) {
        kit.lines._place(panel, chip);
    }

    kit.lines._makeDraggable(panel, header, chip.id);
    kit.lines._makeResizable(panel, spec, chip.id);

    linesConfig.openPanel = {element: panel, chipId: chip.id, onClose: onClose};

    // The filter of a panel that has one is where the typing goes from the start
    var filter = panel.querySelector('.wizard-panel-filter');

    if(filter) {
        filter.focus();
    }

    var out = panel;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

kit.lines.closePanel = function() {

    var open = kit.lines.config.openPanel;

    if(!open) {
        return;
    }

    kit.lines.config.openPanel = null;

    // A panel that writes its answers back reads them out of its own DOM,
    // so it is asked first and taken off the page after
    if(open.onClose) {
        open.onClose();
    }

    open.element.remove();
};

// ////////////////////////////////////////////////////////////////////////

// The buttons row every panel ends with - OK, and nothing else.
kit.lines._buildButtons = function() {

    var buttons = document.createElement('div');
    buttons.className = 'wizard-tippy-buttons';

    var done = document.createElement('button');
    done.type = 'button';
    done.className = 'action-button';
    done.textContent = kit.lines.config.doneLabel;

    done.addEventListener('click', function() {
        kit.lines.closePanel();
    });

    buttons.appendChild(done);

    var out = buttons;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A panel hangs under its chip and stays inside the window on the right.
kit.lines._place = function(panel, chip) {

    var linesConfig = kit.lines.config;
    var box = chip.getBoundingClientRect();
    var room = window.innerWidth - panel.offsetWidth - linesConfig.panelMargin;
    var left = Math.min(box.left + window.scrollX, room);

    panel.style.left = left + 'px';
    panel.style.top = (box.bottom + window.scrollY + linesConfig.panelGap) + 'px';
};

// ////////////////////////////////////////////////////////////////////////

// The header is the handle, through the same drag machinery the micro-forms
// and the IDE menus use. Where the panel is let go is where it opens next
// time, which is what the key is for - one per line.
kit.lines._makeDraggable = function(panel, header, key) {

    $.fn.zato.popup.install_drag(header, {

        dragging_elem: panel,

        on_start: function() {
            var out = {x: panel.offsetLeft, y: panel.offsetTop};
            return out;
        },

        on_end: function() {
            $.fn.zato.popup.save_geometry(key, panel);
        },

        on_move: function(x, y) {
            panel.style.left = x + 'px';
            panel.style.top = y + 'px';
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// The bottom corners resize the panel, through the same popup machinery.
// Everything a panel holds is laid out in flex, so the lists take whatever
// height the panel is dragged to and nothing inside moves out of place.
kit.lines._makeResizable = function(panel, spec, key) {

    $.fn.zato.popup.install_resize(panel, {

        min_width: spec.minWidth,
        min_height: kit.lines.config.panelMinHeight,

        on_end: function() {
            $.fn.zato.popup.save_geometry(key, panel);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// The filter field a panel puts above a long list - the list is walked by
// typing, so the field is what the panel opens on.
kit.lines.buildFilter = function(labelText, placeholder, onInput) {

    var field = document.createElement('div');
    field.className = 'wizard-tippy-field';

    var label = document.createElement('label');
    label.className = 'wizard-tippy-label';
    label.textContent = labelText;
    field.appendChild(label);

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'wizard-panel-filter';
    input.id = 'wizard-panel-filter';
    input.autocomplete = 'off';
    input.placeholder = placeholder;
    field.appendChild(input);

    label.setAttribute('for', input.id);

    input.addEventListener('input', function() {
        onInput(input.value.trim().toLowerCase());
    });

    var out = {field: field, input: input};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One pickable row of a panel list - a radio dot in front of a name.
kit.lines.buildPickRow = function(name, isPicked, onPick) {

    var row = document.createElement('div');
    row.className = 'wizard-pick-row';

    var dot = document.createElement('span');
    dot.className = isPicked ? 'wizard-pick-dot wizard-pick-dot-on' : 'wizard-pick-dot';
    row.appendChild(dot);

    var label = document.createElement('span');
    label.className = 'wizard-pick-name';
    label.textContent = name;
    row.appendChild(label);

    row.addEventListener('click', function() {
        onPick();
    });

    var out = row;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A click anywhere outside an open panel closes it, and so does Escape.
$(document).on('mousedown', function() {
    kit.lines.closePanel();
});

$(document).on('keydown', function(event) {

    if(event.key === 'Escape') {
        kit.lines.closePanel();
    }
});

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
