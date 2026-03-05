import re

try:
    with open('error.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<pre class="exception_value">(.*?)</pre>', html, re.DOTALL)
    if match:
        print("EXCEPTION:", match.group(1).strip())
    
    # Try to extract the template line that failed
    match_line = re.search(r'<div class="commands">(.*?)</pre>', html, re.DOTALL)
    if match_line:
        # Just grab the text that looks like a line number and code
        lines = re.findall(r'<span class="lineno">(.*?)</span>(.*?)<', match_line.group(1))
        for ln, code in lines:
            print(f"Line {ln}: {code.strip()}")
            
except Exception as e:
    print("Error reading HTML:", e)
