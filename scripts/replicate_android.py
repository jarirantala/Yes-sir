import urllib.request
import json
import base64
import os

URL = "https://voiceassistantnsxsctbdhw-voice-assistant.functions.fnc.fr-par.scw.cloud/"
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBsaWNhdGlvbl9jbGFpbSI6W3sibmFtZXNwYWNlX2lkIjoiMzBhNWE3MTUtNjY5Yi00M2RiLWE2YTctYzA2ODdlM2Q5Yzg5IiwiYXBwbGljYXRpb25faWQiOiIzNGE2MGZlNi1hYTUzLTRmY2QtYTdlMC0yNGRkMWU5MzYzNjMifV0sInZlcnNpb24iOjIsImF1ZCI6ImZ1bmN0aW9ucyIsImp0aSI6ImNkY2Q4YzQxLTIzZjItNGNjOC05ZTQ2LTQxODFhYzA1NDk2YiIsImlhdCI6MTczODgzNjAxMCwiaXNzIjoiU0NBTEVXQVkiLCJuYmYiOjE3Mzg4MzYwMTAsInN1YiI6InRva2VuIn0.t-F_kF4Lh-64nI6i9nZ8aJ6XyO4j-V_5zB5e1e1r7y7_X7c4z2t9tD3t_X8zD5q2c3v4x6p9_L5z7v4c4r5t8e2w9q7_L5z7v4c4r5t8e2w9q7"

def replicate_android_upload():
    audio_path = "spoken-test.wav"
    if not os.path.exists(audio_path):
        print(f"Error: {audio_path} not found")
        return

    with open(audio_path, "rb") as f:
        audio_data = f.read()
    
    # Android uses Base64.NO_WRAP
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    payload = {
        "audio_base64": audio_base64,
        "content_type": "audio/wav"
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    print(f"Sending {len(data)} bytes to {URL}")
    
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Auth-Token", TOKEN)
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.getcode()}")
            print(f"Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} {e.reason}")
        print(f"Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    replicate_android_upload()
