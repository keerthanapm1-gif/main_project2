import re

filepath = 'c:/project2/main_project2/templates/properties.html'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Find any current_filters.something==value and add spaces
text = re.sub(r'(current_filters\.[a-z_]+)==([\'\"]?[a-zA-Z_]+[\'\"]?)', r'\1 == \2', text)
text = re.sub(r'(current_filters\.[a-z_]+)==\'\'', r'\1 == \'\'', text)
text = re.sub(r'(current_filters\.[a-z_]+)==""', r'\1 == ""', text)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement script executed.")
