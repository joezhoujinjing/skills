# Case Form Reference

## Table of Contents

- [Overview](#overview)
- [General Tab](#general-tab)
- [Patient Tab](#patient-tab)
- [Products Tab](#products-tab)
- [Events Tab](#events-tab)
- [Analysis Tab](#analysis-tab)
- [Activities Tab](#activities-tab)

## Overview

Case Form captures case-specific information across multiple tabs.

### Limits

- Maximum Products: 200 per case
- Maximum Events: 200 per case
- Maximum Lab Data: 1500 entries
- Maximum Reporters: 100
- UDF Number fields: up to 3 decimal places

### Navigation Shortcuts

| Shortcut     | Action                                 |
| ------------ | -------------------------------------- |
| CTRL+SHIFT+# | Go to tab (1=General, 2=Patient, etc.) |
| ALT+SHIFT+#  | Go to sub-entity (1-10)                |

### Common Features

- Hyperlinks supported in Field Label Help
- E2B icon identifies E2B-required fields
- Mandatory fields from E2B mapping shown with icon
- Clipboard button on popup messages

## General Tab

### Dynamic Workflow Indicators

| Icon     | Status                           |
| -------- | -------------------------------- |
| No light | No timing defined                |
| Red      | Timing exceeded (negative value) |
| Yellow   | Timing in danger                 |
| Green    | Timing in good standing          |

_Not displayed on archived/locked cases_

### General Information Fields

| Field                   | Description                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| Report Type             | Determines field availability (Clinical Study, Literature)            |
| Country                 | Country where adverse event occurred                                  |
| Initial Receipt Date    | Date company became aware (cannot change after regulatory submission) |
| Central Receipt Date    | Date received by Central Safety                                       |
| Medically Confirm       | Whether confirmed by healthcare professional                          |
| Initial Justification   | Reason entered at book-in                                             |
| Case Requires Follow-up | Flag for follow-up needed                                             |
| Classification          | Up to 50 case classifications                                         |

### Amendments/Follow-ups

| Field                             | Description                        |
| --------------------------------- | ---------------------------------- |
| Follow-up Received Date           | Click Add to enter                 |
| Safety Received                   | Central Safety receipt date        |
| Significant                       | Checkbox for significant follow-up |
| Data Clean up                     | Mark as Data Clean up version      |
| Amendment                         | Updated without new information    |
| Amendment/Follow-up Justification | Standard or custom justification   |

**Sorting:** Serial Number, Follow-up Received Date, Central Received Date (default: descending by received date)

### Study Information

| Field              | Description                                           |
| ------------------ | ----------------------------------------------------- |
| Project ID         | Auto-creates Study ID list items                      |
| Center ID          | Select from list                                      |
| Study Phase        | Pre-populated from study config                       |
| Week #             | Week of adverse event                                 |
| Visit #            | Visit number                                          |
| Blinding Status    | Auto-populated; special rights needed for "Broken By" |
| Observe Study Type | Value from dropdown                                   |
| Unblinding Date    | Auto-populates when status changed                    |

### Reporter Information

- Maximum 100 reporters
- Primary reporter shown with blue tab and icon
- Reporter Rearrangement dialog shows First Name, Last Name, Reporter Type

| Field                   | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| Reporter Notes          | Free text with multi-language support                       |
| Institution ID          | Reporter's institution                                      |
| Protect Confidentiality | Hides name/address on reports ("MSK" null flavor in eVAERS) |
| Primary Reporter        | One per case; appears on regulatory reports                 |
| Correspondence Contact  | Address used in letters (multiple allowed)                  |
| Reporter ID             | Reporter identifier                                         |
| Reporter Type           | Administrator-maintained list                               |
| Report Media            | How report was received                                     |
| Intermediary            | Intermediary information                                    |

### Literature Information

Click Select to choose from pre-defined literature references.

## Patient Tab

### Patient Information Fields

| Field                         | Description                                           |
| ----------------------------- | ----------------------------------------------------- |
| Child only Case               | Pregnancy accessible from Parent tab only             |
| Current Medical Status        | History and current condition                         |
| Name (Title, First, MI, Last) | Patient name and initials                             |
| Number of Patients            | Patients involved in adverse event                    |
| Pat. ID                       | Patient Identifier (clinical trials)                  |
| Protect Confidentiality       | "PRIVACY" on reports; "MSK" in eVAERS                 |
| Randomization #               | Drug assignment (clinical trials)                     |
| Sponsor Identifier            | Sponsor's patient ID                                  |
| Patient Notes                 | Free text with multi-language and Null Flavor support |

### Patient Details

| Field           | Description                                   |
| --------------- | --------------------------------------------- |
| Ethnic Group    | Hispanic/Latino, Not Hispanic, etc.           |
| Military Status | Active Duty, Reserve, National Guard, TRICARE |
| Race            | Up to 5 races (no duplicates)                 |

### Pregnancy Information

_Enabled when Gender = Female and Pregnant = Yes_

| Field                     | Description                            |
| ------------------------- | -------------------------------------- |
| Gestation Period          | Period when reaction observed in fetus |
| Number of Fetus           | Neonate data entry                     |
| Prospective/Retrospective | When company learned of case           |

### Event Death Details

| Field                      | Description                                     |
| -------------------------- | ----------------------------------------------- |
| Autopsy Done?              | If No/Unknown, Results Available = No           |
| Autopsy Results Available? | Enabled only if Autopsy Done = Yes              |
| Add                        | Add Cause of Death / Autopsy Results (up to 50) |
| Delete                     | Delete highlighted row                          |

### Other Relevant History

| Field                       | Description                                       |
| --------------------------- | ------------------------------------------------- |
| Start/Stop Date             | Partial dates allowed                             |
| Age/Units                   | For Patient Other Relevant Therapy condition type |
| Family History              | For Medical History Episode condition types       |
| Ongoing                     | If Yes/Unknown, Stop Date disabled                |
| Coded PT/Description        | MedDRA encoding or WHO Drug for historical drugs  |
| Indication PT / Reaction PT | For Patient Other Relevant Therapy                |

**Actions:** Copy, Add, Delete rows

### Lab Data

| Field               | Description                                         |
| ------------------- | --------------------------------------------------- |
| Test Name           | Click Add Test to search; Select for Lab Test Group |
| Norm Low/High       | From test configuration or manual entry             |
| Result/Units        | Numeric result with units                           |
| Assessment          | Qualitative assessment term                         |
| More Info Available | Additional info in Activities tab                   |

**Features:**

- Maximum 1500 entries
- Sort by Date (chronological) or Test Name (alphabetical)
- Copy, Add, Delete, Reorder rows

### Parent Information

Similar to Patient tab; Family History, Age, Units unavailable.

## Products Tab

### Product Types

- **Drug** — Pharmaceutical products
- **Device** — Medical devices
- **Vaccine** — Immunizations

### Product Browser Search

Search by: Ingredient, Family, Product Name, Trade Name (License)

### WHO Drug Browser Search

Search by: Trade Name, Formulation/Strength, Country, Generic

Formats: WHO Drug B (limited fields), WHO Drug C (full fields)

### Drug Information

#### Product Information

| Field                         | Description                                 |
| ----------------------------- | ------------------------------------------- |
| Product Name                  | Select from company products or WHO Drug    |
| Suspect/Concomitant/Treatment | Drug involvement type                       |
| Generic Name                  | Auto-populated; shows Study Name if blinded |
| Product Identifier            | MPID, PhPID, etc.                           |
| Company Drug Code             | Licensed country code                       |
| Drug Code                     | WHO-DRUG code                               |
| WHO Medicinal Product ID      | From WHO drug selection                     |
| Formulation                   | Tablet, liquid, capsule, etc.               |
| Drug Authorization Country    | Company drug code                           |
| Manufacturer                  | Selectable from dropdown                    |
| Concentration                 | Drug amount; cannot modify for Study drug   |
| Interaction?                  | Drug interaction involvement                |
| Contraindicated?              | Used contrary to indication                 |
| Drug Not Administered         | No drug given to patient                    |

#### Substance Information

| Field          | Description        |
| -------------- | ------------------ |
| Substance Name | Ingredient name    |
| Strength       | Substance strength |
| Units          | mg, tsp, etc.      |

#### Product Indication

| Field               | Description                              |
| ------------------- | ---------------------------------------- |
| Reported Indication | As reported (auto-populated from config) |
| Coded Indication    | MedDRA encoded term                      |

#### Quality Control

| Field              | Description                   |
| ------------------ | ----------------------------- |
| QC Safety Date     | QC department reference       |
| QC Cross Reference | QC reference number           |
| CID Number         | Control Identification Number |
| PCID Number        | Product Control ID Number     |
| Lot Number         | Lot number lookup available   |
| QC Result Date     | Analysis result date          |
| QC Result          | Text explanation              |

#### Dosage Regimens

| Field                     | Description                                        |
| ------------------------- | -------------------------------------------------- |
| Start/Stop Date/Time      | Regimen dates (partial allowed)                    |
| Ongoing                   | If checked, Stop Date/Duration/Last Dose disabled  |
| Outside Therapeutic Range | Used outside label                                 |
| Duration of Regimen       | Calculated or manual (Inclusive/Exclusive setting) |
| Dose Description          | From Dose + Units + Frequency                      |
| Daily Dosage              | Calculated from dose × frequency                   |
| Regimen Dosage            | Calculated from daily dose × duration              |
| Accidental Exposure       | Type of accidental exposure                        |
| Pack Units                | Package presentation                               |

#### Product Details

| Field                                      | Description                                                   |
| ------------------------------------------ | ------------------------------------------------------------- |
| First Dose                                 | Earliest regimen start                                        |
| Last Dose                                  | Latest regimen stop                                           |
| Duration of Administration                 | Calculated from first/last doses                              |
| Total Dosage                               | Daily dose × duration                                         |
| Time Between First/Last Dose/Primary Event | Calculated intervals                                          |
| Total Dose to Primary Event                | Cumulative dose to event                                      |
| Action Taken                               | Drug action (Dose Increased disables dechallenge/rechallenge) |
| Dechallenge Results                        | Drug stopped to determine cause                               |
| Rechallenge Results                        | Drug taken again (Pos/Neg/UNK enables date fields)            |
| Gestation Period at Exposure               | Auto-calculated: First Dose - LMP Date                        |
| Taken Previously / Tolerated               | Previous use                                                  |
| Specialized Product Category               | FDA categories for eVAERS                                     |
| Abuse                                      | Patient abuse of product                                      |
| Batch/Lot tested                           | Specification compliance                                      |
| Tampering                                  | Apparent tampering                                            |

### Device Information

#### Device-Specific Fields

| Field                           | Description                                       |
| ------------------------------- | ------------------------------------------------- |
| M/W Info                        | MedWatch device information dialog                |
| EU/CA Device                    | European/Canadian device fields                   |
| Catalog #                       | Manufacturer's catalog number                     |
| UDI System                      | GS1, HIBCC, or ICCBBA                             |
| Unique Identifier (UDI) #       | Device/Production identifier                      |
| Operator of Device              | Healthcare Professional, Patient, Paramedic, etc. |
| Malfunction Type                | Per 21 CFR Part 803                               |
| Device Available for Evaluation | Availability and return date                      |
| CE Marked                       | Preloaded from License; modifiable                |

#### Malfunction Information

| Field                  | Description            |
| ---------------------- | ---------------------- |
| Reported Malfunction   | As reported            |
| Determined Malfunction | Company determination  |
| Listedness             | Malfunction listedness |
| Reportable             | Reportability status   |

#### Incident Information

Multi-record: Event Type Level 1, 2, 3 (cascading), Description

#### Investigation Results

Multi-record: Evaluation Type Level 1, 2, 3 (cascading), Description

#### Device Component Information

| Field             | Description         |
| ----------------- | ------------------- |
| Component Name    | Device component    |
| Component Term ID | Component term ID   |
| Version           | Term ID version     |
| Batch Lot #       | Component batch/lot |

### Vaccine Information

#### Vaccine-Specific Fields

| Field                   | Description        |
| ----------------------- | ------------------ |
| Route of Administration | How vaccine given  |
| Vaccination Site        | Body location      |
| Dose in Series          | Dose number        |
| Vaccinated at           | Type of facility   |
| Purchased by            | Funding source     |
| Prior Adverse Events    | Previous reactions |

#### Vaccine History

Captures prior vaccination history for the patient.

## Events Tab

### Event Information

| Field                   | Description                   |
| ----------------------- | ----------------------------- |
| Description as Reported | Verbatim event text           |
| Event Term              | MedDRA coded term             |
| Primary Event           | Main event for the case       |
| Onset Date/Time         | Event start                   |
| Stop Date/Time          | Event resolution              |
| Duration                | Calculated or manual          |
| Onset Latency           | Time from first dose to onset |
| Onset From Last Dose    | Time from last dose to onset  |

### Diagnosis-Event Relationship

- **D** = Diagnosis
- **S** = Symptom

Symptoms can be associated with a diagnosis.

### Seriousness Criteria

| Criterion                 | Description                   |
| ------------------------- | ----------------------------- |
| Death                     | Patient died                  |
| Life-Threatening          | Immediate risk of death       |
| Hospitalization           | Initial or prolonged          |
| Disability                | Significant incapacity        |
| Congenital Anomaly        | Birth defect                  |
| Other Medically Important | Requires medical intervention |

### Event Assessment

Causality assessment per product-event combination.

| Field                   | Description                    |
| ----------------------- | ------------------------------ |
| Causality as Reported   | Reporter's assessment          |
| Causality as Determined | Company's assessment           |
| Listedness              | On datasheet (Listed/Unlisted) |
| Expectedness            | Expected per label             |

## Analysis Tab

### Case Analysis

| Field                      | Description                     |
| -------------------------- | ------------------------------- |
| Case Serious               | Yes/No                          |
| Company Agent Causal       | Company causality determination |
| Case Listedness            | Overall listedness              |
| Case Outcome               | Resolution status               |
| Company Diagnosis/Syndrome | Company's diagnosis             |

### Case Summary/Narrative

Free text case narrative with multi-language support.

### MedWatch Info Tab

FDA-specific fields for 3500/3500A forms.

### BfArM Info Tab

German regulatory fields.

### AFSSaPS Info Tab

French regulatory fields.

## Activities Tab

### Contact Log

Records all correspondence related to the case.

| Field       | Description               |
| ----------- | ------------------------- |
| Date        | Contact date              |
| Method      | Phone, email, fax, etc.   |
| Contact     | Person contacted          |
| Description | Contact details           |
| Letter      | Associated correspondence |
| Date Sent   | When letter was sent      |

**Letter Generation:**

1. Click New Letter
2. Select template
3. Edit as needed
4. Save and attach

### Action Items

| Field       | Description              |
| ----------- | ------------------------ |
| Date Open   | Item creation date       |
| Date Due    | Completion deadline      |
| Completed   | Actual completion date   |
| Code        | Action item type         |
| Description | Auto-populated from code |
| Group/User  | Responsible party        |

### Notes and Attachments

| Type            | Description               |
| --------------- | ------------------------- |
| File Attachment | Uploaded files            |
| URL Reference   | Web links                 |
| Documentum Link | Document management links |

### Routing

| Field          | Description       |
| -------------- | ----------------- |
| Current State  | Workflow position |
| Current Group  | Assigned group    |
| Current User   | Assigned user     |
| Forward/Return | Routing options   |
| Comments       | Routing notes     |
