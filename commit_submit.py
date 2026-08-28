import urllib.request
try:
    req = urllib.request.Request('http://localhost:8000/submit', method='POST')
    response = urllib.request.urlopen(req)
except Exception as e:
    pass
