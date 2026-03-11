import os
import django
from django.conf import settings
from django.template import loader, TemplateDoesNotExist, TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

def check_templates():
    template_dir = os.path.join(settings.BASE_DIR, 'templates')
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_path = os.path.join(root, file)
                relative_path = os.path.relpath(template_path, template_dir)
                try:
                    loader.get_template(relative_path)
                    print(f"OK: {relative_path}")
                except TemplateSyntaxError as e:
                    print(f"ERROR: {relative_path}")
                    import traceback
                    traceback.print_exc()
                except TemplateDoesNotExist:
                    print(f"NOT FOUND: {relative_path}")
                except Exception as e:
                    print(f"OTHER ERROR: {relative_path}")
                    import traceback
                    traceback.print_exc()

if __name__ == "__main__":
    check_templates()
