import os
import django
from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

def debug_template(name):
    template_path = os.path.join(settings.BASE_DIR, 'templates', name)
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        Template(content)
        print(f"{name} OK")
    except TemplateSyntaxError as e:
        print(f"{name} ERROR: {e}")
        # Try to find the line
        lines = content.split('\n')
        for i in range(len(lines)):
            try:
                Template('\n'.join(lines[:i+1]))
            except TemplateSyntaxError:
                print(f"Likely error line {i+1}: {lines[i]}")
                break

if __name__ == "__main__":
    debug_template('home.html')
    debug_template('properties.html')
