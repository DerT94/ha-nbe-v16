# Changelog

## 0.1.1b1 — beta candidate

- Ignore scaled numeric inputs that cannot be represented, allowing subsequent valid measurements to recover normally.
- Omit unrecognized frame contents from debug messages.
- Include configured and actual raw TCP listener status in integration diagnostics without exposing addresses or payloads.
- Mark measurements unavailable quietly during planned stop or unload, while preserving reporting of actual connection failures.

Functional acceptance was performed on Home Assistant Core 2026.11.2 / Python 3.14.10. This beta declares HA 2026.11.2 as its minimum version. Existing config-entry and sensor unique IDs remain unchanged; no new runtime dependency or migration is required. Earlier HA versions are not qualified for this candidate.

Visual dialog verification and a passive 24-hour observation are release checks, not implied by the functional test results. Z-value mapping uncertainty remains documented in [mapping evidence](docs/mapping-evidence.md). No production release or GitHub release has been published by preparing this candidate.
