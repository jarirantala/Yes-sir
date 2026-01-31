# API Specification: Voice Calendar Backend

## Base URL
`POST /command`

## Description
Primary endpoint for voice commands. Receives a voice transcript, determines user intent (Meeting vs. Todo), and executes the corresponding action.

## Request
**Method:** `POST`
**Content-Type:** `application/json`

### Body Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `transcript` | string | Yes | The natural language text transcribed from user's voice. |
| `timezone` | string | No | The IANA timezone identifier of the user (e.g., "America/New_York"). Defaults to "UTC". |
| `email` | string | No | The recipient email address (for meetings). Defaults to server env `RECIPIENT_EMAIL`. |

### Example Request
```json
{
  "transcript": "Schedule a meeting with John for next Tuesday at 2 PM",
  "timezone": "America/Los_Angeles"
}
```

## Response

### Success (200 OK) - Meeting Created
Returns type "meeting" and confirmation details.

```json
{
  "type": "meeting",
  "message": "Invite sent",
  "data": {
     "summary": "Meeting with John",
     "start_time": "2023-11-07T14:00:00-08:00"
  }
}
```

### Success (200 OK) - Todo Saved
Returns type "todo" and the saved item.

```json
{
  "type": "todo",
  "message": "Task saved",
  "data": {
    "id": "123456",
    "text": "Buy milk",
    "priority": "normal"
  }
}
```

### Error (400 Bad Request)
Returned when required parameters are missing.

```json
{
  "error": "Missing transcript"
}
```

## Legacy Endpoints

## Endpoint: POST /invite

## Description
Receives a voice transcript, parses it for meeting details, and sends a calendar invitation via email.

## Request
**Method:** `POST`
**Content-Type:** `application/json`

### Body Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `transcript` | string | Yes | The natural language text transcribed from user's voice. |
| `timezone` | string | No | The IANA timezone identifier of the user (e.g., "America/New_York"). Defaults to "UTC". |
| `email` | string | No | The recipient email address. If omitted, defaults to the server-configured environment variable `RECIPIENT_EMAIL`. |

### Example Request
```json
{
  "transcript": "Schedule a meeting with John for next Tuesday at 2 PM for 30 minutes",
  "timezone": "America/Los_Angeles",
  "email": "john.doe@example.com"
}
```

## Response

### Success (200 OK)
Returns confirmation that the invite was processed and sent.

```json
{
  "message": "Invite sent",
  "messageId": "0100017f..."
}
```

### Error (400 Bad Request)
Returned when required parameters are missing.

```json
{
  "error": "Missing transcript"
}
```

### Error (500 Internal Server Error)
Returned when email sending fails or configuration is missing.

```json
{
  "error": "Recipient email not configured"
}
```
OR
```json
{
  "error": "Failed to send email",
  "details": "Error message from SES..."
}
```

## Endpoint: POST /todo

## Base URL
`POST /todo`

## Description
Receives a voice transcript of a task, extracts priority, and saves it to the user's todo list.

## Request
**Method:** `POST`
**Content-Type:** `application/json`

### Body Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `transcript` | string | Yes | The natural language text of the task. |
| `priority` | string | No | Explicit priority level ("high", "normal", "low"). Defaults to "normal". |

### Example Request
```json
{
  "transcript": "Buy milk and eggs",
  "priority": "high"
}
```

## Response

### Success (200 OK)
Returns the saved item details.

```json
{
  "id": "123456",
  "status": "saved",
  "item": {
    "text": "Buy milk and eggs",
    "priority": "high",
    "created_at": "2023-10-27T10:00:00Z"
  }
}
```

### Error (500 Internal Server Error)
Returned when database save fails.

```json
{
  "error": "Failed to save item"
}
```
