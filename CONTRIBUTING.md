# Contributing to Yes-sir

This document outlines the standard workflows and protocols for working on the **Yes-sir** project. Both human developers and AI agents should follow these guidelines to ensure quality and consistency.

## 🛠️ Operational Skills

We have defined specific **Skills** located in `.agent/skills/` to automate and standardize common tasks. **You MUST use these skills when performing the corresponding activities.**

| Activity | Condition | Required Skill | Path |
| :--- | :--- | :--- | :--- |
| **Code Review** | Before merging code, refactoring, or when requested. | [Code Review](.agent/skills/code_review/SKILL.md) | `.agent/skills/code_review` |
| **Deployment** | When `backend/` code changes and needs to go live. | [Deployment Manager](.agent/skills/deployment/SKILL.md) | `.agent/skills/deployment` |
| **Testing** | Before deployment or after logic changes. | [QA Runner](.agent/skills/qa_runner/SKILL.md) | `.agent/skills/qa_runner` |
| **Spec Update** | After code changes, refactors, or feature additions. | [Spec Synchronizer](.agent/skills/spec_sync/SKILL.md) | `.agent/skills/spec_sync` |

## 🚀 Workflows

### 1. Backend Development
1.  Make changes to `backend/`.
2.  Run **QA Runner** to ensure local tests pass.
3.  Perform **Code Review** on your changes.
4.  Run **Deployment Manager** to push to Scaleway.
5.  Run **Spec Synchronizer** to ensure documentation (`spec/`) matches code.

### 2. Android Development
1.  Make changes to `android/`.
2.  Run **QA Runner** to verify Android Unit Tests.
3.  Perform **Code Review**.
4.  Run **Spec Synchronizer** to ensure `android_design.md` maps to the new UI/Logic.

## 📝 Documentation Rules
*   Never update code without checking if the **Spec** needs updating.
*   All new features must have a Requirement ID in `requirements.md`.
