---
name: QA Runner
description: Runs automated tests for both Android (JUnit) and Backend (Unittest) to ensure system health.
---

# QA Runner Skill

This skill executes the test suites for the entire stack.

## 1. Backend Tests (Python)
*   **Scope**: Unit tests in `backend/`.
*   **Command**: `python3 -m unittest discover backend`
*   **Criteria**: All tests must PASS.
*   **Mocking**: Ensure tests mock external APIs (Scaleway, Mistral) to avoid costs/latency.

## 2. Android Tests (Kotlin)
*   **Scope**: Unit tests (logic verification).
*   **Command**: `./gradlew testDebugUnitTest` (Run from `android/` directory).
*   **Criteria**: All tests must PASS.

## 3. Health Report
Generate a summary:
```text
[PASS] Backend Tests (N tests)
[FAIL] Android Tests (x/y passed)
       - Error: [Detail]
```

## Usage
Run this skill before deployment or after significant logic changes.
