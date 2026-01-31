import json
import os
import logging
from utils.parser import extract_meeting_details
from utils.emailer import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda Entry Point.
    """
    try:
        # 1. Parse Input
        if 'body' in event:
            # API Gateway sends stringified body
            try:
                body = json.loads(event['body'])
            except (TypeError, json.JSONDecodeError):
                # Sometimes body is already dict in tests or specific configs
                body = event['body'] if isinstance(event['body'], dict) else {}
        else:
            body = event
            
        transcript = body.get('transcript')
        timezone = body.get('timezone', 'UTC')
        recipient_email = body.get('email') or os.environ.get('RECIPIENT_EMAIL')
        
        if not transcript:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing transcript'})
            }
            
        if not recipient_email:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Recipient email not configured'})
            }

        # 2. Process
        logger.info(f"Processing: {transcript} ({timezone})")
        details = extract_meeting_details(transcript, timezone)
        
        # 3. Send Email
        success, msg_id = send_email(recipient_email, details)
        
        if success:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Invite sent', 'messageId': msg_id})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send email', 'details': msg_id})
            }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
