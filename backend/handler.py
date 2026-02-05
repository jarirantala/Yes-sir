import json
import os
import logging
import requests
import database
import llm_service

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_speech_to_text(audio_data, content_type):
    """
    Calls Scaleway's Speech-to-Text API to transcribe audio.
    """
    api_key = os.environ.get('SCALEWAY_API_KEY')
    api_url = os.environ.get('SCALEWAY_API_URL', 'https://api.scaleway.com/speech-to-text/v1/transcriptions')

    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Scaleway API key not configured'})
        }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': content_type
    }

    try:
        response = requests.post(api_url, headers=headers, data=audio_data)
        response.raise_for_status()
        
        transcription = response.json()
        
        return {
            'statusCode': 200,
            'body': json.dumps({'transcript': transcription.get('text')})
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Scaleway API Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to call Speech-to-Text API', 'details': str(e)})
        }

def handle_meeting(parsed_data, email, timezone):
    # Mock meeting logic
    # In a real app, this would use icalendar to generate an event and send email via Scaleway TEM
    
    success = True
    result = "mock-message-id"
    
    if success:
         return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 'meeting', 
                'message': 'Invite sent (MOCKED)', 
                'parsed_data': parsed_data,
                'data': {'messageId': result}
            })
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to send email', 'details': result})
        }

def handle_todo(parsed_data):
    try:
        text = parsed_data.get('title', 'Untitled Task')
        priority = parsed_data.get('priority', 'medium')
        
        item = database.save_todo_item(text, priority)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 'todo', 
                'message': 'Task saved', 
                'parsed_data': parsed_data,
                'data': item
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to save task', 'details': str(e)})
        }

def handler(event, context):
    """
    Scaleway Function Entry Point.
    """
    if not event:
        logger.info("Event is None or empty")
        return {'statusCode': 400, 'body': json.dumps({'error': 'No event data'})}

    logger.info(f"Event keys: {list(event.keys())}")
    headers = event.get('headers', {})
    content_type = headers.get('content-type', 'application/json')
    
    try:
        # 1. Handle Audio Upload (Speech-to-Text)
        if content_type.startswith('audio/'):
            audio_data = event.get('body')
            if not audio_data:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing audio data in body'})}
            
            if event.get('isBase64Encoded', False):
                import base64
                audio_data = base64.b64decode(audio_data)

            return handle_speech_to_text(audio_data, content_type)

        # 2. Handle Text Command (Intent Recognition + Action)
        body = event.get('body', {})
        if isinstance(body, str):
            try:
                body = json.loads(body) if body.strip() else {}
            except json.JSONDecodeError as e:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON body'})}
        
        transcript = body.get('transcript')
        timezone = body.get('timezone', 'UTC')
        email = body.get('email') or os.environ.get('RECIPIENT_EMAIL')

        if not transcript:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing transcript in JSON body'})}

        # Analyze Intent via Mistral
        parsed_data = llm_service.analyze_transcript(transcript, timezone)
        intent = parsed_data.get('intent', 'TODO')
        
        logger.info(f"Intent classified as: {intent}")
        
        if intent == "MEETING":
            if not email:
                return {'statusCode': 500, 'body': json.dumps({'error': 'Recipient email not configured'})}
            return handle_meeting(parsed_data, email, timezone)
        else:
            return handle_todo(parsed_data)

    except Exception as e:
        logger.error(f"Handler Unexpected Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
