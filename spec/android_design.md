# Android App Design

## 1. Architecture: MVVM
We will use **Model-View-ViewModel (MVVM)** to separate UI logic from business logic.

### Components
1.  **View (`MainActivity`)**:
    *   Handles UI rendering (Button, Toasts).
    *   Observes ViewModel state (`LiveData` or `StateFlow`).
2.  **ViewModel (`VoiceViewModel`)**:
    *   Manages `SpeechRecognizer` state (Listening, Error, Result).
    *   Initiates API calls via the Repository.
3.  **Model / Repository (`VoiceRepository`)**:
    *   Abstracts the data source.
    *   Calls `ApiService` (Retrofit).

## 2. Tech Stack
*   **Language**: Kotlin
*   **Network**: Retrofit + OkHttp (for REST API)
*   **Concurrency**: Kotlin Coroutines
*   **Dependency Injection**: Hilt (Optional, or manual DI for simplicity initially)
*   **JSON Parsing**: Gson or Moshi

## 3. Data Flow
1.  User holds "Record".
2.  `SpeechRecognizer` captures audio -> returns String `transcript`.
3.  `VoiceViewModel` receives `transcript`.
4.  `VoiceViewModel` calls `VoiceRepository.sendCommand(transcript)`.
5.  `VoiceRepository` uses `ApiService` to POST to Scaleway.
6.  Backend returns JSON (`{ "type": "meeting", ... }`).
7.  `VoiceViewModel` updates `uiState` with Success/Error.
8.  `MainActivity` shows Toast based on `uiState`.

## 4. API Definition
**POST** `https://<gateway-url>/command`

**Headers**:
*   `Content-Type: application/json`
*   `X-Auth-Token: <YOUR_TOKEN>`

**Body**:
```json
{
  "transcript": "Buy milk",
  "timezone": "Europe/Helsinki"
}
```

**Response**:
```json
{
  "type": "todo",
  "message": "Task saved",
  "data": { ... }
}
```
