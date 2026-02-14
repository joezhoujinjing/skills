# Reports Reference

## Table of Contents

- [Overview](#overview)
- [Expedited Reports](#expedited-reports)
- [Periodic Reports](#periodic-reports)
- [Aggregate Reports](#aggregate-reports)
- [Report Workflow](#report-workflow)
- [ICSR Transmissions](#icsr-transmissions)

## Overview

Argus Safety provides three main categories of reports:

| Type      | Purpose                              | Examples                                                |
| --------- | ------------------------------------ | ------------------------------------------------------- |
| Expedited | Single-case regulatory submissions   | MedWatch, CIOMS I, eVAERS, eMDR                         |
| Periodic  | Aggregate safety summaries over time | PSUR, PBRER, DSUR, IND Annual, NDA Periodic             |
| Aggregate | Case analysis and listings           | Case Data Analysis, CIOMS II Line Listing, Case Listing |

### Supported Expedited Report Forms

- US FDA MedWatch Drug/Device
- US FDA VAERS / eVAERS
- CIOMS I / CIOMS I (Local)
- French CERFA
- Spanish Spontaneous/Clinical
- E2B (R2/R3) ICSR
- eMDR (FDA Medical Device Reports)

## Expedited Reports

### Accessing Expedited Reports

| Location                           | Shows                                               |
| ---------------------------------- | --------------------------------------------------- |
| Case Form > Regulatory Reports tab | Reports for specific case                           |
| Worklist > Reports                 | All assigned reports (scheduled/generated/approved) |
| Reports > Compliance > Expedited   | All expedited reports                               |
| Reports > Compliance > Submitted   | All submitted reports                               |

### Report States

| State              | Description                          |
| ------------------ | ------------------------------------ |
| Scheduled          | Report created, awaiting generation  |
| Generated          | Report produced, awaiting approval   |
| Approved           | Report approved, awaiting submission |
| Submitted          | Report sent to regulatory agency     |
| New Data Available | New data received after generation   |
| Downgrade          | Report no longer required            |

### Lock State Icons

| Icon     | Meaning                                       |
| -------- | --------------------------------------------- |
| Locked   | Case is locked                                |
| Unlocked | Case is unlocked                              |
| SUSAR    | Suspected Unexpected Serious Adverse Reaction |
| Periodic | Case marked for Periodic ICSR submission      |

### Scheduling Reports

**Manual Scheduling:**

1. Open case
2. Regulatory Reports > Schedule New Reports
3. Enter fields:
   - Product (company product from case)
   - License # (country, type, number)
   - Aware Date (dropdown, descending order; "(A)" = Amendment)
   - Protect Confidentiality checkbox
4. Click OK
5. Save case

**Auto-Scheduling:**

1. Regulatory Reports > Auto Schedule (or Auto Schedule Device)
2. System schedules per Console Reporting Rules
3. Suppress Auto-scheduling in codelist prevents auto-scheduling for specific agencies

### Generating Reports

**Method 1: From Case Form**

1. Open locked case
2. Regulatory Reports tab > click Final link
3. Report generates

**Method 2: From Case Details**

1. Case Actions > Open > Search
2. Click Lock State icon > Case Details
3. Select report from Scheduled Regulatory Reports
4. Report generates automatically

**Draft vs Final:**

- Draft: Preview without case lock
- Final: Requires locked case

**Blinded Studies:**

- Users with unblind rights can choose blinded/unblinded version
- Blinded version hides: Study Drug info, Formulation, Concentration, Dose, Batch/Lot, Expiration

### Approving Reports

1. Open case
2. Regulatory Reports tab > click icon > View Report Details
3. Routing tab > State = "Approved"
4. Click Route > enter details > OK

### Batch Reports

1. Reports > Compliance > Expedited
2. Click Batch Print or Create Report
3. Search and select locked cases
4. Click Batch
5. Configure:
   - Format: As Draft or As Final
   - Save with case, mark as submitted (Final only)
   - Blind study product checkbox
   - Protect Confidentiality checkbox
   - Scheduling: Run Now or Run at [date/time]
6. Click OK

### Follow-up Reports

Triggered when significant follow-up entered in General tab.

**System behavior (per admin config):**

- Overwrite existing: Status becomes "New Data Available"
- Create new Follow-up: Original stays, new report scheduled
- Downgrade: Original marked "Downgrade" if no longer required

**eVAERS Follow-up from VAERS:**

- Transition VAERS → eVAERS schedules Follow-up (not Initial)
- Type shows: Initial(A1) or F/U# [Number](A1)

### Reporting Rules Algorithm

**Suppress Duplicate Reports (Drugs only):**
Duplicates matched by: Report Form, Reporting Destination, Aware Date

- If duplicates have different due dates → earliest due date scheduled

**Blinded/Forced Distribution:**

- Blind Study Product: Blinds active blinded studies on report
- Force Distribution: Generates/transmits on due date even if incomplete
- Dynamic comment replacement for force distribution

**IND Cover Letter Placeholder:**

- `IND_SIMILAR_EVENTS` table: Case Number, Protocol, Subject ID, Events
- Prints "None Submitted" if no prior reports

## Periodic Reports

### Report Types

| Type  | Full Name                               | Purpose                |
| ----- | --------------------------------------- | ---------------------- |
| PSUR  | Periodic Safety Update Report           | ICH safety summary     |
| PBRER | Periodic Benefit-Risk Evaluation Report | Updated ICH format     |
| DSUR  | Development Safety Update Report        | Clinical trial safety  |
| CTPR  | Clinical Trial Periodic Report          | EU/FDA trial reporting |
| IND   | Investigational New Drug Annual         | US FDA IND annual      |
| NDA   | New Drug Application Periodic           | US FDA post-market     |

### Creating Periodic Reports

**Access:** Reports > Periodic > [Report Type]

1. Click New Report (or Copy/Modify existing)
2. Configure tabs:
   - **Subject of Report**: Header, agencies, products
   - **Product Selection**: Ingredients, families
   - **Date/Time Range**: Reporting period
   - **Case Selection**: Criteria, filters
   - **Line Listings**: Fields to include
   - **Summaries**: Tabulations, narratives

### Report Output Options

- PDF (default)
- RTF (rich text)
- CSV (data export)
- Run Using: Argus Native or BI Publisher

### Scheduling Options

| Option  | Behavior                        |
| ------- | ------------------------------- |
| Run Now | Execute immediately             |
| Run at  | Schedule for specific date/time |

### Case Categorization

- **Initial**: First submission to agency/form/product
- **Follow-up**: Previously submitted to same agency/form/product

### Storing in Documentum

- Approved reports exported as PDF to Documentum
- Submitted status updated after successful fax/email transmission

## Aggregate Reports

**Access:** Reports > Aggregate Reports > [Report Type]

### Case Data Analysis

Cross-tabular analysis of cases over time.

**Configuration:**
| Field | Description |
|-------|-------------|
| Row1/Row2 | Group cases by row |
| Column1/Column2 | Group cases by column |
| Product Family | Filter by family |
| Selection for Row1 | Restrict row values |
| Advanced Condition | Custom filter |
| Report Number of Cases/Events | Count type |
| Event types | Serious/non-serious, listed/unlisted |
| Top N items | Limit displayed items |
| Show % of Total | Include percentages |
| Blinded | Hide blinded info |
| Use Case Search Results | Limit to prior search |

**Chart Types:**

- Bar Graph
- Line Chart
- Area
- Pie
- Donut
- Stacked

### CIOMS II Line Listing

Standard drug safety review format.

**Tabs:**

1. **Criteria**: Header, footer, product family, date range
2. **Line Listing**: Add/remove fields
3. **Grouping**: Elements, page breaks, sort order

### Case Listing

Flexible case report with custom fields.

**Configuration:**

1. Select fields from Available Fields
2. Use Move Up/Down to arrange
3. Check Blinded to hide info
4. Specify Advanced Condition
5. Set Date Range
6. Configure Sorting Order
7. Enter report title

### System Reports Library

**Access:** Reports > Aggregate Reports > System Report Library

Shows saved aggregate reports (created by user or shared).

**Filters:**

- Report Name
- Description
- Report Type
- Output Type
- Author
- Last Modified
- Available for Periodic
- Shared

**Actions:**

- Print: Execute report
- Open: Edit memorized report
- Transmit: Generate and send
- Delete: Remove (admin or creator only)

### Report Generation Status

**Access:** Reports > Report Generation Status

Shows both Aggregate and Periodic report statuses.

**Status Values:**
| Status | Description |
|--------|-------------|
| Pending | Awaiting execution |
| Executing | Currently running |
| Generated | Complete |
| Error | Failed |

## Report Workflow

### Standard Workflow

```
Schedule → Generate → Approve → Submit
```

### Report Details Dialog

**General Tab:**

- Agency (Reporting Destination)
- Responsibility (User Group)
- Case Nullification Date/Reason

**Scheduling Tab:**

- Reason for scheduling
- Scheduled date

**Routing Tab:**

- Group/User assignment
- Routing comments
- Route button

**Submission Tab:**

- Submission Required (Yes/No)
- Reason for Non-Submission

**Comment Tab:**

- Local comment for specific report

**Transmission Tab:**

- Available Recipients
- Transmission Method
- Comments
- Transmit button

### Unsubmitting Reports

1. Workflow Manager rights required
2. Case may need to be reopened from Archive
3. Enter password and notes
4. Enter reason for unsubmitting

## ICSR Transmissions

### E2B Report Types

| Format   | Use                    |
| -------- | ---------------------- |
| E2B (R2) | Legacy format          |
| E2B (R3) | Current ICH format     |
| eVAERS   | FDA vaccine electronic |
| eMDR     | FDA device electronic  |

### Transmission Flow

1. Report approved
2. Transmission initiated (Worklist > Bulk ICSR Transmit)
3. Stages: Transmit → EDI In → EDI Out → MDN Received → ACK Received
4. Status tracked per report and message

### Acknowledgment Handling

- ACK received confirms regulatory receipt
- Error ACKs require review and resubmission
- View XML acknowledgment available

### Troubleshooting

**Status columns indicate:**

- Green: Stage complete
- Yellow: In progress
- Red: Error/failure

**Actions for failures:**

- Re-transmit
- Mark as Submitted (manual override)
- Remove Transmission (for failed entries)
