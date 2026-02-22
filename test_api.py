import http.client
import json
import base64
conn = http.client.HTTPSConnection("esapi.ubu.ac.th")
payload = json.dumps({
"loginName": base64.b64encode("scwayopu".encode()).decode(),
})
headers = {
'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/student/reg-data", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))