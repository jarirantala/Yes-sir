# Design Document: Personal Assistant Architecture

## 1. System Architecture
The system follows a **Client-Serverless** architecture designed for extensibility. The mobile app acts as the client for multiple "Skills", starting with the **Voice Calendar** skill.

```mermaid
sequenceDiagram
    participant User
    participant App as Assistant App
    participant App as Assistant App
    participant Func as Scaleway Function
    participant TEM as Scaleway TEM
    participant Mongo as MongoDB
    participant Email as User Email

    Note over User, App: Feature: Voice Calendar
    User->>App: Selects "Voice Calendar"
    User->>App: Holds Record Button (Speaks)
    App->>App: AudioRecorder (Save to File)
    User->>App: Releases Button
    App->>Func: POST / (audio/mpeg)
    Func->>App: { "transcript": "..." }
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>Func: POST /command {transcript, timezone}
    Note right of Func: See api.md for details
    Func->>LLM: Prompt (System + Transcript)
    LLM->>Func: JSON { "intent": "MEETING", ... }
    Func->>Func: Route to Calendar Logic
    Func->>Func: Parse Date & Generate .ics
    Func->>TEM: Send Email (w/ attachment)
    TEM->>Email: Deliver Email
    TEM->>Email: Deliver Email
    Func-->>App: 200 OK (JSON + Result)
    App->>App: Display `parsed_data`
    App->>App: Display `parsed_data`
    App-->>User: Toast "Success"
    
    rect rgb(255, 200, 200)
    Note over Func, App: Error Case
    Func-->>App: 4xx/5xx Error { "error": "...", "details": "..." }
    App->>App: Extract `error` & `details`
    App->>User: Display Error Message on Screen
    end

    Note over User, App: Feature: Voice Todo
    User->>App: Selects "Voice Todo"
    User->>App: Holds Record Button (Speaks "Buy milk")
    App->>App: AudioRecorder
    App->>Func: POST / (audio/mpeg)
    Func->>App: { "transcript": "Buy milk" }
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>Func: POST /command {transcript}
    Func->>LLM: Prompt (System + Transcript)
    LLM->>Func: JSON { "intent": "TODO", ... }
    Func->>Func: Route to Todo Logic
    Func->>Mongo: Insert Todo Item
    Func->>Mongo: Insert Todo Item
    Func-->>App: 200 OK (JSON + Result)
    App->>App: Display `parsed_data`
    App-->>User: Toast "Saved"
```

## 2. Key Components

### 2.1 Mobile Application (Android)
*   **Modular Design:** The app is built to support multiple features.
*   **Voice Input:** Centralized voice capture component usable by different skills.
*   **Networking:** Shared API client for backend communication.

### 2.2 Backend (Scaleway Serverless)
*   **Function Endpoint:** Single entry point for assistant requests.
*   **LLM Service:** mistral-small-3.2-24b-instruct-2506 (via Scaleway or External API) for NLU. See [prompts.md](prompts.md) for System Prompt details.
*   **Scaleway Functions:** Python function hosting logic for Voice Calendar and Voice Todo.
*   **Persistence (MongoDB):** Managed Document Store for Todo items and other state.

## 3. Data Flow

### 3.1 Voice Calendar
1.  **Capture:** User speaks commands/meeting details.
2.  **Transcribe:** Device converts speech to text.
3.  **Process:** Backend sends text to Mistral Small to extract structured JSON (Date, Time, Topic).
4.  **Action:** Backend executes the action (Sending Email Invite).

### 3.2 Voice Todo
1.  **Capture:** User speaks task.
2.  **Transcribe:** Device converts speech to text.
3.  **Process:** Backend interprets text (extracts priority, tags).
4.  **Action:** Backend saves the item to MongoDB.