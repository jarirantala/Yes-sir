import parsedatetime
import datetime
import re
import pytz

def extract_meeting_details(transcript, user_timezone='UTC'):
    """
    Parses the transcript to find meeting details.
    
    Args:
        transcript (str): The spoken text.
        user_timezone (str): The timezone of the user (e.g., 'America/New_York').
        
    Returns:
        dict: {
            'summary': str,
            'start_time': datetime.datetime (timezone aware),
            'end_time': datetime.datetime (timezone aware)
        }
    """
    cal = parsedatetime.Calendar()
    
    # 1. Identify Duration
    duration_minutes = 60 # Default REQ-B-004
    
    # Regex for "for X minutes/hours"
    dur_match = re.search(r'\bfor\s+(\d+)\s*(min|minute|hour|hr)s?\b', transcript, re.IGNORECASE)
    if dur_match:
        val = int(dur_match.group(1))
        unit = dur_match.group(2).lower()
        if 'hour' in unit or 'hr' in unit:
            duration_minutes = val * 60
        else:
            duration_minutes = val
    
    # 2. Identify Start Date/Time
    # Default: Tomorrow at 9:00 AM (REQ-B-003)
    try:
        tz = pytz.timezone(user_timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.UTC
        
    now_local = datetime.datetime.now(tz)
    source_time = now_local.replace(tzinfo=None)
    
    start_dt_naive = None
    topic = transcript
    
    # Use nlp() to find date
    nlp_res = cal.nlp(transcript, sourceTime=source_time)
    
    if nlp_res:
        # nlp returns tuple (datetime, flag, start_idx, end_idx, match_text)
        dt_obj, _, _, _, match_text = nlp_res[0]
        start_dt_naive = dt_obj
        
        # Simple topic extraction: remove the date string
        topic = transcript.replace(match_text, "").strip()
        # Cleanup prepositions
        topic = re.sub(r'\s+(at|on|for)\s*$', '', topic).strip()
        topic = re.sub(r'^\s*(at|on|for)\s+', '', topic).strip()
    else:
        # Fallback: Tomorrow 9 AM
        tomorrow = source_time + datetime.timedelta(days=1)
        start_dt_naive = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)
        
    if not topic:
        topic = "Meeting"

    # 3. Finalize
    # parsedatetime returns naive datetime, assume it's in user_timezone
    start_dt = tz.localize(start_dt_naive)
    end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
    
    return {
        'summary': topic,
        'start_time': start_dt,
        'end_time': end_dt
    }
