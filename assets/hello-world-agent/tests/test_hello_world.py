"""Unit and integration tests for the Hello World Agent."""
import sys
import os
from pathlib import Path

# Add app/ to path for peer-level imports
APP_PATH = str(Path(__file__).parent.parent / "app")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── Unit Tests ──────────────────────────────────────────────────────────────

class TestHelloWorldResponse:
    """Unit tests for the Hello World agent response logic."""

    @pytest.mark.asyncio
    async def test_agent_returns_hello_world(self):
        """Agent stream() yields a completed response containing 'Hello World'."""
        from agent import SampleAgent
        from langchain_core.messages import AIMessage

        agent = SampleAgent()

        mock_result = {
            "messages": [AIMessage(content="Hello World")]
        }

        with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            responses = []
            async for chunk in agent.stream("Hi there", "test-ctx"):
                responses.append(chunk)

        completed = [r for r in responses if r.get("is_task_complete")]
        assert len(completed) == 1
        assert "Hello World" in completed[0]["content"]

    @pytest.mark.asyncio
    async def test_agent_stream_yields_working_status(self):
        """Agent stream() yields a working status update before completing."""
        from agent import SampleAgent
        from langchain_core.messages import AIMessage

        agent = SampleAgent()

        with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = {"messages": [AIMessage(content="Hello World")]}

            responses = []
            async for chunk in agent.stream("anything", "ctx-1"):
                responses.append(chunk)

        # First response should be a "working" status
        assert responses[0]["is_task_complete"] is False

    @pytest.mark.asyncio
    async def test_agent_responds_to_any_input(self):
        """Agent returns Hello World regardless of the input message."""
        from agent import SampleAgent
        from langchain_core.messages import AIMessage

        agent = SampleAgent()

        for user_input in ["hello", "What is 2+2?", "Tell me a joke", ""]:
            with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
                mock_invoke.return_value = {"messages": [AIMessage(content="Hello World")]}

                responses = []
                async for chunk in agent.stream(user_input, "ctx-2"):
                    responses.append(chunk)

            completed = [r for r in responses if r.get("is_task_complete")]
            assert len(completed) == 1, f"Expected completion for input: {user_input}"

    @pytest.mark.asyncio
    async def test_agent_handles_errors_gracefully(self):
        """Agent returns an error message when an exception occurs."""
        from agent import SampleAgent

        agent = SampleAgent()

        with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = Exception("LLM unavailable")

            responses = []
            async for chunk in agent.stream("anything", "ctx-err"):
                responses.append(chunk)

        completed = [r for r in responses if r.get("is_task_complete")]
        assert len(completed) == 1
        assert "error" in completed[0]["content"].lower()

    def test_system_prompt_contains_hello_world(self):
        """System prompt instructs agent to respond with Hello World."""
        from agent import get_system_prompt

        prompt = get_system_prompt()
        assert "Hello World" in prompt

    @pytest.mark.asyncio
    async def test_agent_invoke_returns_completed_status(self):
        """agent.invoke() returns AgentResponse with status=completed."""
        from agent import SampleAgent
        from langchain_core.messages import AIMessage

        agent = SampleAgent()

        with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = {"messages": [AIMessage(content="Hello World")]}

            response = await agent.invoke("test", "ctx-inv")

        assert response.status == "completed"
        assert response.message is not None


# ── Integration Test ─────────────────────────────────────────────────────────

class TestHelloWorldIntegration:
    """Integration test for end-to-end agent flow with mocked LLM."""

    @pytest.mark.asyncio
    async def test_end_to_end_hello_world_flow(self):
        """Full agent flow: input → stream → Hello World response (offline, mocked LLM)."""
        from agent import SampleAgent
        from langchain_core.messages import AIMessage

        agent = SampleAgent()

        # Mock the LLM at the graph level by patching _invoke_with_fallback
        with patch.object(agent, "_invoke_with_fallback", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = {
                "messages": [AIMessage(content="Hello World")]
            }

            all_chunks = []
            async for chunk in agent.stream("What do you say?", "integration-ctx"):
                all_chunks.append(chunk)

        # Verify working status was emitted
        assert any(not c["is_task_complete"] for c in all_chunks)
        # Verify final completion
        final = [c for c in all_chunks if c["is_task_complete"]]
        assert len(final) == 1
        assert final[0]["content"] == "Hello World"
        assert mock_invoke.called
