# Personal Assistant

A modular, voice-first mobile application designed to assist with daily tasks and communications.

## Features
### 1. Voice Calendar
Listens to your voice, extracts meeting details, and emails you a calendar invite.
*   *Status:* Partially Implemented
*   *Key Tech:* Android (SpeechRecognizer), AWS Lambda, parsedatetime.

### 2. Voice Todo
Capture tasks and ideas quickly just by speaking. The system automatically identifies priorities and saves them to your list.
*   *Status:* Specification Phase
*   *Key Tech:* Valkey (Redis), Key-Value Store.

### 3. Unified Voice Commands
One button to rule them all. The system intelligently distinguishes between meeting invites and todo items based on natural language processing.


## Documentation
* **[Requirements](spec/requirements.md):** Functional and non-functional requirements (User Stories, EARS).
* **[Design & Architecture](spec/design.md):** System architecture and sequence diagrams.
* **[API Specification](spec/api.md):** Backend API endpoint definition.
* **[Data Dictionary](spec/data_dictionary.md):** Data models and parsing logic.
* **[Implementation Tasks](spec/tasks.md):** Step-by-step implementation plan.

## Project Structure
* `android/`: Android mobile application (Kotlin/Jetpack Compose).
* `spec/`: Documentation and specifications.
* `utils/`: Python helper modules (`parser.py`, `emailer.py`).
* `lambda-function.py`: AWS Lambda entry point.
* `requirements.txt`: Python dependencies for Lambda layer.

## Getting Started
See [tasks.md](spec/tasks.md) for the current development status and remaining work.
