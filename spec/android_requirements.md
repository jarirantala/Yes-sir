# Android App Requirements

## 1. Overview
The **Voice Assistant App** is the primary interface for the user. It allows capturing voice commands, transcribing them, and sending them to the backend for processing.

## 2. Functional Requirements

### 2.1 Voice Capture
* **REQ-A-001**: The app must provide a prominent "Push-to-Talk" button.
* **REQ-A-002**: The app must use `SpeechRecognizer` for on-device or cloud-based transcription (depending on Android version/settings).
* **REQ-A-003**: The app must request `RECORD_AUDIO` permission at runtime.

### 2.2 Backend Communication
* **REQ-A-004**: The app must communicate with the Scaleway Private Function via the API Gateway.
* **REQ-A-005**: All requests must include the `X-Auth-Token` header for authentication.
* **REQ-A-006**: The app must POST a JSON payload containing:
    * `transcript`: The recognized text.
    * `timezone`: The device's current timezone ID (e.g., "Europe/Paris").
    * `email`: (Optional) User email if configured in settings.

### 2.3 UI/UX
* **REQ-A-007**: The dashboard should show the button and a log of recent actions.
* **REQ-A-008**: **Feedback**: Show a Toast or Snackbar upon success (e.g., "Meeting Invited", "Task Saved").
* **REQ-A-009**: **Error Handling**: Show friendly error messages if the network fails or the backend returns an error.

## 3. Non-Functional Requirements
* **NFR-A-001**: **Latency**: The UI must remain responsive while waiting for the API (use background threads/coroutines).
* **NFR-A-002**: **Security**: The Auth Token should be stored securely (e.g., `local.properties` for dev, EncryptedSharedPreferences for prod).
