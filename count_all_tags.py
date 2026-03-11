import re

def count_all_tags(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tags = ['if', 'endif', 'for', 'endfor', 'block', 'endblock', 'else', 'empty']
    counts = {t: len(re.findall(r'\{%\s*' + t + r'\b', content)) for t in tags}
    
    print(f"File: {filename}")
    for t, c in counts.items():
        print(f"{t.upper()}: {c}")
    
    if counts['if'] != counts['endif']:
        print("!!! IF/ENDIF UNBALANCED")
    if counts['for'] != counts['endfor']:
        print("!!! FOR/ENDFOR UNBALANCED")
    if counts['block'] != counts['endblock']:
        print("!!! BLOCK/ENDBLOCK UNBALANCED")

if __name__ == "__main__":
    count_all_tags('templates/home.html')
    count_all_tags('templates/properties.html')
    count_all_tags('templates/base.html')
