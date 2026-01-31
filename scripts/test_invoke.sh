#!/bin/bash

# Get the function endpoint from OpenTofu
ENDPOINT=$(tofu output -raw function_endpoint)

if [ -z "$ENDPOINT" ]; then
  echo "Error: Could not get function endpoint. Have you run 'tofu apply'?"
  exit 1
fi

echo "Invoking function at: https://$ENDPOINT"

# Test Payload (from file)
PAYLOAD_FILE="scripts/payload.json"
if [ -f "$PAYLOAD_FILE" ]; then
  echo "Using payload from $PAYLOAD_FILE"
  # Use @ syntax for curl to read from file
  curl -X POST "https://$ENDPOINT" \
       -H "Content-Type: application/json" \
       -d "@$PAYLOAD_FILE"
else
  echo "Error: $PAYLOAD_FILE not found."
  exit 1
fi

echo -e "\n\nDone."
