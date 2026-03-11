import re

def count_tags(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if_count = len(re.findall(r'\{%\s*if\b', content))
    else_count = len(re.findall(r'\{%\s*else\b', content))
    endif_count = len(re.findall(r'\{%\s*endif\b', content))
    for_count = len(re.findall(r'\{%\s*for\b', content))
    endfor_count = len(re.findall(r'\{%\s*endfor\b', content))
    
    print(f"File: {filename}")
    print(f"IF: {if_count}, ELSE: {else_count}, ENDIF: {endif_count}")
    print(f"FOR: {for_count}, ENDFOR: {endfor_count}")
    
    if if_count != endif_count:
        print("!!! IF/ENDIF UNBALANCED")
    if for_count != endfor_count:
        print("!!! FOR/ENDFOR UNBALANCED")

if __name__ == "__main__":
    count_tags('templates/home.html')
    count_tags('templates/properties.html')
