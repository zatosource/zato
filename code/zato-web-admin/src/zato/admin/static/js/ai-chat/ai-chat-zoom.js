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
            e.stopPropagation();

            var target = e.target;
            var zone = this.detectZone(target, widget);

            if (!zone) {
                zone = 'messages';
            }

            var delta = e.deltaY > 0 ? -0.05 : 0.05;
            var newScale = Math.max(0.7, Math.min(1.5, this.zoneScales[zone] + delta));
            this.zoneScales[zone] = newScale;
            this.applyZoneZoom(widget, zone);
            this.saveZoneScales();

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
            var messagesEls = widget.querySelectorAll('.ai-chat-messages');
            var inputAreaEls = widget.querySelectorAll('.ai-chat-input-area');
            var inputEls = widget.querySelectorAll('.ai-chat-input');

            for (var i = 0; i < messagesEls.length; i++) {
                messagesEls[i].style.fontSize = (this.zoneScales.messages * 100) + '%';
            }
            for (var j = 0; j < inputAreaEls.length; j++) {
                inputAreaEls[j].style.fontSize = (this.zoneScales.inputArea * 100) + '%';
            }
            for (var k = 0; k < inputEls.length; k++) {
                inputEls[k].style.fontSize = (this.zoneScales.input * 100) + '%';
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
