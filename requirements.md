# Requirements: Voice-to-Calendar System

## 1. Introduction
A voice-first Android application that captures spoken meeting details, parses them using a serverless backend, and emails a structured calendar invitation (`.ics`) to the user.

## 2. User Stories
* **As a** busy professional, **I want** to dictate meeting details quickly, **so that** I don't have to type them out manually.
* **As a** user, **I want** the system to automatically calculate dates (e.g., "Next Friday"), **so that** I don't have to look up the calendar.
* **As a** user, **I want** to receive an email invite immediately, **so that** I can add it to my calendar with one click.

## 3. Functional Requirements (EARS Notation)

### 3.1 Mobile App (Frontend)
* **REQ-F-001:** **WHEN** the user holds the record button, **THE SYSTEM SHALL** capture audio via the microphone using `SpeechRecognizer`.
* **REQ-F-002:** **WHEN** the user releases the record button, **THE SYSTEM SHALL** stop recording and transcribe audio to text locally.
* **REQ-F-003:** **WHEN** transcription is complete, **THE SYSTEM SHALL** display the transcribed text on screen.
* **REQ-F-004:** **WHEN** a valid transcript is captured, **THE SYSTEM SHALL** automatically POST the transcript and the device's timezone to the backend API.
* **REQ-F-005:** **WHEN** the API responds successfully, **THE SYSTEM SHALL** show a "Invite Sent" confirmation toast.
* **REQ-F-006:** **WHEN** the API fails, **THE SYSTEM SHALL** display an error message to the user.

### 3.2 Backend (AWS)
* **REQ-B-001:** **WHEN** the API receives a request, **THE SYSTEM SHALL** validate that `transcript` and `timezone` fields are present.
* **REQ-B-002:** **WHEN** parsing the transcript, **THE SYSTEM SHALL** identify the meeting topic, start datetime, and duration.
* **REQ-B-003:** **WHEN** no date is specified in the text, **THE SYSTEM SHALL** default to "Tomorrow at 9:00 AM".
* **REQ-B-004:** **WHEN** no duration is specified, **THE SYSTEM SHALL** default to 60 minutes.
* **REQ-B-005:** **WHEN** parsing is complete, **THE SYSTEM SHALL** generate a valid iCalendar (`.ics`) file.
* **REQ-B-006:** **WHEN** the `.ics` file is ready, **THE SYSTEM SHALL** email it to the configured recipient using AWS SES.

## 4. Non-Functional Requirements
* **NFR-001:** The backend cold start latency shall not exceed 5 seconds.
* **NFR-002:** The mobile app must handle runtime permissions for Microphone gracefully.
* **NFR-003:** API communication must be secured via HTTPS.