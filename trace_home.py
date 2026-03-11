import re

def trace_tags(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if_stack = []
    for i, line in enumerate(lines):
        line_num = i + 1
        # Find matches for if, else, endif
        ifs = re.findall(r'\{%\s*if\b', line)
        endifs = re.findall(r'\{%\s*endif\b', line)
        
        for _ in ifs:
            if_stack.append(line_num)
        for _ in endifs:
            if if_stack:
                if_stack.pop()
            else:
                print(f"STRAY ENDIF on line {line_num}")
                
        if i == 134: # Check just before line 135 (endblock)
            print(f"Stack size at line 135: {len(if_stack)}")
            if if_stack:
                print(f"Unclosed IFs from lines: {if_stack}")

if __name__ == "__main__":
    trace_tags('templates/home.html')
