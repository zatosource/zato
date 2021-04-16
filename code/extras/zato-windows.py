# -*- coding: utf-8 -*-

# Zato
from zato.cli.zato_command import main

if __name__ == '__main__':

    # stdlib
    import re
    import sys
    import os
    curdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(curdir ,"Lib", "site-packages"))

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())