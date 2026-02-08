import json
import logging
import database
import urllib.parse

logger = logging.getLogger()

GOOGLE_MAPS_TRANSIT_URL = "https://www.google.com/maps/dir/?api=1&destination={dest}&travelmode=transit"

def handle_meeting(parsed_data, email, timezone):
    # Mock meeting logic
    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 'meeting', 
            'message': 'Invite sent (MOCKED)', 
            'parsed_data': parsed_data,
            'data': {'messageId': 'mock-message-id'}
        })
    }

def handle_todo(parsed_data):
    try:
        item = database.save_todo_item(parsed_data.get('title', 'Untitled Task'), parsed_data.get('priority', 'medium'))
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 'todo', 'message': 'Task saved', 'parsed_data': parsed_data, 'data': item})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to save task', 'details': str(e)})}

def handle_note(parsed_data):
    try:
        item = database.save_note_item(parsed_data.get('title', ''))
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 'note', 'message': 'Note saved', 'parsed_data': parsed_data, 'data': item})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to save note', 'details': str(e)})}

def handle_transport(parsed_data):
    dest = parsed_data.get('destination', 'Unknown')
    encoded_dest = urllib.parse.quote_plus(dest)
    deeplink = GOOGLE_MAPS_TRANSIT_URL.format(dest=encoded_dest)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 'transport',
            'message': 'Directions ready',
            'parsed_data': parsed_data,
            'data': {
                'destination': dest,
                'deeplink': deeplink
            }
        })
    }

def dispatch_intent(intent, parsed_data, email=None, timezone=None):
    logger.info(f"Dispatching Intent: {intent}")
    
    if intent == "MEETING":
        if not email:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Recipient email not configured'})}
        return handle_meeting(parsed_data, email, timezone)
    
    if intent == "NOTE":
        return handle_note(parsed_data)
        
    if intent == "TRANSPORT":
        return handle_transport(parsed_data)
        
    # Default to TODO
    return handle_todo(parsed_data)
