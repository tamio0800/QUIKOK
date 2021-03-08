"""
ASGI config for Quikok project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import get_default_application
#from django.conf import settings
#from django.core.asgi import get_asgi_application
if os.environ.get('DEV_MODE', False) == 'true':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quikok.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quikok.settings_for_production')
django.setup()
#application = get_asgi_application()
application = get_default_application()