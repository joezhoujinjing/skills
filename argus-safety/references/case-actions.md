# Case Actions

## Table of Contents

- [Finding and Opening Cases](#finding-and-opening-cases)
- [Creating New Cases](#creating-new-cases)
- [Booking In Cases](#booking-in-cases)
- [Duplicate Checking](#duplicate-checking)
- [Saving Cases](#saving-cases)
- [Copying Cases](#copying-cases)
- [Closing Cases](#closing-cases)
- [Deleting Cases](#deleting-cases)
- [Medical Review](#medical-review)
- [Coding Review](#coding-review)
- [Printing](#printing)
- [Case Revisions](#case-revisions)

## Finding and Opening Cases

**Access:** Case Actions > Open

### Search Fields

| Field                     | Description                                                        |
| ------------------------- | ------------------------------------------------------------------ |
| Search For                | Multiple identifiers: Pri/Stdy/Othr/Cntr/Rptr/Pat separated by `/` |
| Date Range                | Select preset or Custom Date Range                                 |
| Follow-up option          | Search on Follow-up Dates (Significant and Non-Significant)        |
| Advanced Condition        | Click AC to create/select condition                                |
| Result from Argus Insight | Import Active Case Series from Insight                             |

**Recent cases:** Access 10 most recently-accessed cases under Active Cases.

**Auto-assignment:** Opening unassigned case in Edit mode auto-assigns to current user.

## Creating New Cases

**Access:** Case Actions > New

### Initial Case Entry Fields

| Field                   | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| Initial Receipt Date    | Date company became aware (full date required)          |
| Central Receipt Date    | Date received by Central Safety                         |
| Country of Incidence    | Where adverse event occurred                            |
| Report Type             | Determines available fields (e.g., Sponsored Trial)     |
| Study ID                | Select from Clinical Trial Selection (clinical trials)  |
| Center ID               | Select from Clinical Trial Selection (clinical trials)  |
| Initial Justification   | Configurable via Justifications dialog                  |
| Product Name            | Primary suspect product (click Select to search)        |
| Generic Name            | Auto-populated from product selection                   |
| Description as Reported | Verbatim event description                              |
| Onset Date/Time         | Event onset date/time                                   |
| ID                      | Reporter Reference, Case Reference, or Case number      |
| Journal/Title           | For literature cases (select from Literature Reference) |

## Booking In Cases

### Workflow

1. Case Actions > New
2. Enter preliminary case information
3. Click **Search** for duplicate check
4. If duplicate found → open existing case
5. If no duplicate → click **Continue**
6. Complete BookIn sections:
   - **Reported Causality**: Reporter's causality assessment
   - **Seriousness Criteria**: Check applicable boxes
   - **Attachments and References**
7. Click **BookIn**
8. System assigns case number (auto or manual)

### Attachments and References

**File Attachment:**

1. Click Add
2. Enter Classification and Description
3. Select "File Attachment" → Add
4. Browse and select file → Click B

**URL Reference:**

1. Select "URL Reference"
2. Enter URL after `http://`

**Documentum Link:**

1. Select "Documentum Link" → Add
2. Search in Document Lookup dialog

### Required Fields for BookIn

- Product
- Event
- Receipt Date
- Report Type
- Country of Incidence
- Seriousness

## Duplicate Checking

### Receipt Range Logic

| Condition                        | Search Range                                               |
| -------------------------------- | ---------------------------------------------------------- |
| No date entered                  | 90 days before to 2 days after System Date                 |
| Full Onset Date                  | 10 days before to 90 days after Onset Date                 |
| Full Initial Receipt Date        | 60 days before to 60 days after Receipt Date               |
| Partial Onset Date (year only)   | 10 days before end of prior year to 90 days after year end |
| Partial Receipt Date (year only) | 60 days before end of prior year to 60 days after year end |

**Note:** If no Receipt Date but Onset Date entered → searches 10 days before to 90 days after Onset Date.

Disable range limits by unchecking **Receipt Range Limits** checkbox.

Wildcard searches available on all text fields.

## Saving Cases

1. Click Case Number to open
2. Case Actions > Save
3. Click OK in saving dialog

## Copying Cases

Creates separate case with reference to original.

**Access:** Case Actions > Copy

### Workflow

1. Enter number of copies
2. Click Yes
3. Select portions to copy (or Select All)
4. Click Copy
5. System generates case ID (auto) or prompts for manual entry

**Note:** Null flavor data is copied with Case Form data.

## Closing Cases

**Access:** Case Actions > Close

1. Click Yes to save and close
2. Click No to close without saving

System behavior:

- Opens next active case if available
- Otherwise displays default Worklist
- If no default Worklist, shows Personal Argus Status

## Deleting Cases

**Access:** Case Actions > Delete

### Workflow

1. Enter justification (manual or select standard)
2. Enter Argus login password
3. Click OK

**Important:** Case information retained in database but inaccessible from application.

## Medical Review

**Access:** Case Actions > Medical Review

### Medical Review Tab

#### Case Narrative Section

- Select narrative field from dropdown
- View saved as default for future cases

#### Case Assessment Section

| Field                | Options              |
| -------------------- | -------------------- |
| Case Serious         | Yes/No               |
| Company Agent Causal | Select from dropdown |
| Listedness           | Select from dropdown |
| Case Outcome         | Select from dropdown |

#### Event Assessment Section

| Column                        | Description                  |
| ----------------------------- | ---------------------------- |
| Product                       | Product Name / Generic Name  |
| Causality as Reported         | Reporter's causality         |
| Causality as Determined       | Company's causality          |
| Event PT/Description/LLT      | Event coding details         |
| D/S                           | Diagnosis or Symptom         |
| Seriousness/Severity/Duration | Event characteristics        |
| Data Sheet                    | Agent datasheets             |
| License                       | Agent licenses               |
| As Determined Listedness      | System-determined listedness |

**Filtering options:** Product, Event, Diagnosis (D/S), Datasheet, Licenses

**Click actions:**

- Product Name → Product Information dialog
- Event Description → Event Information dialog
- License Description → License Product Information
- Datasheet Description → Configured datasheet terms

### Temporal View Tab

Read-only case view before routing.

#### Summary Section

- First Suspect Product
- Generic Name
- Coded Indication
- Company Agent Causal

#### Display Options

- Suspect Products
- Non-Suspect Products
- Patient History
- Patient Lab Data
- Relevant Tests
- Events (All or Serious Only)

#### Event Assessment Grid

| Column   | Description                            |
| -------- | -------------------------------------- |
| ID       | Event type (e.g., HOSP = Hospitalized) |
| Info     | Click (i) for details                  |
| Item     | Item name                              |
| Start    | Assessment start date                  |
| Stop     | Assessment end date                    |
| Duration | Assessment duration                    |

**Dialog boxes available:**

- Death Information
- Event Information
- Hospitalization Information
- Patient History
- Product Information (Temporal)

### Action Items/Additional Info Tab

Contains:

- Contact Log section
- Action Items section
- Notes and Attachments section

## Coding Review

**Access:** Case Actions > Coding Review

Single entry point for viewing and coding.

### Sections

**General Information:**

- Report Type
- Study Info
- Patient Info (age/gender)
- Literature Info

**Product Information:**

- Product Name
- Formulation
- Concentration/Units
- Reported Indication
- Coded Indication LLT (click Encode for dictionary)

**Event Information:**

- Preferred Term (LLT)
- Seriousness
- Intensity
- Duration

**Death Information:**

- Verbatim
- Coded PT (LLT)

**Patient Information:**

- Condition Type
- Verbatim
- Coded PT (LLT)

**Lab Data:**

- Test Name (LLT)
- Results
- Units
- Coded PT (LLT)
- Normal High/Low

**Parent Information:**

- Condition Type
- Verbatim
- Coded PT (LLT)

**Case Analysis:**

- Company Diagnosis/Syndrome
- Coded PT (LLT)

## Printing

**Access:** Case Actions > Print

### Print Case Form

1. Select sections to print (or Select All)
2. Click Print

### Letters Tab

- Click Description link to view letter
- Click Print to print

### Attachments Tab

- Date/time printed as footers (format: dd-mmm-yyyy hh24:mm:ss)
- Click Description link to view
- Click Print to print

### Transmit Tab

1. Select recipient from Available Recipients
2. Select Method
3. Enter Comments
4. Click Transmit

### Medical Summary

**Access:** Case Actions > Print > Medical Summary

Opens Medical Summary Report PDF.

## Case Revisions

**Access:** Case Actions > Case Revisions

### Case Details Dialog Shows:

- Scheduled Reports
- Submitted Reports
- Case Revisions

### Audit Log Details

- Lock icon = Locked state at revision
- Unlock icon = Unlocked state at revision
- Archive icon = Archived state at revision

### Follow-up Designations

- **(S) F/U** = Significant Follow-up
- **(NS) F/U** = Non-Significant Follow-up
