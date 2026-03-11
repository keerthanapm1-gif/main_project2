import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()
from django.template import Template, Engine

try:
    Template('{% if query %}Search Results for "{{ query }}"{% else %}All Available Properties{% endif %}', engine=Engine.get_default())
    print('Inline SUCCESS')
except Exception as e:
    print('Inline FAILED', e)
