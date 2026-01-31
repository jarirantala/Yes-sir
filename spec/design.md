# Design Document: Personal Assistant Architecture

## 1. System Architecture
The system follows a **Client-Serverless** architecture designed for extensibility. The mobile app acts as the client for multiple "Skills", starting with the **Voice Calendar** skill.

```mermaid
sequenceDiagram
    participant User
    participant App as Assistant App
    participant APIG as AWS API Gateway
    participant Lambda as Assistant Lambda
    participant SES as Amazon SES
    participant Valkey as Valkey DB
    participant Email as User Email

    Note over User, App: Feature: Voice Calendar
    User->>App: Selects "Voice Calendar"
    User->>App: Holds Record Button (Speaks)
    App->>App: SpeechRecognizer (Audio -> Text)
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>APIG: POST /invite {transcript, timezone, skill="calendar"}
    Note right of APIG: See api.md for details
    APIG->>Lambda: Trigger Function (Router)
    Lambda->>Lambda: Route to Calendar Logic
    Lambda->>Lambda: Parse Date & Generate .ics
    Lambda->>SES: SendRawEmail (w/ attachment)
    SES->>Email: Deliver Email
    Lambda-->>App: 200 OK
    App-->>User: Toast "Success"

    Note over User, App: Feature: Voice Todo
    User->>App: Selects "Voice Todo"
    User->>App: Holds Record Button (Speaks "Buy milk")
    App->>App: SpeechRecognizer
    App->>User: Transcribed Text
    User->>App: Clicks Send Button
    App->>APIG: POST /todo {transcript, priority="normal"}
    APIG->>Lambda: Trigger Function
    Lambda->>Lambda: Route to Todo Logic
    Lambda->>Valkey: RPUSH todo:list "Buy milk"
    Lambda-->>App: 200 OK (id: 123)
    App-->>User: Toast "Saved"
```

## 2. Key Components

### 2.1 Mobile Application (Android)
*   **Modular Design:** The app is built to support multiple features.
*   **Voice Input:** Centralized voice capture component usable by different skills.
*   **Networking:** Shared API client for backend communication.

### 2.2 Backend (AWS Serverless)
*   **API Gateway:** Single entry point for assistant requests.
*   **Lambda:** Hosts logic for Voice Calendar and Voice Todo. Routes requests based on endpoint/parameters.
*   **Persistence (Valkey):** High-performance key-value store for Todo items and other state.

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
4.  **Action:** Backend saves the item to Valkey.