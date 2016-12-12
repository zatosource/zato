# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Paste
from paste.util.converters import asbool

# Zato
from zato.common.util import get_brython_js
from zato.server.connection.http_soap import NotFound
from zato.server.service import Service

# ################################################################################################################################

page_template = """<!doctype html>
<html>
<head>
    <title>API specification</title>

    <style type="text/css">
        html,body,div,span,applet,object,iframe,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,abbr,acronym,address,big,cite,code,del,dfn,em,font,img,ins,kbd,q,s,samp,small,strike,strong,sub,sup,tt,var,dl,dt,dd,ol,ul,li,fieldset,form,label,legend,table,caption,tbody,tfoot,thead,tr,th,td{margin:0;padding:0;border:0;outline:0;font-weight:inherit;font-style:inherit;font-family:sans-serif;vertical-align:baseline}:focus{outline:0}html{overflow-y:scroll}body{color:black;background:#f3f3f3}ol,ul{list-style:none}table{border-collapse:separate;border-spacing:0}caption,th,td{text-align:left;font-weight:normal}blockquote:before,blockquote:after,q:before,q:after{content:""}blockquote,q{quotes:"" ""}.sf-menu{float:left;margin-bottom:0}.sf-menu li{background:#363636}.sf-menu li li{background:#363636}.sf-menu li li li{background:#363636}.sf-menu li:hover,.sf-menu li.sfHover,.sf-menu a:focus,.sf-menu a:hover,.sf-menu a:active{background:#464646;outline:0}.sf-menu a{border-left:1px solid #fff;border-top:1px solid #CFDEFF;padding:.75em 1em;text-shadow:-1px -1px 0 red;text-decoration:none;display:block;position:relative}span.like-a{color:#fff}.sf-menu a,span.like-a{text-shadow:1px 1px 0 #000}.sf-menu a,.sf-menu a:visited,span.like-a{font-size:11px;font-family:sans-serif;border:none;text-decoration:none}.sf-sub-indicator{display:none}#console-header{background-color:#0e0e0e;box-shadow:0px 0px 4px #333}#logo a:hover{background-color:transparent}#logo a{text-decoration:none;font-size:140%;padding-left:5px;color:#999;font-weight:600;font-family:sans-serif;text-shadow:2px 2px 0 #333}#logout{color:#fff;float:right;font-size:11px;padding-top:6px;padding-right:7.5px}#main-menu{background-color:#363636;border-bottom:3px solid #aaa}#main-menu ul,span.like-a{float:left;font-size:11px;font-family:sans-serif}#main-menu ul li,span.like-a{display:inline}#main-menu ul li a,span.like-a{float:left;text-decoration:none;color:white;padding:10.5px	5px}#main-menu ul li.wide{width:120px}#user-message-div{padding-top:16px;font-size:12px;margin-left:4px;margin-right:4px}.user-message{padding:6px;border-style:dotted;color:#333333;text-align:left}.user-message-success{border-color:#333333;border-width:1px;background-color:#bbdd55}.user-message-failure{border-color:red;border-width:2px;background-color:#eeee33}.error-message{background-color:#ffccbb;padding:6px;margin-bottom:12px;border:1px dotted #999999;font-weight:600;color:#933}.loading{background:url(/static/gfx/ajax-loader.gif) no-repeat;height:16px}.loading:after{content:"Please wait ...";padding-left:30px}#data-table{width:100%;margin-top:8px;margin-left:2%;border:1px solid #ccc;font-size:12px;counter-reset:data_table_counter}#data-table a{font-size:12px}#data-table tr.odd{background-color:#fff}#data-table tr.even{background-color:#e8e8e8}#data-table tr.updated{background-color:#f7f089}#data-table tr.attention td,#data-table tr.updated td{border-bottom:1px solid #a9a244}#data-table td,#data-table th{padding:6px}#data-table th{background:#ddd;font-size:11px}#data-table td{vertical-align:base}#data-table td.inline_header{background:#ddd}#data-table td.numbering:before{content:counter(data_table_counter);counter-increment:data_table_counter}#data-table td.impexp{width:1px}#data-table td.impexp input{display:none;width:1px}.form-data{width:100%;border:1px solid #666;padding:10px;font-size:12px;background-color:#ccc;color:#000;text-shadow:1px 1px 0 #eee}.form-data td{border:none;padding:4px;padding-right:12px}.ui-dialog-titlebar{padding:10px;background-color:#999;font-size:13px;border:1px solid #666;border-bottom:none;text-align:left;text-shadow:1px 1px 0 #aaa;padding-bottom:10px !important}.form_hint{font-size:smaller;color:#333}.attention{background-color:#f7f089}div.bd{box-shadow:1px 1px 10px #000}div.ui-dialog{width:33em !important}p.big-notice{background-color:#ccc;width:50%;margin:0 auto;padding:20px;margin-top:20px;text-align:center;font-size:large;border:1px solid #999}.ui-dialog-titlebar{padding-bottom:0px;background-color:#333;font-size:13px;border:1px solid #666;border-bottom:none;text-align:left;color:#eee;text-shadow:1px 1px 0 #000}.ui-icon-closethick{display:none}.ui-dialog-buttonset{text-align:right}.ui-icon-closethick{display:none}.ui-widget{box-shadow:1px 1px 10px #000}.ui-datepicker{border:1px solid #aaaaaa;background:#fff url(images/ui-bg_glass_75_ffffff_1x400.png) 50% 50% repeat-x;color:#222222;font-size:0.9em}.ui-slider .ui-slider-handle{border:1px solid #999}#popup_container{border-radius:0 0 0 0}h2.zato{font-size:80%;padding:10px;padding-left:4px;color:#222;border-bottom:1px dotted #767676}div.prompt{font-size:11px;padding:10px;padding-left:4px}div.prompt form{padding-top:4px}a{color:#000;font-family:arial,helvetica,clean,sans-serif;text-decoration:underline;padding:3px;padding-left:0px}a:hover{background-color:#e0e030;color:#000033;text-decoration:none}a.top{color:#fff;text-shadow:none}a.top:hover{color:#000}a.hint{color:#333;font-size:10px}#footer{border-top:1px solid #999999;border-bottom:1px solid #999999;margin:5px 5px 0px 0px;padding:5px;background-color:#e0e0e0;text-align:right}.validation-advice{color:#c00}.options-button{cursor:pointer}#markup{width:94%;text-align:center}th.ignore,td.ignore,div.ignore{display:none}div.page_prompt{padding:4px;font-size:12px}div.page_prompt a.current{font-weight:bolder}#id_file{width:100%}.hidden{visibility:hidden;display:none}.visible{visibility:visible}
    </style>

    <style type="text/css">

        /* ///////////////////////////////////
        // Namespaces
        // //////////////////////////////// */

        div.highlight span.header {
            background-color:#e0e030;
            color:#000
        }

        .td-ns {
            background-color: #e1e3e5;
            border: 1px solid #adb3b9;
            border-radius: 3px;
            box-shadow: 0 1px 0 rgba(12, 13, 14, 0.2), 0 0 0 2px #fff inset;
            font-size: 12px;
            line-height: 1.4;
            margin: 0 0.1em;
            margin-bottom: 3px;
            text-shadow: 0 1px 0 #fff;
            white-space: nowrap;
            vertical-align:bottom !important;
        }

        .ns-name {
            float:left;
            font-weight:600
        }

        .ns-name span.docs {
            font-weight:500;
            color: #666;
        }

        .ns-options {
            float:right;
            padding:none !important
        }

        .tr-ns + .tr-service .td-service {
            border-top:none;
        }

        /* ///////////////////////////////////
        // Services
        // //////////////////////////////// */

        .td-service {
            border-left:1px dashed #c3c3c3;
            border-right:1px dashed #c3c3c3;
            border-top:1px dashed #c3c3c3;
        }

        .service-name > .service-desc{
            color:#666
        }

        .service-name > .service-desc {
            display:inline !important;
        }

        .service-name {
            float:left;
            padding-left:3px;
        }

        .service-io th {
            text-align:center;
            font-size:0.9em !important;
            border-bottom:1px solid #c9c9c9 !important;
            border-top:1px solid #c9c9c9 !important;
            border-right:1px solid #c9c9c9 !important;
        }

        .service-io th.input {
            border-left:1px solid #c9c9c9 !important;
        }

        .service-io td {
            padding:10px !important;
            border-bottom:1px dashed #ccc;
            border-right:1px dashed #ccc;
            font-size:1em;
        }

        .service-io td.req-opt {
            font-size:0.8em;
            color:#666;
            font-style:italic
        }

        .io-is-required {
            border-right:1px solid #c9c9c9 !important;
        }

        .tr-io-last td {
            border-bottom:1px solid #c9c9c9 !important;
        }

        .io-name-input {
            border-left:1px solid #c9c9c9 !important;
        }

        .service-options {
            float:right;
        }

        .service-details {
            clear:left;
            padding:5px;
            padding-left:0px;
            color: #555;
        }

        .header-details {
            margin-top:5px;
            padding-top:5px;
            padding-bottom:5px;
            color:#333
        }

        .header-details strong, .header-details em {
            color:#000;
            padding:3px;
            background-color:#e3e3e3;
            font-style:italic;
        }

        .header-details p {
            padding-top:3px;
            padding-bottom:3px;
        }

        .header-details ul {
            list-style-type: "• ";
            padding-left:15px;
        }

        .header-details ol {
            list-style-type:decimal;
            padding-left:20px;
        }

        .header-details li {
            padding-top:2px;
            padding-bottom:2px;
        }

        .service-details .header, .service-details .header a {
            font-size:11px !important;
            color:#333;
        }

        .service-details .header, .service-details .header a:hover {
            color:#000;
        }

        /* ///////////////////////////////////
        // Containers and misc
        // //////////////////////////////// */

        #main-div {
            text-align:center;
        }

        #main-div.no-results {
            text-align:left;
            background-color:#e9e9e9;
            padding:5px;
            border:1px dashed #ccc
        }

        #spec-table {
            width:100%;
            text-align:center;
        }

        #spec-table tr.tr-service:last-child > td {
            border-bottom:1px dashed #ccc;
        }

    </style>

    <script type="text/javascript" src="/apispec/static/brython/_brython/brython.js"></script>
    <script type="text/python" src="/apispec/static/brython/_zato/docs.py"></script>

</head>
<body onload="brython()">

        <div id="hd">
            <div id="console-header">&nbsp;<img src="data:image/png;charset=utf-8;base64, iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAh3pUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadY7LDQMxCETvVJES+Hkw5UQrr5QOUn6wvJZPeQcYjdAwNL6fm14TYSVv0ZEAF56e+i7ReWHMoixz11w826SUHptMl0D2YD+H/vibZui4wyPQcOHSStdhYlqzHtFM5VkjT4iM3eiPv1v8AEsULHmqW1+DAAAJ6WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjMwIgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iMzAiCiAgIHRpZmY6SW1hZ2VXaWR0aD0iMSIKICAgdGlmZjpJbWFnZUhlaWdodD0iMzAiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PoOxCoAAAAAEc0JJVAgICAh8CGSIAAAFl0lEQVRIx72XbYxcVRnHf/87O51ddtvd7m5fTNdunHubpYWyNL7wgdKatraRWEJUTIwaMTq3JGoVbCJCoMiLisE0Rm3sTBNDIgllCcFaG2OwiRJfI8SGZLX2ntkGU0Vxd2kxXbrrzt8P3GmW6Rb4wHK+zNxznvP87nlez4WWUalUCrzdI03TeCH0hhAW1+v1aO5cNAf6EdvPLwQ4juOXbe+4CJym6UpgplarzbwZRbt377768OHDHz158uQNIYTVb5J/PIRwefOhLf+9Ddj7Bm7oA75te2tPT0//smXLFkVRZNvnQwinbI8kSXLfpfZLmrR9T5Zlu5IkcVuapottX1er1aZeB7oT+J7tgWKxWFizZg29vb1NhYuA9cBQCGE78Ok4juutOqIomp6dnR2Q1ANMRsAVkt7xOtAbgYeBQUmF7u5uyuUybW1traKLgGttHwkhDLQuNhoNgC5gedPHi20vTdO0fR7oAPADYKltR1HE4ODghdO2mBLbkjRk+7GxsbGoBbwIWNp0bwSck1QEPtwCLQCPAiubujs6OiiXyxSLRWzPCwciSe+enZ29q8XUK4B+wE3wX2xPAnvSNC3OkR0GrsplLMl9fX0sX74cSU2IL+GhoqTPZFm2pDlh+35AwL8Bomq1OiHpV8AQ8Ik5gl8FOvP/kuTe3t6p9vb2cWDC9lS+Nm8QAyslvT8vINfYvh44JWlibjrtBbYDD6VpGoA/ARtyBQCvAD+V9FCj0fjrq1bV5bb3SPoQ0D7n9M09s8CGLMv+YPthoAjcUS6XGxcKSLVaPQn8OI+6J4Cttm8BngFeknTfgQMHPrZx48a+Uql0L/B1271JktwEfAuYyoGyPQ1kwJeBEeCYpLKko3EcH6Pl7ZoB9RPgg7bPS3oEuBXYXK1Wf75v377ali1bburq6jpnuyipZPtQkiSVEMIvbK8HTkh6wnYV+Jyku/OM+F2SJJtafdHanR7LzVe0/bykHcCGoaGhg9u2bTs0PDyc5n47Amyy/UngKUnTQJvtiqQvAc1c/rXtnUmSnJ+3SeQnXgLcBVRs/0PSEtuThUJhU6lUOteE5uOOfP8NURQVgGO2/y7pO8AgMG77a3Ecb2+FXgSuVqtnJR0E3iVpCLgTmImiaLqzs7M4Pj7eMSfql+YWM7DE9rCkTtv/BO4HhqIoejnLsnXzhX3UOmH7aeB227+1/QowVSgUftbR0VGYmJg4GkLYHEK4XtJ3bc9IqjUajRi4G7hO0lrbz9k+2mg0bikWi38LIWy9JLhSqbw3TdPdwD3AqKRhSTVJz9Xr9Wf7+/sflLTe9lFgxPY7JT0Qx/EfJf1LUt32zbZHgUckrZX0+cHBwf8B3wghVC4KrjRN24DfA6vzVPqPpCfzXC4Af+7u7t65a9eukqQbc8s8LqkAPAkkthdJant1yS9I+kocx4+GEL5p+zZgNEmSDa85se1+oJzX0iOSVlSr1WuAKvACcOWqVauOT09P7wcawIykg7afycvqZZIi22ds/zKKovfZPhRCuBf4Yt4619br9c++BizpSuCy3AI9thfnwfaF/DS3RlE0lsvtBR4Ars2r0YvAqO3vS7oa2AFMSjoC7LHd2Wybtm/PsqxzbsnsAiLbDUmP12q1p+dE+hSwH9g/OjrancuW8pecBs4BZ5MkuXBtqtfrReAKoEOS8xIrYLWkTwE/bIKz3Hwv5V1k3rFu3bozwJk3ulyVy+UzWZY9JenmPEYudC3gzhDCSDOqTwGnbe+v1Wpjb8XNMoqivbbPtnYt2wPAVc0m8V9gH/DgW3WlLZfLpyU9O6drOY+nKdsvaiE/EOr1+scbjcaPJJWaNyDbx4vF4nsWFAyQZdmopLU59LSkD8RxfCJaaLCkEdtnbf9G0uY4jk+8Ld9jWZatCCFsbJ3/P3NnfsE+60ljAAAAAElFTkSuQmC" alt="Zato samurai helmet logo" style="vertical-align:bottom"/>
            <span id="logo"><a href="https://zato.io/docs">Zato</a></span>
            <span style="color:#eee; font-weight:bold; font-size:17px; padding-left:2px">ZATO_PUB_NAME</span>
            </div>
        </div>

    <div id="docs-data" style="display:none">ZATO_DATA</div>

    <div id="markup">
        <table id="data-table" style="border:none">
            <tr>
                <td><div id="main-div"></div></td>
            </tr>
        </table>
    </div>

    <form>
      <input type="hidden" id="cluster_id" value="ZATO_CLUSTER_ID" />
    </form>

</body>
"""

