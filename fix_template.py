import os

filepath = r"c:\project2\main_project2\templates\properties.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix type
content = content.replace("current_filters.type=='house'", "current_filters.type == 'house'")
content = content.replace("current_filters.type=='apartment'", "current_filters.type == 'apartment'")
content = content.replace("current_filters.type=='plot'", "current_filters.type == 'plot'")
content = content.replace("current_filters.type=='commercial'", "current_filters.type == 'commercial'")
content = content.replace("current_filters.type=='pg'", "current_filters.type == 'pg'")

# Fix status
content = content.replace("current_filters.status=='available'", "current_filters.status == 'available'")

# Fix sort
content = content.replace("current_filters.sort=='newest'", "current_filters.sort == 'newest'")
content = content.replace("current_filters.sort=='price_low'", "current_filters.sort == 'price_low'")
content = content.replace("current_filters.sort=='price_high'", "current_filters.sort == 'price_high'")
content = content.replace("current_filters.sort=='popular'", "current_filters.sort == 'popular'")
content = content.replace("current_filters.sort=='oldest'", "current_filters.sort == 'oldest'")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("FIXED properties.html")
