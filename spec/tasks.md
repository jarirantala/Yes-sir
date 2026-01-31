# Implementation Plan

## Phase 1: AWS Backend Setup
- [ ] **Task B-1:** Set up AWS SES
    - [ ] Verify sender email address in AWS SES Console.
    - [ ] Verify recipient email address (if in Sandbox mode).
- [ ] **Task B-2:** Create Lambda Layer
    - [ ] Create `requirements.txt` with `parsedatetime`, `icalendar`, `pytz`.
    - [ ] Install dependencies to a folder and zip it.
    - [ ] Upload as AWS Lambda Layer.
- [ ] **Task B-3:** Implement Lambda Logic
    - [ ] Write `lambda_function.py` to parse JSON input.
    - [ ] Implement `extract_meeting_details(text)` using `parsedatetime`.
    - [ ] Implement `generate_ics(details)` using `icalendar`.
    - [ ] Implement `send_email(ics_data)` using `boto3`.
- [ ] **Task B-4:** Configure API Gateway
    - [ ] Create HTTP API.
    - [ ] Create `POST /invite` route linked to Lambda.
    - [ ] Enable CORS.
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
- [ ] **Task B-5:** Integrate Valkey
    - [ ] Set up Valkey instance.
    - [ ] Add `redis` library to Lambda Layer.
- [ ] **Task B-6:** Implement Todo Logic
    - [ ] Create `POST /todo` endpoint in API Gateway.
    - [ ] Update Lambda to handle `todo` skill.
    - [ ] Implement `save_to_valkey(item)`.
- [ ] **Task F-5:** Mobile Todo Mode
    - [ ] Add UI Selector for "Calendar" vs "Todo" mode.
    - [ ] Update ViewModel to send to `/todo` endpoint when in Todo mode.