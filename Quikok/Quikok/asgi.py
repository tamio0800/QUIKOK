"""
ASGI config for Quikok project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""
from django.conf import settings
import os

from django.core.asgi import get_asgi_application

if settings.DEV_MODE == False:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quikok.settings_for_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quikok.settings')

application = get_asgi_application()
