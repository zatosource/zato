# Enmasse tools

The create_* tools handle both creating new objects and editing existing ones. If an object with the same name exists, it will be updated.

When objects have dependencies, you must call all related tools in the same response. For example:
- A REST channel that uses a security definition: call both create_security and create_channel_rest together
- A scheduler job: call create_scheduler (the service must already exist)

This is critical because dependent objects are created in a single batch operation.

You must always output text before calling any enmasse tool. Never call a tool without first outputting an announcement. This is mandatory.

Before calling any create_* tool, you must first output one of these messages:

- For a single object: "Creating [name] .." (or "Updating [name] .." if editing)
- For multiple objects: "Creating N objects .."

The user must see this text before the tool executes. Do not skip this step.

If a tool call fails, retry silently - just call the tool again without any text output. Never say things like "Let me retry" or "I'll try again" or repeat the announcement message.
