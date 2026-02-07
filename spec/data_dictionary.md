# Data Dictionary

## 1. Meeting Details
Internal data structure used to represent a parsed meeting.

| Field | Type | Description |
|-------|------|-------------|
| `summary` | String | The topic or title of the meeting. Extracted from the transcript by removing date/time keywords. Defaults to "Meeting" if no topic is found. |
| `start_time` | DateTime | The start time of the meeting. Timezone-aware. |
| `end_time` | DateTime | The end time of the meeting. Calculated as `start_time` + `duration`. |

## 2. Transcript Analysis
Logic used to derive the meeting details from the raw transcript.

| Component | Default Value | Extraction Rule |
|-----------|---------------|-----------------|
| **Duration** | 60 minutes | Regex search for "for X minutes/hours". If not found, defaults to 60. |
| **Start Date** | Tomorrow, 9:00 AM | `parsedatetime` NLP analysis. If no date found in text, defaults to tomorrow morning. |
| **Timezone** | UTC | Uses provided `timezone` parameter or matches user's locale. Defaults to UTC if invalid/missing. |

## 3. Todo Item
Internal data structure used to represent a task.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier. |
| `text` | String | The task description. |
| `priority` | Enum | "high", "normal", "low". |
| `created_at`| DateTime | Timestamp of creation. |
| `status` | Enum | "pending", "completed". |

## 4. Note Item
Internal data structure used to represent a stored note.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier. |
| `text` | String | The note content. |
| `created_at`| DateTime | Timestamp of creation. |

## 5. Intent Recognition
Logic used to determine which action to take based on the transcript.

| Intent | Keywords (Case-insensitive) | Default Action |
|--------|-----------------------------|----------------|
| **MEETING** | "meeting", "schedule", "invite", "calendar", "appointment" | Parse as Meeting Details and send invite. |
| **TODO** | "todo", "task", "remind me", "buy" | Parse as Todo Item and save to list. |
| **NOTE** | "note", "brain dump", "remember that", "take a note" | Save content to **Notes** collection. |
| **TRANSPORT** | "bus", "train", "directions", "how do I get to", "transport" | Generate Google Maps transit deep link. |
| **UNKNOWN** | (None) | Fallback to **TODO** treatment. |
