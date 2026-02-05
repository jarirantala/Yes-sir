# API Specification: Voice Assistant Backend

## Endpoint: `POST /`

This is the primary, multi-purpose endpoint for the voice assistant backend. It handles two main types of requests based on the `Content-Type` header:
1.  **Speech-to-Text**: Transcribes raw audio files.
2.  **Commands**: Processes transcribed text to perform actions like creating meetings or todos.

---

### 1. Speech-to-Text

Used to convert an audio file into text.

**Request**
- **Method:** `POST`
- **Content-Type:** `audio/*` (e.g., `audio/mpeg`, `audio/wav`)
- **Body:** The raw binary data of the audio file.

**Response (200 OK)**
Returns the transcribed text in a JSON object.
```json
{
  "transcript": "Schedule a meeting with John for next Tuesday at 2 PM"
}
```

---

### 2. Command Processing

Used to execute an action based on a transcribed text command.

**Request**
- **Method:** `POST`
- **Content-Type:** `application/json`

**Body Parameters**
| Name         | Type   | Required | Description                                                                |
|--------------|--------|----------|----------------------------------------------------------------------------|
| `transcript` | string | Yes      | The natural language text transcribed from the user's voice.               |
| `timezone`   | string | No       | The IANA timezone identifier of the user (e.g., "America/New_York").       |
| `email`      | string | No       | The recipient email address (for meetings). Defaults to a server-side config. |

**Example Request**
```json
{
  "transcript": "Schedule a meeting with John for next Tuesday at 2 PM",
  "timezone": "America/Los_Angeles"
}
```

**Success Response (200 OK) - Meeting Created**
```json
{
  "type": "meeting",
  "message": "Invite sent",
  "parsed_data": {
     "intent": "MEETING",
     "title": "Meeting with John",
     "datetime": "2023-10-31T14:00:00",
     "duration": 60
  },
  "data": {
     "messageId": "mock-message-id"
  }
}
```

**Success Response (200 OK) - Todo Saved**
```json
{
  "type": "todo",
  "message": "Task saved",
  "parsed_data": {
    "intent": "TODO",
    "title": "Buy milk",
    "priority": "normal"
  },
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "text": "Buy milk",
    "priority": "normal",
    "created_at": "2023-10-27T10:00:00Z",
    "status": "pending"
  }
}
```
---

### Error Responses

**400 Bad Request**
Returned for missing or invalid request data.
```json
{
  "error": "Missing transcript in JSON body"
}
```
```json
{
  "error": "Missing audio data in body"
}
```

**500 Internal Server Error**
Returned for server-side issues, such as configuration problems or API failures.
```json
{
  "error": "Recipient email not configured"
}
```
```json
{
  "error": "Failed to call Speech-to-Text API",
  "details": "Error message from the API..."
}
```
```json
{
  "error": "Failed to save task",
  "details": "Error message from the database..."
}
```

