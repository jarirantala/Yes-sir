# Implementation Plan

## Phase 1: Scaleway Backend Setup
- [x] **Task B-1:** Set up Scaleway TEM (Transactional Email)
    - [x] Create a Project in Scaleway Console (User Verified).
    - [x] Enable Transactional Email (TEM).
    - [x] Verify domain and sender logic.
- [x] **Task B-2:** Create Function Package
    - [x] Create `backend/requirements.txt` with `parsedatetime`, `icalendar`, `pytz`, `pymongo`, `dnspython`.
    - [x] Structure project for Scaleway Functions (handler is in `backend/`).
- [x] **Task B-3:** Implement Function Logic
    - [x] Write `handler.py` to handle events.
    - [x] Implement `extract_meeting_details(text)`.
    - [x] Implement `generate_ics(details)`.
    - [x] Implement `send_email(ics_data)` using SMTP or TEM API.
- [x] **Task B-4:** Infrastructure as Code (OpenTofu)
    - [x] Create `main.tf` in root to define Function Namespace and Function resources.
    - [x] Create `variables.tf` in root for secrets.
    - [x] Create `variables.tf` in root for secrets.
    - [x] Create `outputs.tf` in root to expose endpoint.
- [ ] **Task B-8:** Implement API Gateway (OpenTofu) - **Skipped (Provider Limitation)**
    - [ ] Update `main.tf` to set Function privacy to "private".
    - [ ] Add `scaleway_function_token`.
    - [ ] Add `scaleway_api_gateway_gateway` and `scaleway_api_gateway_api`.
    - [ ] Route API Gateway to Function.
- [ ] **Task B-7:** Deploy with OpenTofu
    - [ ] Initialize OpenTofu (`tofu init`).
    - [ ] Plan deployment (`tofu plan`).
    - [ ] Apply deployment (`tofu apply`).
    - [ ] **Validation:** Test with `curl` to ensure email is received.

## Phase 2: Android App Development
- [x] **Task F-1:** Project Initialization
    - [x] Create new Android Studio project (Compose Activity).
    - [x] Add Retrofit and Gson dependencies to `build.gradle`.
    - [x] Add `INTERNET` and `RECORD_AUDIO` permissions to Manifest.
- [x] **Task F-2:** Networking Layer
    - [x] Define `MeetingRequest` and `MeetingResponse` data classes.
    - [x] Create `ApiService` interface with POST method.
    - [x] Initialize `Retrofit` client singleton.
- [x] **Task F-3:** Voice Logic
    - [x] Implement `SpeechRecognizer` contract.
    - [x] Create a composable `RecordButton` that detects touch down/up events.
    - [x] Handle runtime permission request for Microphone.
- [x] **Task F-4:** UI & Integration
    - [x] Build Main Screen with State Hoisting.
    - [x] Connect `SpeechRecognizer` output to `ViewModel`.
    - [x] Trigger API call upon successful transcription.
    - [x] Show Toast/Snackbar on API success/failure.

## Phase 3: Final Polish
- [ ] **Task P-1:** Edge Case Handling
    - [ ] Handle "No internet connection" on Android.
    - [ ] Handle "Date not found" fallback in Python (Default to tomorrow).
- [ ] **Task P-2:** Integration Testing
    - [ ] Record a real meeting request ("Team sync next monday at 10am").
    - [ ] Verify the calendar invite opens correctly in Google Calendar/Outlook.

## Phase 4: Voice Todo Feature
- [x] **Task B-5:** Integrate MongoDB
    - [x] Provision Managed MongoDB Database in Scaleway (User Provided).
    - [x] Add `pymongo` to `requirements.txt`.
- [x] **Task B-6:** Implement Todo Logic
    - [x] Update `handler.py` to handle `todo` intent.
    - [x] Implement `save_to_mongodb(item)` using `pymongo`.
- [ ] **Task F-5:** Mobile Todo Mode
    - [ ] Add UI Selector for "Calendar" vs "Todo" mode.
    - [ ] Update ViewModel to send to `/todo` endpoint when in Todo mode.