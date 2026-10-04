import requests
import os

url = "https://api.murf.ai/v1/speech/voices?model=FALCON"

headers = {
    "api-key": "ap2_65861558-a5b8-4959-9f7f-9b620901b1b1"
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)