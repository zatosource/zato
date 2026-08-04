# Wizard kit

A config-driven framework for multi-step wizard pages, following the dashboard kit conventions - IIFE modules hanging sub-namespaces off one root, all domain specifics injected through config. The root namespace is `$.fn.zato.wizard_kit`, declared in `static/js/common.js`.

A wizard page is one dashboard card holding a step strip, one body per step, a review on the last step and a footer with Back, Next and Cancel. The rendered Django form is the single source of every field's value - whatever the wizard shows on its steps reads from and writes back into the form, so the payload posted on Finish is exactly what the matching full-page editor would post.

A page opened on an object that already exists says so with `is_edit: true` in its `init` options, and its footer is Cancel and Save instead of Back and Next. An edit is not a walk from one end to the other - each step stands on its own, is reached from the step strip and is saved from where it is. Save posts the same whole form Finish does, every step being in the DOM at once, so where the reader happened to be standing makes no difference to what is written. The review step is not offered either, its tab taken out of the strip - looking over what is about to be made is a create's business, an edit having the object in front of it already.

Three instances exist today:

- the HL7 MLLP channel wizard - `static/js/channel/hl7/mllp-wizard/`
- the HL7 MLLP outgoing connection wizard - `static/js/outgoing/hl7/mllp-wizard/`
- the file transfer schedule wizard for SFTP and SMB - `static/js/outgoing/file-transfer-schedule-wizard.js`

## Modules

| Module | Namespace | What it does |
|---|---|---|
| `core.js` | `kit.core` | The step engine and page state machine - step walking, the name badge, submit plumbing, the "How does it work?" wiring |
| `forms.js` | `kit.forms` | The popover micro-form engine - descriptor-driven tippy forms that seed from and write back to the Django form |
| `review.js` | `kit.review` | Card summaries with the fade replay and the review step's grouped-rows renderer with Edit links |
| `choices.js` | `kit.choices` | Pick-one choice cards - a radio group wearing the wizard card look, the selected card unfolds its inline fields |
| `select-rows.js` | `kit.selectRows` | A column of rows, each with its own selects and a delete link, plus the add link under the list |
| `lines.js` | `kit.lines` | Decision lines - a step body written as sentences, each line one label and one value, the value a chip opening a panel or a strip of options |
| `collapse.js` | `kit.collapse` | Collapsibles - a section folded behind one line of the step, and the groups a section or a card folds inside itself |
| `probe.js` | `kit.probe` | The live check - a button that posts what has been filled in so far to an endpoint and paints the verdict, before anything is saved |

An instance uses whichever modules its config declares - MLLP uses toggle rows and popovers, the schedule wizard uses choice cards and the context badge, both use the name badge, the help badges and the review renderer from the same code.

## How an instance is built

The instance module hands its own namespace over to `setup`, together with a config object - setup installs the generic machinery onto the namespace and the instance adds its specifics around it:

```javascript
var wizard = $.fn.zato.channel.hl7.mllp.wizard;

$.fn.zato.wizard_kit.core.setup(wizard, {
    idPrefix: 'mllp-wizard',
    formSelector: '#create-form',
    stepCount: 3,
    requiredFields: ['name', 'service'],
    helpRowSelector: '.dashboard-card-header, .wizard-name-row',
    nameUnique: {source: 'generic_connection', field: 'name',
        filterName: 'type_', filterValue: 'channel-hl7-mllp'},
    onInit: function() { /* wire instance controls */ },
    beforeSave: function(form) { /* write hidden fields */ }
});

$.fn.zato.wizard_kit.forms.setup(wizard, {descriptors: {...}});
$.fn.zato.wizard_kit.review.setup(wizard);
```

The page then calls `wizard.init({list_url: ...})` when the DOM is ready.

## Init options

| Key | Meaning |
|---|---|
| `list_url` | Where Cancel and a finished save go back to |
| `is_edit` | Whether the page was opened on an object that already exists |

## Core config contract

