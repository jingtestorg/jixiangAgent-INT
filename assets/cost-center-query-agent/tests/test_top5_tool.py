"""Unit tests for top-5 cost centers tool invocation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def _setup_path(add_agent_to_path):
    """Ensure app/ is on sys.path for all tests in this module."""
    pass


@pytest.mark.asyncio
async def test_top5_query_returns_list():
    """Test that a top-5 query returns a formatted list of cost centers."""
    from agent import SampleAgent

    mock_tools = [
        MagicMock(
            name="list_a_costcenter_2_for_sap_self",
            description="Retrieve a list of cost center entities"
        )
    ]

    mock_result = {
        "messages": [
            MagicMock(content=(
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

    with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock, return_value=mock_result):
        result = await agent.invoke(
            query="What are the top 5 cost centers?",
            context_id="test-context-top5",
            tools=mock_tools,
        )

    assert result.status == "completed"
    assert "1000" in result.message or "cost center" in result.message.lower()


@pytest.mark.asyncio
async def test_top5_intent_classification():
    """Test intent classification for various top-5 phrasings."""
    from agent import SampleAgent

    agent = SampleAgent()

    top5_queries = [
        "What are the top 5 cost centers?",
        "Show me the top five cost centers",
        "List the top cost centers",
        "Give me the top-5 cost centers",
    ]
    for query in top5_queries:
        intent = await agent._m2_classify_intent(query)
        assert intent == "top5", f"Expected 'top5' for query: {query}"


@pytest.mark.asyncio
async def test_unrecognised_query_classification():
    """Test that unrelated queries are classified as unrecognised."""
    from agent import SampleAgent

    agent = SampleAgent()

    unrecognised_queries = [
        "What is the weather today?",
        "Book a meeting room",
        "Who is the CEO?",
    ]
    for query in unrecognised_queries:
        intent = await agent._m2_classify_intent(query)
        assert intent == "unrecognised", f"Expected 'unrecognised' for query: {query}"
