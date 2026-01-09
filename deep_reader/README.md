# TIA Portal V18 Deep Reader (evidence-first, pouze čtení)

Tato složka obsahuje analyzátor exportu Siemens TIA Portal (Openness XML). Logiku PLC nijak nemění – pouze čte exportní soubory a generuje reporty + offline SCL pro revizi.

## Spuštění (PowerShell)

Z kořene projektu:

```powershell
python deep_reader/tia_deep_reader.py --export-root EXPORT --out deep_reader/out
python deep_reader/generate_deliverables.py --out deep_reader/out --reports deep_reader/reports
python deep_reader/generate_unused_evidence_packs.py --out deep_reader/out --reports deep_reader/reports --evidence-dir deep_reader/evidence_unused
```

## Offline převod XML → SCL (pro čtení/porovnání)

```powershell
python deep_reader/xml_to_scl_export.py --export-root EXPORT --out deep_reader/scl_export
python deep_reader/generate_graph_scl_batch.py --export-root EXPORT --out deep_reader/scl_export/graph_generated
```

## Kde hledat výsledky

- Index: `deep_reader/reports/00_index.md`
- Reporty (CZ): `deep_reader/reports/01_project_comprehension_report.md` … `deep_reader/reports/06_zavislosti_a_ostrovy.md`
- Důkazní balíčky (režim 2): `deep_reader/evidence_unused/INDEX.md`
- Surová evidence: `deep_reader/out/`
- Offline SCL export: `deep_reader/scl_export/`
