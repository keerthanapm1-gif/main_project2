import os
import django
from django.conf import settings
from django.template import loader, TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

try:
    loader.get_template('properties.html')
    print("properties.html OK")
except TemplateSyntaxError as e:
    print(f"properties.html ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
