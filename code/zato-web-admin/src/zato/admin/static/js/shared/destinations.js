// Destinations - what a channel's destination list is made of.
//
// A destination is an outgoing connection the platform delivers each message
// to after the channel's service runs. This module holds the definitions every
// page that edits such a list works from - the kinds of connection a
// destination may be, the options each kind carries and where the connections
// themselves are read from.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// Include this file in the page and read the definitions off the config:
//
//      <script src="/static/js/shared/destinations.js"></script>
//
//      var typeList = $.fn.zato.destinations.config.typeList;
//
// A destination list is stored in a form's hidden "destinations" field as JSON:
//
//      [{"name":"...", "type":"rest", "connection":"...", "is_active":true, "options":{"method":"POST"}}]
//
// and "respond_from" holds either "service" or the name of one destination.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.destinations.config = {
    connectionListUrl: '/zato/destinations/get-connection-list/',
    respondFromService: 'service',
    respondFromServiceLabel: 'The service',
    defaultType: 'rest',

    typeList: [
        {id: 'rest',     label: 'REST'},
        {id: 'hl7-mllp', label: 'MLLP'},
        {id: 'hl7-fhir', label: 'FHIR'},
        {id: 'smtp',     label: 'Email'}
    ],
    optionList: {
        'rest': [
            {id: 'method', label: 'Method', kind: 'select', values: ['POST', 'PUT', 'PATCH', 'GET', 'DELETE']}
        ],
        'hl7-mllp': [],
        'hl7-fhir': [
            {id: 'method', label: 'Method', kind: 'select', values: ['POST', 'PUT', 'PATCH', 'GET', 'DELETE']},
            {id: 'path',   label: 'Path',   kind: 'text',   placeholder: '/Patient'}
        ],
        'smtp': [
            {id: 'to',      label: 'To',      kind: 'text', placeholder: 'name@example.com'},
            {id: 'subject', label: 'Subject', kind: 'text', placeholder: 'Subject line'}
        ]
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
