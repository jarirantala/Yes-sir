# Design Document: Voice-to-Calendar Architecture

## 1. System Architecture
The system follows a **Client-Serverless** architecture.

```mermaid
sequenceDiagram
    participant User
    participant Android as Android App
    participant APIG as AWS API Gateway
    participant Lambda as AWS Lambda
    participant SES as Amazon SES
    participant Email as User Email

    User->>Android: Holds Record Button (Speaks)
    Android->>Android: SpeechRecognizer (Audio -> Text)
    Android->>User: Transcribed Text
    User->>Android: Clicks Send Button
    Android->>APIG: POST /invite {transcript, timezone}
    APIG->>Lambda: Trigger Function
    Lambda->>Lambda: Parse Date (parsedatetime lib)
    Lambda->>Lambda: Generate .ics (icalendar lib)
    Lambda->>SES: SendRawEmail (w/ attachment)
    SES->>Email: Deliver Email
    Lambda-->>Android: 200 OK
    Android-->>User: Toast "Success"