| Key | Meaning |
|---|---|
| `idPrefix` | Every element id on the page starts with it, see the element contract below |
| `formSelector` | The form that Finish posts |
| `stepCount` | How many steps the wizard has |
| `fieldPrefix` | Optional, in front of Django field ids, e.g. `edit-` - this is how one template serves both create and edit. The MLLP outgoing connection wizard is the instance that uses it, its edit endpoint reading `edit-` prefixed names |
| `nameField` | The field the header badge mirrors, `name` by default |
| `requiredFields` | Fields that must not be empty on submit |
| `helpRowSelector` | Optional, the rows the page-wide "How does it work?" badge walks through |
| `nameUnique` | Optional, a live uniqueness check for the name - `{source, field, filterName, filterValue}` |
| `onInit` | Optional, instance wiring run during init |
| `beforeSave` | Optional, runs before validation on Finish, e.g. to serialize rows into hidden fields |
| `missingTargets` | Optional, where each required field is read on the review and answered on its step, keyed by field name - see the section on the answers a save waits for |
| `missingExtra` | Optional, the questions still open that are not one empty field, as a list of the same entries |
| `finishLabel` | Optional, what the button on the last step says - named after the action the wizard ends in, `Save` for all three of them |
| `savedMessage`, `saveErrorMessage`, `redirectDelayMs`, `nextLabel`, `scrollBehavior`, `scrollBlock`, `missingClass`, `missingRowSelector`, `pulsateClass` | Optional, the defaults in `kit.core.defaults` cover them |

`core.setup` installs on the namespace: `config`, `state`, `field`, `fieldSelector`, `init`, `goToStep`, `reveal`, `pulsate`, `missingList`, `checkMissing`, `save`, `updateNameBadge`, `initNameBadge`, `onNameCheckResult`. `wizard.reveal(element)` scrolls one element into view the gentle way, `wizard.pulsate(elements)` pulses a set of them with the shared honey `.pulsate` of `style.css`, the one the updates page wears on a version it has just found - together they are how a refused save shows what it is waiting for. The `wizard.field(name)` accessor resolves `#id_<fieldPrefix><name>` and is the one way into the rendered Django form. `wizard.fieldSelector(name)` returns the same id as a selector string, which is what the shared helpers that mark a field required or check it for uniqueness take - everything inside the kit goes through one of the two, so a prefixed instance is prefixed everywhere.

## Element contract

All ids derive from `idPrefix` and all are required:

- `#<idPrefix>` - the card, also the page-wide help badge's div
- `#<idPrefix>-steps` - the step strip, tabs carry `.wizard-step` and a `data-step` attribute
- `#<idPrefix>-step-body-N` - one body per step, N counted from 0
- `#<idPrefix>-name-badge` - the header badge mirroring the name
- `#<idPrefix>-back`, `-next`, `-cancel`, `-save`, `-status` - the footer. Back is rendered `disabled`, since a page opens on its first step and there is nothing behind it - the step walking takes it from there. Save is rendered `hidden`, a create ending in the Next button rather than in one of its own. Cancel is an `a.wizard-cancel` rather than a button, leaving being no action of the page's own, so it wears the same link face as everything else on a wizard. An edit hides Back and Next and moves Save into the middle they leave
- `#<idPrefix>-how-it-works` - the page-wide help badge
- `#<idPrefix>-review` - where the review step renders

## Instance contract

The namespace must provide:

- `wizard.helpDescriptions()` - the help texts for every badge, usually a thin wrapper around a descriptions module such as `mllp-descriptions.js` or `file-transfer-schedule-descriptions.js`
- `wizard.review.render()` - renders the review step, usually through `review.renderGroups`
- `wizard.review.refreshSummaries()` - recomputes the card summaries

## Micro-form descriptors

Each micro-form is described by a descriptor - `{title, width, pages}`, each page a list of entries. An entry is either one field spec, shown on its own line, or a list of field specs, shown side by side in one row. A field spec points at one of the hidden Django form inputs by name, so opening a micro-form seeds its inputs from the form and pressing OK writes the answers back. Selects clone their choices from the underlying Django select, which keeps the wizard and the matching full-page editor on the same single list of options.

