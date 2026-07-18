
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

let Copy_Tooltip_Timeout = 1000;

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

(function() {
    var suppressedWarnings = [
        'Synchronous XMLHttpRequest',
        'setCapture',
        'releaseCapture',
        'ace.js',
        'Element.setCapture',
        'Element.releaseCapture',
        'setPointerCapture'
    ];

    var suppressedErrors = [
        'log-streaming'
    ];

    var originalWarn = console.warn;
    console.warn = function() {
        var args = Array.prototype.slice.call(arguments);
        var fullMessage = args.join(' ');
        for (var i = 0; i < suppressedWarnings.length; i++) {
            if (fullMessage.includes(suppressedWarnings[i])) {
                return;
            }
        }
        var stack = new Error().stack;
        if (stack && stack.includes('ace.js')) {
            return;
        }
        originalWarn.apply(console, arguments);
    };

    var originalError = console.error;
    console.error = function(message) {
        if (typeof message === 'string') {
            for (var i = 0; i < suppressedErrors.length; i++) {
                if (message.includes(suppressedErrors[i])) {
                    return;
                }
            }
        }
        originalError.apply(console, arguments);
    };
})();

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$(document).ready(function() {
    $("#invoke-service").click($.fn.zato.invoker.on_invoke_submitted);

    $("#payload-format-select").on("change", $.fn.zato.ide.on_payload_format_changed);
    $("#invoke-mode-select").on("change", $.fn.zato.ide.on_invoke_mode_changed);
    $.fn.zato.ide.init_sample_menu();

    if (window.zato && window.zato.initializeMessageViewer) {
        window.zato.initializeMessageViewer();
    }
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.init_editor = function(initial_header_status) {

    // Global variables
    window.zato_undeployed_prefix = "🔷 ";

    // All the keys that we use with LocalStorage
    window.zato_local_storage_key = {
        "zato_action_area_size": "zato.action-area-size",
        "zato_request_history": "zato.request-history",
        "zato_full_history": "zato.full-history",
    }

    // Request history tracking
    window.zato_request_history_index = -1;

    // Our initial file that we process
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();

    // Maps file names to Ace EditorSession objects.
    window.zato_editor_session_map = {};

    window.zato_editor = ace.edit("editor");
    window.zato_editor.setTheme("ace/theme/zato");
    $.fn.zato.ide.set_up_editor_session(window.zato_editor.session);

    window.zato_editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        newLineMode: "unix",
        fontSize: 16,
        fontFamily: "Zato_IDE_Font",
        cursorStyle: "ace"
    });

    // Store a reference to the editor as we will be likely switching to various files
    window.zato_editor_session_map[current_fs_location] = window.zato_editor;

    // Set initial data
    $.fn.zato.ide.populate_invoker_area();

    // Handle browser history back/forward actions
    window.onpopstate = function(event) {
        let name = event.state.name;
        $.fn.zato.ide.populate_document_title(name);
    }

    // Resizes the action area
    hotkeys("F2", $.fn.zato.ide.on_key_toggle_action_area);

    // Same as above (F2)
    window.zato_editor.commands.addCommand({
        name: "on_F2",
        bindKey: {win: "F2",  mac: "F2"},
        exec: function(_ignored_editor) {
            $.fn.zato.ide.on_key_toggle_action_area(null, null);
        }
    })

    // Ignore F1
    window.zato_editor.commands.addCommand({
        name: "on_F21",
        bindKey: {win: "F21",  mac: "F21"},
        exec: function(_ignored_editor) {
            // Explicitly do nothing
        }
    })

    // Ctrl-S to deploy a file
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "s") {
          e.preventDefault();
          $.fn.zato.ide.on_key_deploy_file(null, null);
        }
      });

    // Ctrl-Enter to invoke a service
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
          e.preventDefault();
          $.fn.zato.ide.on_key_invoke(null, null);
        }
      });

    // Ctrl-Up/Down to navigate request history in the textarea
    $("#data-request").on("keydown", function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "ArrowUp") {
            e.preventDefault();
            $.fn.zato.ide.on_request_history_up();
        } else if ((e.ctrlKey || e.metaKey) && e.key === "ArrowDown") {
            e.preventDefault();
            $.fn.zato.ide.on_request_history_down();
        } else if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            $.fn.zato.ide.open_history_overlay();
        }
    });

    // Ctrl-K globally to open history overlay
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
          e.preventDefault();
          $.fn.zato.ide.open_history_overlay();
        }
      });

    // Make sure the menu can be visible
    $(".pure-css-nav").hover(function() {
        $(".pure-css-nav").addClass("position-relative");
    });
    $(".pure-css-nav").mouseleave(function() {
        $(".pure-css-nav").removeClass("position-relative");
    });


    // Set the initial baseline for deployment status from the current editor content BEFORE loading from localStorage
    let key = $.fn.zato.ide.get_last_deployed_key();
    let editor_value = window.zato_editor.getValue();
    console.debug("init_editor: setting initial baseline with key:", JSON.stringify(key));
    console.debug("init_editor: editor_value length:", editor_value ? editor_value.length : null);
    localStorage.setItem(key, editor_value);
    console.debug("init_editor: initial baseline set");

    // This will try to load the content from LocalStorage
    $.fn.zato.ide.load_current_source_code_from_local_storage();

    window.zato_inactivity_interval = null;
    document.onkeydown = $.fn.zato.ide.reset_inactivity_timeout;

    $.fn.zato.ide.update_request_history_buttons();

    let is_mac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    let modifier_key = is_mac ? '⌘' : 'Ctrl';
    let placeholder_text = "Enter parameters as key=value pairs, e.g.:\nkey1=value1\nkey2=value2\n\n" +
                          modifier_key + "+K for full history";
    $("#data-request").attr("placeholder", placeholder_text);

    $.fn.zato.ide.init_resizer();

    let actionAreaContainer = document.getElementById('action-area-container');
    let actionArea = document.getElementById('action-area');

    function resizeDataResponse() {

        // The panel is resized rather than the textarea inside it - both the raw
        // and the parsed views fill the panel, so they always share one height
        // and the panel's bottom edge always stays in view.
        let responsePanel = document.getElementById('response-panel');

        let actionAreaHeight = actionArea.offsetHeight;
        let responsePanelTop = responsePanel.getBoundingClientRect().top;
        let actionAreaTop = actionArea.getBoundingClientRect().top;
        let offsetFromTop = responsePanelTop - actionAreaTop;
        let availableHeight = actionAreaHeight - offsetFromTop - 16;

        if (availableHeight > 100) {
            responsePanel.style.height = availableHeight + 'px';
        }
    }

    let dataRequest = document.getElementById('data-request');
    if (dataRequest) {
        let actionAreaHeight = actionArea.offsetHeight;
        let maxHeight = actionAreaHeight - 200;
        dataRequest.style.maxHeight = maxHeight + 'px';

        let savedHeight = store.get('zato.data-request-height');
        if (savedHeight) {
            dataRequest.style.height = savedHeight;
        }

        let resizeIndicator = document.createElement('div');
        resizeIndicator.id = 'data-request-resize-indicator';
        resizeIndicator.textContent = '⋯';
        resizeIndicator.style.cssText = 'position: absolute; left: 50%; transform: translate(-50%, -50%); font-size: 18px; color: #999; pointer-events: none; padding: 0 5px; z-index: 10; line-height: 1;';
        dataRequest.parentElement.style.position = 'relative';
        dataRequest.parentElement.appendChild(resizeIndicator);

        function updateIndicatorPosition() {
            let rect = dataRequest.getBoundingClientRect();
            let parentRect = dataRequest.parentElement.getBoundingClientRect();
            let top = rect.bottom - parentRect.top + 2;
            resizeIndicator.style.top = top + 'px';
        }
        updateIndicatorPosition();

        let isResizingTextarea = false;
        let startY = 0;
        let startHeight = 0;

        let invokerArea = dataRequest.closest('.invoker-area');

        invokerArea.addEventListener('mousemove', function(e) {
            if (isResizingTextarea) return;

            let rect = dataRequest.getBoundingClientRect();
            let bottomEdge = rect.bottom;
            let mouseY = e.clientY;

            if (mouseY >= bottomEdge - 6 && mouseY <= bottomEdge + 10) {
                invokerArea.style.cursor = 'ns-resize';
                resizeIndicator.style.color = '#666';
            } else {
                invokerArea.style.cursor = '';
                resizeIndicator.style.color = '#999';
            }
        });

        invokerArea.addEventListener('mouseleave', function() {
            if (!isResizingTextarea) {
                invokerArea.style.cursor = '';
                resizeIndicator.style.color = '#999';
            }
        });

        invokerArea.addEventListener('mousedown', function(e) {
            let rect = dataRequest.getBoundingClientRect();
            let bottomEdge = rect.bottom;
            let mouseY = e.clientY;

            if (mouseY >= bottomEdge - 6 && mouseY <= bottomEdge + 10) {
                isResizingTextarea = true;
                startY = e.clientY;
                startHeight = dataRequest.offsetHeight;
                e.preventDefault();
            }
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizingTextarea) return;

            let deltaY = e.clientY - startY;
            let newHeight = startHeight + deltaY;
            let maxHeight = parseInt(dataRequest.style.maxHeight);

            if (newHeight >= 40 && newHeight <= maxHeight) {
                dataRequest.style.height = newHeight + 'px';
                updateIndicatorPosition();
            }
        });

        document.addEventListener('mouseup', function() {
            if (isResizingTextarea) {
                isResizingTextarea = false;
            }
        });
    }

    resizeDataResponse();
    window.addEventListener('resize', () => {
        if (dataRequest) {
            let actionAreaHeight = actionArea.offsetHeight;
            let maxHeight = actionAreaHeight - 200;
            dataRequest.style.maxHeight = maxHeight + 'px';
        }
        resizeDataResponse();
    });

    let resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
            if (entry.target.tagName === 'TEXTAREA') {
                if (entry.target.id === 'data-request') {
                    let height = entry.target.style.height;
                    store.set('zato.data-request-height', height);
                    resizeDataResponse();
                }
            }
        }
    });

    let textareas = actionArea.querySelectorAll('textarea');
    textareas.forEach(ta => {
        resizeObserver.observe(ta);
    });

    $("#history-overlay-close").click($.fn.zato.ide.close_history_overlay);
    $(".invoker-history-overlay-backdrop").click($.fn.zato.ide.close_history_overlay);
    $("#history-search-input").on("input", function() {
        $.fn.zato.ide.filter_history_overlay($(this).val());
    });

    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            if (!$("#request-history-overlay").hasClass("hidden")) {
                e.preventDefault();
                $.fn.zato.ide.close_history_overlay();
            }
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.init_resizer = function() {
    console.debug("init_resizer: START");

    let resizer = document.getElementById('resizer');
    let actionArea = document.getElementById('action-area-container');
    let container = document.getElementById('main-area-container');

    console.debug("init_resizer: resizer element:", resizer);
    console.debug("init_resizer: actionArea element:", actionArea);
    console.debug("init_resizer: container element:", container);

    console.debug("init_resizer: testing store write/read");
    store.set('zato.test-key', 'test-value');
    let testValue = store.get('zato.test-key');
    console.debug("init_resizer: test value retrieved:", JSON.stringify(testValue));

    let savedWidth = store.get('zato.action-area-width');
    console.debug("init_resizer: savedWidth from store:", JSON.stringify(savedWidth));
    console.debug("init_resizer: localStorage.length:", localStorage.length);

    if (savedWidth) {
        actionArea.style.setProperty('width', savedWidth, 'important');
    }

    let isResizing = false;

    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;

        let containerRect = container.getBoundingClientRect();
        let newWidth = containerRect.right - e.clientX;

        if (newWidth >= 200 && newWidth <= containerRect.width - 200) {
            actionArea.style.width = newWidth + 'px';
        }
    });

    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            let widthToSave = actionArea.style.width;
            store.set('zato.action-area-width', widthToSave);
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.reset_inactivity_timeout = function() {
    clearTimeout(window.zato_inactivity_interval);
    $.fn.zato.ide.set_inactivity_handler();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_inactivity_handler = function() {
    window.zato_inactivity_interval = setTimeout($.fn.zato.ide.handle_inactivity, 200)
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.handle_inactivity = function() {
    //  console.debug("Handing inactivity")
    $.fn.zato.ide.save_current_source_code_to_local_storage();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_source_code_to_local_storage = function() {
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = window.zato_editor.getValue();
    localStorage.setItem(key, value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_current_source_code_from_local_storage = function() {
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = localStorage.getItem(key)
    if(value) {
        window.zato_editor.setValue(value);
        window.zato_editor.clearSelection();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Deploys the current file
$.fn.zato.ide.on_key_deploy_file = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_deploy_submitted();
}

// Invokes the current service
$.fn.zato.ide.on_key_invoke = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_invoke_submitted();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.switch_to_action_area = function(name) {

    if(name == "invoker") {
        $.fn.zato.ide.populate_invoker_area();
    }
    else if(name == "info") {
        $.fn.zato.ide.populate_data_model_area();
    }
    else if(name == "settings") {
        $.fn.zato.ide.populate_settings_area();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_header_links_elem = function(prefix) {
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);
    return header_links;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.clear_header_links = function(prefix) {

    // The element where all the links reside ..
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    // .. clean it up.
    header_links.empty();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_link = function(prefix, item_label, text, is_last) {

    // The element where all the links reside ..
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    // .. this is what each link will be based on ..
    let link_pattern = `<input type="button" id="header-{0}-link-{1}" value="{2}"></button>`;

    // .. build a string containing the link ..
    let link_string = String.format(link_pattern, prefix, item_label, text);

    // .. now, the element ..
    link = $(link_string);

    // .. now, append it to our links ..
    header_links.append(link);

    // .. and add a separator unless this is the last link.
    if(!is_last) {
        $("<span> </span>").insertAfter(link);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_span = function(prefix, id, is_visible) {

    if(is_visible) {
        var class_ = "visible";
    }
    else {
        var class_ = "hidden";
    }

    let span = `<span id=${id} class="${class_}"></span>`;
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    header_links.append($(span));
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_left_link = function(item_label, text, is_last) {
    $.fn.zato.ide.add_header_link("left", item_label, text, is_last);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_right_link = function(item_label, text, is_last) {
    $.fn.zato.ide.add_header_link("right", item_label, text, is_last);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_header_status = function(text) {
    let elem_id = `#header-status`;
    let elem = $(elem_id);
    elem.text(text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_invoker_area = function(initial_header_status) {

    // Clear anything that we may already have
    $.fn.zato.ide.clear_header_links("left")
    $.fn.zato.ide.clear_header_links("right")

    // Make sure that we are only showing our own area now
    $(".file-listing-tr").hide();
    $(".invoker-tr").show();

    // Left-hand side links
    $.fn.zato.ide.add_header_left_link("file", "File");
    $.fn.zato.ide.add_header_left_link("deploy", "Deploy", true);

    // The Deploy button was just re-created, so its click handler
    // and deployment status class need to be attached anew
    $("#header-left-link-deploy").click($.fn.zato.invoker.on_deploy_submitted);
    $.fn.zato.ide.set_deployment_status();

    // The progress indicator and the confirmation flash both sit right of the Deploy
    // button - only one of them is ever visible, the flash replaces the indicator
    $('<span id="deploying-please-wait" class="hidden">Deploying ..</span>').insertAfter("#header-left-link-deploy");
    $('<span id="deploy-result-flash" class="dimmed hidden">OK, deployed</span>').insertAfter("#deploying-please-wait");
    // $.fn.zato.ide.add_header_left_link("deploy-all-changed", "Deploy all changed");
    //$.fn.zato.ide.add_header_left_link("previous", "◄ Req.");
    //$.fn.zato.ide.add_header_left_link("next", "Req. ►", true);
    // $.fn.zato.ide.add_header_left_link("clear-request", "Clear request", true);

    // Right-hand side links
    //$.fn.zato.ide.add_header_right_link("open-api", "OpenAPI", true);
    //$.fn.zato.ide.add_header_right_link("push", "Push");
    //$.fn.zato.ide.add_header_right_link("push-all", "Push all", true);

    // One-line status bar
    // $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d "{\"customer_id\":\"123\"}'");
    /*
    $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d "{\"customer_id\":\"123\"}'");
    $("<a href=\"#\">Edit</a>").insertAfter("#header-status");
    $("<a class=\"header-sublink-first\" href=\"#\">Copy</a>").insertAfter("#header-status");
    */

    // Reset the result header to its default state but not the text itself
    // because we still want to show the previous response
    let result_header = $("#result-header");
    result_header.removeClass("invoker-draw-attention");

    // One-line status bar
    $("#header-status").text(initial_header_status);

    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    if(current_fs_location) {
        var button_attrs = "";
    }
    else {
        var button_attrs = `disabled="disabled" class="no-click"`;
    }

    let header_left_link_file_content = `
        <input type="button" id="file-new" value="New" onclick="$.fn.zato.ide.on_file_new()";/>
        <input type="button" id="file-reload" value="Reload" ${button_attrs} onclick="$.fn.zato.ide.on_file_reload();"/>
        <input type="button" id="file-rename" value="Rename" ${button_attrs} onclick="$.fn.zato.ide.on_file_rename();"/>
        <input type="button" id="file-delete" value="Delete" ${button_attrs} onclick="$.fn.zato.ide.on_file_delete();"/>
    `;

    tippy("#header-left-link-file", {
        content: header_left_link_file_content,
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
        onShown(instance) {
            $.fn.zato.ide.postprocess_file_buttons();
        }
      });

    // Offer the channels the current service can be invoked through
    $.fn.zato.ide.refresh_invoke_mode_select();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Human-readable labels for each channel type the invoke mode selector can offer
$.fn.zato.ide.invoke_mode_labels = {
    "rest": "REST channel",
    "hl7-mllp": "MLLP channel",
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Payload format handling - defaults, endpoints and sample assets
$.fn.zato.ide.config = {

    // What the format selector falls back to when a service has no remembered choice
    "default_payload_format": "auto",

    // localStorage key prefix for the per-service payload format
    "payload_format_key_prefix": "zato.ide.payload-format.",

    // localStorage key prefix for the per-service raw/parsed choice of each pane
    "pane_view_key_prefix": "zato.ide.pane-view.",

    // What view a pane starts with when a service has no remembered choice
    "default_pane_view": "raw",

    // Where the parsed view of a payload is rendered
    "parse_payload_url": "/zato/service/ide/parse-payload/",

    // What the parsed pane shows when the payload does not parse
    "parse_failed_text": "(payload does not parse)",

    // Sample payloads offered per format
    "samples": {
        "hl7-v2": [
            {"label": "ADT A01 - admit", "url": "/static/samples/hl7/adt_a01.hl7"},
            {"label": "ORU R01 - lab result", "url": "/static/samples/hl7/oru_r01.hl7"},
        ],
        "fhir": [
            {"label": "Patient", "url": "/static/samples/fhir/patient.json"},
            {"label": "OperationOutcome", "url": "/static/samples/fhir/operation_outcome.json"},
        ],
    },
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_payload_format = function() {
    return $("#payload-format-select").val();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_payload_format_changed = function() {

    let format = $.fn.zato.ide.get_payload_format();

    // The format travels with the invoke form
    $("#data-format").val(format);

    // Remember the choice for this service
    let service_name = $.fn.zato.ide.get_current_service_name();
    if(service_name) {
        localStorage.setItem($.fn.zato.ide.config.payload_format_key_prefix + service_name, format);
    }

    $.fn.zato.ide.update_parsed_toggles();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.restore_payload_format = function() {

    let service_name = $.fn.zato.ide.get_current_service_name();

    var format = null;
    if(service_name) {
        format = localStorage.getItem($.fn.zato.ide.config.payload_format_key_prefix + service_name);
    }

    // A service seen for the first time starts with the default
    if(format === null) {
        format = $.fn.zato.ide.config.default_payload_format;
    }

    $("#payload-format-select").val(format);
    $("#data-format").val(format);

    $.fn.zato.ide.update_parsed_toggles();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_invoke_mode_changed = function() {

    let mode = $("#invoke-mode-select").val();

    // Invoking through an MLLP channel implies the payload is HL7,
    // so the format follows the mode instead of leaking a stale value.
    if(mode.startsWith("hl7-mllp:")) {
        $("#payload-format-select").val("hl7-v2");
        $.fn.zato.ide.on_payload_format_changed();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.update_parsed_toggles = function() {

    let format = $.fn.zato.ide.get_payload_format();

    // The remembered view of each pane is re-applied under the new format
    $.fn.zato.ide.apply_pane_view("request");
    $.fn.zato.ide.apply_pane_view("response");

    // Samples exist only for some formats
    let sample_list = $.fn.zato.ide.config.samples[format];

    if(sample_list === undefined) {
        $("#insert-sample-link").addClass("hidden");
    }
    else {
        $("#insert-sample-link").removeClass("hidden");
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_pane_view_key = function(pane_name) {
    let service_name = $.fn.zato.ide.get_current_service_name();
    return $.fn.zato.ide.config.pane_view_key_prefix + pane_name + "." + service_name;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.apply_pane_view = function(pane_name) {

    // The remembered choice for this pane and service ..
    let key = $.fn.zato.ide.get_pane_view_key(pane_name);
    var view_name = localStorage.getItem(key);

    // .. a pane seen for the first time starts with the default ..
    if(view_name === null) {
        view_name = $.fn.zato.ide.config.default_pane_view;
    }

    // .. an empty pane has nothing to parse, so it stays raw without
    // .. overwriting the remembered choice ..
    let text_elem = pane_name == "request" ? $("#data-request") : $("#data-response");

    if(view_name == "parsed") {
        if(!text_elem.val()) {
            view_name = "raw";
        }
    }

    // .. and re-applying a remembered view is not a new choice to persist.
    $.fn.zato.ide.show_pane_view(pane_name, view_name, false);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.show_pane_view = function(pane_name, view_name, should_persist) {

    let text_elem = pane_name == "request" ? $("#data-request") : $("#data-response");
    let parsed_elem = $(`#data-${pane_name}-parsed`);
    let raw_link = $(`#${pane_name}-view-raw`);
    let parsed_link = $(`#${pane_name}-view-parsed`);

    // A view chosen by hand is remembered for this pane and service
    if(should_persist !== false) {
        let service_name = $.fn.zato.ide.get_current_service_name();
        if(service_name) {
            localStorage.setItem($.fn.zato.ide.get_pane_view_key(pane_name), view_name);
        }
    }

    // The drag-to-resize indicator belongs to the raw request view only
    let resize_indicator = $("#data-request-resize-indicator");

    if(view_name == "raw") {
        parsed_elem.addClass("hidden");
        text_elem.removeClass("hidden");
        parsed_link.removeClass("current");
        raw_link.addClass("current");

        if(pane_name == "request") {
            resize_indicator.removeClass("hidden");
        }
        return;
    }

    // The parsed view takes over the exact height of the raw one,
    // so the swap never moves anything below the pane
    if(pane_name == "request") {
        let raw_height = text_elem[0].style.height;
        if(raw_height) {
            parsed_elem.css("height", raw_height);
        }
    }

    // Parsed view - render the current pane content through the parse endpoint
    let format = $.fn.zato.ide.get_payload_format();
    let data = text_elem.val();

    $.ajax({
        type: "POST",
        url: $.fn.zato.ide.config.parse_payload_url,
        data: JSON.stringify({"data": data, "data_format": format}),
        contentType: "application/json",
        headers: {"X-CSRFToken": $.cookie("csrftoken")},
        success: function(response) {

            let parsed_text = response.parsed_text;
            if(parsed_text === "") {
                parsed_text = $.fn.zato.ide.config.parse_failed_text;
            }

            parsed_elem.text(parsed_text);
            text_elem.addClass("hidden");
            parsed_elem.removeClass("hidden");
            raw_link.removeClass("current");
            parsed_link.addClass("current");

            if(pane_name == "request") {
                resize_indicator.addClass("hidden");
            }
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.init_sample_menu = function() {

    tippy("#insert-sample-link", {
        content: "",
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
        onShow(instance) {

            // The menu always reflects the current format's samples
            let format = $.fn.zato.ide.get_payload_format();
            let sample_list = $.fn.zato.ide.config.samples[format];

            var html = "";
            for(const [index, sample] of sample_list.entries()) {
                html += `<input type="button" value="${sample.label}"
                    onclick="$.fn.zato.ide.insert_sample('${format}', ${index})"/> `;
            }

            instance.setContent(html);
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.insert_sample = function(format, index) {

    let sample = $.fn.zato.ide.config.samples[format][index];

    $.get(sample.url, function(data) {

        $("#data-request").val(data);

        // A sample becomes a fixture - it lands in the per-service request history
        $.fn.zato.ide.save_request_to_history(data);

        // The pane keeps whatever view is remembered for it
        $.fn.zato.ide.apply_pane_view("request");
    }, "text");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_invoke_mode_select = function(binding_list) {

    let select = $("#invoke-mode-select");
    let previous_value = select.val();

    // Rebuild the options from scratch, under the same in-select header
    // the template starts with - direct invocation is always available ..
    select.empty();

    let mode_optgroup = $("<optgroup>");
    mode_optgroup.attr("label", "Invoke as");
    select.append(mode_optgroup);

    let service_option = $("<option>");
    service_option.attr("value", "service");
    service_option.text("Service");
    mode_optgroup.append(service_option);

    // .. followed by one option per channel the service is exposed through ..
    for(const binding of binding_list) {
        let label = $.fn.zato.ide.invoke_mode_labels[binding.channel_type];
        let option = $("<option>");
        option.attr("value", `${binding.channel_type}:${binding.id}`);
        option.text(`${label}: ${binding.name}`);
        mode_optgroup.append(option);
    }

    // .. keep the previous mode if the new service still offers it, otherwise fall back to direct invocation ..
    if(select.find(`option[value="${previous_value}"]`).length) {
        select.val(previous_value);
    }
    else {
        select.val("service");
    }

    // The payload format follows the service too
    $.fn.zato.ide.restore_payload_format();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.refresh_invoke_mode_select = function() {

    let service_name = $.fn.zato.ide.get_current_service_name();

    // Without a service there are no channels to invoke through
    if(!service_name) {
        $.fn.zato.ide.populate_invoke_mode_select([]);
        return;
    }

    let callback = function(data, _unused_status) {
        let json = JSON.parse(data.responseText);

        // The response is empty if the name does not point to a deployed service
        let binding_list = json.current_service_binding_list;
        if(binding_list === undefined) {
            binding_list = [];
        }

        $.fn.zato.ide.populate_invoke_mode_select(binding_list);
    }

    let url = String.format("/zato/service/ide/get-service/{0}/", service_name);
    $.fn.zato.post(url, callback);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_post_load_source_func = function(data) {
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_op_error_func = function(op_name) {
    let result_header_selector = "#result-header";
    _on_error_func = function(options, jq_xhr, text_status, error_message) {
        console.debug(`File ${op_name} impl, on error:  ${jq_xhr.status} -> ${error_message} ->  ${jq_xhr.responseText}`);
        $(result_header_selector).text(`${jq_xhr.status} ${error_message}`);
        $("#data-response").val(jq_xhr.responseText);
        $.fn.zato.invoker.draw_attention([result_header_selector]);
    };
    return _on_error_func;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_op_success_func = function(
    op_name,
    placeholder_verb,
    after_on_file_op_success_func_callback,
)
{
    let _on_success_func = function(options, data) {

        console.debug(`File ${op_name} impl, on success: `+ $.fn.zato.to_dict(data));

        if($.fn.zato.is_object(data)) {
            var data = data;
        }
        else {
            var data = $.parseJSON(data);
        }

        _get_current_file_service_list_func = function() {
            let item = {}
            item.fs_location = "";
            item.fs_location_url_safe = "";
            item.line_number_human = -1;
            item.line_number_human = -1;
            item.current_root_directory = "zato-undefined";
            item.root_directory_count = -1;
            item.name = `(${placeholder_verb} ..)`;

            let out = [item];
            return out;
        }

        $.fn.zato.show_bottom_tooltip(`#file-${op_name}`, `${placeholder_verb} ..`, true);
        $.fn.zato.ide.set_current_fs_location(data.full_path);

        // The callback fetches the service list and its response is what enables
        // the Invoke button, so it must run only after the file finished loading -
        // the file load sees no services in a just-created file and disables
        // the button, which must not race with the enabling response.
        let after_load_func = false;
        if(after_on_file_op_success_func_callback) {
            after_load_func = function() {
                after_on_file_op_success_func_callback();
            };
        }

        $.fn.zato.ide.on_file_selected(
            data.full_path,
            data.full_path_url_safe,
            false,
            after_load_func,
            null, // _get_current_file_service_list_func,
        );
    };
    return _on_success_func;
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_reloaded = function() {

    // Local variables
    let elem_id_selector = "#file-reload";
    let text = "OK, reloaded";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_created = function() {

    // Local variables
    let main_elem_id_selector = "#file-new";
    let main_text = "OK, created";
    let invoke_elem_id_selector = "#invoke-service";
    let invoke_text = "Click here to invoke";

    // Do show the tooltips now
    $.fn.zato.show_bottom_tooltip(main_elem_id_selector, main_text);
    $.fn.zato.show_left_tooltip(invoke_elem_id_selector, invoke_text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_renamed = function() {

    // Local variables
    let elem_id_selector = "#file-rename";
    let text = "OK, renamed";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);

    // We have already switched to demo.py so we need to disable buttons that would rename or delete it
    $.fn.zato.ide.disable_file_rename_button();
    $.fn.zato.ide.disable_file_delete_button();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_deleted = function() {

    // Local variables
    let elem_id_selector = "#file-delete";
    let text = "OK, deleted";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);

    // We have already switched to demo.py so we need to disable buttons that would rename or delete it
    $.fn.zato.ide.disable_file_rename_button();
    $.fn.zato.ide.disable_file_delete_button();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_simple_impl = function(
    current_root_directory,
    file_name,
    current_file_name_field,
    new_file_name,
    url_path,
    form_id,
    options,
    display_timeout,
    op_name,
    placeholder_verb,
    after_on_file_op_success_func_impl
) {

    // Local variables
    let after_on_file_op_success_func_on_file_simple_impl = function() {
        $.fn.zato.ide.populate_current_file_service_list_impl(after_on_file_op_success_func_impl, "1");
    }

    let _on_success_func = $.fn.zato.ide.on_file_op_success_func(op_name, placeholder_verb, after_on_file_op_success_func_on_file_simple_impl);
    let _on_error_func = $.fn.zato.ide.on_file_op_error_func(op_name);

    $.fn.zato.ide.build_singleton_form(form_id, {
        [current_file_name_field]: file_name,
        "new_file_name": new_file_name,
        "root_directory": current_root_directory,
    });

    $.fn.zato.invoker.submit_form(
        url_path,
        "#"+form_id,
        options,
        _on_success_func,
        _on_error_func,
        "json"
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_new_impl = function(current_root_directory, file_name) {

    let url_path = "/zato/service/ide/create-file/";
    let form_id = "file-new-form";
    let options = {};
    let display_timeout = 1;
    let op_name = "new";
    let placeholder_verb = "Deploying"
    let after_on_file_op_success_func_impl = $.fn.zato.ide.after_file_created;

    $.fn.zato.ide.on_file_simple_impl(
        current_root_directory,
        file_name,
        "file_name",
        null,
        url_path,
        form_id,
        options,
        display_timeout,
        op_name,
        placeholder_verb,
        after_on_file_op_success_func_impl,
    )
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_new = function() {

    // Local variables
    let prompt_text = "Create a new file."
    let root_directory_count = $.fn.zato.ide.get_root_directory_count();
    let current_root_directory = $.fn.zato.ide.get_current_root_directory();

    // We need an integer here ..
    root_directory_count = Number(root_directory_count);

    // .. show additional information if we have more than one root directory ..
    if(root_directory_count > 1) {
        prompt_text += "\n\n";
        prompt_text += `Root directory: ${current_root_directory}\n\n`;
    }

    // .. do prompt the user ..
    let file_name = prompt(prompt_text, "");

    // .. proceed if we've received anything ..
    if(file_name) {
        console.debug(`Creating file: "${current_root_directory}" -> "${file_name}"`);
        $.fn.zato.ide.on_file_new_impl(current_root_directory, file_name);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_rename_impl = function(current_root_directory, current_file_name, new_file_name) {

    let url_path = "/zato/service/ide/rename-file/";
    let form_id = "file-rename-form";
    let options = {};
    let display_timeout = 1;
    let op_name = "rename";
    let placeholder_verb = "Renaming"
    let after_on_file_op_success_func_impl = $.fn.zato.ide.after_file_renamed;

    $.fn.zato.ide.on_file_simple_impl(
        current_root_directory,
        current_file_name,
        "current_file_name",
        new_file_name,
        url_path,
        form_id,
        options,
        display_timeout,
        op_name,
        placeholder_verb,
        after_on_file_op_success_func_impl,
    )
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_rename = function() {

    // Local variables
    let prompt_text = "Enter new file name.";
    let fs_location = $.fn.zato.ide.get_current_fs_location();
    let root_directory_count = $.fn.zato.ide.get_root_directory_count();
    let current_root_directory = $.fn.zato.ide.get_current_root_directory();

    let current_file_name = fs_location.replace(current_root_directory, "");
    if(current_file_name.charAt(0) === '/' || current_file_name.charAt(0) === '\\') {
        current_file_name = current_file_name.substring(1);
    }

    // We need an integer here ..
    root_directory_count = Number(root_directory_count);

    // .. show additional information if we have more than one root directory ..
    if(root_directory_count > 1) {
        prompt_text += "\n\n";
        prompt_text += `Root directory: ${current_root_directory}\n\n`;
    }

    // .. do prompt the user ..
    let new_file_name = prompt(prompt_text, current_file_name);

    // .. proceed if we've received anything ..
    if(new_file_name) {
        if(new_file_name != current_file_name) {
            console.debug(`Rename file: "${current_root_directory}" -> "${current_file_name} -> "${new_file_name}"`);
            $.fn.zato.ide.on_file_rename_impl(current_root_directory, current_file_name, new_file_name);
        }
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_delete_impl = function(fs_location) {

    // Local variables
    let after_on_file_op_success_func_on_file_delete_impl = function() {
        $.fn.zato.ide.populate_file_list($.fn.zato.ide.after_file_deleted);
        console.debug(`Deleted "${fs_location}"`);
    }

    let url_path = "/zato/service/ide/delete-file/";
    let form_id = "file-delete-form";
    let options = {};
    let display_timeout = 1;
    let _on_success_func = $.fn.zato.ide.on_file_op_success_func("delete", "Deleting", after_on_file_op_success_func_on_file_delete_impl);
    let _on_error_func = $.fn.zato.ide.on_file_op_error_func("delete");

    $.fn.zato.ide.build_singleton_form(form_id, {
        "fs_location": fs_location,
    });

    $.fn.zato.invoker.submit_form(
        url_path,
        "#"+form_id,
        options,
        _on_success_func,
        _on_error_func,
        "json"
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_delete = function() {

    // Local variables
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let fs_location = current_object_select.attr("data-fs-location");
    let fs_location_url_safe = current_object_select.attr("data-fs-location-url-safe");
    let prompt_text = `Confirm file deletion.\n\n${fs_location}`;

    if(confirm(prompt_text)) {
        console.debug(`Deleting file: "${fs_location}" "${fs_location_url_safe}"`)
        $.fn.zato.ide.on_file_delete_impl(fs_location);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_reload = function() {
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let fs_location = current_object_select.attr("data-fs-location");
    let fs_location_url_safe = current_object_select.attr("data-fs-location-url-safe");
    console.debug(`Reloading file: "${fs_location}" "${fs_location_url_safe}"`)
    $.fn.zato.ide.on_file_selected(
        fs_location,
        fs_location_url_safe,
        false,
        $.fn.zato.ide.after_file_reloaded,
        null,
        "should_convert_pickup_to_work_dir=True",
    );
}


/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_info = function() {

    // Local variables
    let form_id = "file-info-form";
    let fs_location = $.fn.zato.ide.get_current_fs_location();

    console.debug(`Getting file info for: "${fs_location}"`);

    // First, build a dynamic form ..
    $.fn.zato.ide.build_singleton_form(form_id, {
        "fs_location": fs_location,
    });

    // .. collect all the required parameters ..
    const options = {
        "request_form_id": `#${form_id}`,
        "on_started_activate_blinking": ["#getting-info-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,
        "on_post_success_func": $.fn.zato.ide.on_post_success_func,
    }

    // .. and invoke the newly created form now.
    $.fn.zato.invoker.run_sync_form_submitter(options);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.build_singleton_form = function(form_id, items) {

    // Local variables
    let form_selector = `#${form_id}`;
    let parent = $("#singleton-form-parent");

    // First, make sure that such an element doesn't exist ..
    $(form_selector).remove();

    // .. now, create it again ..
    let form = `<form id="${form_id}" method="post"></form>`;

    // .. append it to our parent ..
    parent.append(form);

    // .. get a handle to the newly created form ..
    let form_elem = $(form_selector);

    // .. go through all the fields that we need to create ..
    for(const [key, value] of Object.entries(items)) {

        // .. create a hidden field for each one ..
        let field = `<input type="hidden" name="${key}" value="${value}"/>`;

        // .. and attach it to the form.
        form_elem.append(field);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_document_title = function(name) {
    var prefix = "";
    let has_modified =  $.fn.zato.ide.has_current_object_modified();

    // console.debug("Received has modified: "+ has_modified);

    if(has_modified) {
        prefix = "* ";
    }

    let new_title = `${prefix}${name} - IDE - Zato`;
    document.title = new_title;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.push_url_path = function(object_type, name, name_url_safe) {
    let new_url_path = `/zato/service/ide/${object_type}/${name_url_safe}/?cluster=1`;
    history.pushState({"object_type":object_type, "name": name_url_safe}, null, new_url_path);
    $.fn.zato.ide.populate_document_title(name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.push_service_url_path = function(name) {
    $.fn.zato.ide.push_url_path("service", name, name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.highlight_current_file = function(fs_location) {
    $("a.fs-location-link").each(function(idx) {
        let title = $(this).attr("title");
        if(title == fs_location) {
            $.fn.zato.toggle_css_class(this, "zato-invalid", "current");
        }
        else {
            $.fn.zato.toggle_css_class(this, "current", "zato-invalid");
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_current_file_service_list = function(current_file_service_list, new_service_name) {

    // For later use
    var first_option_elem = null;
    var has_new_service_name_match = false;

    // console.debug("Populate current file service list: "+ current_file_service_list);

    // First, remove anything we already have in the list ..
    $(".option-current-file").remove();

    // .. get a reference to the parent optgroup ..
    let optgroup = $("#optgroup-current-file");

    // .. and populate it anew
    for (const item of current_file_service_list) {

        console.debug("Populate current file item: "+ $.fn.zato.to_dict(item));

        var option = $("<option>");
        option.text(item.name);
        option.attr("class", "option-current-file");
        option.attr("data-service-name", item.name);
        option.attr("data-fs-location", item.fs_location);
        option.attr("data-fs-location-url-safe", item.fs_location_url_safe);
        option.attr("data-line-number", item.line_number_human);
        option.attr("data-is-current-file", "1");
        option.attr("data-current-root-directory", item.current_root_directory);
        option.attr("data-root-directory-count", item.root_directory_count);
        option.appendTo(optgroup);

        if(first_option_elem === null) {
            first_option_elem = option;
        }

        // This will match only if we have a meaningful new service name on input,
        // which will be the case with "on-service-selected" handlers only
        // but not with "on-file-selected" ones.
        if(item.name == new_service_name) {
            option.attr("selected", "selected");
            has_new_service_name_match = true;

            // If we are here, it means that the current service can be invoked
            $.fn.zato.ide.enable_invoke_button();
        }
    }

    // This will be entered only by the "on-file-selected" handlers
    // because they do not have any specific service to select.
    if(!has_new_service_name_match) {
        if(first_option_elem) {
            first_option_elem.attr("selected", "selected");
        }
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_is_current_file = function(current_fs_location) {

    //  console.debug("Setting current file: "+ current_fs_location);

    // Zero out the current file flag for all the select opions ..
    $(`option[data-object-holder="1"]`).attr("data-is-current-file", "0");

    // and enable it back for the ones that point to the current file
    $(`option[data-fs-location="${current_fs_location}"`).attr("data-is-current-file", "1");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.enable_button = function(button_id) {

    // Local variables
    let button = $(button_id);

    // Make it possible to use the button
    button.removeAttr("disabled");
    button.removeClass("no-click");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.disable_button = function(button_id) {

    // Local variables
    let button = $(button_id);

    // Disable the button
    button.attr("disabled", "disabled");
    button.addClass("no-click");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.enable_invoke_button = function() {
    $.fn.zato.ide.enable_button("#invoke-service");
}

$.fn.zato.ide.enable_file_rename_button = function() {
    $.fn.zato.ide.enable_button("#file-rename");
}

$.fn.zato.ide.enable_file_delete_button = function() {
    $.fn.zato.ide.enable_button("#file-delete");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.disable_invoke_button = function() {
    $.fn.zato.ide.disable_button("#invoke-service");
}

$.fn.zato.ide.disable_file_rename_button = function() {
    $.fn.zato.ide.disable_button("#file-rename");
}

$.fn.zato.ide.disable_file_delete_button = function() {
    $.fn.zato.ide.disable_button("#file-delete");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.postprocess_file_buttons = function(current_file_service_list) {
    // A list of buttons that depend on a file being selected.
    const file_buttons = ["#file-rename", "#file-delete", "#file-reload"];

    // Get the current file context
    const current_fs_location = $.fn.zato.ide.get_current_fs_location();

    // If no file is selected, disable all file-related buttons.
    if (!current_fs_location) {
        file_buttons.forEach(button_id => $.fn.zato.ide.disable_button(button_id));

        // Disable invoke only if no service is selected either.
        let selected_service_name = $.fn.zato.ide.get_current_service_name();
        if (!selected_service_name) {
            $.fn.zato.ide.disable_invoke_button();
        }
        else {
            $.fn.zato.ide.enable_invoke_button();
        }
        return;
    }

    // If a file is selected, enable buttons by default, then apply specific disabling rules.
    file_buttons.forEach(button_id => $.fn.zato.ide.enable_button(button_id));

    // Rule: Disable rename/delete for services or demo.py
    const current_object_type = $.fn.zato.ide.get_current_object_type();
    const is_service_view = current_object_type === "service";
    const is_demo_file = current_fs_location.endsWith("demo.py");
    if (is_service_view || is_demo_file) {
        $.fn.zato.ide.disable_file_rename_button();
        $.fn.zato.ide.disable_file_delete_button();
    }

    // Rule: Handle the invoke button state.
    const is_service_file = current_file_service_list && current_file_service_list.length > 0;
    if (is_service_file) {
        // Always enable for services. The click handler deals with deployment.
        $.fn.zato.ide.enable_invoke_button();
    } else {
        $.fn.zato.ide.disable_invoke_button();
    }
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.post_load_source_object = function(
    data,
    object_name,
    current_file_source_code,
    current_file_service_list,
    fs_location,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
) {
    console.debug("post_load_source_object: START");
    console.debug("post_load_source_object: fs_location:", JSON.stringify(fs_location));
    console.debug("post_load_source_object: current_file_source_code length:", current_file_source_code ? current_file_source_code.length : null);

    // First, establish the new baseline for deployment status. The content we just received from the server
    // is now considered the "last deployed" version for the purpose of detecting unsaved changes.
    let key = $.fn.zato.ide.get_last_deployed_key();
    console.debug("post_load_source_object: setting baseline with key:", JSON.stringify(key));
    localStorage.setItem(key, current_file_source_code);
    console.debug("post_load_source_object: baseline set in localStorage");

    // Now, load the content into the editor. Any subsequent 'change' event will compare against the correct baseline.
    $.fn.zato.ide.load_editor_session(fs_location, current_file_source_code, reuse_source_code);

    $.fn.zato.ide.highlight_current_file(fs_location);
    if(get_current_file_service_list_func) {
        current_file_service_list = get_current_file_service_list_func();
    }
    $.fn.zato.ide.populate_current_file_service_list(current_file_service_list, object_name);

    // Check the actual deployment status by comparing editor content against baseline
    console.debug("post_load_source_object: checking deployment status");
    $.fn.zato.ide.set_deployment_status();
    console.debug("post_load_source_object: END");

    $.fn.zato.ide.set_is_current_file(fs_location);
    if(after_post_load_source_func) {
        after_post_load_source_func(data);
    }

    // This will enable or disable file buttons
    $.fn.zato.ide.postprocess_file_buttons(current_file_service_list);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_source_object = function(
    object_type,
    object_name,
    fs_location,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
    extra_qs,
) {

    console.debug("load_source_object: START");
    console.debug("load_source_object: object_type:", JSON.stringify(object_type));
    console.debug("load_source_object: object_name:", JSON.stringify(object_name));
    console.debug("load_source_object: fs_location:", JSON.stringify(fs_location));

    extra_qs = extra_qs || "";

    var callback = function(data, _unused_status) {
        console.debug("load_source_object: callback START");
        let msg = data.responseText;
        console.debug("load_source_object: msg length:", msg ? msg.length : null);
        let json = JSON.parse(msg)
        console.debug("load_source_object: json parsed");
        let current_file_source_code = json.current_file_source_code;
        console.debug("load_source_object: current_file_source_code length:", current_file_source_code ? current_file_source_code.length : null);
        console.debug("load_source_object: current_file_source_code type:", typeof current_file_source_code);
        console.debug("load_source_object: current_file_source_code:", JSON.stringify(current_file_source_code));
        let current_file_service_list = json.current_file_service_list;
        $.fn.zato.ide.post_load_source_object(
            data,
            object_name,
            current_file_source_code,
            current_file_service_list,
            fs_location,
            reuse_source_code,
            after_post_load_source_func,
            get_current_file_service_list_func
        );

        // A service response carries its channel bindings directly, a file response does not,
        // so for files the bindings of whichever service became selected are fetched anew.
        if(object_type == "service") {
            $.fn.zato.ide.populate_invoke_mode_select(json.current_service_binding_list);
        }
        else {
            $.fn.zato.ide.refresh_invoke_mode_select();
        }
    }

    var url = String.format("/zato/service/ide/get-{0}/{1}/?1=1&{2}", object_type, object_name,extra_qs);
    $.fn.zato.post(url, callback);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_cluster_name = function() {
    return $("#cluster_name").val();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_fs_location = function() {
    return $("#current_fs_location").val();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_current_fs_location = function(fs_location) {
    $("#current_fs_location").val(fs_location);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_root_directory = function() {
    return $("#current_root_directory").val();
}

$.fn.zato.ide.set_current_root_directory = function(value) {
    $("#current_root_directory").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_root_directory_count = function() {
    return $("#root_directory_count").val();
}

$.fn.zato.ide.set_root_directory_count = function(value) {
    $("#root_directory_count").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_source_code_key = function() {
    return $.fn.zato.ide.get_cluster_name() + "." + $.fn.zato.ide.get_current_fs_location();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_last_deployed_key = function() {
    let key = "zato.last-deployed." + $.fn.zato.ide.get_current_source_code_key()
    return key;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_object_type = function() {
    let current = $("#current-object-type").val();
    return current;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_current_object_type = function(value) {
    $("#current-object-type").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_object_select = function() {
    let current = $("#object-select :selected");
    //  console.debug("Returning current select: "+ current.text())
    return current;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_service_name = function() {
    let current = $.fn.zato.ide.get_current_object_select();
    return current.attr("data-service-name");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.has_current_object_modified = function() {
    let current = $.fn.zato.ide.get_current_object_select();

    let has_modified = current.attr("data-is-modified") == "1";
    // console.debug("Has current modified: "+ has_modified);
    return has_modified;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_document_changed = function(e) {
    let undo_manager = window.zato_editor.getSession().getUndoManager();
    let has_undo = undo_manager.hasUndo();
    // $.fn.zato.ide.mark_file_modified(has_undo);
    $.fn.zato.ide.on_editor_changed();

    // Make sure there is no selection if there is no undo
    // because there may be some in case the edit we have just undone
    // had come from LocalStorage, in which case it overwrote the whole document,
    // thus making everything use a yellow background which is not necessary.
    if(!has_undo) {
        window.zato_editor.clearSelection()
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.mark_file_modified = function(has_undo) {

    // There will be only one such element but it will not have an ID, hence the iteration.
    $("a.fs-location-link.current").each(function() {
        var elem = $(this);
        var file_name = elem.attr("data-file-name");
        if(has_undo) {
            file_name += " *";
            elem.addClass("modified");
        }
        else {
            elem.removeClass("modified");
        }
        elem.text(file_name);
    })
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_up_editor_session = function(editor_session) {
    editor_session.setMode("ace/mode/python");
    editor_session.setUndoSelect(false);
    editor_session.on("change", $.fn.zato.ide.on_document_changed);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_editor_session = function(fs_location, source_code, reuse_source_code) {

    console.debug(`ZATO_IDE_DEBUG: load_editor_session called for fs_location: ${fs_location}`);
    console.debug(`ZATO_IDE_DEBUG: load_editor_session received source_code:`, JSON.stringify(source_code));
    console.debug(`ZATO_IDE_DEBUG: load_editor_session reuse_source_code:`, reuse_source_code);

    // Do we have a session for this file already?
    let existing_session = window.zato_editor_session_map[fs_location];

    // If we have an existing session and should reuse it, switch to it
    if(existing_session && reuse_source_code) {
        console.debug(`ZATO_IDE_DEBUG: Reusing existing session for ${fs_location}, keeping existing content.`);
        window.zato_editor.setSession(existing_session);
    }
    // If we should not reuse or don't have a session, create/replace with server content
    else {
        console.debug(`ZATO_IDE_DEBUG: Creating new session for ${fs_location} with server source code.`);
        let new_session = ace.createEditSession(source_code);
        $.fn.zato.ide.set_up_editor_session(new_session);
        window.zato_editor.setSession(new_session);
        window.zato_editor_session_map[fs_location] = new_session;
    }

    // Set mode depending on file name
    if(fs_location.endsWith(".py")) {
        window.zato_editor.session.setMode("ace/mode/python");
    }
    else if(fs_location.endsWith(".json")) {
        window.zato_editor.session.setMode("ace/mode/json");
    }
    else {
        window.zato_editor.session.setMode("ace/mode/text");
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_editor_session = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let session = window.zato_editor.getSession();
    console.debug(`ZATO_IDE_DEBUG: save_current_editor_session for ${current_fs_location}`);
    console.debug(`ZATO_IDE_DEBUG: session content length:`, session.getValue().length);
    window.zato_editor_session_map[current_fs_location] = session;
    console.debug(`ZATO_IDE_DEBUG: session map keys:`, Object.keys(window.zato_editor_session_map));
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_last_deployed_from_store = function(key) {
    let last_deployed = localStorage.getItem(key);
    // console.debug("Last deployed in store: "+ !!last_deployed +"; key: "+ key);
    return last_deployed;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.maybe_populate_initial_last_deployed = function() {

    // Check if this file has been ever deployed, if not, we need to populate
    // the store with the current contents of the file because, by definition,
    // it must be the same as the source code from the server given that we've just loaded it.
    // console.debug("In maybe populate initial last deployed");
    let key = $.fn.zato.ide.get_last_deployed_key();
    last_deployed = $.fn.zato.ide.get_last_deployed_from_store(key);

    if(!last_deployed) {
        let editor_value = window.zato_editor.getValue()
        localStorage.setItem(key, editor_value);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.maybe_set_deploy_needed = function() {
    console.debug("In maybe set deploy needed");
    $.fn.zato.ide.set_deployment_status();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_root_directory_info_from_option = function(option) {

    // Local variables
    let current_root_directory = option.attr("data-current-root-directory");
    let root_directory_count = option.attr("data-root-directory-count");

    console.debug(`Setting root dir info: "${current_root_directory}" and "${root_directory_count}"`)

    $.fn.zato.ide.set_current_root_directory(current_root_directory);
    $.fn.zato.ide.set_root_directory_count(root_directory_count);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_selected = function(
    fs_location,
    fs_location_url_safe,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
    extra_qs,
) {
    console.debug("On file selected ..")

    if(reuse_source_code == null) {
        reuse_source_code = true;
    }
    else {
        reuse_source_code = false;
    }

    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_url_path("file", fs_location, fs_location_url_safe);
    $.fn.zato.ide.load_source_object(
        "file",
        fs_location,
        fs_location,
        reuse_source_code,
        after_post_load_source_func,
        get_current_file_service_list_func,
        extra_qs
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed_current_file = function(option_selected) {

    //  console.debug("On object selected current file ..")

    let fs_location = option_selected.attr("data-fs-location");
    var line_number = option_selected.attr("data-line-number");

    let should_center = false;
    let should_animate = true;
    let callback_function = null;

    window.zato_editor.scrollToLine(line_number, should_center, should_animate, callback_function);

    // Selecting a service within the current file does not reload it,
    // yet the newly selected service has its own channel bindings.
    $.fn.zato.ide.refresh_invoke_mode_select();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed_non_current_file = function(option_selected) {

    //  console.debug("On object selected non-current file ..")

    let new_service_name = option_selected.attr("data-service-name");
    let fs_location = option_selected.attr("data-fs-location");
    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_service_url_path(new_service_name);
    $.fn.zato.ide.load_source_object("service", new_service_name, fs_location, true);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed = function(select_elem) {

    select_elem = $(select_elem);
    let option_selected = $("option:selected", select_elem);
    let is_current_file = option_selected.attr("data-is-current-file") == "1";
    let current_object_type = $.fn.zato.ide.get_current_object_type()

    if (window.zato && window.zato.messageViewer) {
        window.zato.messageViewer.hidePanel();
    }

    // This will update the global information about what directory we are
    $.fn.zato.ide.populate_root_directory_info_from_option(option_selected);

    // Handle the selection of a service ..
    if(current_object_type == "service") {

        // .. a service within the current file was selected ..
        if(is_current_file) {
            $.fn.zato.ide.on_object_select_changed_current_file(option_selected);
        }

        // .. a service in another file was selected ..
        else {
            //  console.debug("Switching to an object in another file: "+ option_selected.text());
            $.fn.zato.ide.on_object_select_changed_non_current_file(option_selected);
        }
    }

    // .. handle the selection of a file ..
    else {

        let selected_fs_location = option_selected.attr("data-fs-location");
        let selected_fs_location_url_safe = option_selected.attr("data-fs-location-url-safe");

        // .. we enter here only if we have an actual file to switch to.
        if(selected_fs_location) {
            $.fn.zato.ide.on_file_selected(selected_fs_location, selected_fs_location_url_safe);
        }
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_editor_changed = function() {
    console.debug("on_editor_changed: START");
    $.fn.zato.ide.set_deployment_status();
    console.debug("on_editor_changed: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_status = function() {
    console.debug("set_deployment_status: START");

    // Get the current value of the editor ..
    let editor_value = window.zato_editor.getValue()
    console.debug("set_deployment_status: editor_value length:", editor_value ? editor_value.length : null);
    console.debug("set_deployment_status: editor_value:", JSON.stringify(editor_value));

    // .. get the value of what was last deployed ..
    let key = $.fn.zato.ide.get_last_deployed_key();
    console.debug("set_deployment_status: key:", JSON.stringify(key));

    let last_deployed = $.fn.zato.ide.get_last_deployed_from_store(key);
    console.debug("set_deployment_status: last_deployed length:", last_deployed ? last_deployed.length : null);
    console.debug("set_deployment_status: last_deployed:", JSON.stringify(last_deployed));

    // .. check if they are different ..
    let is_different = editor_value != last_deployed;
    console.debug("set_deployment_status: is_different:", is_different);

    // .. pick the correct CSS class to set for the "Deploy" button
    if(is_different) {
        var button_class_name = "different";
        console.debug("set_deployment_status: setting button_class_name to 'different'");
    }
    else {
        var button_class_name = "not-different";
        console.debug("set_deployment_status: setting button_class_name to 'not-different'");
    }

    // .. set it for the button accordingly ..
    $.fn.zato.ide.set_deployment_button_status_class(button_class_name);

    // .. and for all the select options that point to the current file ..
    $.fn.zato.ide.update_deployment_option_state(is_different);

    // .. update the document title to add or remove the star ..
    let title = document.title;
    console.debug("set_deployment_status: current title:", JSON.stringify(title));
    console.debug("set_deployment_status: title starts with '* ':", title.startsWith('* '));
    if(is_different) {
        if(!title.startsWith('* ')) {
            document.title = '* ' + title;
            console.debug("set_deployment_status: added star to title");
        }
    } else {
        if(title.startsWith('* ')) {
            document.title = title.substring(2);
            console.debug("set_deployment_status: removed star from title");
        } else {
            console.debug("set_deployment_status: title does not start with '* ', not removing");
        }
    }

    console.debug("set_deployment_status: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.update_deployment_option_state = function(is_different, fs_location) {

    fs_location = fs_location || $.fn.zato.ide.get_current_fs_location();
    //  console.debug(`Setting option text: ${is_different} and ${fs_location}`);

    $(`#object-select option[data-fs-location="${fs_location}"]`).each(function() {
        let option = $(this);
        let text = option.text();
        if(is_different) {
            if(text.startsWith(window.zato_undeployed_prefix)) {
                new_text = text;
                is_modified = 0;
            }
            else {
                new_text = window.zato_undeployed_prefix + text;
                is_modified = 1;
            }
        }
        else {
            new_text = text.replace(window.zato_undeployed_prefix, "");;
            is_modified = 0;
        }
        option.text(new_text)
        option.attr("data-is-modified", is_modified);
        //  console.debug(`Opt: ${is_modified} -> ${option.text()}`);
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_class = function(class_name) {
    let button = $("#header-left-link-deploy");
    button.removeClass("different not-different");
    button.addClass(class_name);
    
    if (class_name === "different") {
        button.val("🔷 Deploy");
    } else {
        button.val("Deploy");
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_different = function() {
    $.fn.zato.ide.set_deployment_button_status_class("different");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_not_different = function() {
    $.fn.zato.ide.set_deployment_button_status_class("not-different");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_post_success_func = function() {
    $.fn.zato.ide.set_deployment_button_status_not_different();
    $.fn.zato.ide.update_deployment_option_state(false);
    $.fn.zato.ide.set_deployment_status();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.get_sync_deploy_request_url = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let out = String.format("/zato/service/upload/?qqfile={0}&has_post=true", current_fs_location);
    return out
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_deploy_submitted = function() {

    const options = {
        "request_form_id": "#editor-form",
        "on_started_activate_blinking": ["#deploying-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,
        "on_success_flash_func": $.fn.zato.ide.flash_deploy_success,
        "on_post_success_func": $.fn.zato.ide.on_post_success_func,

    }
    $.fn.zato.invoker.run_sync_deployer(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Deploys the current file first and runs the given function once the deploy succeeded -
// this is what invoking a modified service goes through before the actual invocation.
$.fn.zato.ide.run_sync_deployer = function(on_deployed_func) {

    const options = {
        "request_form_id": "#editor-form",
        "on_started_activate_blinking": ["#deploying-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,
        "on_success_flash_func": $.fn.zato.ide.flash_deploy_success,
        "on_post_success_func": function() {
            $.fn.zato.ide.on_post_success_func();
            on_deployed_func();
        },
    }
    $.fn.zato.invoker.run_sync_deployer(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// A successful deploy reports through a short flash next to the Deploy button -
// the result header and the response area stay untouched.
$.fn.zato.ide.flash_deploy_success = function(options) {

    // A fast deploy would replace the indicator with the flash near-instantly,
    // so the swap waits until the indicator was on screen for a moment
    setTimeout(function() {

        // The deploying indicator stops blinking now that the deploy is done ..
        let blinking = options["on_started_activate_blinking"];
        blinking.each(function(element) {
            $.fn.zato.toggle_css_class($(element), "invoker-blinking", "hidden");
        });

        // .. and the confirmation flashes with the same attention animation
        // the result header uses, hiding again when the animation ends.
        let flash = $("#deploy-result-flash");
        flash.removeClass("hidden");
        flash.addClass("invoker-draw-attention");

        flash.one("animationend", function() {
            flash.addClass("hidden");
            flash.removeClass("invoker-draw-attention");
        });

    }, $.fn.zato.invoker.config.indicator_min_ms);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_deployer = function(options) {

    // Populate the form based on what is inside the editor
    let editor_value = window.zato_editor.getValue()
    $("#data-editor").val(editor_value);

    // Actually deploy the source code
    $.fn.zato.invoker.run_sync_form_submitter(options);

    // Save the current contents of the file for later use
    let key = $.fn.zato.ide.get_last_deployed_key();
    localStorage.setItem(key, editor_value);

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.toggle_current_object_type = function(current) {
    if(current == "service") {
        var new_current = "file";
    }
    else {
        var new_current = "service";
    }
    $.fn.zato.ide.set_current_object_type(new_current);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_undeployed_files_list = function() {

    //  console.debug("Getting undeployed files list");

    let undeployed = [];
    $(`#object-select option[data-is-modified="1"`).each(function() {
        let fs_location = $(this).attr("data-fs-location");
        undeployed.push(fs_location);
    })
    return undeployed;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.mark_as_undeployed = function(undeployed) {

    for(item of undeployed) {
        $.fn.zato.ide.update_deployment_option_state(true, item)
    }
}


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_service_list_response = function(response) {

    //
    // We're switching from files to services here.
    //

    // Local variables
    let object_select = $("#object-select");
    let undeployed = $.fn.zato.ide.get_undeployed_files_list();

    //  console.debug("On service list undeployed: "+ undeployed);

    // Extract the underlying JSON ..
    let data = JSON.parse(response.responseText);

    // .. clear out the form ..
    object_select.empty();

    // .. build the expected optgroups ..
    let optgroup_current_file = `<optgroup label="Current file" id="optgroup-current-file"/>`;
    let optgroup_all_services = `<optgroup label="All services" id="optgroup-all-services"/>`;

    // .. add our optgroups to the select ..
    object_select.append(optgroup_current_file);
    object_select.append(optgroup_all_services);

    // .. extract the newly created optgroups ..
    let optgroup_current_file_object = $("#optgroup-current-file");
    let optgroup_all_services_object = $("#optgroup-all-services");

    // .. build an option element for services from the current file and append it to the "Current file" optgroup ..
    // .. we go here if there are no services in the current file ..

    if(!data.current_file_service_list.length) {

        // Build an option indicating that there are no services ..
        var option = `<option
            class="option-current-file"
            data-object-holder="1"
            data-is-current-file="1"
            data-line-number="-1"
            data-fs-location=""
            data-fs-location-url-safe=""
            data-current-root-directory="${data.current_root_directory}"
            data-root-directory-count="${data.root_directory_count}"
            data-service-name=""
            >(No services in current file)</option>`;

        // .. append it to our select ..
        optgroup_current_file_object.append(option);
    }

    // .. we go here if there are some services in the current file ..
    else {
        for(service_item of data.current_file_service_list) {

            console.debug("Current file service: "+ $.fn.zato.to_dict(service_item));
            var option = `<option
                class="option-current-file"
                data-object-holder="1"
                data-is-current-file="1"
                data-line-number="${service_item.line_number_human}"
                data-fs-location="${service_item.fs_location}"
                data-fs-location-url-safe="${service_item.fs_location_url_safe}"
                data-current-root-directory="${service_item.current_root_directory}"
                data-root-directory-count="${service_item.root_directory_count}"
                data-service-name="${service_item.name}"
                >${service_item.name}</option>`;
            optgroup_current_file_object.append(option);
        }
    }

    // .. build an option element for each service and append it to the "All services" optgroup ..
    for(service_item of data.service_list) {
        let is_current_file = service_item.fs_location == data.current_fs_location ? "1" : "0";
        var option = `<option
            class="option-all-objects"
            data-object-holder="1"
            data-is-current-file="${is_current_file}"
            data-line-number="${service_item.line_number_human}"
            data-fs-location="${service_item.fs_location}"
            data-fs-location-url-safe="${service_item.fs_location_url_safe}"
            data-current-root-directory="${service_item.current_root_directory}"
            data-root-directory-count="${service_item.root_directory_count}"
            data-service-name="${service_item.name}"
            >${service_item.name}</option>`;
        optgroup_all_services_object.append(option);
    }

    // .. switch to services ..
    $.fn.zato.ide.toggle_current_object_type("file");

    // .. mark the relevant select options as undeployed ..
    $.fn.zato.ide.mark_as_undeployed(undeployed);

    // .. services can be invoked now.
    $.fn.zato.ide.enable_invoke_button();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_file_list_response = function(response) {

    //
    // We're switching from services to files here.
    //

    // Extract the underlying JSON ..
    let data = JSON.parse(response.responseText);

    // Local variables
    let object_select = $("#object-select");
    let undeployed = $.fn.zato.ide.get_undeployed_files_list();
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let root_directory_count = Object.keys(data).length;

    // console.debug("On file list undeployed: "+ undeployed);
    // console.debug("File list data: "+ $.fn.zato.to_dict(data));
    // console.debug("Data length: "+ root_directory_count);

    // .. clear out the form ..
    object_select.empty();

    // .. go through everything we were given ..
    Object.entries(data).forEach(([dir_name, file_list]) => {

        // .. build an options group for each directory ..
        let optgroup_id = $.fn.zato.slugify("optgroup-" + dir_name);
        let optgroup = `<optgroup label="{0}" id="{1}"/>`;

        // .. append it to the form ..
        object_select.append(String.format(optgroup, dir_name, optgroup_id));

        // .. get a reference to it so that we can use it below ..
        let optgroup_object = $("#" + optgroup_id);

        // .. go through each file in that directory, if there are any ..
        if(file_list.length) {
            for(file_item of file_list) {

                // Loop-local variables
                let selected_option;

                let file_name = file_item.file_name;
                let file_name_url_safe = file_item.file_name_url_safe;

                // .. get the file name alone ..
                let file_name_short = file_name.replace(dir_name, "");

                // .. the file may begind with a slash ..
                let first_character = file_name_short.charAt(0);

                // .. which we need to remove ..
                if(first_character == "/" || first_character == "\\") {
                    file_name_short = file_name_short.substring(1);
                }

                // .. the file may only belong to a project's directory ..
                if(file_name_short.startsWith("impl/src/")) {
                    file_name_short = file_name_short.replace("impl/src/", "");
                }
                else if(file_name_short.startsWith("impl\\src\\")) {
                    file_name_short = file_name_short.replace("impl\\src\\", "");
                }

                // .. we need to select this option if it points to the file that we currently have opened ..
                if(file_name == current_fs_location) {
                    selected_option = `selected="selected"`;
                }
                else {
                    selected_option = "";
                }

                // .. now, we can build a new option for this file ..
                let option = `<option
                    class="option-all-objects"
                    ${selected_option}
                    data-is-current-file="1"
                    data-fs-location="${file_name}"
                    data-fs-location-url-safe="${file_name_url_safe}"
                    data-current-root-directory="${dir_name}"
                    data-root-directory-count="${root_directory_count}"
                    >${file_name_short}</option>`;

                // .. and append it to the form ..
                optgroup_object.append(option);
            }
        }
        // .. if there are no files, be explicit about it.
        else {
            let option = `<option
                class="option-all-objects"
                data-is-current-file="1"
                data-fs-location=""
                data-fs-location-url-safe=""
                data-current-root-directory="${dir_name}"
                data-root-directory-count="${root_directory_count}"
                >No files</option>`;
            optgroup_object.append(String.format(option));
        }
    });

    // .. switch to files ..
    $.fn.zato.ide.toggle_current_object_type("service");

    // .. mark the relevant select options as undeployed ..
    $.fn.zato.ide.mark_as_undeployed(undeployed);

    // .. enable buttons that can be used in the files view ..
    $.fn.zato.ide.enable_file_rename_button();
    $.fn.zato.ide.enable_file_delete_button();

    // .. services cannot be invoked in the files view.
    $.fn.zato.ide.disable_invoke_button();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.post_populate_current_file_service_list_impl = function(after_func) {

    _post_func = function(response) {
        console.debug("post_populate_current_file_service_list_impl: response:", JSON.stringify(response));
        let data = JSON.parse(response.responseText);
        console.debug("post_populate_current_file_service_list_impl: data.current_file_service_list:", JSON.stringify(data.current_file_service_list));
        console.debug("post_populate_current_file_service_list_impl: data.current_fs_location:", JSON.stringify(data.current_fs_location));
        $.fn.zato.ide.on_service_list_response(response);
        if(after_func) {
            after_func();
        }
    }
    return _post_func;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_current_file_service_list_impl = function(after_func, should_wait_for_services) {

    let url_path_prefix = "/zato/service/ide/get-service-list/";
    if(should_wait_for_services === undefined) {
        should_wait_for_services = "";
    }

    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let url_path = `${url_path_prefix}?fs_location=${current_fs_location}&should_wait_for_services=${should_wait_for_services}`;

    console.debug("populate_current_file_service_list_impl: url_path:", JSON.stringify(url_path));
    console.debug("populate_current_file_service_list_impl: current_fs_location:", JSON.stringify(current_fs_location));
    console.debug("populate_current_file_service_list_impl: should_wait_for_services:", JSON.stringify(should_wait_for_services));

    let callback = $.fn.zato.ide.post_populate_current_file_service_list_impl(after_func);
    $.fn.zato.invoker.invoke(url_path, "", callback)
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_file_list = function(after_callback_func) {
    let url_path = "/zato/service/ide/get-file-list/";
    let callback = function(response) {
        $.fn.zato.ide.on_file_list_response(response);
        if(after_callback_func) {
            after_callback_func();
        }
    }
    $.fn.zato.invoker.invoke(url_path, "", callback)
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_toggle_object_select = function() {

    let current_object_type = $.fn.zato.ide.get_current_object_type();

    // We are switching from services to files ..
    if(current_object_type == "service") {
        $.fn.zato.ide.populate_file_list();
    }

    // .. or from files to services.
    else {
        $.fn.zato.ide.populate_current_file_service_list_impl()
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_request_history_key = function() {
    let cluster_name = $.fn.zato.ide.get_cluster_name();
    let key = window.zato_local_storage_key.zato_request_history + "." + cluster_name;
    return key;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_request_history = function() {
    return $.fn.zato.invoker.get_history($.fn.zato.ide.get_request_history_key());
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.update_request_history_buttons = function() {
    console.debug("update_request_history_buttons: START");

    let history = $.fn.zato.ide.get_request_history();
    let history_length = history.length;
    let current_index = window.zato_request_history_index;

    console.debug("update_request_history_buttons: history_length:", history_length);
    console.debug("update_request_history_buttons: current_index:", current_index);

    let up_button = $("#request-history-up");
    let down_button = $("#request-history-down");

    if (history_length === 0) {
        console.debug("update_request_history_buttons: history is empty, disabling both buttons");
        $.fn.zato.ide.disable_button("#request-history-up");
        $.fn.zato.ide.disable_button("#request-history-down");
    } else {
        if (current_index < history_length - 1) {
            console.debug("update_request_history_buttons: enabling up button");
            $.fn.zato.ide.enable_button("#request-history-up");
        } else {
            console.debug("update_request_history_buttons: disabling up button");
            $.fn.zato.ide.disable_button("#request-history-up");
        }

        if (current_index > 0) {
            console.debug("update_request_history_buttons: enabling down button (current_index > 0)");
            $.fn.zato.ide.enable_button("#request-history-down");
        } else if (current_index === 0) {
            console.debug("update_request_history_buttons: enabling down button (current_index === 0)");
            $.fn.zato.ide.enable_button("#request-history-down");
        } else {
            console.debug("update_request_history_buttons: disabling down button");
            $.fn.zato.ide.disable_button("#request-history-down");
        }
    }

    console.debug("update_request_history_buttons: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_full_history_key = function() {
    let cluster_name = $.fn.zato.ide.get_cluster_name();
    let key = window.zato_local_storage_key.zato_full_history + "." + cluster_name;
    return key;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_full_history = function() {
    return $.fn.zato.invoker.get_history($.fn.zato.ide.get_full_history_key());
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.save_request_to_history = function(request_text, response_text) {
    let key = $.fn.zato.ide.get_request_history_key();
    $.fn.zato.invoker.save_to_history(key, request_text, response_text);

    let full_history_key = $.fn.zato.ide.get_full_history_key();
    $.fn.zato.invoker.save_to_history(full_history_key, request_text, response_text);

    window.zato_request_history_index = -1;
    $.fn.zato.ide.update_request_history_buttons();
    $.fn.zato.ide.populate_history_overlay();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_request_history_up = function() {
    let key = $.fn.zato.ide.get_request_history_key();
    window.zato_request_history_index = $.fn.zato.invoker.on_history_up(key, "#data-request", window.zato_request_history_index);
    $.fn.zato.ide.update_request_history_buttons();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_request_history_down = function() {
    let key = $.fn.zato.ide.get_request_history_key();
    window.zato_request_history_index = $.fn.zato.invoker.on_history_down(key, "#data-request", window.zato_request_history_index);
    $.fn.zato.ide.update_request_history_buttons();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.open_history_overlay = function() {
    console.debug("open_history_overlay: START");

    let overlay = $("#request-history-overlay");
    let history = $.fn.zato.ide.get_request_history();

    console.debug("open_history_overlay: history:", JSON.stringify(history));

    $.fn.zato.ide.populate_history_overlay(history);

    overlay.removeClass("hidden");

    $("#history-search-input").val("");
    $("#history-search-input").focus();

    $.fn.zato.ide.init_history_overlay_drag();

    console.debug("open_history_overlay: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.init_history_overlay_drag = function() {
    let content = document.querySelector(".invoker-history-overlay-content");
    let header = document.querySelector(".invoker-history-overlay-header");

    if (!content || !header || header.dataset.dragInitialized) {
        return;
    }

    header.dataset.dragInitialized = "true";
    header.style.cursor = "move";

    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    header.addEventListener("mousedown", function(e) {
        if (e.target.closest(".invoker-history-close-button")) {
            return;
        }

        isDragging = true;

        let rect = content.getBoundingClientRect();
        initialX = e.clientX - rect.left;
        initialY = e.clientY - rect.top;

        content.style.position = "fixed";
        content.style.margin = "0";
    });

    document.addEventListener("mousemove", function(e) {
        if (!isDragging) return;

        e.preventDefault();

        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        content.style.left = currentX + "px";
        content.style.top = currentY + "px";
    });

    document.addEventListener("mouseup", function() {
        isDragging = false;
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.close_history_overlay = function() {
    console.debug("close_history_overlay: called");
    $("#request-history-overlay").addClass("hidden");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.format_timestamp = function(timestamp) {
    return $.fn.zato.invoker.format_timestamp(timestamp);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_history_overlay = function(history, is_search_result) {
    if (!history) {
        history = $.fn.zato.ide.get_full_history();
    }

    // Item selection reads from what the overlay actually shows, which may be
    // a filtered subset whose indexes do not map to the full history
    $.fn.zato.ide.history_overlay_items = history;
    $.fn.zato.ide.history_overlay_is_search_result = !!is_search_result;

    let callbacks = {
        on_select: function(index) {
            $.fn.zato.ide.on_history_item_selected(index);
        },
        on_delete: function(index) {
            $.fn.zato.ide.on_history_item_delete(index);
        }
    };

    $.fn.zato.invoker.populate_history_list(
        $("#history-overlay-list"),
        history,
        is_search_result,
        callbacks
    );
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_history_item_selected = function(index) {
    console.debug("on_history_item_selected: index:", index);

    // The list the overlay was populated with is the one the index refers to
    let history = $.fn.zato.ide.history_overlay_items;
    let item = history[index];
    let request_text = typeof item === 'string' ? item : item.text;

    console.debug("on_history_item_selected: request_text:", JSON.stringify(request_text));

    $("#data-request").val(request_text);

    // Browsing continues from the chosen item, except that indexes
    // of a filtered list do not map to the full history
    if($.fn.zato.ide.history_overlay_is_search_result) {
        window.zato_request_history_index = -1;
    }
    else {
        window.zato_request_history_index = parseInt(index);
    }
    console.debug("on_history_item_selected: set window.zato_request_history_index to:", window.zato_request_history_index);

    $.fn.zato.ide.close_history_overlay();
    $.fn.zato.ide.update_request_history_buttons();

    // Choosing a request must never leave the invoke button disabled
    // as long as there is a service to invoke
    let service_name = $.fn.zato.ide.get_current_service_name();
    if(service_name) {
        $.fn.zato.ide.enable_invoke_button();
    }

    $("#data-request").focus();

    console.debug("on_history_item_selected: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.filter_history_overlay = function(search_text) {
    let key = $.fn.zato.ide.get_request_history_key();
    let result = $.fn.zato.invoker.filter_history(key, search_text);
    $.fn.zato.ide.populate_history_overlay(result.history, result.is_search_result);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_history_item_delete = function(index) {
    let key = $.fn.zato.ide.get_request_history_key();
    let history = $.fn.zato.invoker.delete_history_item(key, index);
    $.fn.zato.ide.populate_history_overlay(history);
    $.fn.zato.ide.update_request_history_buttons();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
