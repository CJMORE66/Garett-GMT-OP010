# Repository Guidelines

## Project Structure & Module Organization
- `OP10_100A2/Program blocks/OP010/03_Auto/HMI` contains the actively maintained SCL blocks (for example `AutoProcessDataPopUp.scl` plus its companion DB files) that drive the OP10 station HMI behavior.
- `SZ23055_Garret_OP010/OP10_100A2` stores the previous delivery of the same logic, including shared PLC data types and tag definitions; diff it when validating refactors.
- Root-level documentation (`OP10_REFERENCE.md`, `OP10_REFERENCE_CZ.md`, `flowchart.mmd/svg`) describes the sequence flow; update these after any change to the automation narrative.
- Shared interface assets (PLC tag spreadsheets and SDF exports) live at the root so they can be synced with MES/I/O owners without digging into project folders.

## Build, Test, and Development Commands
- **TIA Portal Compile:** Inside the OP10_100A2 project, run `Project > Compile > Software (Ctrl+Shift+F7)` before committing new blocks to ensure DB signatures stay consistent.
- **PLCSim Run:** Use `Online > Start simulation` to execute the compiled project against PLCSim, focusing on OP010/03_Auto sequences and HMI popups.
- **Mermaid Diagram Refresh:** Regenerate the flowchart with `mmdc -i flowchart.mmd -o flowchart.svg` after altering process steps.

## Coding Style & Naming Conventions
- Keep SCL block declarations uppercase (`FUNCTION_BLOCK "AutoProcessDataPopUp"`) and indent logic with tabs or two spaces to match the existing Siemens export.
- Comment multi-step regions with the `REGION … END_REGION` pattern already present so structured view filtering keeps working.
- Data blocks that mirror HMI structures should use PascalCase (`AutoProcess_HMI`, `ProcessData`) and expose only the tags required for visualization; mark hidden members with `ExternalVisible := 'False'`.
- Python utility shims (currently `cgi.py`) follow PEP 8 and should include docstrings explaining their narrow purpose.

## Testing Guidelines
- Validate every SCL block change in PLCSim with both nominal and error-path indexes (e.g., AutoProcess indices 1 and 16) to exercise range checks.
- When adding tags, export `PLCTags.sdf` and compare against the Excel tracker to confirm MES-facing names remain stable.
- There is no automated coverage target yet; document manual test steps in the pull request so the next agent can replay them.

## Commit & Pull Request Guidelines
- Follow the existing short, imperative commit style (`Add PLC tag definitions`, `chANGES WITH RO BOT LOGIC`). Scope each commit to one functional area (HMI popup, PLC tags, docs).
- Pull requests must summarize logic changes, list affected blocks/DBs, link any issue IDs, and attach screenshots of updated HMI dialogs or diffs of exported tag tables when relevant.
