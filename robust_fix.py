import os
import re

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Add spaces around == if they are missing
    # Pattern: {{ something==something }} or {% if something=="something" %}
    # We look for == inside {% ... %} and {{ ... }}
    
    def add_spaces(match):
        tag_content = match.group(1)
        # Add spaces around == if not present
        # But be careful not to break already spaced ones
        fixed = re.sub(r'([^ ])==', r'\1 ==', tag_content)
        fixed = re.sub(r'==([^ ])', r'== \1', fixed)
        return match.group(0).replace(tag_content, fixed)

    content = re.sub(r'\{% (.*?) %\}', add_spaces, content, flags=re.DOTALL)
    content = re.sub(r'\{\{ (.*?) \}\}', add_spaces, content, flags=re.DOTALL)

    # Fix 2: Remove newlines inside {% ... %} tags that cause issues
    def remove_newlines(match):
        return match.group(0).replace('\n', ' ').replace('\r', ' ')

    content = re.sub(r'\{% (.*?) %\}', remove_newlines, content, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {path}")

templates_dir = 'templates'
for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        fix_file(os.path.join(templates_dir, filename))
