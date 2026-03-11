import sys, os, django
sys.path.append('c:\\project2\\main_project2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

from django.template import Template, Engine

with open('templates/properties.html', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    engine = Engine.get_default()
    template = Template(content, engine=engine)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
