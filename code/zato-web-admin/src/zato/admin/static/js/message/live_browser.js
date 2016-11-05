$(document).ready(function() {

    $.fn.zato.message.live_browser.WebSocketClient = new Class({

        initialize: function(address, username, secret) {

            var self = this;

            this.address = address;
            this.username = username;
            this.secret = secret;

            self.current_callback = null;
            self.current_callback_params = null;

            this.auth_token = '';
            this.is_authenticated = false;
            this.is_connected = false;
            this.auth_req_id = 'zato.web.admin.ws.auth.' + $.fn.zato.get_random_string();

            console.log('Connecting to '+ this.address);

            // WebSocket client
            this.conn = new WebSocket(this.address);
            this.conn.onopen = this.on_open;
            this.conn.onclose= this.on_close;
            this.conn.onmessage = this.on_message;

        },

        authenticate: function() {

            req = self.get_request();

            req.meta.action = 'authenticate';
            req.meta.sec_type = 'jwt';
            req.meta.id = this.auth_req_id;
            req.meta.username = self.username;
            req.meta.secret = self.secret;

            self.send(req);
        },

        get_request: function() {
            req = {};
            req.meta = {};
            req.meta.client_name = 'zato.web.admin.live.message.browser ('+ window.navigator.userAgent + ')';
            req.meta.client_id = 'zato.wa.msg.browser.' + $.fn.zato.get_random_string();
            req.meta.timestamp = new Date().toISOString();

            return req;
        },

        send: function(req) {
            var req = JSON.stringify(req)
            console.log('Sending '+ req);
            self.conn.send(req);
        },

        on_open: function() {
            console.log('Opened connection to ' + self.address);
            self.authenticate();
        },

        on_close: function() {
            if(self.is_connected) {
                console.log('Closed connection to ' + self.address);
            }
        },

        on_after_subscription: function(msg) {
            if(msg.meta.status == "200") {
                $.fn.zato.user_message(true, "OK, subscribed successfully");
            }
            else {
                $.fn.zato.user_message(false, "Encountered an error, check server logs for details");
            }
        },

        on_message: function(e) {
            console.log('Received message ' + e.data);
            var msg = JSON.parse(e.data);

            if(!self.is_authenticated) {
                if(msg.meta.status == 200) {
                    if(msg.meta.in_reply_to != self.auth_req_id) {
                        console.warn('Received reply to an unknown request');
                    }
                    else {
                        console.log('User '+ self.username + ' logged in to '+ self.address);
                        self.auth_token = msg.data.token;
                        self.is_authenticated = true;
                        self.is_connected = true;
                        self.ping();
                    }
                }
                else {
                    console.warn('Did not receive status 200, cannot continue');
                }
            }
            else {
                if(msg.data != "zato-keep-alive-ping") {
                    if(self.current_callback) {
                        self.current_callback(msg);
                        self.current_callback = null;
                    }
                    else {
                        console.log('Ignoring message '+ e.data);
                    }
                }
            }
        },

        invoke_service: function(service_name, request) {
            req = self.get_request();
            req.meta.action = 'invoke-service';
            req.meta.id = 'zato.web.admin.ws.ping.' + $.fn.zato.get_random_string()
            req.data = {};
            req.data.input = {'data': {
                'service_name': service_name,
                'request': request
            }};

            self.send(req);
        },

        ping: function() {
            console.log('Sending ping to server');
            self.invoke_service('zato.ping');
        },

        get_input: function() {
            return {
                "cluster_id": $("#id_cluster").val(),
                "query": $("#id_query").val()
            };
        },

        form_submitted: function() {
            var input = self.get_input();
            if(!(input.cluster_id && input.query)) {
                return;
            }
            self.current_callback = self.on_after_subscription;
            self.invoke_service("tmp.live-browser.subscribe", {"query":input.query});
        }

    });

    $.fn.zato.message.live_browser.credentials_loaded = function(data, status) {
        if(status=='success') {
            console.log('Credentials loaded '+ JSON.stringify(data));
            var data = JSON.parse(data.responseText);
            var client = new $.fn.zato.message.live_browser.WebSocketClient(data.address, data.username, data.jwt_token);

            // Creates a globally accessible object
            self = client;

            // Intercept form submit clicks to handle everything in jQuery
            $("#main_page_form").submit(function(e) {
              client.form_submitted();
              e.preventDefault();
            });

        }
        else {
            console.warn(data);
        }
    }

   $.fn.zato.post('/zato/messages/live-browser/get-connection-details?cluster=' + $.fn.zato.get_url_param('cluster'),
        $.fn.zato.message.live_browser.credentials_loaded, "", null, true);

});