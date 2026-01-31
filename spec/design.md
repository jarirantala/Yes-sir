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
    App->>App: SpeechRecognizer (Audio -> Text)
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>Func: POST /command {transcript, timezone}
    Note right of Func: See api.md for details
    Func->>Func: Route to Calendar Logic
    Func->>Func: Parse Date & Generate .ics
    Func->>TEM: Send Email (w/ attachment)
    TEM->>Email: Deliver Email
    Func-->>App: 200 OK

    App-->>User: Toast "Success"

    Note over User, App: Feature: Voice Todo
    User->>App: Selects "Voice Todo"
    User->>App: Holds Record Button (Speaks "Buy milk")
    App->>App: SpeechRecognizer
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>App: SpeechRecognizer
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>Func: POST /command {transcript}
    Func->>Func: Route to Todo Logic
    Func->>Mongo: Insert Todo Item
    Func-->>App: 200 OK (id: 123)
    App-->>User: Toast "Saved"
```

## 2. Key Components

### 2.1 Mobile Application (Android)
*   **Modular Design:** The app is built to support multiple features.
*   **Voice Input:** Centralized voice capture component usable by different skills.
*   **Networking:** Shared API client for backend communication.

### 2.2 Backend (Scaleway Serverless)
*   **Function Endpoint:** Single entry point for assistant requests.
*   **Scaleway Functions:** Python function hosting logic for Voice Calendar and Voice Todo.
*   **Persistence (MongoDB):** Managed Document Store for Todo items and other state.

## 3. Data Flow

### 3.1 Voice Calendar
1.  **Capture:** User speaks commands/meeting details.
2.  **Transcribe:** Device converts speech to text.
3.  **Process:** Backend interprets text to extract structured data (Date, Time, Topic).
4.  **Action:** Backend executes the action (Sending Email Invite).

### 3.2 Voice Todo
1.  **Capture:** User speaks task.
2.  **Transcribe:** Device converts speech to text.
3.  **Process:** Backend interprets text (extracts priority, tags).
4.  **Action:** Backend saves the item to MongoDB.