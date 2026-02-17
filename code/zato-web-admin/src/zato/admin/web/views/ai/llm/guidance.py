# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from operator import itemgetter

# fastembed
from fastembed import TextEmbedding

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

guidance_snippets = [
    'Task type: service creation - deploy_service tool available',
    'Task type: debugging - check logs and error messages',
    'Task type: configuration - use create/update tools for connections',
    'Task type: documentation lookup - search_documentation tool available',
    'Task type: code review - focus on error handling patterns',
    'Task type: integration - verify endpoint connectivity',
    'Task type: data transformation - validate input/output formats',
    'Task type: security - check authentication and permissions',
    'Task type: performance - review query patterns and caching',
    'Task type: deployment - verify service dependencies',
]

# ################################################################################################################################
# ################################################################################################################################

class GuidanceSelector:
    """ Selects relevant guidance snippets based on user message using embeddings.
    """

    def __init__(self) -> 'None':
        self.model = None
        self.guidance_vectors = None
        self._initialized = False

# ################################################################################################################################

    def _ensure_initialized(self) -> 'None':
        """ Lazily initializes the embedding model and pre-computes guidance vectors.
        """
        if self._initialized:
            return

        logger.info('Initializing guidance selector with fastembed')
        self.model = TextEmbedding('BAAI/bge-small-en-v1.5')
        self.guidance_vectors = list(self.model.embed(guidance_snippets))
        self._initialized = True
        logger.info('Guidance selector initialized with %d snippets', len(guidance_snippets))

# ################################################################################################################################

    def select_guidance(self, user_message:'str', top_k:'int'=2, threshold:'float'=0.60) -> 'anylist':
        """ Selects the top_k most relevant guidance snippets for the given user message.
        Only includes snippets with similarity above the threshold.
        """
        self._ensure_initialized()

        user_vector = list(self.model.embed([user_message]))[0]

        similarities = []
        for i, gv in enumerate(self.guidance_vectors):
            similarity = float(user_vector @ gv)
            similarities.append((i, similarity))

        similarities.sort(key=itemgetter(1), reverse=True)

        out = []
        for i, score in similarities[:top_k]:
            if score >= threshold:
                out.append(guidance_snippets[i])

        logger.info('Selected guidance for message: %s -> %s', user_message[:50], out)

        return out

# ################################################################################################################################
# ################################################################################################################################

_guidance_selector = None

def get_guidance_selector() -> 'GuidanceSelector':
    """ Returns the singleton guidance selector instance.
    """
    global _guidance_selector
    if _guidance_selector is None:
        _guidance_selector = GuidanceSelector()
    return _guidance_selector

# ################################################################################################################################

def select_guidance_for_message(user_message:'str', top_k:'int'=2) -> 'str':
    """ Convenience function to select guidance and format it for injection.
    """
    selector = get_guidance_selector()
    snippets = selector.select_guidance(user_message, top_k)

    if not snippets:
        return ''

    out = '[Guidance: ' + '; '.join(snippets) + ']'
    return out

# ################################################################################################################################
# ################################################################################################################################
