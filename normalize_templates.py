import os
import re

def normalize_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Rule 1: Find all {% ... %} tags and ensure they are on a single line, 
    # and have single spaces around the content.
    def clean_block_tag(match):
        inner = match.group(1)
        # Replace all internal whitespace (newlines, multiple spaces) with a single space
        inner = ' '.join(inner.split())
        return '{% ' + inner + ' %}'

    # Rule 2: same for {{ ... }} tags
    def clean_variable_tag(match):
        inner = match.group(1)
        inner = ' '.join(inner.split())
        return '{{ ' + inner + ' }}'

    # We need to be careful with regex because tags can be nested (rare but possible in some engines, 
    # but Django usually doesn't nest {% ... %} inside each other, though it can have {{ }} inside some logic).
    # But for Luxia, simple regex should work.
    
    # We use a non-greedy match that stops at the first %} or }}
    content = re.sub(r'\{%(.*?)%\}', clean_block_tag, content, flags=re.DOTALL)
    content = re.sub(r'\{\{(.*?)\}\}', clean_variable_tag, content, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Normalized {path}")

templates_dir = 'templates'
for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        normalize_template(os.path.join(templates_dir, filename))
