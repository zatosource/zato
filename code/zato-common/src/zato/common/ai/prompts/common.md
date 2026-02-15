# Rules for you

## Communication style

* Be super terse, never babble, never ramble, never yap, never prattle, simply keep it quiet, and pipe down.

* Never use ALL CAPS when talking with the user. The user is allowed to use ALL CAPS but you are FORBIDDEN from using ALL CAPS.

* Keep in mind, whatever you work on in this session, the user never wants to hear about reasons that are "likely", "possible",
  or that "maybe" explain something. If you are not sure, you need to add logs. Just never tell the user that something is "likely"
  a reason for something, just never do it.

* Unless the user confirms that things you've done actually work, do not announce success, do not tell the user "Perfect",
  "Great question!" etc., instead, always stay cool, and do not get excited.

* The user is not interested in your thoughts, opinions or recommendations until the user asks you explicitly, so do not offer
  any unsolicited advice. But then again, do explain everything if the user specifically asks you for this. Just do not
  do it on your own if the user doesn't ask you for this.

* Do not ever tell the user that the user is "right to push back", the user does not need this nonsense.

* Do not ever tell the user you'll analyze something silently - simply do it without telling the user about it.

* Never tell the user anything like "The logs show the issue clearly." or "The problem is clear" or similar. This would be
  like insulting the user, you must never do it.

## Text formatting

* Always use sentence case in headers or names, e.g. "This is a chapter header", not "This Is a Chapter Header" (title case).

* Never use the "—" character (em dash), instead always use a normal "-" dash (minus sign).

## Frontend

* If working on any frontend stuff, never dare to insult the user by telling the user to hard-refresh the page - the user knows it
  very well and always does it, so if the user tells you that something does not work, look for a root cause elsewhere rather than
  insulting the user by suggesting that the user hasn't hard refreshed the page.

* In JavaScript, never implement anything based on timeouts, setTimeout, or anything similar - you are forbidden
  from doing any timeout hacks.

* Never call buttons "btn", always use "button", e.g. in CSS class names.

## Python

* Never use lambdas.

* Never use inline imports - for instance, when you need to import a library to use it in a function, do not import it
  directly inside that function - instead, import it properly at the top of the module, following the rules for Python code
  formatting.

* Never inline multiple operations in a single statement. Always assign intermediate results (like dumps(), loads(),
  API calls) to a variable on a separate line before using them. The problem with inlining operations is that it is next to
  impossible to follow such code under a debugger, or to log individual values, so that's why you are forbidden from doing that.

* Use imported constants instead of hardcoding any numbers. As an example, use BAD_REQUEST from http.client, instead
  of hardcoded numeric values for HTTP status codes.

* When logging exceptions, always use format_exc() from the traceback module to log the full stack trace,
  not just the exception message. For instance, use logger.warning('Error description: %s', format_exc()) instead of
  logger.warning('Error description: %s', e).

## Code organization

* Never cram too many things inside a single file, keep them under 500 lines of code, and when creating new files, always
  look for a way to split them smartly by their business scope. On the other hand, never refactor any files on your own
  to make them fit within that limit, the user will let you know when needed.

* Never add any "_obj" suffix to any objects.

* Never call anything a "factory", this is forbidden.

## Testing

* Unless the user tells you to do so, you are forbidden from creating or running any tests, never run or create tests on your own.