docs_py = '''# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Brython
from browser import document as doc, window
from browser.html import A as a, DIV as div, TABLE as table, TR as tr, TD as td

# ################################################################################################################################

_anon_ns = 'zato_anonymous'

# ################################################################################################################################

# Taken from https://docs.python.org/3.3/library/itertools.html#itertools.zip_longest

class ZipExhausted(Exception):
    pass

def chain(*iterables):
    """ chain('ABC', 'DEF') --> A B C D E F
    """
    for it in iterables:
        for element in it:
            yield element

def repeat(object, times=None):
    """ repeat(10, 3) --> 10 10 10
    """
    if times is None:
        while True:
            yield object
    else:
        for i in range(times):
            yield object

def zip_longest(*args, **kwds):
    """ zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    """
    fillvalue = kwds.get('fillvalue')
    counter = len(args) - 1
    def sentinel():
        nonlocal counter
        if not counter:
            raise ZipExhausted
        counter -= 1
        yield fillvalue
    fillers = repeat(fillvalue)
    iterators = [chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass

# ################################################################################################################################

tr_ns_html_contents_template = """
<td id="td-ns-{name}" class="td-ns">
  <div id="ns-name-{name}" class="ns-name"><span class="header">{ns_name_human}</span> <span class="docs">{ns_docs_md}</span></div>
  <div id="ns-options-{name}" class="ns-options">
    <a href="#" id="a-ns-options-toggle-services-{name}">Toggle services</a>
    |
    <a href="#" id="a-ns-options-toggle-all-details-{name}">Toggle all details</a>
  </div>
</td>
"""

tr_service_html_contents_template = """
<td id="td-service-{ns_name}-{name}" class="td-service">
  <div id="service-name-{ns_name}-{name}" class="service-name"><span class="header">{service_no}. {display_name}</span> <span class="service-desc" id="service-desc-{ns_name}-{name}"></span></div>
  <div id="service-options-{ns_name}-{name}" class="service-options"><a href="#" id="a-toggle-details-{ns_name}-{name}">Toggle details</a></div>
  <div id="service-details-header-{ns_name}-{name}" class="hidden service-details service-details-toggle-{ns_name}-{name}">
    <span class="header">
      <a href="#" id="service-header-docs-{ns_name}-{name}">Docs</a>
      |
      <a href="#" id="service-header-deps-{ns_name}-{name}">Dependencies</a>
      |
      <a href="#" id="service-header-io-{ns_name}-{name}">I/O</a>
    </span>
  </div>
  <div id="service-details-deps-{ns_name}-{name}" class="hidden header-details service-details-toggle-{ns_name}-{name}">Dependencies</div>
  <div id="service-details-io-{ns_name}-{name}" class="hidden header-details service-details-toggle-{ns_name}-{name}">I/O</div>
  <div id="service-details-docs-{ns_name}-{name}" class="hidden visible current-item header-details service-details-toggle-{ns_name}-{name}"/>
</td>
"""

deps_template = """
<p>Invokes: {invokes}</p>
<p>Invoked by: {invoked_by}</p>
"""

io_template = """
<table class="service-io">
  <thead>
    <tr>
      <th colspan="3" class="input">Input</th>
      <th colspan="3">Output</th>
    </tr>
  </thead>
  <tbody id="io-tbody-{name}">
    {rows}
  </tbody>
</table>
"""

io_row_template = """
    <tr class="{tr_class}">
      <td class="io-name-input">{input_name}</td>
      <td class="io-data-type">{input_data_type}</td>
      <td class="io-is-required req-opt">{input_is_required}</td>
      <td class="io-name">{output_name}</td>
      <td class="io-data-type">{output_data_type}</td>
      <td class="io-is-required req-opt">{output_is_required}</td>
    </tr>
"""

none_html = '<span class="form_hint">(None)</span>'
header_details = ('deps', 'io', 'docs')

# ################################################################################################################################

class APISpec(object):
    """ Main object responsible for representation of API specifications.
    """
    def __init__(self, data):
        self.data = data
        self.spec_table = table(id='spec-table')
        self.cluster_id = doc['cluster_id'].value

# ################################################################################################################################

    def toggle_visible_hidden(self, e, id, needs_visible, _attrs=('visible', 'hidden')):
        elem = doc[id]
        current = [_elem.strip() for _elem in elem.class_name.split(' ')]

        for name in _attrs:
            try:
                current.remove(name)
            except ValueError:
                pass

        current.append('visible' if needs_visible else 'hidden')
        elem.class_name = ' '.join(current)

        if e:
            e.preventDefault()

# ################################################################################################################################

    def _switch_css_class(self, id, class_name, needs_add=True):
        elem = doc[id]
        classes = set(elem.class_name.split(' '))

        if needs_add:
            classes.add(class_name)
        else:
            classes.remove(class_name)

        elem.class_name = ' '.join(classes)

# ################################################################################################################################

    def _toggle(self, e, selector, needs_visible=None):
        for elem in doc.get(selector=selector):
            if needs_visible is None:
                needs_visible = 'hidden' in elem.class_name
            self.toggle_visible_hidden(e, elem.id, needs_visible)

# ################################################################################################################################

    def toggle_simple(self, selector_prefix, ns_name):
        def _toggle(e):
            self._toggle(e, '.{}{}'.format(selector_prefix, ns_name))
        return _toggle

# ################################################################################################################################

    def toggle_details(self, selector_prefix, ns_name, service_name):
        def _toggle(e):
            selector = '.{}{}-{}'.format(selector_prefix, ns_name, service_name)
            elems = doc.get(selector=selector)
            for elem in elems:
                if 'service-details-header' in elem.id or 'current-item' in elem.class_name:
                    self._toggle(None, '#{}'.format(elem.id))
        return _toggle

# ################################################################################################################################

    def toggle_all_details(self, ns_name):
        def _toggle(e):

            self._toggle(e, '.tr-service-ns-{}'.format(ns_name), True)

            # Iterate as long as we don't hit upon another header
            for elem in doc.get(selector='#tr-ns-{} ~ tr'.format(ns_name)):
                if 'tr-ns' in elem.id:
                    break

                selector = '.service-details-toggle-{}-{}'.format(ns_name, elem.id.replace('tr-service-', ''))
                elems = doc.get(selector=selector)

                for elem in elems:
                    if 'service-details-header' in elem.id or 'current-item' in elem.class_name:
                        self._toggle(None, '#{}'.format(elem.id))

        return _toggle

# ################################################################################################################################

    def highlight(self, id_pattern, *pattern_args, needs_add=True):
        def _highlight(e):
            id = id_pattern.format(*pattern_args)
            self._switch_css_class(id, 'highlight', needs_add)
        return _highlight

# ################################################################################################################################

    def switch_detail(self, ns_name, service_name, current):
        def _switch(e):

            # Switch everything off ..
            for detail in header_details:
                id = '#service-details-{}-{}-{}'.format(detail, ns_name, service_name)
                elems = doc.get(selector=id)

                for elem in elems:

                    classes = elem.class_name.split(' ')
                    if 'current-item' in classes:
                        classes.remove('current-item')
                    elem.class_name = ' '.join(classes)

                self._toggle(None, id, False)

            # .. and switch on only the required one.
            current_id = 'service-details-{}-{}-{}'.format(current, ns_name, service_name)
            _current = doc[current_id]
            self._toggle(None, '#{}'.format(current_id), True)

            classes = _current.class_name.split(' ')
            classes.append('current-item')
            _current.class_name = ' '.join(classes)

            # Don't forget about cancelling the default handler
            e.preventDefault()

        return _switch

# ################################################################################################################################

    def get_tr_ns_html(self, ns_name, ns_name_human, ns_docs_md=''):
        return tr_ns_html_contents_template.format(name=ns_name, ns_name_human=ns_name_human, ns_docs_md=ns_docs_md)

# ################################################################################################################################

    def _get_deps(self, deps):
        out = []
        for name in deps:
            out.append('<a href="/zato/service/overview/{name}/?cluster={cluster_id}">{name}</a>'.format(
                name=name, cluster_id=self.cluster_id))

        return ', '.join(out) or none_html

# ################################################################################################################################

    def get_deps_html(self, invokes, invoked_by):
        return deps_template.format(invokes=self._get_deps(invokes), invoked_by=self._get_deps(invoked_by))

# ################################################################################################################################

    def get_io_html(self, name, io):
        if not io:
            return none_html

        _input = io['input_required'] + io['input_optional']
        _output = io['output_required'] + io['output_optional']

        rows = []

        _io = list(zip_longest(_input, _output))
        len_io = len(_io)
        for idx, elems in enumerate(_io, 1):
            _input_elem, _output_elem = elems

            if not _input_elem:
                input_name, input_data_type, input_is_required = '---', '---', '---'
            else:
                input_name = _input_elem['name']
                input_data_type = _input_elem['subtype']
                input_is_required = 'required' if _input_elem['is_required'] else 'optional'

            if not _output_elem:
                output_name, output_data_type, output_is_required = '---', '---', '---'
            else:
                output_name = _output_elem['name']
                output_data_type = _output_elem['subtype']
                output_is_required = 'required' if _output_elem['is_required'] else 'optional'

            rows.append(io_row_template.format(tr_class='tr-io-last' if idx == len_io else '',
                input_name=input_name, input_data_type=input_data_type, input_is_required=input_is_required,
                output_name=output_name, output_data_type=output_data_type, output_is_required=output_is_required))

        return io_template.format(name=name, rows='\\n'.join(rows))

# ################################################################################################################################

    def get_tr_service_html(self, service_no, service):
        display_name = service['name']
        name = self.get_service_name(service['name'])
        ns_name = self.get_ns(service['namespace_name'])
        return tr_service_html_contents_template.format(
            display_name=display_name, name=name, ns_name=ns_name, service_no=service_no)

# ################################################################################################################################

    def get_ns(self, ns):
        return ns if ns else _anon_ns

# ################################################################################################################################

    def get_service_name(self, name):
        return name.replace('.', '-')

# ################################################################################################################################

    def run(self):
        """ Creates a table with all the namespaces and services.
        """
        default_ns_name_human = """
            <span class="form_hint" style="font-size:100%;font-style:italic">(Services without a namespace)</span>
        """

        # Maps names of services to their summaries and descriptions
        service_details = {}

        # All namespaces
        namespaces = list(self.data.get('namespaces', {}).values())
        for values in namespaces:

            # Config
            services = values['services']

            if not services:
                continue

            ns_docs_md = values['docs_md']
            ns_name = self.get_ns(values['name'])

            # Create a new row for each namespace
            tr_ns = tr(id='tr-ns-{}'.format(ns_name))
            tr_ns.class_name='tr-ns'
            tr_ns.html = self.get_tr_ns_html(
                ns_name, (ns_name if ns_name != _anon_ns else default_ns_name_human), ns_docs_md)

            # Append namespaces to the main table
            self.spec_table <= tr_ns

            # Append a row for each service in a given namespace
            for idx, service in enumerate(services):
                service_name = self.get_service_name(service['name'])
                tr_service = tr(id='tr-service-{}'.format(service_name))
                tr_service.class_name='visible tr-service tr-service-ns-{}'.format(ns_name)
                tr_service.html = self.get_tr_service_html(idx+1, service)
                self.spec_table <= tr_service
                service_details[service_name] = {

                    'ns_name': ns_name,
                    'docs': {
                        'summary': service['docs']['summary_html'],
                        'full': service['docs']['full_html'],
                    },
                    'deps': {
                        'invokes': service['invokes'],
                        'invoked_by': service['invoked_by']
                    },
                    'io': service['simple_io'].get('zato', {})

                }

        # Don't display anything if there are no services in the only namespace
        if len(namespaces) == 1 and not namespaces[0]['services']:
            doc['main-div'].html = '<b>No results</b>'
            doc['main-div'].class_name = 'no-results'
            return

        # We can append the table with contents to the main div
        doc['main-div'] <= self.spec_table

        # Now we can set up details by their div IDs
        for name, details in service_details.items():

            ns_name = details['ns_name']
            name = self.get_service_name(name)

            docs = details['docs']
            doc['service-desc-{}-{}'.format(ns_name, name)].html = docs['summary']
            doc['service-details-docs-{}-{}'.format(ns_name, name)].html = docs['full'] or none_html

            deps = details['deps']
            doc['service-details-deps-{}-{}'.format(ns_name, name)].html = self.get_deps_html(deps['invokes'], deps['invoked_by'])

            io = details['io']
            doc['service-details-io-{}-{}'.format(ns_name, name)].html = self.get_io_html(name, io)

            elem = doc['a-toggle-details-{}-{}'.format(ns_name, name)]
            elem.bind('click', self.toggle_details('service-details-toggle-', details['ns_name'], name))

            elem.bind('mouseover', self.highlight('service-name-{}-{}', ns_name, name))
            elem.bind('mouseout', self.highlight('service-name-{}-{}', ns_name, name, needs_add=False))

            for detail in header_details:
                elem = doc['service-header-{}-{}-{}'.format(detail, ns_name, name)]
                elem.bind('click', self.switch_detail(ns_name, name, detail))

        for item in namespaces:
            ns_name = self.get_ns(item['name'])

            elem = doc['a-ns-options-toggle-services-{}'.format(ns_name)]
            elem.bind('click', self.toggle_simple('tr-service-ns-', ns_name))
            elem.bind('mouseover', self.highlight('ns-name-{}', ns_name))
            elem.bind('mouseout', self.highlight('ns-name-{}', ns_name, needs_add=False))

            elem = doc['a-ns-options-toggle-all-details-{}'.format(ns_name)]
            elem.bind('click', self.toggle_all_details(ns_name))
            elem.bind('mouseover', self.highlight('ns-name-{}', ns_name))
            elem.bind('mouseout', self.highlight('ns-name-{}', ns_name, needs_add=False))

# ################################################################################################################################

apispec = APISpec(loads(doc['docs-data'].text))
apispec.run()

# ################################################################################################################################
'''

