// Decision lines - settings written as sentences, one decision per line.
//
// A decision line is a question on the left and its answer on the right.
// The answer is a chip that opens a pick panel, a strip of options with the
// picked one in the accent, a switch, or a summary link opening a popover
// micro-form. A wizard step, a dialog tab or a column of a listing page
// reads the same way through them. This file fills the chips and the
// strips and opens the panels, the look is static/css/shared/decision-lines.css
// and a host tunes it through the --decision-* tokens on its own container,
// or under the panelClass it hands to openPanel for the panels.
//
// The markup a host writes:
//
//      <div class="decision-lines">
//          <div class="decision-line">
//              <label class="decision-line-label">Which service</label>
//              <span class="decision-line-slot" id="my-slot-service"></span>
//          </div>
//      </div>
//
// and what fills the slot:
//
//      $.fn.zato.decision_lines.setChip('my-slot-service', {
//          text: 'zato.ping',
//          isBlank: false,
//          panel: {
//              title: 'Service',
//              width: 340,
//              panelClass: 'my-pick-panel',
//              build: function(content, panel) { ... }
//          }
//      });
//
//      $.fn.zato.decision_lines.setSegments('my-slot-mode', optionList, 'active', onPick);
//
// A panel wears the shared popup chrome - the dark header with the grip,
// the sandy body of the micro-forms, the buttons row - so it is the same
// popup the micro-forms and the IDE menus open, and it is dragged by its
// header just like them. What goes inside a panel is the host's own, built
// out of buildFilter and buildPickRow or anything else.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var decisionLines = $.fn.zato.decision_lines;

// ////////////////////////////////////////////////////////////////////////

