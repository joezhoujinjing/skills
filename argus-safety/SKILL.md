---
name: argus-safety
description: Oracle Argus Safety pharmacovigilance database reference guide (Release 8.1.1). Use when answering questions about Argus Safety case management, adverse event reporting, regulatory submissions, MedDRA coding, worklist management, ICSR transmissions, or any pharmacovigilance workflow in Oracle Argus. Covers case entry, medical review, product/event tracking, compliance reports, and E2B submissions.
---

# Oracle Argus Safety Reference

Enterprise pharmacovigilance system for tracking adverse events, managing safety cases, and submitting regulatory reports.

## Quick Reference

| Task                                                                      | Reference File                                              |
| ------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Login, navigation, basic UI                                               | [getting-started.md](references/getting-started.md)         |
| Worklist queues, action items, bulk operations                            | [worklist.md](references/worklist.md)                       |
| Creating/opening/copying/deleting cases                                   | [case-actions.md](references/case-actions.md)               |
| Case Form tabs (General, Patient, Products, Events, Analysis, Activities) | [case-form.md](references/case-form.md)                     |
| Expedited, periodic, compliance reports                                   | [reports.md](references/reports.md)                         |
| E2B/ICSR electronic submissions                                           | [icsr-transmissions.md](references/icsr-transmissions.md)   |
| MedDRA coding and browser                                                 | [meddra.md](references/meddra.md)                           |
| Advanced conditions query builder                                         | [advanced-conditions.md](references/advanced-conditions.md) |
| Field descriptions and data entry rules                                   | [field-reference.md](references/field-reference.md)         |

## Core Concepts

### Case Lifecycle

1. **Book-in** — Initial case entry with product, event, receipt date
2. **Data Entry** — Complete Case Form (General, Patient, Products, Events, Analysis)
3. **Medical Review** — Causality assessment, narrative writing
4. **Coding** — MedDRA encoding of events/indications
5. **Report Generation** — Expedited/periodic reports scheduled
6. **Submission** — E2B/ICSR transmission to regulatory agencies
7. **Lock/Archive** — Case finalization

### Key Terminology

- **ICSR**: Individual Case Safety Report (E2B format)
- **MedDRA**: Medical Dictionary for Regulatory Activities
- **PT**: Preferred Term (MedDRA level)
- **LLT**: Lowest Level Term (MedDRA level)
- **S/U/R**: Serious/Unlisted/Related (case-level flags)
- **SUSAR**: Suspected Unexpected Serious Adverse Reaction
- **Null Flavor**: Coded reason for missing data (per E2B R3)

### Case Form Tabs

1. **General** — Case identifiers, study info, reporter details
2. **Patient** — Demographics, medical history, lab data
3. **Products** — Drugs/devices/vaccines with dosage regimens
4. **Events** — Adverse events with MedDRA coding, seriousness criteria
5. **Analysis** — Case assessment, narratives, regulatory info
6. **Activities** — Contact log, action items, routing

## Common Workflows

### Create New Case

1. Case Actions > New
2. Enter: Receipt Date, Country, Report Type, Product, Event
3. Click Search (duplicate check)
4. Click Continue > BookIn

### Medical Review

1. Case Actions > Medical Review
2. Complete Case Narrative
3. Assess causality (Reported vs Determined)
4. Review Event Assessment grid
5. Route case to next workflow state

### Generate Expedited Report

1. Reports > Compliance > Expedited Reports
2. Select agency/destination
3. Generate report
4. Review draft PDF
5. Approve and transmit

## Keyboard Shortcuts

| Shortcut     | Action                                 |
| ------------ | -------------------------------------- |
| CTRL+SHIFT+# | Go to tab (1=General, 2=Patient, etc.) |
| ALT+SHIFT+#  | Go to sub-entity (product/event #)     |
| CTRL+ALT+X   | Generate query action items            |

## Date Formats

Acceptable: `DDMMMYYYY`, `DDMMMYY`, `DDMMYYYY`
Separators: `.` `-` `/`
Example: `15-MAR-2024` or `15.03.2024`
