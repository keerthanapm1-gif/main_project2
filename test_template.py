import sys, os, django
sys.path.append('c:\\project2\\main_project2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()
from django.template.loader import render_to_string
try:
    render_to_string('properties.html')
    print('SUCCESS')
except Exception as e:
    import traceback
    with open('template_error_debug.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("Error saved to template_error_debug.txt")