decisionLines.config = {

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
decisionLines.setChip = function(slotId, spec) {

    var slot = document.getElementById(slotId);
    slot.textContent = '';

    var chip = document.createElement('button');
    chip.type = 'button';
    chip.className = spec.isBlank ? 'decision-chip decision-chip-blank' : 'decision-chip';
    chip.id = slotId + '-chip';

    var value = document.createElement('span');
    value.className = 'decision-chip-value';
    value.textContent = spec.text;
    chip.appendChild(value);

    if(spec.note) {
        var note = document.createElement('span');
        note.className = 'decision-chip-note';
        note.textContent = spec.note;
        chip.appendChild(note);
    }

    chip.appendChild(decisionLines._buildCaret());

    // The press on a chip must not reach the document, whose own press is
    // what closes an open panel - the click below is where a chip toggles
    chip.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    chip.addEventListener('click', function(event) {

        event.stopPropagation();

        // A second click on the same chip is how a panel is closed again
        var linesConfig = decisionLines.config;
        var wasOpen = linesConfig.openPanel;

        decisionLines.closePanel();

        if(wasOpen) {
            if(wasOpen.chipId === chip.id) {
                return;
            }
        }

        decisionLines.openPanel(chip, spec.panel);
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
// optionList - [{name, label, is_active}], currentName - which one is picked.
// An option that is off keeps its place in the list but is not put on screen.
decisionLines.setSegments = function(slotId, optionList, currentName, onPick) {

    var slot = document.getElementById(slotId);
    slot.textContent = '';

    // The strip is the shared tab component, recolored by decision-lines.css
    var strip = document.createElement('div');
    strip.className = 'decision-segments dashboard-tabs';

    for(var optionIdx = 0; optionIdx < optionList.length; optionIdx++) {

        var option = optionList[optionIdx];

        if(option.is_active) {
            strip.appendChild(decisionLines._buildSegment(option, currentName, onPick));
        }
    }

    slot.appendChild(strip);

    var out = strip;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

decisionLines._buildSegment = function(option, currentName, onPick) {

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'decision-segment dashboard-tab';
    button.textContent = option.label;

    if(option.name === currentName) {
        button.className = button.className + ' decision-segment-active dashboard-tab-active';
    }

    button.addEventListener('click', function() {
        onPick(option.name);
    });

    var out = button;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

decisionLines._buildCaret = function() {

    var caret = document.createElement('span');
    caret.className = 'decision-chip-caret';
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
// spec: {title, width, minWidth, build(body, panel), geometryKey, panelClass}
decisionLines.openPanel = function(chip, spec) {

    var linesConfig = decisionLines.config;

    // Where the panel was left is remembered under its chip, unless the caller opens the
    // same panel off more than one chip - a list does, one per row, and it is one panel
    var geometryKey = spec.geometryKey ? spec.geometryKey : chip.id;

    var panel = document.createElement('div');
    panel.className = 'zato-popup decision-pick-panel';
    panel.id = 'decision-pick-panel';
    panel.style.width = spec.width + 'px';

    // The host's own class, which is where it overrides the pick panel
    // tokens - the panel is appended to document.body, so no container
    // of the host's page is above it
    if(spec.panelClass) {
        panel.classList.add(spec.panelClass);
    }

    var header = document.createElement('div');
    header.className = 'zato-popup-header';
    header.appendChild($.fn.zato.popup.build_grip());
    header.appendChild(document.createTextNode(spec.title));
    panel.appendChild(header);

    var body = document.createElement('div');
    body.className = 'micro-form-body';
    panel.appendChild(body);

    // Clicks inside the panel are the panel's own, only the ones outside close it
    panel.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    var content = document.createElement('div');
    content.className = 'decision-pick-panel-content';
    body.appendChild(content);
    body.appendChild(decisionLines._buildButtons());

    document.body.appendChild(panel);

    var onClose = spec.build(content, panel);

    // A panel the user has already moved or resized opens the way it was
    // left, the rest hang under their chip
    var isRestored = $.fn.zato.popup.restore_geometry(geometryKey, panel);

    if(!isRestored) {
        decisionLines._place(panel, chip);
    }

    decisionLines._makeDraggable(panel, header, geometryKey);
    decisionLines._makeResizable(panel, spec, geometryKey);

    linesConfig.openPanel = {element: panel, chipId: chip.id, onClose: onClose};

    // The filter of a panel that has one is where the typing goes from the start
    var filter = panel.querySelector('.decision-pick-panel-filter');

    if(filter) {
        filter.focus();
    }

    var out = panel;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

decisionLines.closePanel = function() {

    var open = decisionLines.config.openPanel;

    if(!open) {
        return;
    }

    decisionLines.config.openPanel = null;

    // A panel that writes its answers back reads them out of its own DOM,
    // so it is asked first and taken off the page after
    if(open.onClose) {
        open.onClose();
    }

    open.element.remove();
};

// ////////////////////////////////////////////////////////////////////////

// The buttons row every panel ends with - OK, and nothing else.
decisionLines._buildButtons = function() {

    var buttons = document.createElement('div');
    buttons.className = 'micro-form-buttons';

    var done = document.createElement('button');
    done.type = 'button';
    done.className = 'action-button';
    done.textContent = decisionLines.config.doneLabel;

    done.addEventListener('click', function() {
        decisionLines.closePanel();
    });

    buttons.appendChild(done);

    var out = buttons;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A panel hangs under its chip and stays inside the window on the right.
decisionLines._place = function(panel, chip) {

    var linesConfig = decisionLines.config;
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
decisionLines._makeDraggable = function(panel, header, key) {

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
decisionLines._makeResizable = function(panel, spec, key) {

    $.fn.zato.popup.install_resize(panel, {

        min_width: spec.minWidth,
        min_height: decisionLines.config.panelMinHeight,

        on_end: function() {
            $.fn.zato.popup.save_geometry(key, panel);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// The filter field a panel puts above a long list - the list is walked by
// typing, so the field is what the panel opens on.
decisionLines.buildFilter = function(labelText, placeholder, onInput) {

    var field = document.createElement('div');
    field.className = 'micro-form-field';

    var label = document.createElement('label');
    label.className = 'micro-form-label';
    label.textContent = labelText;
    field.appendChild(label);

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'decision-pick-panel-filter';
    input.id = 'decision-pick-panel-filter';
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
decisionLines.buildPickRow = function(name, isPicked, onPick) {

    var row = document.createElement('div');
    row.className = 'decision-pick-row';

    var dot = document.createElement('span');
    dot.className = isPicked ? 'decision-pick-dot decision-pick-dot-on' : 'decision-pick-dot';
    row.appendChild(dot);

    var label = document.createElement('span');
    label.className = 'decision-pick-name';
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
    decisionLines.closePanel();
});

// Escape is caught on the way down, before the dialog a host may sit in gets
// to close itself on the same key - jQuery UI listens for it on the document
// and on the dialog - and only while a panel is open, so with none open the
// key is the dialog's as before.
document.addEventListener('keydown', function(event) {

    if(event.key !== 'Escape') {
        return;
    }

    if(!decisionLines.config.openPanel) {
        return;
    }

    event.preventDefault();
    event.stopPropagation();
    decisionLines.closePanel();
}, true);

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
