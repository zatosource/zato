# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Brings up the whole local LLM stack for interactive use - the Ollama container,
the model and the browser console connected to it - and prints where to log in.
Nothing in the test suite imports this module, it is run by make llm-console only.
"""

# stdlib
import sys

# local
import containers

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Starts Ollama, pulls the model if needed, starts the console and prints its URL.
    """

    if not containers.is_docker_available():
        print('Docker is not available')
        sys.exit(1)

    print('[CONSOLE] making sure Ollama is up ..')
    containers.ensure_ollama()

    print(f'[CONSOLE] making sure the model `{containers.Model_Name}` is present ..')
    containers.ensure_model()

    print('[CONSOLE] making sure the console is up ..')
    containers.ensure_console()

    print(f'[CONSOLE] ready - log in at {containers.Console_URL}')
    print(f'[CONSOLE] the model to pick is `{containers.Model_Name}`')

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
