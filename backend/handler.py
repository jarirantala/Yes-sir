import json
import os
import logging
import datetime
import uuid
import pymongo
import requests
# from utils.parser import extract_meeting_details
# from utils.emailer import send_email

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# MongoDB Client (Global to reuse across invocations)
client = None

def get_mongo_collection():
    global client
    if not client:
        user = os.environ.get('MONGO_USERNAME')
        password = os.environ.get('MONGO_PASSWORD')
        db_name = os.environ.get('MONGO_DB_NAME', 'voice_assistant')
        
        instance_id = os.environ.get('MONGO_INSTANCE_ID')
        private_network_id = os.environ.get('MONGO_PRIVATE_NETWORK_ID')
        cert_file = os.environ.get('MONGO_TLS_CERT_FILE', 'cert.pem')
        
        # If running in Scaleway Function, cert.pem should be in root (./cert.pem) or backend/cert.pem depending on deployment structure.
        # Assuming it is packaged at root of function zip.
        if not os.path.exists(cert_file):
             # Fallback to absolute path or relative path if needed
             cert_file = os.path.join(os.path.dirname(__file__), cert_file)

        if not instance_id or not private_network_id:
            # Fallback for local testing or public endpoint if user provides HOST instead
            host = os.environ.get('MONGO_HOST')
            if host:
                uri = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority"
            else:
                 raise ValueError("MONGO_INSTANCE_ID or MONGO_HOST not set")
        else:
            # Scaleway Private Network Connection String
            # mongodb+srv://{username}:{password}@{instance_id}.{private_network_id}.internal/?tls=true&tlsCAFile={tls_certificate}
            host = f"{instance_id}.{private_network_id}.internal"
            uri = f"mongodb+srv://{user}:{password}@{host}/?tls=true&tlsCAFile={cert_file}"

        client = pymongo.MongoClient(uri)
        
    db = client[db_name]
    return db['todos']

def determine_intent(transcript):
    """
    Determines if the transcript is a MEETING or TODO.
    """
    transcript_lower = transcript.lower()
    meeting_keywords = ["meeting", "schedule", "invite", "calendar", "appointment"]
    todo_keywords = ["todo", "task", "remind me", "buy", "note"]
    
    for word in meeting_keywords:
        if word in transcript_lower:
            return "MEETING"
            
    for word in todo_keywords:
        if word in transcript_lower:
            return "TODO"
            
    return "TODO" # Default fallback

def handle_speech_to_text(audio_data, content_type):
    """
    Calls Scaleway's Speech-to-Text API to transcribe audio.
    """
    api_key = os.environ.get('SCALEWAY_API_KEY')
    api_url = os.environ.get('SCALEWAY_API_URL', 'https://api.scaleway.com/speech-to-text/v1/transcriptions') # Example URL

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
        # Note: The Scaleway API might expect multipart/form-data instead of raw bytes.
        # This implementation assumes raw bytes are accepted.
        # If not, the code will need to be adjusted to build a multipart request.
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


def handle_meeting(transcript, timezone, recipient_email):
    # details = extract_meeting_details(transcript, timezone)
    # success, result = send_email(recipient_email, details)
    
    # Mock for now while dependencies are sorted out
    success = True
    result = "mock-message-id"
    
    if success:
         return {
            'statusCode': 200,
            'body': json.dumps({'type': 'meeting', 'message': 'Invite sent (MOCKED)', 'data': {'messageId': result}})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to send email', 'details': result})
        }

def handle_todo(transcript):
    try:
        collection = get_mongo_collection()
        
        # Simple priority extraction
        priority = "normal"
        if "high priority" in transcript.lower() or "urgent" in transcript.lower():
            priority = "high"
            
        item = {
            'id': str(uuid.uuid4()),
            'text': transcript,
            'priority': priority,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        collection.insert_one(item)
        # Remove _id (ObjectId) before returning
        item.pop('_id', None)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 'todo', 'message': 'Task saved', 'data': item})
        }
    except Exception as e:
        logger.error(f"Mongo Error: {e}")
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
        # If content-type suggests audio, process as speech-to-text
        if content_type.startswith('audio/'):
            audio_data = event.get('body')
            if not audio_data:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing audio data in body'})}
            
            # Body might be base64 encoded by the gateway, decode if so.
            # This is a common pattern, but might need adjustment.
            if event.get('isBase64Encoded', False):
                import base64
                audio_data = base64.b64decode(audio_data)

            return handle_speech_to_text(audio_data, content_type)

        # Otherwise, assume JSON and process as before
        body = event.get('body', {})
        if isinstance(body, str):
            try:
                body = json.loads(body) if body.strip() else {}
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse Error: {e} - Body: {body[:100]}")
                return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON body'})}
        
        transcript = body.get('transcript')
        if not transcript:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing transcript in JSON body'})}

        logger.info(f"Received Transcript: {transcript}")
        
        intent = determine_intent(transcript)
        logger.info(f"Intent classified as: {intent}")
        
        if intent == "MEETING":
            recipient_email = body.get('email') or os.environ.get('RECIPIENT_EMAIL')
            if not recipient_email:
                return {'statusCode': 500, 'body': json.dumps({'error': 'Recipient email not configured'})}
            timezone = body.get('timezone', 'UTC')
            return handle_meeting(transcript, timezone, recipient_email)
        else:
            return handle_todo(transcript)

    except Exception as e:
        logger.error(f"Handler Unexpected Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
