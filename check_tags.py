import re

def trace_tags(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    tags = re.findall(r'\{%(.*?)%\}', content)
    stack = []
    
    for tag in tags:
        tag_content = tag.strip().split()
        if not tag_content:
            continue
            
        cmd = tag_content[0]
        
        if cmd == 'if':
            stack.append(cmd)
            print(f"PUSH: {cmd} (Stack: {len(stack)}) - Full tag: {tag.strip()}")
        elif cmd == 'for':
            stack.append(cmd)
            print(f"PUSH: {cmd} (Stack: {len(stack)}) - Full tag: {tag.strip()}")
        elif cmd == 'block':
            stack.append(cmd)
            print(f"PUSH: {cmd} (Stack: {len(stack)}) - Full tag: {tag.strip()}")
        elif cmd == 'endif':
            if not stack or stack[-1] != 'if':
                print(f"ERROR: Found endif but stack is {stack}")
            else:
                stack.pop()
                print(f"POP: {cmd} (Stack: {len(stack)})")
        elif cmd == 'endfor':
            if not stack or stack[-1] != 'for':
                print(f"ERROR: Found endfor but stack is {stack}")
            else:
                stack.pop()
                print(f"POP: {cmd} (Stack: {len(stack)})")
        elif cmd == 'endblock':
            if not stack or stack[-1] != 'block':
                print(f"ERROR: Found endblock but stack is {stack}")
            else:
                stack.pop()
                print(f"POP: {cmd} (Stack: {len(stack)})")

trace_tags('templates/properties.html')
