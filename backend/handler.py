import json
import os
import logging
import urllib.request
import urllib.error
import database
import llm_service
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def encode_multipart_formdata(fields, files):
    boundary = uuid.uuid4().hex.encode('utf-8')
    body = bytearray()
    
    for name, value in fields.items():
        body.extend(b'--' + boundary + b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode('utf-8'))
        body.extend(str(value).encode('utf-8'))
        body.extend(b'\r\n')
        
    for name, (filename, content, content_type) in files.items():
        body.extend(b'--' + boundary + b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
        if content_type:
            body.extend(f'Content-Type: {content_type}\r\n'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend(content)
        body.extend(b'\r\n')
        
    body.extend(b'--' + boundary + b'--\r\n')
    
    content_type_header = f'multipart/form-data; boundary={boundary.decode("utf-8")}'
    return bytes(body), content_type_header

def handle_speech_to_text(audio_data, content_type, is_base64=False):
    """
    Calls Scaleway's Speech-to-Text API (OpenAI compatible) to transcribe audio.
    """
    api_key = os.environ.get('SCALEWAY_API_KEY')
    api_url = os.environ.get('SCALEWAY_API_URL', 'https://api.scaleway.ai/v1/audio/transcriptions')

    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Scaleway API key not configured'})
        }

    # Robust audio data handling
    if isinstance(audio_data, str):
        logger.info(f"handle_speech_to_text: audio_data is string, is_base64={is_base64}")
        # If it's a string, it might be raw binary treated as a string OR already decoded base64
        # We try to recover it.
        try:
            # Try latin-1 first as it's 1:1 for 0-255
            audio_data = audio_data.encode('latin-1')
        except Exception as e:
            logger.warning(f"Failed latin-1 encoding, falling back to utf-8: {e}")
            audio_data = audio_data.encode('utf-8', errors='ignore')

    logger.info(f"STT: Audio size {len(audio_data)} bytes. Start: {audio_data[:20]!r}")

    # Prepare multipart data
    fields = {
        'model': os.environ.get('STT_MODEL', 'whisper-large-v3')
    }
    
    # Determine extension from content_type if possible
    ext = 'wav'
    lower_ct = content_type.lower()
    if 'mpeg' in lower_ct or 'mp3' in lower_ct: ext = 'mp3'
    elif 'ogg' in lower_ct: ext = 'ogg'
    elif 'm4a' in lower_ct: ext = 'm4a'
    elif 'flac' in lower_ct: ext = 'flac'
    
    files = {
        'file': (f'audio.{ext}', audio_data, content_type)
    }

    body = None
    debug_header = "N/A"
    try:
        body, content_type_header = encode_multipart_formdata(fields, files)
        
        # Log headers exactly as sent (first 1000 bytes should cover it)
        header_end = body.find(audio_data[:20]) if len(audio_data) > 20 else 500
        if header_end < 0: header_end = 500
        debug_header = body[:header_end].decode('utf-8', errors='replace')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': content_type_header
        }
        
        req = urllib.request.Request(api_url, data=body, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            
            return {
                'statusCode': 200,
                'body': json.dumps({'transcript': result.get('text')})
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"STT API Error: {e.code} {e.reason} Body: {error_body}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'STT_API_ERROR', 
                'details': f"{e.code} {e.reason}", 
                'upstream_error': error_body,
                'debug': {
                    'multipart_header': debug_header,
                    'audio_start': str(audio_data[:32]),
                    'audio_len': len(audio_data),
                    'content_type': content_type,
                    'is_base64_src': is_base64
                }
            })
        }
    except Exception as e:
        logger.error(f"STT Unexpected Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'STT_UNEXPECTED_ERROR', 'details': str(e)})
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
    
    # Case-insensitive header lookup
    content_type = next((v for k, v in headers.items() if k.lower() == 'content-type'), 'application/json')
    
    try:
        # 1. Handle Audio Upload (Speech-to-Text)
        if content_type.startswith('audio/') or content_type.startswith('multipart/form-data'): 
             # Note: Android might send multipart, but here we expect raw binary for simplicity OR handle existing logic
             # If Android sends raw binary with audio/x Header, we wrap it.
             # If Android sends multipart, we might need to parse it (complex). 
             # Current design assumes Android sends raw bytes with Content-Type: audio/mpeg
            
            if content_type.startswith('audio/'):
                is_base64 = event.get('isBase64Encoded', False)
                audio_data = event.get('body')
                if not audio_data:
                    return {'statusCode': 400, 'body': json.dumps({'error': 'Missing audio data in body'})}
                
                if is_base64:
                    import base64
                    audio_data = base64.b64decode(audio_data)
    
                return handle_speech_to_text(audio_data, content_type, is_base64=is_base64)

        # 2. Handle Text Command or Base64 Audio (Intent Recognition + Action)
        body = event.get('body', {})
        if isinstance(body, str):
            try:
                body = json.loads(body) if body.strip() else {}
            except json.JSONDecodeError as e:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON body'})}
        
        # Check for Base64 Audio in JSON
        audio_base64 = body.get('audio_base64')
        if audio_base64:
            import base64
            content_type = body.get('content_type', 'audio/wav')
            try:
                audio_data = base64.b64decode(audio_base64)
                return handle_speech_to_text(audio_data, content_type, is_base64=True)
            except Exception as e:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid base64 in audio_base64', 'details': str(e)})}

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

