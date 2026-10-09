# Specification: cost-center-query-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read the project input (`product-requirements-document.md` and `intent.md`)
- [ ] Bootstrap agent code in `assets/cost-center-query-agent/` using instructions from the sap-agent-bootstrap section (invoke from inside `assets/cost-center-query-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills are needed — the query logic is simple (2 intents, single API, no multi-step workflows or domain-specific lookup tables). Instructions fit cleanly in the system prompt.

---

## Project-Specific Tasks

### MCP Server for Cost Center API

- [ ] Invoke `mcp-translation-file` skill with the downloaded API spec at `specification/cost-center-query-agent/api-specs/CE_COSTCENTER_0001.edmx` (OData, ORD ID: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`) to generate a translation file, limiting scope to cost center read operations
- [ ] Invoke `setup-solution` skill to create the MCP server asset for the generated translation file
- [ ] Read the generated `asset.yaml` of the MCP server and copy the `ordId` exactly for use in the agent's `requires`

MCP API: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`
MCP tool scope: read-only
Resources in scope: CostCenter

### Agent System Prompt

- [ ] In `assets/cost-center-query-agent/app/agent.py`, implement `get_system_prompt()` with instructions to:
  - Classify user intent as one of: (a) total cost center count, (b) list top 5 cost centers, (c) unrecognised query
  - For (a): call the cost center MCP tool with `$count=true` or retrieve all and count; return a sentence like "There are X active cost centers."
  - For (b): retrieve cost centers sorted by cost center ID (ascending), take top 5; return a formatted list with cost center ID and name
  - For (c): return a clear message that the query is not supported, with examples of supported questions
  - Always set page size (`top`) to a maximum of 100 when calling tools that support pagination
  - Never fabricate data; relay tool errors verbatim
  - Never call SAP APIs directly — use MCP tools only

### Cost Center Count Query (R1)

- [ ] Verify the agent correctly handles a natural language question about total cost center count (e.g. "How many cost centers do we have?")
- [ ] Confirm the response contains the correct integer count in a plain English sentence

### Top 5 Cost Centers Query (R2)

- [ ] Verify the agent correctly handles a natural language question about top 5 cost centers (e.g. "What are the top 5 cost centers?")
- [ ] Confirm the response contains a ranked list of 5 cost centers with their IDs and names

### Error Handling (R5)

- [ ] Implement fallback messaging for unrecognised queries — agent must return a clear, human-readable explanation
- [ ] Implement fallback messaging when the SAP API call fails — agent must return a clear error message, not silently fail

### MCP Wiring

- [ ] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module
- [ ] Add MCP server dependency to `assets/cost-center-query-agent/asset.yaml` under `requires` using the exact `ordId` from the generated MCP server asset

---

## Business Instrumentation

- [ ] Implement business step instrumentation for all 5 milestones from the PRD:

  | ID | Milestone | Log on achieved | Log on missed |
  |----|-----------|-----------------|---------------|
  | M1 | NL Query Received | `M1.achieved: natural language query received from controller` | `M1.missed: no query received or input was empty` |
  | M2 | Intent Classified | `M2.achieved: intent classified as [count\|top5]` | `M2.missed: intent could not be classified — returning fallback response` |
  | M3 | API Call Executed | `M3.achieved: cost center API call completed successfully` | `M3.missed: API call failed — [error detail]` |
  | M4 | Answer Computed | `M4.achieved: answer computed — [count value or top-5 list]` | `M4.missed: answer computation failed — empty or invalid API response` |
  | M5 | Answer Delivered | `M5.achieved: response delivered to controller` | `M5.missed: response delivery failed` |

- [ ] Add OpenTelemetry custom spans for each business step using `@tracer.start_as_current_span` decorator on regular async methods (not inside async generators)
- [ ] Extract business logic from `stream()` into a plain async helper (e.g. `_run_agent()`) to avoid `GeneratorExit` context errors; instrument `_run_agent()`
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [ ] Verify `specification/cost-center-query-agent/api-specs/CE_COSTCENTER_0001.edmx` exists (downloaded during spec generation)
- [ ] After `mcp-translation-file` and `setup-solution` complete, verify:
  - `specification/cost-center-query-agent/mcps/CE_COSTCENTER_0001/api-spec.edmx` exists
  - `specification/cost-center-query-agent/mcps/CE_COSTCENTER_0001/translation.json` exists
  - `specification/cost-center-query-agent/mcps/CE_COSTCENTER_0001/.tool-list.json` exists
- [ ] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP setup is complete

---

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit test for cost center count tool call (`tests/test_count_tool.py`) — run immediately after writing
- [ ] Write unit test for top-5 cost centers tool call (`tests/test_top5_tool.py`) — run immediately after writing
- [ ] Write one integration test (`tests/test_agent_integration.py`) exercising end-to-end flow: NL query → intent classification → API tool call → formatted response (mocked LLM and MCP tools, offline)
- [ ] Run `pytest` from `assets/cost-center-query-agent/` (no args)
- [ ] If coverage < 70%, add targeted tests and re-run
- [ ] Run `pytest` again (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/cost-center-query-agent/`
