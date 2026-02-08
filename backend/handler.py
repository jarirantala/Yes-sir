import json
import os
import logging
import database
import llm_service
import stt_service
import base64
import datetime
import pytz

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# URL Templates
GOOGLE_MAPS_TRANSIT_URL = "https://www.google.com/maps/dir/?api=1&destination={dest}&travelmode=transit"

def _parse_event_body(event):
    """
    Recovers and parses the request body, handling gateway-imposed base64 encoding.
    """
    body = event.get('body', {})
    is_base64 = event.get('isBase64Encoded', False)
    
    if isinstance(body, str) and body:
        if is_base64:
            try:
                body = base64.b64decode(body).decode('utf-8')
            except Exception as e:
                logger.warning(f"Failed to decode base64 body: {e}")
        
        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON body: {e}. Body start: {body[:100]}")
            return None
    
    return body if isinstance(body, dict) else {}

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

def handler(event, context):
    if not event:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No event data'})}

    method = event.get('httpMethod', 'POST')
    
    # Handle DELETE for cleanup
    if method == 'DELETE':
        body = _parse_event_body(event)
        item_id = body.get('id')
        item_type = body.get('type')
        
        if not item_id or not item_type:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing id or type for deletion'})}
            
        success = False
        if item_type == 'todo':
            success = database.delete_todo_item(item_id)
        elif item_type == 'note':
            success = database.delete_note_item(item_id)
            
        return {
            'statusCode': 200 if success else 404,
            'body': json.dumps({'success': success, 'message': 'Item deleted' if success else 'Item not found'})
        }

    # Handle GET for listing
    if method == 'GET':
        params = event.get('queryStringParameters', {})
        action = params.get('action')
        item_type = params.get('type')
        
        if action == 'list':
            if item_type == 'todo':
                items = database.get_all_todos()
                return {'statusCode': 200, 'body': json.dumps({'status': 'success', 'type': 'todo_list', 'data': items})}
            elif item_type == 'note':
                items = database.get_all_notes()
                return {'statusCode': 200, 'body': json.dumps({'status': 'success', 'type': 'note_list', 'data': items})}
            
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid GET request parameters'})}

    try:
        headers = event.get('headers', {})
        content_type = next((v for k, v in headers.items() if k.lower() == 'content-type'), 'application/json')
        
        # 1. Handle Direct Audio Upload (Raw Binary)
        if content_type.startswith('audio/'):
            is_base64 = event.get('isBase64Encoded', False)
            audio_data = event.get('body')
            if not audio_data:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing audio data'})}
            if is_base64:
                audio_data = base64.b64decode(audio_data)
            return stt_service.handle_speech_to_text(audio_data, content_type)

        # 2. Parse JSON Body (for text commands or base64 audio)
        body = _parse_event_body(event)
        if body is None:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON body'})}

        # 3. Handle Base64 Audio in JSON
        if body.get('audio_base64'):
            try:
                audio_data = base64.b64decode(body['audio_base64'])
                return stt_service.handle_speech_to_text(audio_data, body.get('content_type', 'audio/wav'))
            except Exception as e:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid base64 audio', 'details': str(e)})}

        # 4. Handle Text Command (Transcript)
        transcript = body.get('transcript')
        if not transcript:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing transcript'})}

        timezone = body.get('timezone', 'UTC')
        email = body.get('email') or os.environ.get('RECIPIENT_EMAIL') or os.environ.get('SENDER_EMAIL')

        # Generate current time for the prompt
        try:
            tz = pytz.timezone(timezone)
        except:
            tz = pytz.UTC
        current_time_iso = datetime.datetime.now(tz).isoformat()
        
        logger.info(f"Analyzing transcript: '{transcript}' in timezone {timezone}")
        parsed_data = llm_service.analyze_transcript(transcript, current_time_iso)
        intent = parsed_data.get('intent', 'TODO')
        logger.info(f"Extracted Intent: {intent}")
        
        if intent == "MEETING":
            if not email:
                return {'statusCode': 500, 'body': json.dumps({'error': 'Recipient email not configured'})}
            return handle_meeting(parsed_data, email, timezone)
        
        if intent == "NOTE":
            return handle_note(parsed_data)
            
        if intent == "TRANSPORT":
            dest = parsed_data.get('destination', 'Unknown')
            import urllib.parse
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
        
        return handle_todo(parsed_data)

    except Exception as e:
        logger.error(f"Handler Error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

