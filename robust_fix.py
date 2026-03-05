import re

path = r'c:\project2\main_project2\templates\properties.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Completely clean any bad states for those variables
fixes = [
    # Clean out any backslashes just in case
    (r"\\'house\\'", "'house'"),
    (r"\\'apartment\\'", "'apartment'"),
    (r"\\'plot\\'", "'plot'"),
    (r"\\'commercial\\'", "'commercial'"),
    (r"\\'pg\\'", "'pg'"),
    (r"\\'available\\'", "'available'"),
    (r"\\'newest\\'", "'newest'"),
    (r"\\'price_low\\'", "'price_low'"),
    (r"\\'price_high\\'", "'price_high'"),
    (r"\\'popular\\'", "'popular'"),
    (r"\\'oldest\\'", "'oldest'"),
]
for bad, good in fixes:
    content = content.replace(bad, good)
    
# Now fix missing spaces by forcing them correctly. 
# We'll match with or without spaces, and with or without backslashes
content = re.sub(r"current_filters\.type\s*==\s*\\?'house\\?'", "current_filters.type == 'house'", content)
content = re.sub(r"current_filters\.type\s*==\s*\\?'apartment\\?'", "current_filters.type == 'apartment'", content)
content = re.sub(r"current_filters\.type\s*==\s*\\?'plot\\?'", "current_filters.type == 'plot'", content)
content = re.sub(r"current_filters\.type\s*==\s*\\?'commercial\\?'", "current_filters.type == 'commercial'", content)
content = re.sub(r"current_filters\.type\s*==\s*\\?'pg\\?'", "current_filters.type == 'pg'", content)
content = re.sub(r"current_filters\.status\s*==\s*\\?'available\\?'", "current_filters.status == 'available'", content)
content = re.sub(r"current_filters\.sort\s*==\s*\\?'newest\\?'", "current_filters.sort == 'newest'", content)
content = re.sub(r"current_filters\.sort\s*==\s*\\?'price_low\\?'", "current_filters.sort == 'price_low'", content)
content = re.sub(r"current_filters\.sort\s*==\s*\\?'price_high\\?'", "current_filters.sort == 'price_high'", content)
content = re.sub(r"current_filters\.sort\s*==\s*\\?'popular\\?'", "current_filters.sort == 'popular'", content)
content = re.sub(r"current_filters\.sort\s*==\s*\\?'oldest\\?'", "current_filters.sort == 'oldest'", content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex clean completed.")

