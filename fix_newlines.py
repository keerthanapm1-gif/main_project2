import re

filepath = r"c:\project2\main_project2\templates\properties.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix multi-line tags using regex
# We want to replace newlines inside {% ... %} with a space.
# It's tricky with regex, so we'll do it iteratively or with a function.

def remove_newlines_in_tags(match):
    return match.group(0).replace('\n', ' ').replace('\r', ' ')

content = re.sub(r'\{%[^%]*%\}', remove_newlines_in_tags, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("FIXED NEWLINES IN TAGS")
