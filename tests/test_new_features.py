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

def delete_item(item_id, item_type):
    print(f"Cleaning up {item_type} ID: {item_id}")
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': TOKEN
    }
    data = json.dumps({'id': item_id, 'type': item_type}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=data, headers=headers, method="DELETE")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            print(f"Cleanup Status: {response.status} - {result.get('message')}")
            return result.get('success')
    except Exception as e:
        print(f"Cleanup Error: {e}")
        return False

if __name__ == "__main__":
    # 1. Test NOTE
    print("--- Testing NOTE intent ---")
    res = send_command("Take a note that the secret code for the vault is 9988.")
    if res and res.get('data', {}).get('id'):
        delete_item(res['data']['id'], 'note')
    
    # 2. Test TRANSPORT (No DB storage, no cleanup needed)
    print("\n--- Testing TRANSPORT intent ---")
    send_command("How do I get to Helsinki-Vantaa Airport by train?")

    # 3. Test Finnish NOTE
    print("\n--- Testing Finnish NOTE intent ---")
    res = send_command("Kirjoita muistiinpano että saunan lämpötila on 80 astetta.")
    if res and res.get('data', {}).get('id'):
        delete_item(res['data']['id'], 'note')
