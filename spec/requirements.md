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
* **As a** user, **I want** to capture random thoughts as tasks, **so that** I don't forget them.
* **As a** user, **I want** these tasks to be saved to a list, **so that** I can review them later.

### Feature 3: Unified Assistant
* **As a** user, **I want** to just speak without selecting a specific mode, **so that** the assistant figures out if I mean a meeting or a todo automatically.

## 3. Functional Requirements (EARS Notation)

### 3.0 Platform / General
* **REQ-GEN-001:** **WHEN** the app launches, **THE SYSTEM SHALL** present a dashboard of available assistant features (currently starting with Voice Calendar).

### 3.1 Feature: Mobile Voice Capture (Unified)
* **REQ-F-001:** **WHEN** the user holds the record button, **THE SYSTEM SHALL** capture audio via the microphone using `SpeechRecognizer`.
* **REQ-F-002:** **WHEN** the user releases the record button, **THE SYSTEM SHALL** stop recording and transcribe audio to text locally.
* **REQ-F-003:** **WHEN** transcription is complete, **THE SYSTEM SHALL** display the transcribed text on screen.
* **REQ-F-004:** **WHEN** a valid transcript is captured, **THE SYSTEM SHALL** automatically POST the transcript and the device's timezone to the backend `POST /command` endpoint.
* **REQ-F-005:** **WHEN** the API responds with a "meeting" type, **THE SYSTEM SHALL** show a "Invite Sent" confirmation toast.
* **REQ-F-006:** **WHEN** the API responds with a "todo" type, **THE SYSTEM SHALL** show a "Task Saved" confirmation toast.
* **REQ-F-007:** **WHEN** the API fails or returns unknown intent, **THE SYSTEM SHALL** display an error message.

### 3.2 Feature: Intent Recognition (Backend)
* **REQ-B-020:** **WHEN** the `POST /command` endpoint receives a request, **THE SYSTEM SHALL** analyze the transcript for intent keywords.
* **REQ-B-021:** **WHEN** the transcript contains specific keywords (e.g., "meeting", "invite", "schedule"), **THE SYSTEM SHALL** classify the intent as **MEETING**.
* **REQ-B-022:** **WHEN** the transcript contains specific keywords (e.g., "todo", "task", "remind me"), **THE SYSTEM SHALL** classify the intent as **TODO**.
* **REQ-B-023:** **WHEN** no keywords match, **THE SYSTEM SHALL** default to **TODO** (fallback).

### 3.3 Feature: Voice Calendar (Backend)
* **REQ-B-001:** **WHEN** the intent is **MEETING**, **THE SYSTEM SHALL** proceed with extraction logic.
* **REQ-B-002:** **WHEN** parsing the transcript, **THE SYSTEM SHALL** identify the meeting topic, start datetime, and duration.
* **REQ-B-003:** **WHEN** no date is specified in the text, **THE SYSTEM SHALL** default to "Tomorrow at 9:00 AM".
* **REQ-B-004:** **WHEN** no duration is specified, **THE SYSTEM SHALL** default to 60 minutes.
* **REQ-B-005:** **WHEN** parsing is complete, **THE SYSTEM SHALL** generate a valid iCalendar (`.ics`) file.
* **REQ-B-006:** **WHEN** the `.ics` file is ready, **THE SYSTEM SHALL** email it to the configured recipient using AWS SES.

### 3.4 Feature: Voice Todo (Backend)
* **REQ-B-010:** **WHEN** the intent is **TODO**, **THE SYSTEM SHALL** extract the task description and priority.
* **REQ-B-011:** **WHEN** the task is parsed, **THE SYSTEM SHALL** save the item to the persistent key-value store.
* **REQ-B-012:** **WHEN** the item is saved, **THE SYSTEM SHALL** respond with the saved item ID.

## 4. Non-Functional Requirements
* **NFR-001:** The backend cold start latency shall not exceed 5 seconds.
* **NFR-002:** The mobile app must handle runtime permissions for Microphone gracefully.
* **NFR-003:** API communication must be secured via HTTPS.
* **NFR-004:** The architecture must be extensible to support future assistant skills (e.g., Reminders, Notes).
* **NFR-005:** The system shall support persistent storage for Todo items with low latency (<100ms).