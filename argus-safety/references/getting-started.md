# Getting Started with Argus Safety

## Table of Contents

- [Logging In/Out](#logging-inout)
- [Personal Argus Status](#personal-argus-status)
- [Quick Launch Toolbar](#quick-launch-toolbar)
- [Basic Features](#basic-features)
- [Field Validations](#field-validations)
- [Date Entry](#date-entry)
- [Null Flavors](#null-flavors)
- [Argus Insight Integration](#argus-insight-integration)

## Logging In/Out

### Login

1. Open Internet Explorer, enter Argus Safety URL
2. Enter username and password
3. Select database from dropdown, click Login

**Notes:**

- Incorrect password attempts configurable (default: 3)
- Date/time format uses 24-hour Web server format
- Use Application Access portlet for switching enterprises

### Logout

Click **Logout** on top-right frame

## Personal Argus Status

Home page displays:

- Cases assigned to logged-in user
- Contact Log entries
- Action Item entries

**Fields:**
| Field | Description |
|-------|-------------|
| Case Quick Launch | Enter case number to search |
| (Country) Case Number | Case with country in brackets |

## Quick Launch Toolbar

Located top-right of screen. Hover for tooltips.

| Icon                | Function                | Notes                       |
| ------------------- | ----------------------- | --------------------------- |
| New Case from Image | Create case from image  |                             |
| New Case            | Open Initial Case Entry |                             |
| Open Case           | Open Case Search        |                             |
| Close Case          | Close current case      |                             |
| Print Case          | Open Case Print dialog  |                             |
| Save Case           | Save with changes       |                             |
| Forward Case        | Route case forward      |                             |
| Return Case         | Route case back         |                             |
| Worklist            | Open Worklist           | Default to New if none set  |
| Lock Case           | Lock/Unlock case        | For Local PRPT cases only   |
| Local Lock          | Local lock toggle       | Visible for Local PRPT only |
| Medical Review      | Open Medical Review     |                             |
| Coding Review       | Open Coding Review      |                             |
| Draft Report        | View expedited reports  |                             |
| ICSR Check          | DTD validation          |                             |
| Validation Check    | Case validation         |                             |

**Shortcut visibility** driven by Common Profile switches and menu access rights.

## Basic Features

### Common Icons

| Icon              | Function                            |
| ----------------- | ----------------------------------- |
| Left/Right arrows | Page navigation                     |
| Notepad           | Notes dialog (filled = has content) |
| Up/Down arrows    | Reorder items                       |
| Sort arrow        | Current sort column                 |
| Orange dot        | Field justification needed          |
| Green dot         | Justification added                 |
| Red dot           | Mandatory validation error          |

## Field Validations

1. Click icon next to field for Field Justification dialog
2. Enter specific reason OR select standard reason
3. Click OK to overwrite warning
4. Orange icon → Green icon

**Validation types:**

- **Red** = Mandatory (must correct to save)
- **Orange** = Optional (enter justification to proceed)

### Field-Level Help

Double-click any field label to get information about that field.

### Change Password

1. Utilities > Change Password
2. Enter old password
3. Enter new password twice
4. Click OK

_Note: LDAP users cannot change passwords_

## Date Entry

**Format:** `dd-mmm-yyyy`

**Acceptable formats:**

- `DDMMMYYYY` (e.g., 15MAR2024)
- `DDMMMYY` (e.g., 15MAR24)
- `DDMMYYYY` (e.g., 15032024)

**Separators:** `.` `-` `/`

## Null Flavors

Used to describe reasons for missing data per E2B (R3) guidelines.

**Agencies supporting Null Flavors:** CBER, EMA, PMDA

### Usage

1. Click NF button next to field
2. Select Null Flavor from dropdown
3. Button changes grey → blue when selected

**Warning:** Selecting Null Flavor clears existing field data.

To replace Null Flavor with actual data: click NF button and enter data.

## Argus Insight Integration

_Enterprise Edition only_

### Share Case Series: Argus → Insight

1. Search and select case in Argus Safety
2. Open Argus Insight
3. Check "Make Active from Argus"
4. Case series becomes active in Insight

### Share Case Series: Insight → Argus

1. Case Actions > Open
2. Click "Result from Argus Insight"
3. Search results populated from Insight's Active Case Series

## Multi-Language Text

Certain fields support multiple languages for Expedited reports.

1. Click English language icon
2. Enter English text
3. Select language from dropdown
4. Enter text in selected language
5. Spell-check available

**Language icons:**

- English flag
- Japanese flag
- Globe (other languages)
