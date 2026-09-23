# Specification: hello-world-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md`, `intent.md`)
- [x] Bootstrap agent code in `assets/hello-world-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/hello-world-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills needed — the response logic is a simple hardcoded value with no branching or domain-specific knowledge required.

---

## Project-Specific Tasks

## Hello World Response Logic

- [x] In `assets/hello-world-agent/app/agent_executor.py`, implement the agent response logic so that **any** user input results in the agent returning the string `"Hello World"`.
- [x] Ensure the system prompt in `assets/hello-world-agent/app/agent.py` instructs the agent to always respond with "Hello World" regardless of user input.

---

## Business Instrumentation

- [x] Implement business step instrumentation for milestones M1–M4 from the PRD: structured logging with pattern `[MILESTONE_ID].[achieved|missed]: [description]` and OpenTelemetry custom spans.
  - `M1.achieved: agent bootstrapped successfully` / `M1.missed: agent failed to start`
  - `M2.achieved: hello world response generated` / `M2.missed: response did not match expected value`
  - `M3.achieved: all tests passed` / `M3.missed: one or more tests failed`
  - `M4.achieved: agent deployed and responding` / `M4.missed: agent deployment failed or not reachable`
- [x] Extract business logic from `stream()` into a plain async helper to avoid `GeneratorExit` context errors.
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

No MCP tools or SAP API integrations required for this agent. Skip all MCP-related tasks.

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit test in `assets/hello-world-agent/tests/test_hello_world.py` verifying the agent returns "Hello World" for any input; run immediately after writing
- [x] Write one integration test executing end-to-end agent flow with mocked LLM responses (tests must run offline)
- [x] Run `pytest` from `assets/hello-world-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Verify `assets/hello-world-agent/app/agent.py` has exactly 9 decorated functions — run `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/hello-world-agent/app/agent.py` and confirm it returns 9
- [x] Run `pytest` again from `assets/hello-world-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/hello-world-agent/`
