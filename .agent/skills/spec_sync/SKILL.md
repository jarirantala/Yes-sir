---
name: Spec Synchronizer
description: Checks for discrepancies between the codebase and the specification files.
---

# Spec Synchronizer Skill

This skill helps maintain consistency between code and documentation.

## 1. Identify Changes
Check which files have been modified (e.g., via `git status` or user input).

## 2. Check Triggers
If **Code** changes, verify **Spec**:

| Code Asset | Target Spec | Action |
| :--- | :--- | :--- |
| `backend/handler.py` (logic/flow) | `spec/design.md` | Check Sequence Diagrams. |
| `backend/llm_service.py` (prompts) | `spec/prompts.md` | Ensure system prompt matches. |
| `CommandResponse.kt` (schema) | `spec/api.md` | Update JSON schema definitions. |
| `MainActivity.kt` (UI) | `spec/android_design.md` | Update Screen Flow/UI description. |
| `Main Requirements` | `spec/requirements.md` | Ensure no new features crept in without REQ IDs. |

## 3. Report Discrepancies
*   If a disparity is found (e.g., new field in API but not in spec), flag it.
*   **Auto-Fix**: If allowed, verify the code source as truth and update the markdown spec.

## Usage
Run this skill after major refactors or before PR/Code Review.
