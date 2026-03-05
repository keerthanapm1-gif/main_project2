import urllib.request

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/properties/')
    print("Success:", response.status)
except Exception as e:
    print("Error:", e)
    with open('real_error.html', 'w', encoding='utf-8') as f:
        f.write(e.read().decode('utf-8'))
