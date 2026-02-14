# ICSR Transmissions Reference

## Table of Contents

- [Overview](#overview)
- [Transmission Types](#transmission-types)
- [Bulk ICSR Transmit](#bulk-icsr-transmit)
- [Transmission Stages](#transmission-stages)
- [Acknowledgments](#acknowledgments)
- [Troubleshooting](#troubleshooting)

## Overview

ICSR (Individual Case Safety Report) is the standard electronic format for transmitting adverse event reports to regulatory agencies worldwide.

### Supported Formats

| Format   | Description          | Agencies       |
| -------- | -------------------- | -------------- |
| E2B (R2) | ICH legacy format    | Various        |
| E2B (R3) | Current ICH standard | EMA, FDA, PMDA |
| eVAERS   | Electronic VAERS     | FDA (vaccines) |
| eMDR     | Electronic MDR       | FDA (devices)  |

### Message Types

- **ichicsr**: Standard ICSR message
- **Periodic**: For periodic ICSR submissions

## Transmission Types

### Individual Transmission

From Case Form > Regulatory Reports:

1. Select report
2. View Report Details > Transmission tab
3. Select recipients and method
4. Click Transmit

### Bulk Transmission

From Worklist > Bulk ICSR Transmit:

- Reports Tab: Individual ICSR reports
- Messages Tab: ESM messages (multiple reports)

## Bulk ICSR Transmit

**Access:** Worklist > Bulk ICSR Transmit

### Reports Tab

#### Search Criteria

| Field                   | Description                        |
| ----------------------- | ---------------------------------- |
| Report                  | E2B, eVAERS, or eMDR               |
| Message Type            | ichicsr (disabled for eMDR/eVAERS) |
| Periodic Report         | Enabled for periodic message types |
| Range                   | Date range selection               |
| Only show failures      | Filter to failed transmissions     |
| Show all with error ACK | Include error acknowledgments      |

#### Results Columns

| Column             | Description                    |
| ------------------ | ------------------------------ |
| Action             | Available user actions         |
| Local Company Name | Sending company                |
| Transmit           | Processing Report stage        |
| EDI In             | EDI In stage                   |
| EDI Out            | EDI Out stage                  |
| MDN Rec.           | MDN Received stage             |
| ACK Rec.           | Acknowledgment Received stage  |
| Status Details     | Latest failure/success message |

#### User Options

| Option                    | Description                |
| ------------------------- | -------------------------- |
| View Report Details       | Read-only report details   |
| View ICSR Report          | Open ICSR Viewer           |
| ICSR Transmission History | View transmission history  |
| Remove Transmission       | Remove failed transmission |
| Re-Transmit               | Regenerate and retransmit  |
| Mark as Submitted         | Manual submission override |

_Note: Options hidden for already-submitted reports_

### Messages Tab

Shows ESM (Electronic Submission Manager) messages containing multiple reports.

#### Search Criteria

| Field                   | Description           |
| ----------------------- | --------------------- |
| Report                  | E2B, eVAERS, or eMDR  |
| Agency Trading Partners | Target agency/partner |
| Transmit Date Range     | Date filter           |

#### Results Columns

| Column              | Description                  |
| ------------------- | ---------------------------- |
| Reports             | Number of reports in message |
| Action              | Available actions            |
| Trading Partner     | Agency/partner name          |
| EDI Receive Receipt | EDI receipt status           |
| Local Msg #         | Local message number         |
| Remote Msg #        | Remote message number        |
| File Name           | Message file name            |
| Transmit to EDI     | EDI transmit status          |
| EDI Tracking ID     | EDI tracking identifier      |
| EDI Transmit Date   | Transmission date            |

#### User Options

| Option                    | Description                 |
| ------------------------- | --------------------------- |
| ICSR Transmission History | View transmission history   |
| View Acknowledgement      | View ACK (if received)      |
| View Reports              | Open all reports in message |
| View XML acknowledgement  | View business-level ACK     |

## Transmission Stages

### Stage Flow

```
Transmit → EDI In → EDI Out → MDN Received → ACK Received
```

### Stage Legend

| Color  | Status       |
| ------ | ------------ |
| Grey   | Not started  |
| Yellow | In progress  |
| Green  | Complete     |
| Red    | Error/Failed |

### Stage Descriptions

| Stage        | Description                               |
| ------------ | ----------------------------------------- |
| Transmit     | Report being processed for transmission   |
| EDI In       | Received by EDI gateway                   |
| EDI Out      | Sent from EDI gateway to agency           |
| MDN Received | Message Disposition Notification received |
| ACK Received | Regulatory acknowledgment received        |

## Acknowledgments

### ACK Types

| Type         | Description                   |
| ------------ | ----------------------------- |
| Positive ACK | Successful receipt/processing |
| Error ACK    | Receipt with errors           |
| Rejection    | Report rejected               |

### Handling Error ACKs

1. Review error details in Status Details
2. Correct case data if needed
3. Regenerate report
4. Re-transmit

### Viewing Acknowledgments

- **View Acknowledgement**: Display ACK report (Messages tab)
- **View XML acknowledgement**: Raw XML business-level ACK

## Troubleshooting

### Common Issues

#### Transmission Failure

**Symptoms:** Red status in transmission stages
**Actions:**

1. Check Status Details for error message
2. Verify network/gateway connectivity
3. Re-transmit when resolved

#### Error ACK Received

**Symptoms:** ACK Received shows error
**Actions:**

1. View Acknowledgement for details
2. Correct data issues in case
3. Regenerate report
4. Re-transmit

#### Report Stuck in Pending

**Symptoms:** Transmit stage not progressing
**Actions:**

1. Check AG Service status
2. Verify report generation completed
3. Check gateway availability

### Bulk Operations

| Action                        | Description                         |
| ----------------------------- | ----------------------------------- |
| Re-transmit Multiple          | Retry multiple failed transmissions |
| Submit Multiple Reports       | Mark multiple as submitted          |
| Remove Multiple Transmissions | Clear multiple failed entries       |

### Manual Override

When automated transmission fails, use "Mark as Submitted" to:

- Record submission for audit trail
- Allow case workflow to proceed
- Document manual submission method

### Status Monitoring

**Access:** Reports > Report Generation Status

Filter by:

- Report Name
- Draft/Final
- Report Type
- Scheduled By
- Scheduled On
- Run At Date

### Gateway Configuration

Transmission settings configured in:

- Argus Console > System Configuration
- Trading Partner setup
- EDI Gateway configuration

_Contact system administrator for gateway issues._
