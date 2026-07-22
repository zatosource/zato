# Wizard kit

A config-driven framework for multi-step wizard pages, following the dashboard kit conventions - IIFE modules hanging sub-namespaces off one root, all domain specifics injected through config. The root namespace is `$.fn.zato.wizard_kit`, declared in `static/js/common.js`.

A wizard page is one dashboard card holding a step strip, one body per step, a review on the last step and a footer with Back, Next and Cancel. The rendered Django form is the single source of every field's value - whatever the wizard shows on its steps reads from and writes back into the form, so the payload posted on Finish is exactly what the matching full-page editor would post.

Two instances exist today:

- the HL7 MLLP channel wizard - `static/js/channel/hl7/mllp-wizard/`
- the file transfer schedule wizard for SFTP and SMB - `static/js/outgoing/file-transfer-schedule-wizard.js`

## Modules

| Module | Namespace | What it does |
|---|---|---|
| `core.js` | `kit.core` | The step engine and page state machine - step walking, the name badge, submit plumbing, the "How does it work?" wiring |
| `forms.js` | `kit.forms` | The popover micro-form engine - descriptor-driven tippy forms that seed from and write back to the Django form |
| `review.js` | `kit.review` | Card summaries with the fade replay and the review step's grouped-rows renderer with Edit links |
| `choices.js` | `kit.choices` | Pick-one choice cards - a radio group wearing the wizard card look, the selected card unfolds its inline fields |

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

## Core config contract

| Key | Meaning |
|---|---|
| `idPrefix` | Every element id on the page starts with it, see the element contract below |
| `formSelector` | The form that Finish posts |
| `stepCount` | How many steps the wizard has |
| `fieldPrefix` | Optional, in front of Django field ids, e.g. `edit-` - this is how one template serves both create and edit |
| `nameField` | The field the header badge mirrors, `name` by default |
| `requiredFields` | Fields that must not be empty on submit |
| `helpRowSelector` | Optional, the rows the page-wide "How does it work?" badge walks through |
| `nameUnique` | Optional, a live uniqueness check for the name - `{source, field, filterName, filterValue}` |
| `onInit` | Optional, instance wiring run during init |
| `beforeSave` | Optional, runs before validation on Finish, e.g. to serialize rows into hidden fields |
| `savedMessage`, `saveErrorMessage`, `redirectDelayMs`, `finishLabel`, `nextLabel` | Optional, the defaults in `kit.core.defaults` cover them |

`core.setup` installs on the namespace: `config`, `state`, `field`, `init`, `goToStep`, `save`, `updateNameBadge`, `initNameBadge`, `onNameCheckResult`. The `wizard.field(name)` accessor resolves `#id_<fieldPrefix><name>` and is the one way into the rendered Django form.

## Element contract

All ids derive from `idPrefix` and all are required:

- `#<idPrefix>` - the card, also the page-wide help badge's div
- `#<idPrefix>-steps` - the step strip, tabs carry `.wizard-step` and a `data-step` attribute
- `#<idPrefix>-step-body-N` - one body per step, N counted from 0
- `#<idPrefix>-name-badge` - the header badge mirroring the name
- `#<idPrefix>-back`, `-next`, `-cancel`, `-status` - the footer
- `#<idPrefix>-how-it-works` - the page-wide help badge
- `#<idPrefix>-review` - where the review step renders

## Instance contract

The namespace must provide:

- `wizard.helpDescriptions()` - the help texts for every badge, usually a thin wrapper around a descriptions module such as `mllp-descriptions.js` or `file-transfer-schedule-descriptions.js`
- `wizard.review.render()` - renders the review step, usually through `review.renderGroups`
- `wizard.review.refreshSummaries()` - recomputes the card summaries

## Micro-form descriptors

Each micro-form is described by a descriptor - `{title, width, pages}`, each page a list of entries. An entry is either one field spec, shown on its own line, or a list of field specs, shown side by side in one row. A field spec points at one of the hidden Django form inputs by name, so opening a micro-form seeds its inputs from the form and pressing OK writes the answers back. Selects clone their choices from the underlying Django select, which keeps the wizard and the matching full-page editor on the same single list of options.

A spec's keys: `field` (the Django form field name), `label`, `kind` - one of `text`, `select`, `checkbox` or a kind the instance registered - plus the optional `unitField`, `width`, `placeholder` and `hint`.

Field kinds beyond the built-in ones come from the instance:

```javascript
wizard.forms.registerKind('securityList', {
    build: function(fieldSpec, row) { ... },
    save: function(popper, fieldSpec) { ... }
});
```

## Review groups

The review step renders from a list of groups - each group is `{label, step, rows}`, each row a `[key, value]` pair. The value is usually text but may also be a ready DOM Node, e.g. a badge. Each group carries an Edit link that jumps back to the step the answers came from.

Card summaries go through `review.setSummary(elementId, text)`, which replays the fade-in when the text changed.

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

The shared stylesheet is `static/css/shared/wizard-kit.css` - the card, the step strip, the badges, the name row, sections, toggle rows, option cards, choice cards, the review, the popover micro-forms (tippy theme `wizard`), the footer and the status area. An instance stylesheet adds only what is truly its own, e.g. the MLLP security rows or the tolerance grid.

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
