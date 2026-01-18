
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init = function() {

    let openapi_import_content = `
        <input type="button" id="openapi-from-copy-paste" value="From copy/paste" onclick="$.fn.zato.http_soap.openapi.on_from_copy_paste();"/>
        <input type="button" id="openapi-from-url" value="From URL" onclick="$.fn.zato.http_soap.openapi.on_from_url();"/>
    `;

    tippy("#openapi-import-link", {
        content: openapi_import_content,
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_copy_paste = function() {
    alert("From copy/paste clicked");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_url = function() {
    alert("From URL clicked");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
