import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()
from django.template import Template, Context
try:
    Template('{% with room_id=request.user.id|stringformat:"s"|add:"_"|add:other_user.id|stringformat:"s" %}{% endwith %}')
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
