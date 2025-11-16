import requests
import json

url = "https://mb26kncdfg.execute-api.us-east-1.amazonaws.com/dev/research"

payload = json.dumps({
  "topic": "AI In Healthcare"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
