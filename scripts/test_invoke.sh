#!/bin/bash

# Get the function endpoint from OpenTofu
ENDPOINT=$(tofu output -raw function_endpoint)

if [ -z "$ENDPOINT" ]; then
  echo "Error: Could not get function endpoint. Have you run 'tofu apply'?"
  exit 1
fi

echo "Invoking function at: https://$ENDPOINT"

# Test Payload (Meeting Intent)
PAYLOAD='{
  "transcript": "Schedule a meeting with Team for tomorrow at 10 AM",
  "timezone": "Europe/Paris",
  "email": "test@example.com"
}'

curl -X POST "https://$ENDPOINT" \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD"

echo -e "\n\nDone."
