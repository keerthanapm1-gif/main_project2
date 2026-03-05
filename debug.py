import urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:8000/properties/')
    print('SUCCESS')
except Exception as e:
    with open('error.html', 'wb') as f:
        f.write(e.read())
    print('ERROR HTML SAVED')
