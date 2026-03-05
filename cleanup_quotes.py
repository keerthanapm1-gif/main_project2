import sys
f = r'c:\project2\main_project2\templates\properties.html'
with open(f, 'r', encoding='utf-8') as file:
    text = file.read()

text = text.replace("\\'", "'")

with open(f, 'w', encoding='utf-8') as file:
    file.write(text)
print("Finished cleaning up quotes.")
