(function() {
    'use strict';

    var STORAGE_KEY_ZONE_ZOOM = 'zato.ai-chat.zone-zoom';

    var AIChatZoom = {

        zoneScales: {
            messages: 1.0,
            inputArea: 1.0,
            input: 1.0
        },

        init: function() {
            this.loadZoneScales();
        },

        loadZoneScales: function() {
            var stored = localStorage.getItem(STORAGE_KEY_ZONE_ZOOM);
            if (stored) {
                try {
                    var parsed = JSON.parse(stored);
                    this.zoneScales = {
                        messages: parsed.messages || 1.0,
                        inputArea: parsed.inputArea || 1.0,
                        input: parsed.input || 1.0
                    };
                } catch (e) {
                    console.debug('AIChatZoom.loadZoneScales: failed to parse');
                }
            }
        },

        saveZoneScales: function() {
            localStorage.setItem(STORAGE_KEY_ZONE_ZOOM, JSON.stringify(this.zoneScales));
        },

        handleWheel: function(widget, e, currentScale) {
            if (!e.ctrlKey) {
                return currentScale;
            }

            e.preventDefault();

            var target = e.target;
            var zone = this.detectZone(target, widget);

            if (zone) {
                var delta = e.deltaY > 0 ? -0.05 : 0.05;
                var newScale = Math.max(0.7, Math.min(1.5, this.zoneScales[zone] + delta));
                this.zoneScales[zone] = newScale;
                this.applyZoneZoom(widget, zone);
                this.saveZoneScales();
                console.debug('AIChatZoom.handleWheel: zone:', zone, 'scale:', newScale);
            }

            return currentScale;
        },

        detectZone: function(target, widget) {
            if (target.closest('.ai-chat-messages')) {
                return 'messages';
            }
            if (target.closest('.ai-chat-input')) {
                return 'input';
            }
            if (target.closest('.ai-chat-input-area')) {
                return 'inputArea';
            }
            return null;
        },

        applyZoneZoom: function(widget, zone) {
            var element = null;
            var scale = this.zoneScales[zone];

            if (zone === 'messages') {
                element = widget.querySelector('.ai-chat-messages');
            } else if (zone === 'input') {
                element = widget.querySelector('.ai-chat-input');
            } else if (zone === 'inputArea') {
                element = widget.querySelector('.ai-chat-input-area');
            }

            if (element) {
                element.style.fontSize = (scale * 100) + '%';
            }
        },

        applyAllZoneZooms: function(widget) {
            var messagesEl = widget.querySelector('.ai-chat-messages');
            var inputAreaEl = widget.querySelector('.ai-chat-input-area');
            var inputEl = widget.querySelector('.ai-chat-input');

            if (messagesEl) {
                messagesEl.style.fontSize = (this.zoneScales.messages * 100) + '%';
            }
            if (inputAreaEl) {
                inputAreaEl.style.fontSize = (this.zoneScales.inputArea * 100) + '%';
            }
            if (inputEl) {
                inputEl.style.fontSize = (this.zoneScales.input * 100) + '%';
            }
        },

        applyZoom: function(widget, scale) {
            this.applyAllZoneZooms(widget);
        },

        resetZoom: function(widget) {
            widget.style.transform = '';
            return 1.0;
        }
    };

    window.AIChatZoom = AIChatZoom;

})();
