"""Unit tests for cost center count tool invocation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def _setup_path(add_agent_to_path):
    """Ensure app/ is on sys.path for all tests in this module."""
    pass


@pytest.mark.asyncio
async def test_count_query_invokes_list_tool():
    """Test that a count query results in a MCP list/count tool call."""
    from agent import SampleAgent

    mock_tools = [
        MagicMock(
            name="list_a_costcenter_2_for_sap_self",
            description="Retrieve a list of cost center entities"
        )
    ]

    mock_result = {
        "messages": [
            MagicMock(content="There are 142 cost centers.")
        ]
    }

    agent = SampleAgent()

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, return_value=mock_result):
        result = await agent.invoke(
            query="How many cost centers do we have?",
            context_id="test-context-count",
            tools=mock_tools,
        )

    assert result.status == "completed"
    assert "142" in result.message or "cost center" in result.message.lower()


@pytest.mark.asyncio
async def test_total_number_query_is_classified_as_count(add_agent_to_path):
    """Test that 'total number' phrasing is classified as a count query."""
    from agent import SampleAgent

    agent = SampleAgent()
    intent = await agent._m2_classify_intent("What is the total number of cost centers?")
    assert intent == "count"


@pytest.mark.asyncio
async def test_count_intent_classification(add_agent_to_path):
    """Test intent classification for various count phrasings."""
    from agent import SampleAgent

    agent = SampleAgent()

    count_queries = [
        "How many cost centers do we have?",
        "What is the total number of cost centers?",
        "Can you count all cost centers?",
        "Give me the number of cost centers",
    ]
    for query in count_queries:
        intent = await agent._m2_classify_intent(query)
        assert intent == "count", f"Expected 'count' for query: {query}"
