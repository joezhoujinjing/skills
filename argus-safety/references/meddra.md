# MedDRA Browser Reference

## Table of Contents

- [Overview](#overview)
- [MedDRA Hierarchy](#meddra-hierarchy)
- [Using the Browser](#using-the-browser)
- [Encoding Events](#encoding-events)
- [Encoding Indications](#encoding-indications)
- [MedDRA Recoding](#meddra-recoding)
- [Coding Status](#coding-status)

## Overview

MedDRA (Medical Dictionary for Regulatory Activities) is the international medical terminology used in Argus Safety for coding adverse events, medical history, and indications.

### Purpose

- Standardize adverse event terminology
- Enable regulatory reporting consistency
- Support signal detection and analysis
- Facilitate global safety data exchange

## MedDRA Hierarchy

MedDRA uses a five-level hierarchy:

| Level                 | Abbreviation | Description                                          | Example                      |
| --------------------- | ------------ | ---------------------------------------------------- | ---------------------------- |
| System Organ Class    | SOC          | Highest grouping by etiology, manifestation, purpose | Cardiac disorders            |
| High Level Group Term | HLGT         | Superordinate grouping                               | Cardiac arrhythmias          |
| High Level Term       | HLT          | Superordinate term linking PT to HLGT                | Supraventricular arrhythmias |
| Preferred Term        | PT           | Distinct concept for symptoms, signs, diagnoses      | Atrial fibrillation          |
| Lowest Level Term     | LLT          | Most specific; synonyms and lexical variants         | AF, Auricular fibrillation   |

### Term Relationships

- Each LLT links to exactly one PT
- Each PT links to at least one HLT
- PTs may have multiple SOC assignments (primary SOC designated)
- LLTs include current terms and non-current (legacy) terms

## Using the Browser

### Accessing MedDRA Browser

**From Case Form:**

- Events tab > Event Information > click Encode
- Products tab > Product Indication > click Encode
- Patient tab > Other Relevant History > click Encode

**From Menu:**

- Utilities > MedDRA Browser (standalone access)

### Browser Dialog Fields

| Field              | Description                          |
| ------------------ | ------------------------------------ |
| Search Term        | Enter partial or full term to search |
| Search Level       | LLT, PT, HLT, HLGT, or SOC           |
| Full Search        | Check for wildcard search (%term%)   |
| Current Terms Only | Exclude non-current LLTs             |

### Search Methods

| Method      | Syntax                | Example                                   |
| ----------- | --------------------- | ----------------------------------------- |
| Starts with | term                  | "head" finds "headache"                   |
| Contains    | %term% or Full Search | "%ache%" finds "headache", "stomach ache" |
| Exact       | "term" (quotes)       | "Headache" only                           |

### Search Results

- Results displayed in hierarchy view
- Click + to expand levels
- Click term to select
- Double-click to select and close

## Encoding Events

### Auto-Encode Mode

1. Enter verbatim in Description as Reported
2. Press TAB or ENTER
3. System searches MedDRA
4. If single match found → auto-populates
5. If multiple matches → browser opens for selection

### Manual Encode Mode

1. Enter verbatim in Description as Reported
2. Click Encode button
3. MedDRA Browser opens
4. Search and select appropriate term
5. Click Select

### Event Encoding Fields

| Field                   | Source                     |
| ----------------------- | -------------------------- |
| Description as Reported | User entry (verbatim)      |
| Event PT                | Selected Preferred Term    |
| Event LLT               | Selected Lowest Level Term |
| SOC                     | System Organ Class         |
| HLGT                    | High Level Group Term      |
| HLT                     | High Level Term            |

### Viewing Encoded Hierarchy

Click the encoding status icon next to any coded term to view complete MedDRA hierarchy.

## Encoding Indications

### Product Indication Encoding

1. Navigate to Products tab > Product Indication
2. Enter Reported Indication (verbatim)
3. Tab out for auto-encode or click Encode
4. Coded Indication LLT populated

### Patient History Encoding

1. Navigate to Patient tab > Other Relevant History
2. Enter Condition description
3. Tab out for auto-encode or click Encode
4. Coded PT (Description of condition LLT) populated

### Indication vs Event

| Field           | Dictionary | Use                 |
| --------------- | ---------- | ------------------- |
| Event Term      | MedDRA     | Adverse events      |
| Indication      | MedDRA     | Reason for drug use |
| Historical Drug | WHO Drug   | Past medications    |

## MedDRA Recoding

### When Recoding Occurs

- MedDRA version upgrade
- Term deprecation (non-current)
- Organizational changes in hierarchy

### Recoding Logic

| Scenario                      | Action                    |
| ----------------------------- | ------------------------- |
| LLT still current             | No change                 |
| LLT non-current, PT unchanged | Keep PT, flag LLT         |
| LLT non-current, PT changed   | May require manual review |
| Term deleted                  | Requires manual recoding  |

### Mass Recoding

Performed by system administrator:

1. Load new MedDRA version
2. Run recoding utility
3. Review exceptions
4. Manual correction of unmapped terms

## Coding Status

### Worklist > Coding Status

**Access:** Worklist > Coding Status

### Status Icons

| Icon         | Description                 |
| ------------ | --------------------------- |
| Empty circle | Not yet coded               |
| Green check  | Successfully coded          |
| Yellow clock | Submitted to Central Coding |
| Red X        | Error from Central Coding   |

### Search Filters

| Field              | Description                         |
| ------------------ | ----------------------------------- |
| Date Range         | Filter by date or Custom Date Range |
| Advanced Condition | Custom filter criteria              |

### Results Columns

| Column               | Description                                                            |
| -------------------- | ---------------------------------------------------------------------- |
| Case Number          | Case identifier                                                        |
| Seriousness Criteria | Fatal/Life-Threatening indicator                                       |
| Aging (Days)         | Days from receipt to coding completion (or current date if incomplete) |
| Coding State         | Green check (all coded) or Red X (incomplete)                          |

### Central Coding Integration

When configured for Central Coding:

1. Verbatim submitted to coding center
2. Status shows "Pending"
3. Coded term returned to Argus
4. Status updates to "Coded" or "Error"

## Coding Best Practices

### Verbatim Entry

- Enter exactly as reported
- Include relevant modifiers (severity, location)
- Don't pre-interpret or abbreviate

### Term Selection

- Select most specific appropriate LLT
- Verify PT accurately represents event
- Consider primary SOC for analysis

### Diagnosis vs Symptom

- **D (Diagnosis)**: Confirmed medical condition
- **S (Symptom)**: Individual sign/symptom
- Symptoms can be associated with a diagnosis

### Special Situations

| Situation         | Approach                                             |
| ----------------- | ---------------------------------------------------- |
| Multiple events   | Code each separately                                 |
| Syndrome          | Code syndrome PT; optionally code components         |
| Lab abnormality   | Use Lab Data section; code if clinically significant |
| Pregnancy outcome | Use appropriate pregnancy/fetal PT                   |

## WHO Drug Coding

### For Historical Drugs

1. Patient tab > Other Relevant History
2. Select Condition Type = Historical Drug
3. Enter drug name
4. Click Encode
5. WHO Drug Browser opens
6. Search by: Trade Name, Formulation, Strength, Country, Generic

### WHO Drug Formats

| Format     | Features                                           |
| ---------- | -------------------------------------------------- |
| WHO Drug B | Limited fields (no Formulation, Country, Strength) |
| WHO Drug C | Full fields available                              |

### WHO Drug Fields

| Field                | Description        |
| -------------------- | ------------------ |
| Trade Name           | Brand name         |
| Generic              | INN/generic name   |
| Formulation          | Dosage form        |
| Strength             | Drug strength      |
| Country              | Sales country code |
| Medicinal Product ID | WHO identifier     |
