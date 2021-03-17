"""
This module is a modified vendor copy of the Imbox package from https://pypi.org/project/imbox/

The MIT License (MIT)

Copyright (c) 2013 Martin Rusev

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from zato.common.ext.imbox.messages import Messages
from zato.common.ext.imbox.vendors.helpers import merge_two_dicts


class GmailMessages(Messages):
    authentication_error_message = ('If you\'re not using an app-specific password, grab one here: '
                                    'https://myaccount.google.com/apppasswords')
    hostname = 'imap.gmail.com'
    name = 'gmail'
    FOLDER_LOOKUP = {

        'all_mail': '"[Gmail]/All Mail"',
        'all': '"[Gmail]/All Mail"',
        'all mail': '"[Gmail]/All Mail"',
        'sent': '"[Gmail]/Sent Mail"',
        'sent mail': '"[Gmail]/Sent Mail"',
        'sent_mail': '"[Gmail]/Sent Mail"',
        'drafts': '"[Gmail]/Drafts"',
        'important': '"[Gmail]/Important"',
        'spam': '"[Gmail]/Spam"',
        'starred': '"[Gmail]/Starred"',
        'trash': '"[Gmail]/Trash"',
    }

    GMAIL_IMAP_ATTRIBUTE_LOOKUP_DIFF = {
        'subject': '(X-GM-RAW "subject:\'{}\'")',
        'label': '(X-GM-LABELS "{}")',
        'raw': '(X-GM-RAW "{}")'
    }

    def __init__(self,
                 connection,
                 parser_policy,
                 **kwargs):

        self.IMAP_ATTRIBUTE_LOOKUP = merge_two_dicts(self.IMAP_ATTRIBUTE_LOOKUP,
                                                     self.GMAIL_IMAP_ATTRIBUTE_LOOKUP_DIFF)

        super().__init__(connection, parser_policy, **kwargs)
