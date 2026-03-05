import urllib.request
import re
try:
    urllib.request.urlopen('http://127.0.0.1:8000/properties/')
    print('SUCCESS')
except Exception as e:
    html = e.read().decode('utf-8')
    match = re.search(r'<pre class="exception_value">(.*?)</pre>', html, re.DOTALL)
    if match:
        val = match.group(1).strip()
        print('EXCEPTION:', val)
    
    # Also find the traceback frame if possible
    frames = re.findall(r'<div class="commands">(.*?)</div>', html, re.DOTALL)
    for frame in frames:
        if 'properties.html' in frame:
            print("FRAME INVOLVED:", frame[:500])
