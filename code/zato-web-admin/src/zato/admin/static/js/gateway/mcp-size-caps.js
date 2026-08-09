// MCP gateway - the size caps micro-form, one descriptor for both pages
// that open it. The kit's popover engine renders it against whichever host
// it was set up with - the wizard's own form on the wizard page, a handful
// of hidden fields on the gateway list.

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
$.fn.zato.gateway.mcp.size_caps_descriptor = {
    title: 'Size caps',
    width: '430px',
    pages: [[
        [
            {field: 'max_response_size', label: 'Max response size (tokens)', kind: 'number'},
            {field: 'min_size_threshold', label: 'Activation threshold (tokens)', kind: 'number'}
        ],
        [
            {field: 'size_cap_mode', label: 'Over the cap', kind: 'select'},
            {field: 'characters_per_token', label: 'Characters per token', kind: 'text'}
        ]
    ]]
};
