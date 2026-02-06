import json
import os
import logging
import database
import llm_service
import stt_service
import base64

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def handler(event, context):
    if not event:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No event data'})}

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

        parsed_data = llm_service.analyze_transcript(transcript, timezone)
        intent = parsed_data.get('intent', 'TODO')
        
        if intent == "MEETING":
            if not email:
                return {'statusCode': 500, 'body': json.dumps({'error': 'Recipient email not configured'})}
            return handle_meeting(parsed_data, email, timezone)
        
        return handle_todo(parsed_data)

    except Exception as e:
        logger.error(f"Handler Error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