A spec's keys: `field` (the Django form field name), `label`, `kind` - one of `text`, `number`, `select`, `checkbox` or a kind the instance registered - plus the optional `unitField`, `width`, `placeholder` and `hint`.

`forms.setup` asks its host for `config.idPrefix`, `field(name)`, `helpDescriptions()` and, unless the host says otherwise, a review to refresh, so a page that is no wizard at all can host one of these popovers on a few hidden inputs of its own - the HL7 MLLP channel list opens the wizard's Message matchers straight from its Match column that way. Such a host passes `onDone`, what accepting the last page comes to, and `showCancel: true`, its popover being the whole of the save rather than one answer on a page saved later on, which puts a Cancel next to the button that accepts it. `forms.helpDescriptions(shared)` says the host's field help again under the ids the popover inputs take.

A `number` field is stepped with the arrows the browser draws on it and is only as wide as a count needs, whatever the label above it says. A `checkbox` puts its switch at the end of the line its label takes, so a page of them reads as one column of switches rather than as one switch per length of text.

Field kinds beyond the built-in ones come from the instance:

```javascript
wizard.forms.registerKind('securityList', {
    build: function(fieldSpec, row) { ... },
    save: function(popper, fieldSpec) { ... }
});
```

## Select rows

A select row list is a column of rows, each holding one or more selects with a delete link at its end, and an add link under the list. Both the security definitions the MLLP wizard picks in its REST popover and the destinations it lists on step 2 are such rows, on a popover and on a step body respectively, so the two read as one kind of control.

The list is whatever element carries `.wizard-select-list`. A row is appended by handing over what goes into it and what to do once it is deleted - the delete link and the row itself come from the kit:

```javascript
$.fn.zato.wizard_kit.selectRows.appendRow(list,
    function(row) { row.appendChild(mySelect); },
    function() { /* the row is already gone from the DOM */ }
);

list.after($.fn.zato.wizard_kit.selectRows.buildAddLink('Add security', function() { ... }));
```

## Decision lines

A step whose answers are few but consequential reads better as sentences than as a form. A line is a label and one value, the value either a chip that opens a panel or a strip of options with the picked one in the accent:

```javascript
$.fn.zato.wizard_kit.lines.setChip('mllp-wizard-slot-destinations', {
    text: '3 destinations',
    note: '1 paused',
    panel: {title: 'destinations', width: 980, minWidth: 700, build: buildDestinationsPanel}
});

$.fn.zato.wizard_kit.lines.setSegments('mllp-wizard-slot-delivery', modeList, currentMode, onPick);
```

The template holds the labels and one empty slot per line, the instance fills the slots on every render. A chip is solid once its line has an answer and dashed while it is still waiting for one, which is the only difference between them - an unanswered line reads as unanswered, never as a fault.

A strip of options is the shared tab component of `shared/tabs.css`, the same one the step headers use, with its tokens repointed - no border, nothing rounded, no capitals, and the picked option in the lighter of the two dashboard blues so a strip inside a step never reads as the step strip above it.

Every option carries `is_active`, and one that is off is not put on screen. An option not yet ready to be offered is turned off rather than deleted, so turning it back on is all it takes to have it again.

A panel wears the shared popup chrome of `shared/popup.css` - the dark header with the grip, the sandy body, the buttons row with OK - so it is the same popup the micro-forms and the IDE menus open, and `$.fn.zato.popup.install_drag` makes its header the handle. `$.fn.zato.popup.install_resize` adds the grip in each bottom corner, so a panel is dragged wider and taller from either side, never below the `minWidth` its own spec names by the kit's `panelMinHeight`. Where a panel is left is where it opens next time - `save_geometry` writes it under the chip's id when a drag or a resize ends and `restore_geometry` reads it back, clamped to the window in case the window is smaller now, and only a panel that was never moved hangs under its chip. One panel is open at a time, a press outside it or Escape closes it.

