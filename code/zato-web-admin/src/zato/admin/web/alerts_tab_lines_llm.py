# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines of the Alerts tab of an outgoing LLM connection - the ones every outgoing connection has, built in
# alerts_tab_lines.py, and the LLM's own: completions cut short by the token limit, refusals, the two-step latency
# of completions and a token budget. alerts_tab.py lists them under the llm type next to the other types' lines.

# Zato
from zato.admin.web.alerts_tab_lines import active_line, connection_failures_line, email_line, error_rate_line, \
    failures_in_a_row_line, Latency_Window_Unit_Field, Line_Kind_Popover, llm_line, Refusals_Window_Unit_Field, \
    Section_Failures, Section_Traffic, Status_Codes_Field, status_codes_line, Token_Budget_Unit_Field, \
    Token_Budget_Window_Unit_Field, Truncations_Window_Unit_Field, use_llm_line
from zato.common.alerting.object_config import alert_type_llm, get_defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The status codes an outgoing LLM connection alerts on before anything is typed - the seeded rule's own, 429 among them
LLM_Status_Codes_Default = get_defaults(alert_type_llm)[Status_Codes_Field]

# ################################################################################################################################
# ################################################################################################################################

# The completions the provider stopped generating because the connection's max tokens was reached - the reply
# arrived with a 200 and reads fine, only it is incomplete
def _truncated_completions_line() -> 'anydict':
    out = {
        'name': 'truncated_completions',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Truncated completions',
        'title': 'Truncated completions',
        'fields': ['truncations', 'truncations_window'],
        'rows': [['truncations'], ['truncations_window']],
        'unit_field': Truncations_Window_Unit_Field,
        'summary': 'Alert after {truncations|completion|completions} cut short by the token limit ' + \
            f'in the last {{{Truncations_Window_Unit_Field}@truncations_window}}',
        'how_it_works': 'How many completions cut short by the token limit raise an alert, and how long the window ' + \
            'they are counted over. The provider stopped generating because max tokens was reached - the reply arrived ' + \
            'with a 200 and looks fine, only it is incomplete. Raising the connection\'s max tokens or shortening ' + \
            'the prompt is the remedy.',
    }
    return out

# ################################################################################################################################

# The completions the provider declined - it refused to answer or a content filter blocked the prompt or the reply
def _refusals_line() -> 'anydict':
    out = {
        'name': 'refusals',
        'section': Section_Failures,
        'kind': Line_Kind_Popover,
        'label': 'Refusals',
        'title': 'Refusals',
        'fields': ['refusals', 'refusals_window'],
        'rows': [['refusals'], ['refusals_window']],
        'unit_field': Refusals_Window_Unit_Field,
        'summary': 'Alert after {refusals|refusal|refusals} ' + \
            f'in the last {{{Refusals_Window_Unit_Field}@refusals_window}}',
        'how_it_works': 'How many refused completions raise an alert, and how long the window they are counted over. ' + \
            'The provider declined to answer or a content filter blocked the prompt or the reply - most refusals arrive ' + \
            'with a 200, so nothing but the finish reason tells one apart from an answer.',
    }
    return out

# ################################################################################################################################

# How long completions take, in seconds - a warning above the first threshold, an error above the second
def _slow_completions_line() -> 'anydict':
    out = {
        'name': 'slow_completions',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': 'Slow completions',
        'title': 'Slow completions',
        'fields': ['warning_latency', 'error_latency', 'latency_window'],
        'rows': [['warning_latency', 'error_latency'], ['latency_window']],
        'unit_field': Latency_Window_Unit_Field,
        'summary': 'Warning above {warning_latency|second|seconds}, error above {error_latency|second|seconds}, ' + \
            f'averaged over the last {{{Latency_Window_Unit_Field}@latency_window}}',
        'how_it_works': 'Completions averaging more than the first number of seconds raise a warning, more than ' + \
            'the second an error, and how long the window they are averaged over. Fractions such as 7.5 are fine.',
    }
    return out

# ################################################################################################################################

# The tokens the connection used - input and output added up across every call in the window, the budget
# a count in thousands, millions or billions with a unit select of its own next to the window's
def _token_budget_line() -> 'anydict':
    out = {
        'name': 'token_budget',
        'section': Section_Traffic,
        'kind': Line_Kind_Popover,
        'label': 'Token budget',
        'title': 'Token budget',
        'fields': ['token_budget', 'token_budget_window'],
        'rows': [['token_budget'], ['token_budget_window']],
        'unit_field': Token_Budget_Window_Unit_Field,
        'field_units': {'token_budget': Token_Budget_Unit_Field},
        'summary': f'Alert above {{{Token_Budget_Unit_Field}@token_budget}} tokens ' + \
            f'in the last {{{Token_Budget_Window_Unit_Field}@token_budget_window}}',
        'how_it_works': 'How many tokens raise an alert - a count in thousands, millions or billions, fractions such as ' + \
            '2.5 are fine - and how long the window they are added up over. Input and output tokens are added up ' + \
            'across every call the connection made, as the provider reported them.',
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def llm_lines() -> 'anylist':
    """ The lines of the tab of an outgoing LLM connection, in the order they are read - the core four, the failures
    with the provider's status codes and the LLM's own two, then how long completions take and how many tokens they use.
    """
    out = [
        active_line(),
        use_llm_line(),
        llm_line(),
        email_line(),
        failures_in_a_row_line(),
        error_rate_line(),
        status_codes_line(LLM_Status_Codes_Default),
        connection_failures_line(),
        _truncated_completions_line(),
        _refusals_line(),
        _slow_completions_line(),
        _token_budget_line(),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################
