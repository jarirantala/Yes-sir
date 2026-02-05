# Android App Requirements

## 1. Overview
The **Voice Assistant App** is the primary user interface. It is responsible for capturing the user's voice, sending it to the backend for transcription and processing, and displaying the result.

## 2. Functional Requirements

### 2.1 Voice Capture & Transcription
*   **REQ-A-001**: The app must provide a prominent "Push-to-Talk" button.
*   **REQ-A-002**: The app must record audio locally when the user presses the button. This audio will be sent to the backend for transcription. The `SpeechRecognizer` will no longer be used.
*   **REQ-A-003**: The app must request `RECORD_AUDIO` and `INTERNET` permissions at runtime.
*   **REQ-A-004**: The app must manage the audio recording lifecycle (start, stop, save to a temporary file, and clean up).

### 2.2 Backend Communication
*   **REQ-A-005**: The app must communicate with the Scaleway Function backend.
*   **REQ-A-006**: All requests must include the `X-Auth-Token` header for authentication.
*   **REQ-A-007**: To get a transcript, the app must `POST` the recorded audio file to the backend with a `Content-Type` of `audio/*`.
*   **REQ-A-008**: After receiving a transcript, the app will send a second `POST` request with a `Content-Type` of `application/json` to the same endpoint to execute the command. The payload will contain:
    *   `transcript`: The recognized text received from the first request.
    *   `timezone`: The device's current timezone ID (e.g., "Europe/Paris").

### 2.3 UI/UX
*   **REQ-A-009**: The UI should display the current status (e.g., "Recording...", "Transcribing...", "Processing...").
*   **REQ-A-010**: **Feedback**: Show a Toast or Snackbar upon success (e.g., "Meeting Invite Sent", "Task Saved").
*   **REQ-A-011**: **Error Handling**: Show friendly error messages if the network fails or the backend returns an error.

## 3. Non-Functional Requirements
*   **NFR-A-001**: **Latency**: The UI must remain responsive while recording and waiting for the API (use background threads/coroutines).
*   **NFR-A-002**: **Security**: The Auth Token should not be hardcoded and should be stored securely.
