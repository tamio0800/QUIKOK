# custom_exception_reporter.py
#
from django.views import debug
from django import template

TECHNICAL_500_TEXT_TEMPLATE = """ 
# custom template here, copy the original and make adjustments 
"""

class CustomExceptionReporter(debug.ExceptionReporter):
    def get_traceback_text(self):
        t = debug.DEBUG_ENGINE.from_string(TECHNICAL_500_TEXT_TEMPLATE)
        c = template.Context(self.get_traceback_data(), autoescape=False, use_l10n=False)
        return t.render(c)