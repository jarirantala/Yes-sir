# Requirements: Personal Assistant System

## 1. Introduction
The **Personal Assistant System** is a modular, voice-first mobile application designed to help users manage their daily tasks, schedule, and communications. 
The application extends beyond a single utility, providing a platform for various assistant features.
**Feature #1 (Voice Calendar)** focuses on capturing spoken meeting details and automating calendar invitations.

## 2. User Stories
* **As a** busy professional, **I want** a single assistant app to handle various administrative tasks, **so that** I can save time.

### Feature 1: Voice Calendar
* **As a** user, **I want** to dictate meeting details quickly, **so that** I don't have to type them out manually.
* **As a** user, **I want** the system to automatically calculate dates (e.g., "Next Friday"), **so that** I don't have to look up the calendar.
* **As a** user, **I want** to receive an email invite immediately, **so that** I can add it to my calendar with one click.

### Feature 2: Voice Todo
* **As a** user, **I want** to capture random thoughts as tasks, **so that** I can review and check them off later.

### Feature 3: Second Brain (Notes)
* **As a** user, **I want** to dictate long-form notes or "brain dumps", **so that** they are stored as searchable text.
* **As a** user, **I want** these notes to be kept separate from my actionable todos, **so that** I can keep my focus clear.

### Feature 4: Public Transportation Helper
* **As a** user, **I want** to ask for public transit directions to a place, **so that** I can quickly get on my way.
* **As a** user, **I want** the system to provide a direct link to Google Maps transit directions, **so that** I don't have to manually search for it.

### Feature 5: Unified Assistant
* **As a** user, **I want** to just speak without selecting a specific mode, **so that** the assistant figures out if I mean a meeting, a todo, a note, or a navigation request automatically.

## 3. Functional Requirements (EARS Notation)

### 3.0 Platform / General
* **REQ-GEN-001:** **WHEN** the app launches, **THE SYSTEM SHALL** present a dashboard of available assistant features (currently starting with Voice Calendar).

### 3.1 Feature: Mobile Voice Capture (Unified)
* **REQ-F-001:** **WHEN** the user holds the record button, **THE SYSTEM SHALL** capture audio via the microphone to a local temporary file using `AudioRecorder`.
* **REQ-F-002:** **WHEN** the user releases the record button, **THE SYSTEM SHALL** stop recording and upload the audio file to the backend for transcription.
* **REQ-F-003:** **WHEN** transcription is complete, **THE SYSTEM SHALL** display the transcribed text on screen.
* **REQ-F-004:** **WHEN** a valid transcript is captured, **THE SYSTEM SHALL** automatically POST the transcript and the device's timezone to the backend `POST /command` endpoint.
* **REQ-F-005:** **WHEN** the API responds with a "meeting" type, **THE SYSTEM SHALL** show a "Invite Sent" confirmation toast.
* **REQ-F-006:** **WHEN** the API responds with a "todo" type, **THE SYSTEM SHALL** show a "Task Saved" confirmation toast.
* **REQ-F-007:** **WHEN** the API fails or returns an error, **THE SYSTEM SHALL** display the specific error message and details returned by the backend on the screen.
* **REQ-F-008:** **WHEN** a successful response is received, **THE SYSTEM SHALL** display the `parsed_data` JSON on the main screen for user verification.

### 3.2 Feature: Intent Recognition (Backend LLM)
* **REQ-B-020:** **WHEN** the `POST /command` endpoint receives a request, **THE SYSTEM SHALL** send the transcript to **mistral-small-3.2-24b-instruct-2506** for analysis.
* **REQ-B-021:** **THE SYSTEM SHALL** use **System Prompting** to define the assistant's persona and enforce a strict JSON output format.
* **REQ-B-022:** **THE SYSTEM SHALL** enable **JSON Mode** (if supported by the provider) or strictly enforce JSON structure via the prompt to ensure deterministic parsing.
* **REQ-B-023:** **THE SYSTEM SHALL** extract the following fields in the JSON output:
*   `intent`: One of "MEETING", "TODO", "NOTE", or "TRANSPORT".
    *   `title`: A concise summary, note content, or destination.
    *   `datetime`: ISO 8601 formatted date/time (for meetings).
    *   `duration`: Duration in minutes (for meetings).
    *   `priority`: One of "low", "medium", "high" (for todos).
    *   `destination`: The target location for navigation (for transport).
* **REQ-B-024:** **WHEN** the LLM fails to return valid JSON, **THE SYSTEM SHALL** treat it as a generic Todo.

### 3.3 Feature: Voice Calendar (Backend)
* **REQ-B-001:** **WHEN** the intent is **MEETING**, **THE SYSTEM SHALL** proceed with extraction logic.
* **REQ-B-002:** **WHEN** parsing the transcript, **THE SYSTEM SHALL** identify the meeting topic, start datetime, and duration.
* **REQ-B-003:** **WHEN** no date is specified in the text, **THE SYSTEM SHALL** default to "Tomorrow at 9:00 AM".
* **REQ-B-004:** **WHEN** no duration is specified, **THE SYSTEM SHALL** default to 60 minutes.
* **REQ-B-005:** **WHEN** parsing is complete, **THE SYSTEM SHALL** generate a valid iCalendar (`.ics`) file.
* **REQ-B-006:** **WHEN** the `.ics` file is ready, **THE SYSTEM SHALL** email it to the configured recipient using Scaleway Transactional Email (TEM).

### 3.4 Feature: Voice Todo (Backend)
* **REQ-B-010:** **WHEN** the intent is **TODO**, **THE SYSTEM SHALL** extract the task description and priority.
* **REQ-B-011:** **WHEN** the task is parsed, **THE SYSTEM SHALL** save the item to the MongoDB database.
* **REQ-B-012:** **WHEN** the item is saved, **THE SYSTEM SHALL** respond with the saved item ID.

### 3.5 Feature: Second Brain (Backend)
* **REQ-B-030:** **WHEN** the intent is **NOTE**, **THE SYSTEM SHALL** extract the note content as `title`.
* **REQ-B-031:** **WHEN** the note is parsed, **THE SYSTEM SHALL** save the note to the "notes" collection in MongoDB.
* **REQ-B-032:** **WHEN** the note is saved, **THE SYSTEM SHALL** respond with the note's text content and timestamp.

### 3.6 Feature: Public Transportation Helper (Backend)
* **REQ-B-040:** **WHEN** the intent is **TRANSPORT**, **THE SYSTEM SHALL** identify the destination.
* **REQ-B-041:** **THE SYSTEM SHALL** generate a Google Maps Deep Link using the format: `https://www.google.com/maps/dir/?api=1&destination=<DESTINATION>&travelmode=transit`.
* **REQ-B-042:** **THE SYSTEM SHALL** respond with the destination name and the generated deep link.

## 4. Non-Functional Requirements
* **NFR-001:** The backend cold start latency shall not exceed 5 seconds.
* **NFR-002:** The mobile app must handle runtime permissions for Microphone gracefully.
* **NFR-003:** API communication must be secured via HTTPS.
* **NFR-004:** The architecture must be extensible to support future assistant skills (e.g., Reminders, Notes).
* **NFR-005:** The system shall support persistent storage for Todo items with low latency (<100ms).