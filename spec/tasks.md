# Implementation Plan

## Phase 1: Scaleway Backend Setup
- [ ] **Task B-1:** Set up Scaleway TEM (Transactional Email)
    - [ ] Create a Project in Scaleway Console.
    - [ ] Enable Transactional Email (TEM).
    - [ ] Verify domain and sender logic.
- [ ] **Task B-2:** Create Function Package
    - [ ] Create `backend/requirements.txt` with `parsedatetime`, `icalendar`, `pytz`, `scaleway-functions-python`.
    - [ ] Structure project for Scaleway Functions (handler is in `backend/`).
- [ ] **Task B-3:** Implement Function Logic
    - [ ] Write `handler.py` to handle events.
    - [ ] Implement `extract_meeting_details(text)`.
    - [ ] Implement `generate_ics(details)`.
    - [ ] Implement `send_email(ics_data)` using SMTP or TEM API.
- [ ] **Task B-4:** Deploy Function
    - [ ] Deploy function using Scaleway Console or CLI.
    - [ ] Configure Environment Variables (TEM Key, etc.).
    - [ ] **Validation:** Test with `curl` to ensure email is received.

## Phase 2: Android App Development
- [ ] **Task F-1:** Project Initialization
    - [ ] Create new Android Studio project (Compose Activity).
    - [ ] Add Retrofit and Gson dependencies to `build.gradle`.
    - [ ] Add `INTERNET` and `RECORD_AUDIO` permissions to Manifest.
- [ ] **Task F-2:** Networking Layer
    - [ ] Define `MeetingRequest` and `MeetingResponse` data classes.
    - [ ] Create `ApiService` interface with POST method.
    - [ ] Initialize `Retrofit` client singleton.
- [ ] **Task F-3:** Voice Logic
    - [ ] Implement `SpeechRecognizer` contract.
    - [ ] Create a composable `RecordButton` that detects touch down/up events.
    - [ ] Handle runtime permission request for Microphone.
- [ ] **Task F-4:** UI & Integration
    - [ ] Build Main Screen with State Hoisting.
    - [ ] Connect `SpeechRecognizer` output to `ViewModel`.
    - [ ] Trigger API call upon successful transcription.
    - [ ] Show Toast/Snackbar on API success/failure.

## Phase 3: Final Polish
- [ ] **Task P-1:** Edge Case Handling
    - [ ] Handle "No internet connection" on Android.
    - [ ] Handle "Date not found" fallback in Python (Default to tomorrow).
- [ ] **Task P-2:** Integration Testing
    - [ ] Record a real meeting request ("Team sync next monday at 10am").
    - [ ] Verify the calendar invite opens correctly in Google Calendar/Outlook.

## Phase 4: Voice Todo Feature
- [ ] **Task B-5:** Integrate MongoDB
    - [ ] Provision Managed MongoDB Database in Scaleway.
    - [ ] Add `pymongo` to `requirements.txt`.
- [ ] **Task B-6:** Implement Todo Logic
    - [ ] Update `handler.py` to handle `todo` intent.
    - [ ] Implement `save_to_mongodb(item)` using `pymongo`.
- [ ] **Task F-5:** Mobile Todo Mode
    - [ ] Add UI Selector for "Calendar" vs "Todo" mode.
    - [ ] Update ViewModel to send to `/todo` endpoint when in Todo mode.