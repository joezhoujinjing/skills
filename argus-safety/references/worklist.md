# Worklist Management

## Table of Contents

- [Overview](#overview)
- [New and Open Tabs](#new-and-open-tabs)
- [Action Items](#action-items)
- [Reports](#reports)
- [Bulk Transmit](#bulk-transmit)
- [Bulk Print](#bulk-print)
- [Bulk ICSR Transmit](#bulk-icsr-transmit)
- [Local Labeling](#local-labeling)
- [Coding Status](#coding-status)
- [Letters](#letters)
- [Intake](#intake)

## Overview

Worklist menu displays:

- New cases created in system
- Cases assigned to users
- To-do items (letters, reports, action items)
- Transmission status of reports
- Bulk printed reports

## User Options (All Worklists)

| Option                 | Description                        | Available In                |
| ---------------------- | ---------------------------------- | --------------------------- |
| Open Read Only         | Open case read-only                | New, Open                   |
| Accept Case            | Accept and assign case             | New                         |
| View Case              | Open case                          | Action Items                |
| Accept Action Item     | Accept action item                 | Action Items                |
| Assign Action Item     | Assign to user (Workflow Managers) | Action Items                |
| Case Summary           | View case summary                  | Action Items, Open, Reports |
| Adjust Priority        | Modify priority (Workflow Manager) | New, Open                   |
| Close Multiple Cases   | Close multiple cases               | New, Open                   |
| Adjust Assignment      | Change assignment                  | New, Open                   |
| Close Case             | Close single case                  | New, Open                   |
| Adjust Case Owner      | Reassign owner (Workflow Manager)  | New, Open                   |
| Medical Review         | View Medical Review                | New, Open, Reports          |
| Coding Review          | View Coding Review                 | New, Open                   |
| Route Multiple Cases   | Route to workflow state            | New, Open                   |
| Print / Print Multiple | Print case forms                   | New, Open                   |

## New and Open Tabs

**Access:** Worklist > New or Worklist > Open

- **New**: Unaccepted/unassigned cases
- **Open**: Accepted and assigned cases

### Filter Options

| Filter            | Description                      |
| ----------------- | -------------------------------- |
| Workflow State    | Filter by current workflow state |
| Product           | Filter by product in case        |
| Event PT          | Filter by event preferred term   |
| Event as Reported | Event verbatim text              |
| Case Report Type  | Filter by report type            |
| Product Group     | Filter by product group          |

**View modes:** Individual, Group, View All

### Results Columns

| Column         | Description                                     |
| -------------- | ----------------------------------------------- |
| Lock Status    | Locked state icon + Initial/Follow-up indicator |
| Receipt Date   | Initial or latest follow-up date (configurable) |
| Aware Date     | Latest significant follow-up or initial receipt |
| Days Open      | Days since receipt to current date              |
| Days Remaining | Days until due per admin config                 |
| Event PT       | Primary event preferred term                    |
| Event Verbatim | Primary event as reported                       |
| S/U/R          | Serious/Unlisted/Related flags (Y/N/?)          |
| F, LT or H     | Fatal, Life-Threatening, Hospitalized           |
| Study ID       | Clinical study identifier                       |
| Reporter Type  | Primary reporter type                           |
| Assigned To    | Current owner or "Unassigned"                   |
| Owner          | Case owner                                      |

**SUSAR indicator:** Special icon in lock state column

## Action Items

**Access:** Worklist > Action Items

Shows complete action item description in Description field.

### Query Action Items

- Generated based on advanced condition rules
- Due Date = System Date + configured days
- Open Date = creation date
- Resolved queries auto-close action items

**Generate Queries:** Click icon or CTRL+ALT+X

### Query Attributes

| Attribute         | Description                               |
| ----------------- | ----------------------------------------- |
| Query Name        | Must begin with "QUERY\_"                 |
| Query Condition   | Advanced condition (if true, insert text) |
| Query Letter Text | Text for generated letter                 |
| Query Item Text   | Text for open queries list                |

**Letter placeholder:** `[OPEN_QUERY]` populates open queries

### Filter Options

- **View Query Action Items**: Show only query items
- **Overdue Action Items**: Due date before today

## Reports

**Access:** Worklist > Reports

### Filter Options

| Filter                  | Description                    |
| ----------------------- | ------------------------------ |
| Reporting Destination   | Agency name                    |
| Report Status           | Approved, Generated, Scheduled |
| Report Form             | Report description             |
| By Destination          | Multi-select agencies          |
| By Product Family       | Multi-select product families  |
| By Country of Incidence | Multi-select countries         |

### Results Columns

| Column                | Description                          |
| --------------------- | ------------------------------------ |
| Suspect Product       | Trade name ("+" = multiple suspects) |
| Diagnosis             | Primary Event Diagnosis PT           |
| Event Verbatim        | Primary event as reported            |
| F or LT               | Fatal or Life-Threatening            |
| 7/15                  | Due within 7 or 15 days              |
| Report Form           | Click link to view draft PDF         |
| Initial/Follow-up (#) | Report type with F/U number          |
| Downgrade             | Yes if downgrade report              |

### Report Options

| Option                           | Description                    |
| -------------------------------- | ------------------------------ |
| View Report                      | View PDF                       |
| Local Labeling                   | View labeling dialog           |
| Report Details                   | Open report details            |
| View Multiple Reports            | Open multiple reports          |
| Accept Report                    | Accept unassigned report       |
| Approve Report                   | Approve (Generated state only) |
| Mark for Non-Submission          | Mark not to submit             |
| Mark Multiple for Non-Submission | Bulk non-submission            |
| Mark Multiple for Approval       | Bulk approval                  |

## Bulk Transmit

**Access:** Worklist > Bulk Transmit

Lists transmission status for all cases.

### Columns

| Column             | Description            |
| ------------------ | ---------------------- |
| Report Form        | Click for draft PDF    |
| Recipient Company  | Recipient company name |
| Date Created       | Report creation date   |
| Date Sent          | Transmission date      |
| # of Pages         | Page count             |
| Attempts           | Transmission attempts  |
| Sender             | Sender name            |
| Lock State         | Case lock status       |
| Sender Agency Name | Generating agency      |
| Status             | Report status          |

### Options

| Option                        | Description                |
| ----------------------------- | -------------------------- |
| View Transmission             | View PDF                   |
| Mark report as Submitted      | Mark as submitted          |
| Remove transmission           | Remove failed transmission |
| Re-transmit                   | Regenerate and retransmit  |
| Submit Multiple Reports       | Bulk submit                |
| Re-transmit Multiple          | Bulk retransmit            |
| Remove Multiple Transmissions | Bulk remove                |

## Bulk Print

**Access:** Worklist > Bulk Print

Displays bulk print events.

### Options

| Option                     | Description                       |
| -------------------------- | --------------------------------- |
| Remove Print Job           | Remove from list                  |
| Re-print                   | Change status to pending, reprint |
| Submit Multiple Reports    | Bulk submit                       |
| Re-print Multiple          | Bulk reprint                      |
| Remove Multiple Print Jobs | Bulk remove                       |

## Bulk ICSR Transmit

**Access:** Worklist > Bulk ICSR Transmit

Shows ICSR reports awaiting submission.

### Reports Tab

**Search criteria:**

- Report type: E2B, eVAERS, eMDR
- Message Type (ichicsr for eMDR/eVAERS)
- Periodic Report (enabled for periodic message types)
- Date Range
- Show failures only checkbox
- Show error ACKs checkbox

**Status columns:** Transmit, EDI In, EDI Out, MDN Rec., ACK Rec.

**Options:**

- View Report Details (read-only)
- View ICSR Report (ICSR Viewer)
- ICSR Transmission History

### Messages Tab

Shows ESM messages (may contain multiple reports).

**Search criteria:**

- Report type
- Agency Trading Partners
- Transmit Date Range

**Options:**

- ICSR Transmission History
- View Acknowledgement
- View Reports
- View XML acknowledgement

## Local Labeling

**Access:** Worklist > Local Labeling

### Features

- Filter by Product Family
- Filter by Diagnosis (D) or Symptom (S)
- Filter by Datasheet
- Filter by License country

**Process button:** Triggers global and local rules for assessed licenses.

## Coding Status

**Access:** Worklist > Coding Status

### Status Icons

| Icon        | Meaning                                |
| ----------- | -------------------------------------- |
| Empty       | Not yet coded                          |
| Green check | Successfully coded                     |
| Pending     | Submitted to Central Coding, no result |
| Error       | Returned error from Central Coding     |

### Search Options

- Date Range (or Custom Date Range)
- Advanced Condition

### Results

| Column               | Description                                  |
| -------------------- | -------------------------------------------- |
| Seriousness Criteria | Fatal/Life-Threatening indicator             |
| Aging (Days)         | Days from receipt to coding completion       |
| Coding State         | Green check (complete) or red X (incomplete) |

## Letters

**Access:** Worklist > Letters

Lists all emails across all cases.

### Search Options

| Field                     | Description                        |
| ------------------------- | ---------------------------------- |
| Current Letter            | Select letter type                 |
| Date Range                | Filter by date                     |
| No previous notifications | Cases without prior correspondence |
| AC                        | Advanced Condition builder         |

## Intake

**Access:** Worklist > Intake

View incoming attachments for case creation.

### Pending Tab

| Field                 | Description               |
| --------------------- | ------------------------- |
| Priority              | Case priority             |
| Case Type             | Report type               |
| Reporter Type         | Primary reporter type     |
| Group                 | Current group owner       |
| Central Site/LAM Site | Current site              |
| Attachment Name       | Associated attachment     |
| Classification        | Attachment classification |
| Description           | Attachment description    |

### Rejected Tab

| Field          | Description                         |
| -------------- | ----------------------------------- |
| Generic Name   | Suspect product generic name        |
| F, LT or H     | Fatal/Life-Threatening/Hospitalized |
| Reporter Type  | Primary reporter type               |
| Country        | Country of incident                 |
| Classification | Attachment classification           |
| Description    | Attachment description              |
| Rejected Date  | Date of rejection                   |
