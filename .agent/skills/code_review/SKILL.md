---
name: Code Review
description: Conducts a comprehensive code review focusing on clean code practices, security, and maintainability.
---

# Code Review Skill

This skill guides you through a systematic code review process for the **Yes-sir** project. Follow these steps to ensure code quality, security, and maintainability.

## 1. Preparation
*   **Identify Target Files**: Focus on modified or new files. Use `git diff --name-only` if applicable, or review the specific files mentioned by the user.
*   **Context**: Ensure you understand the purpose of the code (e.g., read associated specs).

## 2. Static Analysis Checklist
Scan the code for the following violations. If found, document them in the report.

### File & Function Size
*   [ ] **Files**: Should not exceed **200 lines**. (Refactor into modules/classes if larger).
*   [ ] **Functions**: Should not exceed **40 lines**. (Extract methods if larger).
*   [ ] **Nesting**: Avoid deep nesting (max 3 levels). Use guard clauses to flatten logic.

### Clean Code Practices
*   [ ] **Naming**: conform to language standards (snake_case for Python, camelCase for Kotlin).
*   [ ] **Variables**: Avoid single-letter names (`x`, `i`) or generic names (`data`, `temp`) unless in very short scopes.
*   [ ] **Comments**: Avoid "what" comments. Comments should explain "why". Prefer self-documenting code.
*   [ ] **Magic Numbers**: Replace hardcoded numbers/strings with named constants.

### Architecture & Design
*   [ ] **SRP (Single Responsibility Principle)**: Does a class/function do one thing?
*   [ ] **Dependency Injection**: Are dependencies passed in or hardcoded? (Hardcoded is bad for testing).
*   [ ] **State**: Is state managed explicitly (e.g., Sealed Classes) or loosely (Strings/Booleans)?

### Security
*   [ ] **Secrets**: NO API keys or passwords in the code. Use environment variables.
*   [ ] **Input Validation**: Are inputs validated before processing (especially in Backend handlers)?

## 3. Reporting
Generate a `code_review_report.md` (or similar) with your findings.

### Format
```markdown
# Code Review Report

## Summary
[Brief overview of health]

## Critical Issues
1. [File/Line]: [Issue Description] - [Recommendation]

## Improvements
1. [File/Line]: [Suggestion]

## Action Plan
*   [ ] [Step 1]
```
