# Cost Center NL Query Agent

AI agent enabling Finance Controllers to query SAP S/4HANA cost center data via natural language.

## Business challenge

Finance Controllers need to answer department questions about cost center data in SAP S/4HANA Controlling — specifically the total count of cost centers and the top 5 cost centers — without running manual SAP transactions. Today this requires navigating SAP GUI, which takes ~30 minutes per query and requires SAP training.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Query resolution time for cost center questions | ~30 min (manual SAP transaction) | Under 1 minute | — | Overhead Cost Accounting / Financial Analytics | user |

## Key Milestones

1. **Agent receives NL query** — Controller submits a natural language question about cost centers via the agent interface.
2. **API call executed** — Agent translates the intent and calls the SAP S/4HANA Cost Center API (CE_COSTCENTER_0001).
3. **Data retrieved** — API response with cost center records is fetched successfully.
4. **Answer computed** — Agent computes total count and/or identifies top 5 cost centers from the data.
5. **Answer delivered** — Agent returns a clear, human-readable response to the controller without any SAP transaction required.

## Business Architecture (RBA)

### End-to-End Process

Finance (generic)

### Process Hierarchy

```
Finance (E2E)
└── Plan to Optimize Financials (generic)
    └── Plan and analyze financials (BPS-412)
        └── Perform financial analysis
        └── Perform management accounting
└── Record to Report (generic)
    └── Perform accounting and financial close (BPS-413)
        └── Perform financial reporting
```

### Summary

Finance Controllers querying SAP S/4HANA Controlling cost center data via natural language maps to the Finance E2E — specifically "Plan to Optimize Financials" (Management Accounting / Financial Analysis) and "Record to Report" (Financial Reporting) — enabling AI-driven, transaction-free cost center insights.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|-------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Query total count of cost centers via natural language | SAP S/4HANA Cloud — Overhead Cost Accounting, Financial Analytics | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | No | OData API available; no pre-built MCP server — agent calls API directly |
| Query top 5 cost centers via natural language | SAP S/4HANA Cloud — Overhead Cost Accounting, Financial Analytics | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | No | Same API used with sorting/top-N query parameters |
| Natural language understanding & intent routing | Custom AI agent required | — | — | — | — | — | Yes | No standard SAP NL interface for Controlling queries; custom Python agent needed |

### Key findings

- SAP S/4HANA Cloud (Public & Private Edition) covers Overhead Cost Accounting and Financial Analytics as mandatory capabilities for the targeted sub-processes.
- The Cost Center OData API (`CE_COSTCENTER_0001:v1`) is available and supports list/count operations suitable for both query types.
- No pre-built MCP server exists for the cost center APIs — the agent will integrate directly via the OData API.
- The only gap is the natural language interface itself, which requires a custom AI agent.
- APIs marked `unavailable` (on-premise variants) are excluded; cloud API `CE_COSTCENTER_0001` is the target.

## Recommendations

### AI Agent for Cost Center Natural Language Queries

#### Executive Summary

Python AI agent (A2A) querying SAP S/4HANA cost center data via OData API.

#### Recommended Solution

A pro-code Python agent using the A2A protocol. The agent accepts natural language questions from Finance Controllers, determines the intent (total count or top 5 cost centers), calls the SAP S/4HANA `CE_COSTCENTER_0001` OData API with appropriate query parameters, and returns a plain-language answer. No SAP GUI access or transaction knowledge is required by the controller.

#### Recommended solution category

AI Agent

#### Intent fit
95%
