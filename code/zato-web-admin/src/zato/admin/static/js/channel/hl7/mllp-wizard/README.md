# HL7 MLLP channel wizard

The three-step page that creates an HL7 MLLP channel, rendered by `templates/zato/channel/hl7/mllp-wizard.html`. The step engine, the popovers, the review renderer and the decision lines come from the wizard kit in `static/js/wizard-kit/` - this directory holds only what is MLLP's own. The wizard posts to the same create endpoint the full-page editor uses, so a channel created here is a channel created there.

## Modules

| Module | Namespace | What it does |
|---|---|---|
| `core.js` | `wizard` | The kit instance - required fields, the name uniqueness check, the state, the help texts and `beforeSave` |
| `forms.js` | `wizard.forms` | The popover micro-forms of step 1 - transport, REST, routing - and the `securityList` field kind |
| `destinations.js` | `wizard.destinations` | Step 2 - the four decision lines, the state behind them and the serialization into the hidden fields |
| `destination-panels.js` | `wizard.destinations.panels` | The three panels step 2 opens - the destination picker, the service list and the reply list |
| `review.js` | `wizard.review` | The card summaries of step 2 and the review of step 3 |

They load in that order, after the kit and after `common/badge-picker.js`, because `core.js` calls `kit.core.setup` and `review.js` calls `kit.review.setup` at load time.

## Step 2 - four decisions

The step is four sentences, one decision each:

| Line | Value | Written into |
|---|---|---|
| Incoming messages go to | how many destinations, and how many of them are paused | `destinations` |
| Each message is handled by | the service | `service` |
| The destinations receive it | at the same time, one after another, or as the service decides | `delivery_mode` |
| The reply is produced by | the service or one destination | `respond_from` |

The delivery line only appears once there is a destination - with nothing to deliver to, the order they are delivered in is not a question. "The service decides" is the mode where the service hands each destination its own message through `self.destination[name]`.

The reply follows the list on its own: when the destination that was to produce it is paused or removed, the reply goes back to the service.

### The state

`wizard.state` carries `destinationList` - `{type, connection, isActive, options}` in the order messages travel - plus `delivery` and `respondFrom`. `destinations.serialize` writes all three into the hidden fields on Finish, in the shape the full-page editor produces. Everything else on step 2 lives in the rendered Django form, as it does on every other step.

### The destination picker

The panel behind the first line is the shared badge picker of `common/badge-picker.js`, the same control the security groups and the MCP gateways use - available connections on the left, the ones messages go to on the right, moved by a click or dragged across with the marquee selection and the ghost the picker draws. The filter row above the zones narrows by kind of connection and by name, which is how a list of hundreds is walked.

The right zone is the order of one-after-another delivery, so what the panel is closed with is what the channel does - `panels._readPicker` reads the zone back into `destinationList`.

A destination badge carries the switch that pauses it and the options its kind has, e.g. the method a REST call is made with. They come from the type and option definitions of `shared/destinations.js`, the same ones the editor uses, and they show only in the right zone, since a connection nothing is sent to has nothing to configure.

A row is read left to right: the kind comes first in a column of its own, so every name below starts at the same place, then the name, then the options held against the right edge where they line up as a column too. The options grow into whatever the name leaves and give way first when a name is long - past that the name is the one that gives way, with an ellipsis, and the switch at the end never gives way at all.

## Help texts

`wizard.helpDescriptions` returns the map behind every "How does it work?" badge - the shared field descriptions of `mllp-descriptions.js`, re-keyed for the popover inputs, plus the entries for the controls only the wizard has. A decision line takes part through its label's `for`, which names the chip the line holds.
