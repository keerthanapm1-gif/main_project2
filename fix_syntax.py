import re

file_path = 'c:/project2/main_project2/templates/properties.html'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix current_filters.type=='house' etc.
text = re.sub(r"current_filters\.([a-z_]+)==([\'\"])", r"current_filters.\1 == \2", text)
text = re.sub(r"current_filters\.([a-z_]+)\s*==\s*([\'\"])", r"current_filters.\1 == \2", text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Replaced syntax successfully.")
