# Yes-sir: Personal Voice Assistant

A modular, voice-first mobile application designed to assist with daily tasks and communications.

## Features

### 1. Unified Voice Interface
One simple "Hold to Speak" button for all interactions. The system intelligently captures your voice, transcribes it, and determines your intent using advanced LLM technology.

### 2. Intelligent Intent Recognition
Powered by **Mistral Small 3.2 (24B Instruct)**, the system automatically distinguishes between:
*   **Meeting Invites**: "Schedule a sync with the team tomorrow at 2 PM." -> Extracts Title, Date, Time, Duration.
*   **Todo Items**: "Remind me to buy milk urgently." -> Extracts Task Description and Priority (Low/Medium/High).
*   **Second Brain (Notes)**: "I just had an idea for a sci-fi novel about AI." -> Persists long-form thoughts.
*   **Transportation Helper**: "How do I get to Helsinki Central Station?" -> Generates direct Google Maps transit links.

### 3. Multilingual (English & Finnish)
*   **Full Finnish Support**: Speak and interact in Finnish!
*   **Whisper STT**: optimized with language hinting for high-accuracy Finnish transcription.
*   **Bilingual LLM**: Mistral natively understands Finnish commands and converts them to structured outcomes.

### 4. Voice Contexts
*   **Calendar**: Automatically extracts meeting details relative to your current time (e.g., "tomorrow").
*   **Tasks & Notes**: Persisted in **MongoDB** for later review.

## Technical Architecture

### Android Application (`android/`)
*   **Language**: Kotlin
*   **UI Framework**: Jetpack Compose
*   **Architecture**: MVVM with `Sealed Class` State Management.
*   **Audio**: Raw audio capture via `MediaRecorder` (AAC/M4A), uploaded directly to the backend.
*   **Network**: OkHttp/Retrofit for multipart audio upload and JSON API calls.

### Serverless Backend (`backend/`)
*   **Runtime**: Python 3.10+ (Scaleway Functions).
*   **Design**: Modular Controller Pattern.
    *   `handler.py`: Entry point and request routing.
    *   `llm_service.py`: Integration with **Mistral Small 3.2** for NLU and JSON extraction.
    *   `database.py`: MongoDB abstraction layer.
*   **Services**:
    *   **Speech-to-Text**: Scaleway STT API.
    *   **Database**: MongoDB (Atlas or Scaleway Managed).

## Documentation

*   **[Requirements](spec/requirements.md)**: Functional and non-functional requirements.
*   **[Design & Architecture](spec/design.md)**: System diagrams, data flow, and component descriptions.
*   **[Android Design](spec/android_design.md)**: Mobile app architecture and UI flow.
*   **[System Prompts](spec/prompts.md)**: The prompt engineering used for Mistral.
*   **[API Specification](spec/api.md)**: Backend endpoint contract.

## Project Structure

```text
├── android/                 # Android Studio Project
│   ├── app/src/main/java/   # Kotlin Source Code
│   │   ├── ...
│   │   ├── ui/
│   │   │   ├── VoiceUiState.kt      # State Management
│   │   │   └── components/
│   │   │       └── CommonComponents.kt # Reusable UI
│   └── ...
├── backend/                 # Python Serverless Function
│   ├── handler.py           # Main Entry Point
│   ├── llm_service.py       # Mistral Integration
│   ├── database.py          # Database Logic
│   └── requirements.txt     # Python Dependencies
├── spec/                    # Documentation
└── README.md                # Project Overview
```

## Getting Started

### 🤝 Contributing & Workflows
See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the project's standard operating procedures and available **Skills**.

### Backend Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on deploying the Python function to Scaleway.

### Android Setup
1.  Open `android/` in Android Studio.
2.  Sync Gradle.
3.  Build and Run on a physical device (Emulators may have microphone issues).
