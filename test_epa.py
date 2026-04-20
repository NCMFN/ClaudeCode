import urllib.request
import json
try:
    url = "https://data.epa.gov/efservice/SEMS_ACTIVE_SITES/ROWS/0:100/JSON"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print("EPA SEMS_ACTIVE_SITES length:", len(data))
except Exception as e:
    print("EPA SEMS_ACTIVE_SITES Error:", e)
