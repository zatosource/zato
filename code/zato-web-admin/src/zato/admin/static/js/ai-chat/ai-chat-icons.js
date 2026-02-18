var AIChatIcons = {

    pin: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M15 12.423L16.577 14v1H12.5v5l-.5.5l-.5-.5v-5H7.423v-1L9 12.423V5H8V4h8v1h-1zM8.85 14h6.3L14 12.85V5h-4v7.85zM12 14"/></svg>',

    lock: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M5 21V9h3V7q0-1.671 1.165-2.835Q10.329 3 12 3t2.836 1.165T16 7v2h3v12zm1-1h12V10H6zm7.066-3.934q.434-.433.434-1.066t-.434-1.066T12 13.5t-1.066.434Q10.5 14.367 10.5 15t.434 1.066q.433.434 1.066.434t1.066-.434M9 9h6V7q0-1.25-.875-2.125T12 4t-2.125.875T9 7zM6 20V10z"/></svg>',

    export: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M6 20q-.825 0-1.412-.587T4 18v-3h2v3h12v-3h2v3q0 .825-.587 1.413T18 20zm6-4l-5-5l1.4-1.45l2.6 2.6V4h2v8.15l2.6-2.6L17 11z"/></svg>',

    chevronDown: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6l-6-6z"/></svg>',

    checklist: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 10h4.616V9H12zm0 5h4.616v-1H12zm-2.126-4.626q.357-.357.357-.874t-.357-.874T9 8.269t-.874.357t-.357.874t.357.874t.874.357t.874-.357m0 5q.357-.357.357-.874t-.357-.874T9 13.269t-.874.357t-.357.874t.357.874t.874.357t.874-.357M5.616 20q-.691 0-1.153-.462T4 18.384V5.616q0-.691.463-1.153T5.616 4h12.769q.69 0 1.153.463T20 5.616v12.769q0 .69-.462 1.153T18.384 20zm0-1h12.769q.23 0 .423-.192t.192-.424V5.616q0-.231-.192-.424T18.384 5H5.616q-.231 0-.424.192T5 5.616v12.769q0 .23.192.423t.423.192M5 5v14z"/></svg>',

    get: function(name, size) {
        var svg = this[name];
        if (!svg) {
            return '';
        }
        if (size) {
            svg = svg.replace(/width="24"/, 'width="' + size + '"');
            svg = svg.replace(/height="24"/, 'height="' + size + '"');
        }
        return svg;
    }

};