The `build` function fills the body and may return a function to run when the panel closes, which is how a panel that edits the DOM directly - a badge picker, say - writes its answers back into the state. It runs while the panel is still on the page, so it can read the answers out of it. Inside a panel the kit offers `buildFilter` and `buildPickRow`, so a panel is a filter above a list of rows, and the row under it holds nothing but OK.

A list in a panel keeps its height with the scrollbar always in view, which is what makes a filter over hundreds of entries feel steady - nothing resizes as the matches narrow. The panel runs one flex column from itself down to the lists, so the room a corner adds or takes away lands on the lists alone and the filter, the headings and the buttons row stay exactly where they are.

## Collapsibles

A step with more to offer than it has room for folds the rest away. A section is folded behind one line reading like the rest of the step - a label, a link saying what is currently set and a soft hint offering the click:

```javascript
$.fn.zato.wizard_kit.collapse.initSection({
    toggleId: 'mllp-wizard-edit-options',
    bodyId: 'mllp-wizard-options-body',
    hintId: 'mllp-wizard-hint-options'
});

$.fn.zato.wizard_kit.collapse.initGroups('#mllp-wizard-tolerance-body');
```

A group is folded behind its own heading with a chevron, and groups sit inside a section or a card one heading after another, each opening on its own. The markup is `.wizard-collapse-group` holding a `.wizard-collapse-group-title` and the `.wizard-collapse-group-body` right after it, and the template decides what starts open by putting `hidden` on the bodies it wants closed.

Both hide with the `hidden` attribute rather than with a height that animates - a body sliding out of something that is itself sliding open is what makes an opening jerk. The spacing, the indent under a heading and the chevron are the kit's, so an instance writes only what its own body holds.

## The live check

Some answers can be proven right there and then. A probe is one button and one verdict beside it - it posts the named fields of the rendered Django form to an endpoint of the instance's choosing and paints what comes back:

```javascript
$.fn.zato.wizard_kit.probe.init(wizard, {
    slotId: 'mllp-outconn-wizard-slot-check',
    buttonId: 'mllp-outconn-wizard-check',
    endpoint: '/zato/outgoing/hl7/mllp/wizard/test/?cluster=1',
    fields: ['address', 'start_seq', 'end_seq', 'recv_timeout'],
    runLabel: 'Test the connection'
});
```

The template holds the row and its label, the label pointing at `buttonId` so the check is a regular "How does it work?" stop, and the kit fills the slot. Nothing is stored, so a probe works on the first step of a wizard that has never saved - which is the point of it, a reader finding out that an address is wrong before creating anything rather than after.

The endpoint answers with `{is_ok, summary}`. What the one line says is the instance's own view's business, the kit only decides how it looks - green for the answer that came back, red for the one that did not. A probe that has not been run yet says nothing at all, so a step only walked through never reads as a failure. `init` returns a handle with `reset()`, for an instance clearing the verdict once an answer the check was about has changed.

## Review groups

The review step renders from a list of groups - each group is `{label, step, rows}`, each row a `[key, value]` pair. The value is usually text but may also be a ready DOM Node, e.g. a badge. Each group carries an Edit link that goes to the step the answers came from.

A group may also carry:

- `listRows` - rows of one repeating kind, one per destination say, shown before the rest of the group. Once there are more of them than `kit.review.config.listScrollAfter`, they go into a box that scrolls, so a long list never pushes the rest of the review off the page. The box is given its height as a count of rows, which is why a review row is one line tall.
- `edit` - what to open on the step the Edit link goes to, for a group whose answers are given in a micro-form, a panel or a folded card rather than on the step itself. A group whose answers are on the step needs none.

The pointer anywhere on a group marks the whole group - the label wears `$.fn.zato.highlight_badge`, the same class and the same pair of calls the data tables use on the name cell of a row with an inline form open, and the group's rule and rows take the honey up in the stylesheet.

