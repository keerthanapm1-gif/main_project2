import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

from django.template.loader import render_to_string

try:
    render_to_string('properties.html')
    print("Success: Template properties.html rendered without syntax errors.")
except Exception as e:
    import traceback
    with open('error_out.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
