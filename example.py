"""
Example of calling api with request.
Expected output:
    {'code': 1, 'msg': 'crutch has not been registered'}
"""

import requests

payload = {
  "uuid": "testuuid123455",
  "status": "ok",
  "loc": {
    "latitude": 23.1914,
    "longitude": -13.1283
  }
}

r = requests.post(url="http://127.0.0.1:8000/demoboard/heartbeat", json=payload)

if r.ok:
    print(r.json())
else:
    print(f"Server internal error: {r.status_code}")