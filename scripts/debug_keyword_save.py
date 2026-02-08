import sys
import os
import json
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Also add backend to path so 'import database' works inside handler.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from backend import handler

# Mock event
event = {
    'httpMethod': 'POST',
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps({
        'type': 'keyword',
        'key': 'gym',
        'value': '123 Fitness'
    })
}

# Run handler
response = handler.handler(event, None)
print(json.dumps(response, indent=2))
