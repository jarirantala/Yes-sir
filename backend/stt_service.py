import os
import json
import logging
import urllib.request
import urllib.error
from utils.multipart import encode_multipart_formdata

logger = logging.getLogger()

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
        try:
            # latin-1 is 1:1 for 0-255 encoding
            audio_data = audio_data.encode('latin-1')
        except Exception as e:
            logger.warning(f"Failed latin-1 encoding, falling back to utf-8: {e}")
            audio_data = audio_data.encode('utf-8', errors='ignore')

    logger.info(f"STT: Audio size {len(audio_data)} bytes. Start: {audio_data[:20]!r}")

    # Prepare multipart data
    fields = {
        'model': os.environ.get('STT_MODEL', 'whisper-large-v3')
    }
    
    # Determine extension from content_type
    ext = _get_extension_from_content_type(content_type)
    
    files = {
        'file': (f'audio.{ext}', audio_data, content_type)
    }

    try:
        body, content_type_header = encode_multipart_formdata(fields, files)
        
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
                'upstream_error': error_body
            })
        }
    except Exception as e:
        logger.error(f"STT Unexpected Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'STT_UNEXPECTED_ERROR', 'details': str(e)})
        }

def _get_extension_from_content_type(content_type):
    lower_ct = content_type.lower()
    if 'mpeg' in lower_ct or 'mp3' in lower_ct: return 'mp3'
    if 'ogg' in lower_ct: return 'ogg'
    if 'm4a' in lower_ct: return 'm4a'
    if 'flac' in lower_ct: return 'flac'
    return 'wav'
