import urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:5000/')
except Exception as e:
    with open('error_utf8.html', 'w', encoding='utf-8') as f:
        f.write(e.read().decode('utf-8'))
