# Project: TRACING (Garret) - Gemini Enhanced TIA Portal Tooling

This project comprises several components designed to enhance interaction with Siemens TIA Portal projects, primarily through analysis and AI-powered assistance. It combines offline analysis of TIA Portal exports with an in-IDE integration for context-aware information retrieval.

## 1. `deep_reader` (Python Analysis Tool)

A Python-based tool for comprehensive, evidence-first analysis of Siemens TIA Portal (Openness XML) export files. It focuses on extracting PLC logic, generating detailed reports, and providing offline SCL conversions.

*   **Purpose:** Reads TIA Portal XML exports to generate detailed reports on project structure, symbol usage, call dependencies, HMI tag mappings, and potential issues like absolute DB addressing or unused blocks. It does not modify PLC logic but provides insights for review and optimization.
*   **Main Technologies:** Python 3, XML parsing (ElementTree), CSV, JSON.
*   **Key Features:**
    *   Parses Program blocks (OB/FB/FC/DB), PLC data types (UDTs), PLC tags, HMI tags, and AutomationML hardware configuration.
    *   Infers read/write access to PLC symbols.
    *   Identifies call relationships between program blocks.
    *   Generates reports on project comprehension, unused elements analysis, monitoring consolidation blueprints, and migration roadmaps.
    *   Includes heuristics to identify "no-touch" critical components (e.g., safety-related blocks, critical OBs) and provides risk assessments.
    *   Converts XML exports to readable SCL for offline review and comparison.
*   **Building and Running:**
    1.  Ensure Python 3 is installed.
    2.  Navigate to the project root (`D:\AI_ANALYZE\GARRET\TRACING\OP10`).
    3.  Place TIA Portal Openness XML exports into the `EXPORT` directory.
    4.  Run the following commands from PowerShell:
        ```powershell
        python deep_reader/tia_deep_reader.py --export-root EXPORT --out deep_reader/out
        python deep_reader/generate_deliverables.py --out deep_reader/out --reports deep_reader/reports
        python deep_reader/generate_unused_evidence_packs.py --out deep_reader/out --reports deep_reader/reports --evidence-dir deep_reader/evidence_unused
        ```
*   **Output:** Generates various CSV, JSON, and Markdown reports in `deep_reader/out` and `deep_reader/reports`, including:
    *   `deep_reader/reports/01_project_comprehension_report.md`
    *   `deep_reader/reports/02_unused_elements_analysis.md`
    *   `deep_reader/reports/03_monitoring_consolidation_blueprint.md`
    *   `deep_reader/reports/04_migration_roadmap.md`
    *   `deep_reader/reports/05_risk_assessment_matrix.csv`
    *   `deep_reader/reports/no_touch_register.csv`
    *   Raw data such as `objects.csv`, `call_edges.csv`, `symbol_usage.csv`, `hmi_tags.csv`, `plc_tags.csv` in `deep_reader/out`.

## 2. `TIA_Gemini_AddIn` (C# TIA Portal Add-In)

A C# project designed as an Add-In for Siemens TIA Portal, integrating Google's Gemini AI directly into the engineering environment.

*   **Purpose:** Provides context-aware assistance to TIA Portal users by querying the Gemini API about selected TIA Portal objects.
*   **Main Technologies:** C#, .NET Framework, Siemens TIA Portal Openness API, Google Gemini API.
*   **Key Features:**
    *   Adds a "Ask Gemini" context menu item to the TIA Portal project tree.
    *   Upon selection, it constructs a prompt containing the name and type of the selected TIA Portal object.
    *   Calls the `gemini-1.5-flash` model via the Google Generative Language API.
    *   Displays Gemini's response in a standard `MessageBox` within TIA Portal.
*   **Development Conventions:** Standard C# .NET project structure, uses `Newtonsoft.Json` for JSON serialization/deserialization.
*   **Security Note:** Contains a hardcoded API key (`API_KEY`) for the Gemini API. This is generally not recommended for production environments and should be secured (e.g., via environment variables or a secure configuration management system).
*   **Building and Running:** As a TIA Portal Add-In, it needs to be compiled and installed within the TIA Portal environment. The solution file `TIA_Gemini_AddIn.sln` is present for building.

## 3. `.opencode` (Minimal JavaScript/Node.js Plugin Host)

This directory appears to host a minimal Node.js environment primarily to utilize the `@opencode-ai/plugin`.

*   **Purpose:** Likely serves as a wrapper or host for some specific functionality provided by the `@opencode-ai/plugin`, potentially for internal tooling or specialized AI-related tasks not directly integrated into TIA Portal itself.
*   **Main Technologies:** Node.js, `npm`/`bun` for package management.
*   **Key Files:** `package.json` (lists `@opencode-ai/plugin` as a dependency).
*   **Building and Running:** Standard Node.js package management (`npm install` or `bun install`) would be used to set up dependencies. Further execution would depend on the specific scripts or entry points defined by the `@opencode-ai/plugin` or a custom script in this directory (none explicitly identified yet beyond `package.json`).
