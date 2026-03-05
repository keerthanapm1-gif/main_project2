import os
import django
import traceback
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

from django.template.loader import get_template

template_dir = r"c:\project2\main_project2\templates"
has_error = False

with open("template_errors_utf8.txt", "w", encoding="utf-8") as f:
    for filename in os.listdir(template_dir):
        if filename.endswith(".html"):
            try:
                get_template(filename)
                f.write(f"[OK]     {filename}\n")
            except Exception as e:
                f.write(f"[ERROR]  {filename}:\n")
                f.write(traceback.format_exc())
                has_error = True

sys.exit(1 if has_error else 0)
