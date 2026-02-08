# Android App Design

## 1. Architecture: MVVM
We will use **Model-View-ViewModel (MVVM)** to separate UI logic from business logic.

### Components
1.  **View (`MainActivity`)**:
    *   Handles UI rendering (Button, Toasts).
    *   Observes ViewModel state (`LiveData` for UI flow, `StateFlow` for data lists).
2.  **ViewModel (`VoiceViewModel`)**:
    *   Manages `AudioRecorder` state (Recording, Idle).
    *   Initiates API calls via the Repository.
    *   Implements **Session-based Caching**: Loads data on-demand (Lazy Loading) once per session.
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

## 3. Data Flow & Navigation
1.  **Global UI Shell**: A `ModalNavigationDrawer` wrap the app, providing direct access to Home, To-Dos, and Notes.
2.  **Voice Interaction**:
    - User holds "Record".
    - `AudioRecorder` captures audio to file.
    - User releases "Record".
    - `VoiceViewModel` calls `VoiceRepository.transcribeAudio(file)`.
    - Backend returns transcript.
    - `VoiceViewModel` calls `VoiceRepository.sendCommand(transcript)`.
    - Backend returns structured result.
3.  **Real-time Cache Sync**:
    - When a new TODO/NOTE is created via voice, it is immediately prepended to the local `StateFlow` cache.
4.  **Lazy Loading**:
    - Database lists are fetched from the backend ONLY when the user first visits the To-Do or Note screen.
    - Subsequent visits use the cached data.

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