The pointer on the link itself shows a tooltip naming where the link goes, the group's label in lower case, e.g. `Edit tolerance`. The link's own text keeps its color.

Card summaries go through `review.setSummary(elementId, text)`, which replays the fade-in when the text changed.

Every question a step asks has a row of its own, whether it has been answered or not - a row left out is a question the reader cannot check. A row states what is set, never what not setting it would mean, so an unanswered one reads as `Not set` or as the plain absence it is, e.g. `No service`.

## The answers a save waits for

A wizard is saved once every question it must answer has been. Which those are is one map in the core config, keyed by field name, saying where each field is read on the review and where it is answered:

```javascript
missingTargets: {
    name:      {group: 'Basics', label: 'Name'},
    start_seq: {group: 'Transport', anchorSelector: '#mllp-wizard-row-transport'}
},

missingExtra: function() {
    return [{label: 'Service', group: 'Destinations and service',
        anchorSelector: '#mllp-wizard-line-service'}];
}
```

- `group` is the label of the review group the field is read in, one of those `review.render` passes to `renderGroups`. Both are usually read off one map on the instance's own config, so the two files name a section once.
- `label` is optional - it defaults to the label of the micro-form input the field is edited in, the descriptors being the one place a popover field is named. A field no popover holds spells its own out.
- `anchorSelector` is optional - it is the row a refused save marks and scrolls to, e.g. the line that opens the popover holding the field. By default it is the field's own row, whatever matches `kit.core.defaults.missingRowSelector` around it.

Which step an answer is given on is never declared - the kit reads it off the step body the anchor sits in.

`missingExtra` is for a question that is not one empty field, e.g. an MLLP channel needing either a service or a destination, neither of them required on its own.

`wizard.missingList()` is every such question still open. The review renderer reads it on each render and writes `Missing` in red into the section each entry belongs to - over the row already asking the question, or as a row of its own for a question no row mentions, so an instance writes its rows as if everything were answered. `wizard.checkMissing()` is what a save runs before it posts: every open question pulses where it is asked, the ones off screen included, and the page scrolls to the first of them - with the review on screen that is the word `Missing` in it, anywhere else the label of the row on the step the answer is given on, the row itself wearing `.wizard-missing`. Nothing is said in a message area or a popup - the page shows what it is waiting for where the answer is given.

## Choice cards

Cards share a `data-choice-group` value, each has its own `data-choice-id`, and the body with the card's inline fields is optional:

```javascript
var handle = $.fn.zato.wizard_kit.choices.init({
    group: 'ready',
    onChange: function(choiceId) { ... }
});

handle.get();          // the selected card's data-choice-id
handle.set('marker');  // selects a card programmatically
```

Clicks inside the unfolded body do not re-select, so typing into the card's own inputs never steals the focus.

## CSS

The shared stylesheet is `static/css/shared/wizard-kit.css` - the card, the step strip, the badges, the name row, sections, toggle rows, select rows, the service picker, option cards, choice cards, the review, the popover micro-forms (tippy theme `wizard`), the live check, the footer and the status area. The decision lines have one of their own, `static/css/shared/wizard-lines.css` - the lines, the chips, the options strip and the panels, including how a badge picker sits inside a panel. An instance stylesheet adds only what is truly its own, e.g. the MLLP tolerance grid.

Parameterization runs through the `--wizard-*` tokens, declared with defaults on `:root` because the popover micro-forms are appended to `document.body`, outside any page container. An instance recolors itself by overriding the tokens in its own stylesheet, also on `:root`, since one page carries one wizard.

| Token | Meaning |
|---|---|
| `--wizard-accent` | The step strip, links and focus color |
| `--wizard-done` | The green of summaries and success |
| `--wizard-error` | The red of alerts and failures |
| `--wizard-border` | Hairlines inside the card |
| `--wizard-border-strong` | Input borders and off sliders |
| `--wizard-text` | The main text color |
| `--wizard-text-muted` | Secondary text |
| `--wizard-text-faint` | Hints and placeholders |
