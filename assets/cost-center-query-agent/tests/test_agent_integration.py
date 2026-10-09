"""Integration test: end-to-end agent flow with mocked LLM and MCP tools."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage


@pytest.fixture(autouse=True)
def _setup_path(add_agent_to_path):
    """Ensure app/ is on sys.path for all tests in this module."""
    pass


@pytest.mark.asyncio
async def test_full_count_flow():
    """Integration test: NL query → intent classification → API tool call → response."""
    from agent import SampleAgent

    # Mock the MCP tools returned by get_mcp_tools
    mock_cost_center_tool = MagicMock()
    mock_cost_center_tool.name = "list_a_costcenter_2_for_sap_self"
    mock_cost_center_tool.description = "Retrieve a list of cost center entities"

    # Mock LLM response simulating agent calling the tool and computing an answer
    mock_llm_response = {
        "messages": [
            AIMessage(content="There are 142 cost centers in the system.")
        ]
    }

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, return_value=mock_llm_response):
        result = await agent.invoke(
            query="How many cost centers do we have?",
            context_id="integration-test-count",
            tools=[mock_cost_center_tool],
        )

    assert result.status == "completed"
    assert result.message is not None
    assert len(result.message) > 0


@pytest.mark.asyncio
async def test_full_top5_flow():
    """Integration test: top-5 query flows through the full agent pipeline."""
    from agent import SampleAgent

    mock_cost_center_tool = MagicMock()
    mock_cost_center_tool.name = "list_a_costcenter_2_for_sap_self"
    mock_cost_center_tool.description = "Retrieve a list of cost center entities"

    mock_llm_response = {
        "messages": [
            AIMessage(content=(
                "Here are the top 5 cost centers:\n"
                "1. 1000 - Corporate Finance\n"
                "2. 2000 - Information Technology\n"
                "3. 3000 - Human Resources\n"
                "4. 4000 - Sales & Marketing\n"
                "5. 5000 - Operations"
            ))
        ]
    }

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, return_value=mock_llm_response):
        result = await agent.invoke(
            query="What are the top 5 cost centers?",
            context_id="integration-test-top5",
            tools=[mock_cost_center_tool],
        )

    assert result.status == "completed"
    assert result.message is not None
    # Should return a list of cost centers
    assert "1000" in result.message or "Corporate" in result.message


@pytest.mark.asyncio
async def test_fallback_on_api_failure():
    """Integration test: when the API fails, agent returns an error message (not a silent failure)."""
    from agent import SampleAgent

    mock_cost_center_tool = MagicMock()
    mock_cost_center_tool.name = "list_a_costcenter_2_for_sap_self"

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, side_effect=Exception("API unavailable")):
        result = await agent.invoke(
            query="How many cost centers do we have?",
            context_id="integration-test-error",
            tools=[mock_cost_center_tool],
        )

    assert result.status in ("completed", "error")
    # Must not return empty — user must be informed
    assert result.message is not None
    assert len(result.message) > 0


@pytest.mark.asyncio
async def test_milestone_logging(caplog):
    """Integration test: verify M1 and M2 milestones are logged during agent execution."""
    import logging
    from agent import SampleAgent

    mock_llm_response = {
        "messages": [AIMessage(content="There are 142 cost centers.")]
    }

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, return_value=mock_llm_response):
        with caplog.at_level(logging.INFO, logger="agent"):
            await agent.invoke(
                query="How many cost centers do we have?",
                context_id="test-milestone-logging",
                tools=[],
            )

    log_messages = [r.message for r in caplog.records]
    # M1 should be logged
    assert any("M1.achieved" in msg for msg in log_messages)
    # M2 should be logged with intent
    assert any("M2.achieved" in msg or "M2.missed" in msg for msg in log_messages)
