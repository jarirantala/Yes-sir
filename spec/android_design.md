# Android App Design

## 1. Architecture: MVVM
We will use **Model-View-ViewModel (MVVM)** to separate UI logic from business logic.

### Components
1.  **View (`MainActivity`)**:
    *   Handles UI rendering (Button, Toasts).
    *   Observes ViewModel state (`LiveData` or `StateFlow`).
2.  **ViewModel (`VoiceViewModel`)**:
    *   Manages `AudioRecorder` state (Recording, Idle).
    *   Initiates API calls via the Repository (Upload, then Execute).
3.  **UI State (`VoiceUiState`)**:
    *   Defined in `ui/VoiceUiState.kt`.
    *   Sealed class representing states: `Ready`, `Listening`, `Transcribing`, `Processing`, `Success`, `Error`.
4.  **Reusable Components**:
    *   Located in `ui/components/CommonComponents.kt`.
    *   Provides standardized `StatusText` and `JSONCard` elements.
5.  **Model / Repository (`VoiceRepository`)**:
    *   Abstracts the data source.
    *   Calls `ApiService` (Retrofit) for both `transcribeAudio` and `sendCommand`.

## 2. Tech Stack
*   **Language**: Kotlin
*   **Network**: Retrofit + OkHttp (for REST API)
*   **Concurrency**: Kotlin Coroutines
*   **Dependency Injection**: Hilt (Optional, or manual DI for simplicity initially)
*   **JSON Parsing**: Gson or Moshi
*   **Audio**: `MediaRecorder` (AAC/M4A)

## 3. Data Flow
1.  User holds "Record".
2.  `AudioRecorder` captures audio to file.
3.  User releases "Record".
4.  `VoiceViewModel` calls `VoiceRepository.transcribeAudio(file)`.
5.  Backend returns JSON (`{ "transcript": "..." }`).
6.  `VoiceViewModel` shows transcript to user.
7.  User confirms / Auto-sends.
8.  `VoiceViewModel` calls `VoiceRepository.sendCommand(transcript)`.
9.  Backend returns JSON (`{ "type": "meeting", "parsed_data": {...}, ... }`).
10. `VoiceViewModel` updates `uiState` with Success/Error AND `parsedData`.
    *   **Success**: Show Toast + Display `parsedData`.
    *   **Error**: Display backend `error` and `details` text on screen (not just Toast).
11. `MainActivity` renders the state accordingly.

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
