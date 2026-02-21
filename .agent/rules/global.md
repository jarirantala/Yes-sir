---
trigger: always_on
---

# Project Standards: Android & Scaleway Backend

## 1. Android Development (Frontend)
- **Language:** Use Kotlin (latest stable) for all Android code. Avoid Java.
- **Architecture:** Follow MVVM (Model-View-ViewModel) with Clean Architecture principles.
- **UI Framework:** Use Jetpack Compose exclusively. No XML layouts unless explicitly requested.
- **Dependency Injection:** Use Hilt for DI.
- **Networking:** Use Retrofit with OkHttp and Kotlin Serialization for JSON.
- **Async:** Use Kotlin Coroutines and Flow for all asynchronous operations.

## 2. Scaleway Backend (Cloud)
- **Deployment:** All backend services must be containerized (Docker).
- **Database:** Use Scaleway Managed PostgreSQL.
- **Storage:** Use Scaleway Object Storage (S3-compatible) for file uploads.
- **Secrets Management:** Never hardcode API keys. Use environment variables or Scaleway Secret Manager.
- **API Design:** Follow RESTful principles and provide OpenAPI (Swagger) documentation.

## 3. Communication & Code Style
- **Commit Messages:** Use Conventional Commits (e.g., `feat:`, `fix:`, `chore:`).
- **Error Handling:** Always implement structured error handling. No empty `catch` blocks.
- **Testing:** - Android: Write UI tests with Espresso/Compose Test and Unit tests with JUnit5.
    - Backend: Minimum 70% code coverage for business logic.
- **Documentation:** All public functions must have KDoc (for Kotlin) or relevant docstrings.

## 4. Agent Constraints
- Before modifying Gradle files, always run a dependency check.
- If a change affects the API contract between Android and Scaleway, update the documentation artifact first.