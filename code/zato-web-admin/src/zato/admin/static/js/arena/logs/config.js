
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.arena === 'undefined') { $.fn.zato.arena = {}; }
if (typeof $.fn.zato.arena.logs === 'undefined') { $.fn.zato.arena.logs = {}; }

$.fn.zato.arena.logs.config = {

    cluster_id: '1',

    scopes: {
        scheduler: {
            name: 'scheduler',
            display_name: 'Scheduler',
            aliases: ['job', 'run', 'task', 'customer', 'cust', 'svc', 'service', 'err', 'error', 'dur', 'duration'],
            default_limit: 50
        },
        pubsub: {
            name: 'pubsub',
            display_name: 'Pub/Sub',
            aliases: ['topic', 'ep', 'endpoint', 'queue', 'q'],
            default_limit: 50
        }
    },

    urls: {
        search: '/zato/arena/logs/search/',
        get: '/zato/arena/logs/get/',
        series: '/zato/arena/logs/series/',
        children: '/zato/arena/logs/children/',
        by_attr: '/zato/arena/logs/by-attr/',
        by_range: '/zato/arena/logs/by-range/',
        by_float_range: '/zato/arena/logs/by-float-range/',
        by_text: '/zato/arena/logs/by-text/'
    },

    pagination: {
        default_limit: 50,
        page_sizes: [25, 50, 100, 200]
    }
};
