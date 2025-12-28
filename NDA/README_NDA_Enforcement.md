# NDA Enforcement (Per-build + Revocation)

This folder provides a minimal, dependency-light NDA enforcement layer you can plug into your app.

## What it does
- Pins NDA acceptance to a specific **build_id**, **nda_version**, and **nda_doc_sha256**
- Blocks app startup until acceptance exists for the current build/version/hash
- Writes append-only event logs (JSONL) + latest-state cache (JSON)
- Supports immediate revocation on suspected/confirmed NDA breach
- Exports audit events to CSV

## Files
- `nda_enforcement/` package
- `example_integration.py` shows how to wire enforcement into startup and acceptance
- `Tester_OnePage_Legal_Summary.pdf` is a tester-friendly summary handout

## Integration
1. Ship your NDA PDF with each build.
2. Compute the NDA SHA256 (at build time preferred) and pin it in config.
3. On app start, call:
   - `allowed, msg = on_app_start(cfg, tester_id)`
4. If blocked, show NDA + checkbox and capture "I Agree", then:
   - `record_acceptance(cfg, tester_name, tester_email, tester_id, acceptance_type="InApp")`
5. On breach:
   - `report_breach(cfg, tester_id, detail="...")`

## Storage location
Default is `%APPDATA%/AdvancedTapeRestorer/nda` on Windows or `~/.local/share/AdvancedTapeRestorer/nda`.
