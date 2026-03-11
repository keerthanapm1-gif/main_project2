"""
Script to fix all 3 template syntax errors:
1. home.html: split endif across two lines
2. properties.html: split if tags across two lines (bhk radio buttons)
3. loan_eligibility.html: == without spaces + split if for 20yrs option
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ─── 1. Fix home.html ────────────────────────────────────────────────────────
path = os.path.join(BASE, 'templates', 'home.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split {% endif %} across lines
old_split = '{% else %}25{% endif\n            %}+'
new_single = '{% else %}25{% endif %}+'
content = content.replace(old_split, new_single)

# Windows line endings version
old_split_crlf = '{% else %}25{% endif\r\n            %}+'
content = content.replace(old_split_crlf, new_single)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('home.html: fixed')

# ─── 2. Fix properties.html ──────────────────────────────────────────────────
path = os.path.join(BASE, 'templates', 'properties.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all 3 split {% if %} across lines  (handle both \n and \r\n)
import re

# Pattern: {% if request.GET.bhk=='N'\n                                %}checked{% endif %}
for val in ['1', '2', '3']:
    pattern = r"\{%\s*if request\.GET\.bhk=='" + val + r"'\s*\n\s*%\}checked\{%\s*endif\s*%\}"
    replacement = "{{% if request.GET.bhk == '{v}' %}}checked{{% endif %}}".format(v=val)
    # Use re.sub with re.MULTILINE
    content = re.sub(pattern, replacement, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('properties.html: fixed')

# ─── 3. Fix loan_eligibility.html ────────────────────────────────────────────
path = os.path.join(BASE, 'templates', 'loan_eligibility.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix missing spaces around == for all tenure year values
for yr in ['5', '10', '15', '20', '25', '30']:
    content = content.replace(
        'tenure_years=="' + yr + '"',
        'tenure_years == "' + yr + '"'
    )

# Fix split-line if for 20 Years option (both \n and \r\n)
for nl in ['\n', '\r\n']:
    content = content.replace(
        'tenure_years == "20"' + nl + '                            %}selected',
        'tenure_years == "20" %}selected'
    )

# Also fix split filter version if it somehow still exists
if '|split:' in content:
    content = re.sub(
        r'\{%\s*for y in.*?split.*?%\}.*?\{%\s*endfor\s*%\}',
        '''<option value="5">5 Years</option>
                        <option value="10">10 Years</option>
                        <option value="15">15 Years</option>
                        <option value="20" selected>20 Years (Popular)</option>
                        <option value="25">25 Years</option>
                        <option value="30">30 Years</option>''',
        content, flags=re.DOTALL
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('loan_eligibility.html: fixed')

print('\nAll done. Run: python manage.py check')
