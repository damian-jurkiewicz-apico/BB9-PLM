# 🧾 Naming Conventions

This document defines consistent naming conventions used across the entire CNC machine system stack, including CAD components, IO signals, requirements, Jira tasks, Git branches, CSV exports, and automation scripts.

---

## 📦 Component Prefixes

| Prefix       | Meaning                            | Used In                                 | Example           |
|--------------|-------------------------------------|------------------------------------------|-------------------|
| `C_`         | Mechanical component                | Fusion 360, CSV (BOM), Jira, README      | `C_Table`, `C_Frame` |
| `EQ_`        | Equipment (drive, sensor, etc.)     | Fusion, IO Mapping                       | `EQ_LimitSwitch_Y+` |
| `CTX_`       | Contextual interface component      | CAD naming, sketches, requirements       | `CTX_Table_R5`    |

---

## 📡 IO Signal Identifiers

| Prefix       | Meaning                            | Used In                                | Example           |
|--------------|-------------------------------------|-----------------------------------------|-------------------|
| `IO_`        | Physical IO signal (In/Out)         | io_mapping.csv, PLC code, Jira          | `IO_HOME_X`, `IO_LIMIT_Y+` |

---

## 📑 Requirements

| Prefix       | Meaning                            | Used In                                | Example           |
|--------------|-------------------------------------|-----------------------------------------|-------------------|
| `REQ_`       | Engineering requirement             | `requirements/*.md`, Jira               | `REQ_CTX_TABLE_R5` |

---

## 🧰 Jira Task Identifiers

| Format       | Meaning                            | Used In                                | Example           |
|--------------|-------------------------------------|-----------------------------------------|-------------------|
| `KAN-xxx`    | Jira task key                      | Jira, Git commits, PR titles            | `KAN-5`           |

---

## 🌱 Git Branch Naming

| Format                           | Meaning                                  | Example                          |
|----------------------------------|-------------------------------------------|----------------------------------|
| `feature/KAN-xxx-description`    | Feature development branch                | `feature/KAN-5-io-mapping`       |
| `bugfix/KAN-xxx-fix`             | Bugfix branch                             | `bugfix/KAN-9-fix-limits`        |

---

## 🏷️ Git Tags

| Format             | Meaning                                | Example              |
|--------------------|-----------------------------------------|----------------------|
| `vX.Y-KAN-xxx`      | Tagged milestone for specific task       | `v0.1-KAN-5`         |
| `vX.Y-ZZZZ`         | General system version or milestone     | `v1.0-ALPHA`         |

---

## 🐍 Script Naming

| Format             | Used In          | Example                    |
|--------------------|------------------|----------------------------|
| `snake_case.py`     | `scripts/` folder | `export_sketch_area.py`    |
| `lowercase.csv`     | `fusion/`, `io/`  | `bom_2025-07-10.csv`       |

---

## 📘 Notes

- All identifiers (e.g. `C_`, `REQ_`, `IO_`) should be consistently reused across all artifacts: CAD, code, requirements, and Jira.
- Each Jira task should be traceable to a real system output: a file, a code module, a BOM change, etc.
- Consistent naming ensures full traceability and reduces ambiguity across disciplines (mechanical, electrical, control logic).

---