# ################################################################################################################################

class _Base(Service):

    def validate_input(self):
        if not asbool(self.server.fs_server_config.apispec.pub_enabled):

            # Note that we are using the same format that regular 404 does
            raise NotFound(self.cid, '[{}] Unknown URL:[{}] or SOAP action:[]'.format(
                self.cid, self.wsgi_environ['zato.http.channel_item']['url_path']))

# ################################################################################################################################

class Main(_Base):
    """ Returns public version of API specifications.
    """
    def handle(self):

        replace_with = {
            'ZATO_DATA': self.invoke('zato.apispec.get-api-spec'),
            'ZATO_CLUSTER_ID': str(self.server.cluster_id),
            'ZATO_PUB_NAME': self.server.fs_server_config.apispec.pub_name,
            'ZATO_PUB_CSS_STYLE': self.server.fs_server_config.apispec.pub_css_style,
        }

        _page_template = page_template

        for k, v in replace_with.items():
            _page_template = _page_template.replace(k, v)

        self.response.payload = _page_template
        self.response.headers['Content-Type'] = 'text/html'

# ################################################################################################################################

class BrythonJS(_Base):
    """ Returns Brython's main source code module.
    """
    def handle(self):
        self.response.payload = get_brython_js()
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class BrythonJSON(_Base):
    """ Brython's 'json' module.
    """
    def handle(self):
        _json = """var $module = (function($B){

return  {
    loads : function(json_obj){
        return $B.jsobject2pyobject(JSON.parse(json_obj))
    },
    load : function(file_obj){
        return $module.loads(file_obj.$content);
    },
    dumps : function(obj){return JSON.stringify($B.pyobject2jsobject(obj))},
}

})(__BRYTHON__)
"""
        self.response.payload = _json
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class Frontend(_Base):
    """ Returns Brython frontend code to display API specifications.
    """
    def handle(self):
        self.response.payload = docs_py
        self.response.headers['Content-Type'] = 'text/python'

# ################################################################################################################################
