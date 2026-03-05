import re

with open('c:/project2/main_project2/templates/properties.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all template tags
tokens = re.findall(r'{%\s*(if|for|empty|else|endif|endfor|block|endblock|extends)(?:\s+.*?)?\s*%}', text)

stack = []
for cmd in tokens:
    if cmd in ['if', 'for', 'block']:
        stack.append(cmd)
    elif cmd in ['endif', 'endfor', 'endblock']:
        if not stack:
            print(f"Error: {cmd} without start block")
            continue
        expected = {'endif': 'if', 'endfor': 'for', 'endblock': 'block'}[cmd]
        top = stack.pop()
        if top != expected:
            print(f"Error: Mismatched tag! Expected end{top}, got {cmd}")
    print(f"Parsed {cmd}, stack now: {stack}")

if stack:
    print("Error: Unclosed tags left in stack:", stack)
else:
    print("All balanced!")
