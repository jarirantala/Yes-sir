import json
import os
import logging
import datetime
import uuid
import pymongo
from utils.parser import extract_meeting_details
from utils.emailer import send_email

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
    # Debug: Log event keys to understand structure
    if event:
        logger.info(f"Event keys: {list(event.keys())}")
        if 'body' in event:
            logger.info(f"Body type: {type(event['body'])}")
    else:
        logger.info("Event is None or empty")

    try:
        # Parse Body
        body = event.get('body', {})
        
        # If body is a string (common in HTTP triggers), try to parse it
        if isinstance(body, str):
            try:
                if not body.strip():
                     body = {}
                else:
                    body = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse Error: {e} - Body: {body[:100]}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON body'})
                }
        
        # Handle case where body might be None
        if not body:
            body = {}
            
        transcript = body.get('transcript')
        timezone = body.get('timezone', 'UTC')
        recipient_email = body.get('email') or os.environ.get('RECIPIENT_EMAIL')
        
        if not transcript:
             return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing transcript'})
            }

        logger.info(f"Received Transcript: {transcript}")
        
        intent = determine_intent(transcript)
        logger.info(f"Intent classified as: {intent}")
        
        if intent == "MEETING":
            if not recipient_email:
                 return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Recipient email not configured'})
                }
            return handle_meeting(transcript, timezone, recipient_email)
        else:
            return handle_todo(transcript)

    except Exception as e:
        logger.error(f"Handler Unexpected Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
