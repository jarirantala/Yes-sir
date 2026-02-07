import os
import json
import logging
import datetime
import urllib.request
import urllib.error

logger = logging.getLogger()

SYSTEM_PROMPT_TEMPLATE = """You are a multilingual Personal Assistant fluent in English and Finnish.
Your goal is to extract structured data from the user's spoken command (which may be in English or Finnish).

MATCH ONE OF THE FOLLOWING INTENTS and output ONLY valid JSON using English keys.

### 1. MEETING
**Trigger**: User wants to schedule an event, meeting, call, or appointment.
**Finnish Context**: "Varaa kalenterista...", "Tapaaminen...", "Sovittu meno..."
**Output Schema**:
{
  "intent": "MEETING",
  "title": "string (concise summary of the meeting, e.g., 'Meeting with John')",
  "datetime": "string (ISO 8601 format, absolute time calculated relative to {{current_time}})",
  "duration": "integer (minutes, default to 60 if not specific)"
}

### 2. TODO
**Trigger**: User wants to remember a task, buy something, or do something later.
**Finnish Context**: "Muista ostaa...", "Tee tämä myöhemmin...", "Lisää listalle..."
**Output Schema**:
{
  "intent": "TODO",
  "title": "string (the task description)",
  "priority": "string (enum: 'low', 'medium', 'high' - default 'medium')"
}

### 3. NOTE
**Trigger**: User wants to save a random thought, a brain dump, or a piece of information that isn't a task or a meeting.
**Finnish Context**: "Kirjoita muistiinpano...", "Laita ylös...", "Aivopesu..."
**Output Schema**:
{
  "intent": "NOTE",
  "title": "string (the full content of the note)"
}

### 4. TRANSPORT
**Trigger**: User wants public transportation directions, bus routes, or train times to a specific destination.
**Finnish Context**: "Miten pääsen...", "Bussiaikataulut...", "Reitti kohteeseen..."
**Output Schema**:
{
  "intent": "TRANSPORT",
  "destination": "string (the name or address of the destination)"
}

### RULES
1. **Current Reference**: Today is {{current_time}}. Use this to resolve relative dates like "tomorrow" (huomenna), "next Friday" (ensi perjantaina), "in 2 hours" (kahden tunnin päästä).
2. **Ambiguity**: If unclear, default to TODO.
3. **Format**: Output raw JSON only. No Markdown blocks (```json), no explanations.
"""

def analyze_transcript(transcript, timezone="UTC"):
    """
    Sends the transcript to Mistral Small 3.2 to extract intent and entities.
    """
    api_key = os.environ.get('LLM_API_KEY')
    # Default to a placeholder standard endpoint, user must configure
    api_url = os.environ.get('LLM_API_URL', 'https://api.scaleway.ai/v1/chat/completions') 
    model = os.environ.get('LLM_MODEL', 'mistral-small-3.2-24b-instruct-2506')

    if not api_key:
        logger.error("LLM_API_KEY not configured")
        raise Exception("LLM configuration missing")

    # Calculate current time in ISO format for the prompt
    # Note: simple UTC now, ideal would be timezone aware calculation if timezone is valid
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Format System Prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{{current_time}}", current_time)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ],
        "temperature": 0.1, # Low temperature for deterministic JSON
        "response_format": {"type": "json_object"} # standard for updated models
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.load(response)
            content = result['choices'][0]['message']['content']
            
            logger.info(f"LLM Raw Response: {content}")
            
            # Parse JSON
            parsed_data = json.loads(content)
            return parsed_data

    except urllib.error.HTTPError as e:
        logger.error(f"LLM API Request Failed: {e.code} {e.reason}")
        raise Exception(f"Failed to contact AI service: {e.code}")
    except urllib.error.URLError as e:
        logger.error(f"LLM Connection Failed: {e.reason}")
        raise Exception(f"Failed to contact AI service: {e.reason}")
    except json.JSONDecodeError as e:
        logger.error(f"LLM JSON Parse Failed. Content: {content if 'content' in locals() else 'unknown'}")
        logger.warning("Falling back to generic TODO")
        return {
            "intent": "TODO",
            "title": transcript,
            "priority": "medium"
        }
    except Exception as e:
        logger.error(f"LLM Processing Error: {e}")
        raise e
