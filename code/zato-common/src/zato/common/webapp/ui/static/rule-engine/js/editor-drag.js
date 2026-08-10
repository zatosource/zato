'use strict';

(function() {

// Console diagnostics for the caret - throttled so a drag does not flood
// the console
var caretLogLast = {};
var caretPointer = {x: null, y: null};
document.addEventListener('dragover', function(event) { caretPointer.x = event.clientX; caretPointer.y = event.clientY; }, true);
var caretLog = function(location, message, data, throttleKey) {
    if (throttleKey !== undefined) {
        var now = Date.now();
        if (caretLogLast[throttleKey] !== undefined && now - caretLogLast[throttleKey] < 250) { return; }
        caretLogLast[throttleKey] = now;
    }
    console.log('[caret] ' + location + ' - ' + message, JSON.stringify(data));
};

editorView.dragState = null;

// ////////////////////////////////////////////////////////////////////////

// A drag says two things and two things only - the rest of the page steps
// back, and the hovered line shows one insertion caret snapped to the gap
// middle nearest the pointer
editorView.markPossibleDrops = function() {
    this.container.classList.add('editor-dragging');
};

editorView.clearPossibleDrops = function() {
    this.container.classList.remove('editor-dragging');
};

// One caret per line, keyed by the line's list name
editorView.insertionMarkers = {};

editorView.clearInsertionMarkers = function() {
    var self = this;
    Object.keys(this.insertionMarkers).forEach(function(name) {
        self.insertionMarkers[name].element.remove();
    });
    this.insertionMarkers = {};
};

// How far from a row's outermost glyph the caret stands when a slot lies at
// a row break and has no second text to center between
editorView.rowEdgeOffset = 8;

// Whether an element paints its own edge - a visible border or background
// makes the box edge the rendered edge
editorView.paintsOwnEdge = function(element, side) {
    var style = window.getComputedStyle(element);

    var borderColor = side === 'right' ? style.borderRightColor : style.borderLeftColor;
    var borderStyle = side === 'right' ? style.borderRightStyle : style.borderLeftStyle;
    var hasBorder = borderStyle !== 'none' && borderColor !== 'rgba(0, 0, 0, 0)' && borderColor !== 'transparent';

    var background = style.backgroundColor;
    var hasBackground = background !== 'rgba(0, 0, 0, 0)' && background !== 'transparent';

    return hasBorder || hasBackground;
};

// The eye sees glyphs and drawn borders, not layout boxes - a clause box is
// inflated by transparent token padding and its hidden remove control, so
// the caret must center between rendered edges instead of box edges
editorView.visibleEdge = function(element, box, side) {

    // The outermost token of a clause decides its rendered edge - the
    // hidden remove control after it takes box space but paints nothing
    var tokens = element.querySelectorAll('.editor-token, .editor-token-input');
    var target = element;
    var targetBox = box;

    if (tokens.length > 0) {
        target = side === 'right' ? tokens[tokens.length - 1] : tokens[0];
        targetBox = target.getBoundingClientRect();
    }

    // A chip or a bordered token is seen at its box edge
    if (this.paintsOwnEdge(target, side)) {
        return side === 'right' ? targetBox.right : targetBox.left;
    }

    // Bare text is seen at its outermost glyph
    var walker = document.createTreeWalker(target, NodeFilter.SHOW_TEXT);
    var node = walker.nextNode();
    var edge = null;

    while (node !== null) {
        if (node.textContent.trim() !== '') {
            var range = document.createRange();
            range.selectNodeContents(node);
            var textBox = range.getBoundingClientRect();

            if (textBox.width > 0) {
                if (side === 'right') {
                    if (edge === null || textBox.right > edge) { edge = textBox.right; }
                }
                else if (edge === null || textBox.left < edge) {
                    edge = textBox.left;
                }
            }
        }
        node = walker.nextNode();
    }

    // A neighbour with no rendered text, e.g. one holding only an input,
    // falls back to its box edge
    if (edge === null) {
        edge = side === 'right' ? targetBox.right : targetBox.left;
    }

    return edge;
};

// Every insertion slot of the line as fixed anchor points, each in the
// middle of the rendered gap between the two words around it. A joiner
// like "and" is a word of its own standing inside its slot, so that slot
// offers one anchor on each side of the joiner. A gap across a row break
// has no shared middle, so its anchor stands at the start of the lower
// row - never at the end of the upper one.
editorView.slotAnchors = function(line) {
    var self = this;
    var anchors = [];

    var chip = line.querySelector('.editor-add-chip');

    // The anchors of one rendered gap between two adjacent words
    var pushGapAnchors = function(index, position, leftElement, rightElement) {
        var leftBox = leftElement === null ? null : leftElement.getBoundingClientRect();
        var rightBox = rightElement.getBoundingClientRect();

        // What the eye sees of each word, not what layout reserves
        var leftEdge = leftBox === null ? null : self.visibleEdge(leftElement, leftBox, 'right');
        var rightEdge = self.visibleEdge(rightElement, rightBox, 'left');

        // Wrapped words live on rows of their own, and adjacent rows touch
        // or overlap by subpixels, so only vertical centers close to each
        // other mean one shared row
        var sameRow = false;
        if (leftBox !== null) {
            var leftMiddleY = (leftBox.top + leftBox.bottom) / 2;
            var rightMiddleY = (rightBox.top + rightBox.bottom) / 2;
            var smallerHeight = Math.min(leftBox.height, rightBox.height);
            sameRow = Math.abs(leftMiddleY - rightMiddleY) < (smallerHeight / 2);
        }

        // Words on one row - one anchor in the middle of their gap
        if (sameRow) {
            anchors.push({
                index: index,
                position: position,
                kind: 'between',
                x: (leftEdge + rightEdge) / 2,
                rowTop: Math.min(leftBox.top, rightBox.top),
                rowBottom: Math.max(leftBox.bottom, rightBox.bottom)
            });
            return;
        }

        // A row break - the gap's one anchor stands at the start of the
        // lower row, before its first word. Nothing is ever droppable at
        // the end of a row, so a drop always lands exactly at its caret.
        anchors.push({
            index: index,
            position: position,
            kind: 'row-start',
            x: rightEdge - self.rowEdgeOffset,
            rowTop: rightBox.top,
            rowBottom: rightBox.bottom
        });
    };

    // Clauses and the separator words between them in document order - a
    // joiner like the conditions line's "and" or a keyword like the then
    // line's leading "then" and its between-action "and" all belong to the
    // slot whose clauses they stand between
    var groupElements = [];
    var slotSeparators = [[]];
    line.querySelectorAll('.editor-group, .editor-token-joiner, .editor-keyword').forEach(function(element) {
        if (element.classList.contains('editor-group')) {
            groupElements.push(element);
            slotSeparators.push([]);
        }
        else {
            slotSeparators[slotSeparators.length - 1].push(element);
        }
    });

    var slotCount = groupElements.length + 1;

    for (var index = 0; index < slotCount; index += 1) {

        // The words around the slot in visual order - the previous clause,
        // then any separator words standing in the slot, then the next
        // clause or the add chip
        var words = [];
        if (index > 0) { words.push(groupElements[index - 1]); }

        slotSeparators[index].forEach(function(separator) { words.push(separator); });
        words.push(index >= groupElements.length ? chip : groupElements[index]);

        // A slot with no left word at all still gets one anchor before its
        // only word
        if (words.length === 1) {
            pushGapAnchors(index, 0, null, words[0]);
            continue;
        }

        for (var position = 0; position < words.length - 1; position += 1) {
            pushGapAnchors(index, position, words[position], words[position + 1]);
        }
    }

    return anchors;
};

// The anchor the pointer stands closest to - its own row band decides
// first, the horizontal distance breaks the tie within the band
editorView.nearestAnchor = function(anchors, clientX, clientY) {
    var best = null;
    var bestRowDistance = 0;
    var bestGapDistance = 0;

    anchors.forEach(function(anchor) {
        var rowDistance = 0;
        if (clientY < anchor.rowTop) { rowDistance = anchor.rowTop - clientY; }
        else if (clientY > anchor.rowBottom) { rowDistance = clientY - anchor.rowBottom; }

        var gapDistance = Math.abs(clientX - anchor.x);

        if (best === null || rowDistance < bestRowDistance || (rowDistance === bestRowDistance && gapDistance < bestGapDistance)) {
            best = anchor;
            bestRowDistance = rowDistance;
            bestGapDistance = gapDistance;
        }
    });

    return best;
};

editorView.placeInsertionMarker = function(line, dropName, anchor) {
    var self = this;

    // A single caret on the whole canvas - entering one line takes it away
    // from every other line
    Object.keys(this.insertionMarkers).forEach(function(name) {
        if (name !== dropName) {
            self.insertionMarkers[name].element.remove();
            delete self.insertionMarkers[name];
        }
    });

    var entry = this.insertionMarkers[dropName];

    // The same anchor keeps its caret - the caret only ever jumps from one
    // anchor to another
    var key = anchor.index + ':' + anchor.position + ':' + anchor.kind;
    if (entry !== undefined && entry.key === key) { return; }

    if (entry === undefined) {
        var element = document.createElement('span');
        element.className = 'editor-insert-marker';
        this.container.appendChild(element);
        entry = {element: element, key: ''};
        this.insertionMarkers[dropName] = entry;
    }

    entry.element.style.left = (anchor.x - 1) + 'px';
    entry.element.style.top = (anchor.rowTop - 1) + 'px';
    entry.element.style.height = (anchor.rowBottom - anchor.rowTop + 2) + 'px';
    entry.key = key;

    // The dot whose place the caret takes steps aside - every other dot
    // keeps showing where else the caret could go
    var chosenDotKey = dropName + ':' + key;
    this.previewMarkers.forEach(function(marker) {
        marker.element.style.visibility = marker.key === chosenDotKey ? 'hidden' : '';
    });

    caretLog('placeInsertionMarker', 'caret snapped', {
        drop_name: dropName,
        index: anchor.index,
        position: anchor.position,
        kind: anchor.kind,
        anchor_x: Math.round(anchor.x * 10) / 10,
        row_top: Math.round(anchor.rowTop * 10) / 10,
        row_bottom: Math.round(anchor.rowBottom * 10) / 10,
        pointer: {x: caretPointer.x, y: caretPointer.y},
        hidden_dot: chosenDotKey,
        dots_total: this.previewMarkers.length
    });
};

editorView.attachVocabularyDrag = function() {
    var self = this;

    this.elements('.vocabulary-item[draggable="true"]').forEach(function(element) {
        element.addEventListener('dragstart', function(event) {
            var path = element.getAttribute('data-path');
            self.dragState = {path: path};

            caretLog('dragstart', 'drag begins', {path: path});

            // The dots stay up for the whole drag, showing every place the
            // caret can snap to - a pending hover put-away must not take
            // them down mid-drag
            if (self.potentialHideTimer !== null) { clearTimeout(self.potentialHideTimer); self.potentialHideTimer = null; }
            self.showPreview();

            var attribute = vocabulary.attribute(path);

            // The ghost under the pointer is the token the drop will leave
            // in the rule, not a copy of the list row
            var ghost = shared.makeGhost([attribute.phrase], false);
            ghost.firstChild.classList.add('drag-ghost-token');

            event.dataTransfer.setDragImage(ghost, 16, 12);
            event.dataTransfer.setData('text/plain', 'vocabulary');
            self.markPossibleDrops();
        });

        element.addEventListener('dragend', function() {
            caretLog('dragend', 'drag ends', {});
            self.dragState = null;
            self.clearInsertionMarkers();
            self.clearPreview('dragend');
            self.clearPossibleDrops();
            shared.removeGhost();
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

// A card the rule does not use yet points at where it could go - while the
// pointer is on the card, a small dot marks every place the drag caret can
// snap to, one dot per anchor
editorView.potentialHideTimer = null;
editorView.previewMarkers = [];

// Half the hint dot's size - the dot is centered on its anchor
editorView.hintRadius = 3;

editorView.clearPreview = function(reason) {
    if (this.previewMarkers.length > 0) {
        caretLog('clearPreview', 'dots removed', {reason: reason, count: this.previewMarkers.length});
    }

    this.previewMarkers.forEach(function(marker) {
        marker.element.remove();
    });
    this.previewMarkers = [];
};

editorView.showPreview = function() {
    var self = this;
    this.clearPreview('refresh');

    this.elements('.editor-line').forEach(function(line) {
        var dropName = line.getAttribute('data-drop');

        self.slotAnchors(line).forEach(function(anchor) {
            var middleY = (anchor.rowTop + anchor.rowBottom) / 2;

            var element = document.createElement('span');
            element.className = 'editor-insert-hint';
            element.style.left = (anchor.x - self.hintRadius) + 'px';
            element.style.top = (middleY - self.hintRadius) + 'px';
            self.container.appendChild(element);

            // The key ties the dot to its anchor, so the drag caret can
            // put away exactly the dot whose place it takes
            self.previewMarkers.push({
                element: element,
                key: dropName + ':' + anchor.index + ':' + anchor.position + ':' + anchor.kind
            });
        });
    });

    caretLog('showPreview', 'dots placed', {count: this.previewMarkers.length});
};

// Hovering either side of the same fact lights both - a token in the canvas
// and the vocabulary card it came from answer each other. A card the rule
// does not use yet shows every landing place instead, but only once the
// pointer rests on the card, so a sweep across the list paints nothing.
editorView.attachPathHighlight = function() {
    var self = this;

    // Anything pending from before this render must not fire into the new one
    if (this.potentialHideTimer !== null) { clearTimeout(this.potentialHideTimer); this.potentialHideTimer = null; }
    this.clearPreview('render');

    var mark = function(path, isOn) {
        self.elements('[data-path="' + path + '"]').forEach(function(element) {
            element.classList.toggle('editor-path-match', isOn);
        });
    };

    var askPreview = function() {

        // A drag owns the dots - a hover must not rebuild them and lose
        // the one the caret is hiding
        if (self.dragState !== null) { return; }

        // Arriving from another unused card cancels its pending put-away,
        // so gliding along the list keeps the hints steady
        if (self.potentialHideTimer !== null) { clearTimeout(self.potentialHideTimer); self.potentialHideTimer = null; }
        self.showPreview();
    };

    var dropPreview = function() {

        // Leaving the card is how every drag begins - the put-away this
        // would schedule was exactly what wiped the dots mid-drag
        if (self.dragState !== null) {
            caretLog('dropPreview', 'put-away skipped, drag running', {});
            return;
        }

        // The put-away waits a beat, so gliding to the next unused card
        // keeps the hints instead of blinking them
        if (self.potentialHideTimer === null) {
            self.potentialHideTimer = setTimeout(function() {
                self.potentialHideTimer = null;
                self.clearPreview('hover-away');
            }, editorModel.config.potentialDelayMilliseconds);
        }
    };

    this.elements('.editor-token[data-path], .vocabulary-item[data-path]').forEach(function(element) {
        var path = element.getAttribute('data-path');
        var isCard = element.classList.contains('vocabulary-item');

        element.addEventListener('mouseenter', function() {
            var tokens = self.elements('.editor-token[data-path="' + path + '"]');

            if (isCard && tokens.length === 0) {
                askPreview();
            }
            else {
                mark(path, true);
            }
        });

        element.addEventListener('mouseleave', function() {
            mark(path, false);

            var tokens = self.elements('.editor-token[data-path="' + path + '"]');
            if (isCard && tokens.length === 0) { dropPreview(); }
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.attachDropLines = function() {
    var self = this;

    this.elements('.editor-line').forEach(function(line) {
        var dropName = line.getAttribute('data-drop');

        line.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            event.preventDefault();

            var anchors = self.slotAnchors(line);
            var anchor = self.nearestAnchor(anchors, event.clientX, event.clientY);

            caretLog('dragover', 'anchors and pick', {drop_name: dropName, pointer: {x: event.clientX, y: event.clientY}, anchors: anchors.map(function(a) { return {index: a.index, position: a.position, kind: a.kind, x: Math.round(a.x * 10) / 10, row_top: Math.round(a.rowTop * 10) / 10, row_bottom: Math.round(a.rowBottom * 10) / 10}; }), chosen: {index: anchor.index, position: anchor.position, kind: anchor.kind, x: Math.round(anchor.x * 10) / 10}}, 'anchors-' + dropName);

            self.placeInsertionMarker(line, dropName, anchor);
        });

        line.addEventListener('drop', function(event) {
            event.preventDefault();
            if (self.dragState === null) { return; }

            var anchors = self.slotAnchors(line);
            var anchor = self.nearestAnchor(anchors, event.clientX, event.clientY);
            self.clearInsertionMarkers();
            self.dropAt(dropName, self.dragState.path, anchor);
            self.dragState = null;
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

// A drop changes exactly one thing - the new clause appears at the caret
// with its gaps rendered as placeholders, no menu jumps at the user, and
// no existing clause changes its words
editorView.dropAt = function(dropName, path, anchor) {
    var position = anchor.index;

    if (dropName === 'conditions') {
        editorModel.rule.conditions.splice(position, 0, {subject: path, comparator: null, values: []});

        if (editorModel.rule.conditions.length > 1) {

            // The caret's side of the slot's joiner decides where the new
            // "and" goes - left of the joiner binds the new clause to the
            // clause before it, right of the joiner binds it to the clause
            // after it, so an existing "or" never jumps across the new
            // clause and no existing pairing changes
            var joinerIndex;
            if (position === 0) { joinerIndex = 0; }
            else if (anchor.position === 0) { joinerIndex = position - 1; }
            else { joinerIndex = position; }

            editorModel.rule.joiners.splice(joinerIndex, 0, 'and');
        }
        this.render();
        this.playArrival(dropName, position);
        return;
    }

    var attribute = vocabulary.attribute(path);
    var values = attribute.type === 'yes/no' ? ['true'] : [''];
    editorModel.rule[dropName].splice(position, 0, {target: path, values: values});

    this.render();
    this.playArrival(dropName, position);
};

// ////////////////////////////////////////////////////////////////////////

// How the new clause announces itself after the drop - it pops in with a
// small overshoot while a ring pings outwards as it settles, transform and
// shadow only, so nothing else on the line ever moves
editorView.playArrival = function(dropName, position) {
    var group = this.container.querySelector('[data-group="' + dropName + '-' + position + '"]');
    group.classList.add('editor-arrive');

    caretLog('playArrival', 'arrival effect', {drop_name: dropName, position: position});
};

// ////////////////////////////////////////////////////////////////////////

// A rule just opened and not yet touched teaches itself in the three
// beats of a real drag - a ghost of the first card's phrase lifts off the
// card, condenses into the bead at its front and flies as a comet along a
// motion path to the if line, where a caret already stands ready and the
// phrase springs back into being with the same ring a real drop plays.
// The rehearsal loops until the first edit or click, then stays away for
// as long as this rule is open.
editorView.nudgeDismissedKey = null;
editorView.nudgeListenerAttached = false;

// Which open rule the rehearsal belongs to
editorView.nudgeKey = function() {
    return editorModel.definitionId + ':' + editorModel.ruleKey;
};

editorView.removeNudge = function() {
    var overlay = this.container.querySelector('.editor-nudge');
    if (overlay !== null) { overlay.remove(); }
};

editorView.dismissNudge = function() {
    this.nudgeDismissedKey = this.nudgeKey();
    this.removeNudge();
};

editorView.showNudge = function() {
    var self = this;
    this.removeNudge();

    // Only an untouched, just-opened rule rehearses - dirty rules and
    // rules the user already engaged with stay quiet
    if (editorModel.rule === null) { return; }
    if (!editorModel.config.trackChanges) { return; }
    if (editorModel.isDirty()) { return; }
    if (this.nudgeDismissedKey === this.nudgeKey()) { return; }

    // The host may not show the palette at all
    var card = this.container.querySelector('.vocabulary-item[draggable="true"]');
    var chip = this.container.querySelector('.editor-line[data-drop="conditions"] .editor-add-chip');
    if (card === null || chip === null) { return; }

    var cardBox = card.getBoundingClientRect();
    var chipBox = chip.getBoundingClientRect();

    // The journey begins exactly where the in-rule dot stands at the card's
    // front - the dot sits at -15px, 7px wide, so its centre is 11.5px left
    // of the card - and ends where a real drop lands, just before the if
    // line's add chip. The bead covers that dot exactly.
    var startX = cardBox.left - 11.5;
    var startY = (cardBox.top + cardBox.bottom) / 2;
    var endX = chipBox.left - 16;
    var endY = (chipBox.top + chipBox.bottom) / 2;

    // Where the grab itself happens - the centre of the card the phrase
    // is picked off
    var liftX = (cardBox.left + cardBox.right) / 2;
    var liftY = (cardBox.top + cardBox.bottom) / 2;

    // One smooth curve for the whole journey - it leaves the card already
    // on a gentle climb, sweeps just over the bead at the card's front,
    // crests early and glides down long and shallow into the landing. A
    // single cubic has no joins, so there is no point anywhere on the way
    // where the trajectory can visibly change character.
    var distanceX = liftX - endX;
    var lift = Math.min(Math.max(distanceX * 0.18, 40), 90);
    var c1X = liftX - (distanceX * 0.28);
    var c1Y = liftY - (lift * 0.8);
    var c2X = endX + (distanceX * 0.3);
    var c2Y = endY - (lift * 0.35);
    var path = 'M ' + liftX + ' ' + liftY +
        ' C ' + c1X + ' ' + c1Y + ', ' + c2X + ' ' + c2Y + ', ' + endX + ' ' + endY;

    var overlay = document.createElement('div');
    overlay.className = 'editor-nudge';

    // The comet is particles, not a stroke - a lit head and a tail of
    // sparks, every spark flying the identical arc a fixed beat behind
    // the one before it, smaller and dimmer with every place down the
    // tail, so the tail tapers, bunches where the flight is slow and
    // stretches where it is fast
    var sparkCount = 10;
    var sparksHtml = '';

    for (var sparkIndex = 0; sparkIndex < sparkCount; sparkIndex++) {
        sparksHtml += '<span class="editor-nudge-spark"></span>';
    }

    overlay.innerHTML =
        sparksHtml +
        '<span class="editor-nudge-head"></span>' +
        '<span class="editor-nudge-dot"></span>' +
        '<span class="editor-nudge-lift"></span>' +
        '<span class="editor-nudge-ghost"></span>' +
        '<span class="editor-nudge-chip"></span>' +
        '<span class="editor-nudge-caret"></span>' +
        '<span class="editor-nudge-ring"></span>';

    var headElement = overlay.querySelector('.editor-nudge-head');
    headElement.style.offsetPath = 'path("' + path + '")';

    var sparkElements = overlay.querySelectorAll('.editor-nudge-spark');

    for (var trailIndex = 0; trailIndex < sparkElements.length; trailIndex++) {
        var spark = sparkElements[trailIndex];

        // How deep into the tail this spark rides - 0 right behind the
        // head, 1 at the very end of the tail
        var depth = (trailIndex + 1) / sparkCount;

        var sparkSize = 7 - (depth * 4.5);

        spark.style.offsetPath = 'path("' + path + '")';
        spark.style.width = sparkSize + 'px';
        spark.style.height = sparkSize + 'px';

        // The beat this spark lags behind the head - the whole timeline
        // shifted, so the spark repeats the head's exact flight later
        spark.style.animationDelay = ((trailIndex + 1) * 28) + 'ms';

        // Dimmer with every place down the tail
        spark.style.setProperty('--editor-nudge-spark-opacity', (0.75 * (1 - depth) + 0.1).toFixed(2));
    }

    var phrase = vocabulary.attribute(card.getAttribute('data-path')).phrase;

    // The pick-up - a copy of the phrase over the card itself. It only
    // plays the stationary grab - fade in, lift up - and crossfades into
    // the flight ghost at this very spot, so nothing ever swaps while in
    // motion.
    var liftElement = overlay.querySelector('.editor-nudge-lift');

    liftElement.textContent = phrase;
    liftElement.style.left = liftX + 'px';
    liftElement.style.top = liftY + 'px';

    // The flight ghost - the dragged thing itself, translucent the way a
    // real drag ghost is, riding the same arc the comet streams under
    var ghostElement = overlay.querySelector('.editor-nudge-ghost');
    ghostElement.textContent = phrase;
    ghostElement.style.offsetPath = 'path("' + path + '")';

    // The chip carries the card's own phrase and materialises at the
    // landing point once the comet has arrived there
    var chipElement = overlay.querySelector('.editor-nudge-chip');
    chipElement.textContent = phrase;
    chipElement.style.left = endX + 'px';
    chipElement.style.top = endY + 'px';

    var caretElement = overlay.querySelector('.editor-nudge-caret');
    caretElement.style.left = (endX - 1) + 'px';
    caretElement.style.top = (chipBox.top - 1) + 'px';
    caretElement.style.height = (chipBox.height + 2) + 'px';

    var ringElement = overlay.querySelector('.editor-nudge-ring');
    ringElement.style.left = (endX - 14) + 'px';
    ringElement.style.top = (endY - 14) + 'px';

    // The departure bead marks where the journey begins
    var dotElement = overlay.querySelector('.editor-nudge-dot');
    dotElement.style.left = (startX - 5) + 'px';
    dotElement.style.top = (startY - 5) + 'px';

    this.container.appendChild(overlay);

    caretLog('showNudge', 'rehearsal shown', {
        path: path,
        liftX: Math.round(liftX),
        liftY: Math.round(liftY),
        startX: Math.round(startX),
        startY: Math.round(startY),
        endX: Math.round(endX),
        endY: Math.round(endY)
    });

    // Samples the actors' real on-screen positions across the first loop,
    // so the motion can be read from the console - where each one is,
    // how visible it is and how fast it moves between samples
    var samplerStart = performance.now();
    var samplerPrevious = null;

    var sampleFrame = function() {
        var elapsed = performance.now() - samplerStart;

        // One full loop is enough to read the choreography
        if (elapsed > 5100) { return; }
        if (overlay.parentNode === null) { return; }

        var liftBox = liftElement.getBoundingClientRect();
        var ghostBox = ghostElement.getBoundingClientRect();
        var headBox = headElement.getBoundingClientRect();

        var sample = {
            tMs: Math.round(elapsed),
            loopPct: Math.round(elapsed / 50) / 100 * 100,
            lift: {
                x: Math.round(liftBox.left + liftBox.width / 2),
                y: Math.round(liftBox.top + liftBox.height / 2),
                opacity: getComputedStyle(liftElement).opacity
            },
            ghost: {
                x: Math.round(ghostBox.left + ghostBox.width / 2),
                y: Math.round(ghostBox.top + ghostBox.height / 2),
                opacity: getComputedStyle(ghostElement).opacity
            },
            head: {
                x: Math.round(headBox.left + headBox.width / 2),
                y: Math.round(headBox.top + headBox.height / 2),
                opacity: getComputedStyle(headElement).opacity
            }
        };

        // How far the visible carrier moved since the last sample - the
        // stall will show as speed collapsing to zero while still visible
        if (samplerPrevious !== null) {
            var dx = sample.ghost.x - samplerPrevious.ghost.x;
            var dy = sample.ghost.y - samplerPrevious.ghost.y;
            sample.ghostStepPx = Math.round(Math.sqrt(dx * dx + dy * dy));

            var liftDx = sample.lift.x - samplerPrevious.lift.x;
            var liftDy = sample.lift.y - samplerPrevious.lift.y;
            sample.liftStepPx = Math.round(Math.sqrt(liftDx * liftDx + liftDy * liftDy));
        }

        samplerPrevious = sample;
        caretLog('nudge-sample', 't=' + sample.tMs + 'ms', sample);

        setTimeout(function() { requestAnimationFrame(sampleFrame); }, 80);
    };

    requestAnimationFrame(sampleFrame);

    // The first click anywhere means the user is at work - the rehearsal
    // steps aside for this rule
    if (!this.nudgeListenerAttached) {
        this.nudgeListenerAttached = true;
        this.container.addEventListener('pointerdown', function() {
            self.dismissNudge();
        });
    }

    // The path is measured against the current layout - a resize outdates
    // it, so the overlay goes and the next render rebuilds it
    window.addEventListener('resize', function() {
        self.removeNudge();
    }, {once: true});
};

})();
