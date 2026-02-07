import json
import urllib.request
import os

ENDPOINT = "https://voiceassistantnsxsctbdhw-voice-assistant.functions.fnc.fr-par.scw.cloud/"
TOKEN = "c6504938-090c-482d-88ec-5573427303f2"

def send_command(transcript):
    print(f"Testing transcript: '{transcript}'")
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': TOKEN
    }
    data = json.dumps({'transcript': transcript}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            print(f"Status: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("--- Testing NOTE intent ---")
    send_command("Take a note that the secret code for the vault is 9988.")
    
    print("\n--- Testing TRANSPORT intent ---")
    send_command("How do I get to Helsinki-Vantaa Airport by train?")

    print("\n--- Testing Finnish NOTE intent ---")
    send_command("Kirjoita muistiinpano että saunan lämpötila on 80 astetta.")
