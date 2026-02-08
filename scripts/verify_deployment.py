import sys
import subprocess
import json
import time
import urllib.request
import urllib.error

def get_terraform_output(output_name):
    try:
        # Try terraform first
        result = subprocess.run(['terraform', 'output', '-raw', output_name], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        # Try tofu
        result = subprocess.run(['tofu', 'output', '-raw', output_name], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error getting {output_name}: {e}")
    return None

def verify():
    endpoint = get_terraform_output('function_endpoint')
    token = get_terraform_output('function_token')
    
    if not endpoint or not token:
        print("Could not get endpoint/token. Terraform state might be locked or outputs missing.")
        # If running terraform apply, state is locked. We can't verify easily.
        return False

    url = f"https://{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": token
    }
    # Bad payload to trigger 400
    payload = {
        "type": "keyword",
        # Missing key/value
    }
    
    print(f"Checking URL: {url}")
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            print(f"Response status: {response.status}")
            response_body = response.read().decode('utf-8')
            print(f"Response body: {response_body}")
            # If 200 OK, something is wrong (expected 400)
            print("Unexpected success (200 OK). Expected 400.")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"Response status: {e.code}")
        response_body = e.read().decode('utf-8')
        print(f"Response body: {response_body}")
        
        if e.code == 400:
            try:
                body = json.loads(response_body)
                if 'received_body' in body:
                    print("SUCCESS: 400 response contains 'received_body'. New version is active!")
                    return True
                else:
                    print("FAILURE: 400 response does NOT contain 'received_body'. Old version still active.")
                    return False
            except json.JSONDecodeError:
                print("FAILURE: Response body is not JSON.")
                return False
        else:
            print(f"Unexpected status code: {e.code}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    if verify():
        sys.exit(0)
    else:
        sys.exit(1)
