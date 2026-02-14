# Advanced Conditions Reference

## Table of Contents

- [Overview](#overview)
- [Creating Advanced Conditions](#creating-advanced-conditions)
- [Condition Elements](#condition-elements)
- [Operators](#operators)
- [Using Advanced Conditions](#using-advanced-conditions)
- [Query Action Items](#query-action-items)

## Overview

Advanced Conditions are custom query filters used throughout Argus Safety to:

- Filter case searches
- Define reporting rules
- Create action item triggers
- Generate aggregate reports
- Support workflow automation

## Creating Advanced Conditions

### Accessing the Builder

Click **AC** button anywhere Advanced Conditions are available:

- Case Open form
- Worklist filters
- Report configurations
- Aggregate reports
- Action Item codelist

### Builder Interface

| Section           | Description                      |
| ----------------- | -------------------------------- |
| Available Fields  | Case data elements to filter on  |
| Condition Builder | Build filter logic               |
| Operators         | Comparison and logical operators |
| Values            | Criteria values                  |
| Preview           | Test condition against database  |

### Basic Structure

```
[Field] [Operator] [Value]
```

Example:

```
Case Seriousness = "Yes"
```

### Combining Conditions

Use logical operators:

- **AND**: Both conditions must be true
- **OR**: Either condition can be true
- **NOT**: Negates condition

Example:

```
(Case Seriousness = "Yes") AND (Country of Incidence = "United States")
```

## Condition Elements

### Case-Level Fields

| Category       | Fields                                           |
| -------------- | ------------------------------------------------ |
| General        | Case Number, Report Type, Country, Receipt Date  |
| Classification | Case Classification, Seriousness, Listedness     |
| Study          | Study ID, Project ID, Center ID, Blinding Status |
| Workflow       | Workflow State, Assigned User, Case Owner        |

### Patient Fields

| Category     | Fields                               |
| ------------ | ------------------------------------ |
| Demographics | Age, Gender, Weight, Height          |
| History      | Medical History, Condition Type      |
| Pregnancy    | Pregnant, Gestation Period, LMP Date |
| Death        | Autopsy Done, Cause of Death         |

### Product Fields

| Category       | Fields                                   |
| -------------- | ---------------------------------------- |
| Identification | Product Name, Generic Name, Drug Code    |
| Classification | Suspect/Concomitant/Treatment, Drug Type |
| Dosage         | Dose, Frequency, Route, Duration         |
| Actions        | Action Taken, Dechallenge, Rechallenge   |

### Event Fields

| Category        | Fields                                  |
| --------------- | --------------------------------------- |
| Coding          | Event PT, Event LLT, SOC                |
| Characteristics | Seriousness Criteria, Severity, Outcome |
| Timing          | Onset Date, Stop Date, Duration         |
| Assessment      | Causality, Listedness, Expectedness     |

### Report Fields

| Category    | Fields                        |
| ----------- | ----------------------------- |
| Scheduling  | Due Date, Aware Date, License |
| Status      | Report State, Submission Date |
| Destination | Agency, Report Form           |

## Operators

### Comparison Operators

| Operator    | Description           | Use With        |
| ----------- | --------------------- | --------------- |
| =           | Equal to              | All types       |
| !=          | Not equal to          | All types       |
| >           | Greater than          | Numbers, Dates  |
| >=          | Greater than or equal | Numbers, Dates  |
| <           | Less than             | Numbers, Dates  |
| <=          | Less than or equal    | Numbers, Dates  |
| LIKE        | Pattern match         | Text            |
| NOT LIKE    | Pattern doesn't match | Text            |
| IN          | In list of values     | Multiple values |
| NOT IN      | Not in list           | Multiple values |
| IS NULL     | Field is empty        | All types       |
| IS NOT NULL | Field has value       | All types       |
| BETWEEN     | Within range          | Numbers, Dates  |

### Pattern Matching (LIKE)

| Pattern | Matches                          |
| ------- | -------------------------------- |
| `ABC%`  | Starts with "ABC"                |
| `%ABC`  | Ends with "ABC"                  |
| `%ABC%` | Contains "ABC"                   |
| `A_C`   | "A" + any single character + "C" |

### Logical Operators

| Operator | Description         |
| -------- | ------------------- |
| AND      | All conditions true |
| OR       | Any condition true  |
| NOT      | Negates condition   |
| ( )      | Group conditions    |

### Operator Precedence

1. NOT
2. AND
3. OR

Use parentheses to control evaluation order.

## Using Advanced Conditions

### Case Search

1. Case Actions > Open
2. Click AC button
3. Build or select condition
4. Click Search

### Worklist Filtering

1. Navigate to Worklist section
2. Click Advanced dropdown
3. Select or create condition
4. Apply filter

### Aggregate Reports

1. Reports > Aggregate Reports
2. In Advanced Condition field, click AC
3. Build condition
4. Include in report configuration

### Reporting Rules

_Configured in Argus Console_

- Define which cases trigger expedited reports
- Specify agency-specific rules
- Set scheduling criteria

### Saving Conditions

1. Build condition
2. Click Save/Memorize
3. Enter name
4. Select sharing option:
   - Private (user only)
   - Shared (specific groups)
   - Public (all users)

### Loading Saved Conditions

1. Click AC button
2. Select from dropdown
3. Modify if needed
4. Apply

## Query Action Items

### Overview

Query Action Items are automatically generated based on Advanced Conditions to prompt users about missing or questionable data.

### Configuration

_In Argus Console > Codelist > Action Item Type_

| Attribute         | Description                            |
| ----------------- | -------------------------------------- |
| Query Name        | Must begin with "QUERY\_"              |
| Query Condition   | Advanced Condition that triggers query |
| Query Letter Text | Text for generated letters             |
| Query Item Text   | Text for action item list              |

### Example Query

| Field       | Value                                        |
| ----------- | -------------------------------------------- |
| Name        | QUERY_Preg_LMP                               |
| Condition   | Patient is pregnant AND LMP Date is null     |
| Letter Text | Please provide Date of Last Menstrual Period |
| Item Text   | Patient missing Date of LMP                  |

### Triggering Queries

Queries generated when:

1. Case saved
2. Generate Query icon clicked (Quick Launch)
3. Shortcut: CTRL+ALT+X

### Query Resolution

- When condition no longer met, action item auto-closes
- System date used as close date
- No duplicate queries created for same condition

### Letter Placeholder

Use `[OPEN_QUERY]` in letter templates to include all open query text.

## Best Practices

### Performance

- Use indexed fields when possible
- Avoid complex nested conditions
- Limit use of LIKE with leading wildcards
- Test with Preview before saving

### Maintenance

- Document condition purpose
- Use meaningful names
- Review and update periodically
- Remove unused conditions

### Common Patterns

**Serious Cases:**

```
Case Seriousness = "Yes"
```

**US Cases with Specific Product:**

```
(Country of Incidence = "United States")
AND (Product Name LIKE "DRUGNAME%")
```

**Overdue Reports:**

```
(Report Due Date < SYSDATE)
AND (Report State = "Scheduled")
```

**Clinical Trial Cases:**

```
Report Type IN ("Sponsored Trial", "Investigator Initiated")
```

**Cases Requiring Follow-up:**

```
(Case Requires Follow-up = "Yes")
AND (Latest Contact Date IS NULL OR Latest Contact Date < SYSDATE - 30)
```
