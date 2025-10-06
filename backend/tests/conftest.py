"""
Pytest configuration and global fixtures.

This module provides global mocking for external dependencies to ensure
tests can run without requiring actual API credentials or external services.
All imports of third-party services (Supabase, Retell, OpenAI) are mocked
at the module level before application code is imported.
"""

import sys
from unittest.mock import MagicMock, AsyncMock, Mock
import pytest


# Mock Supabase before any imports
class MockSupabaseClient:
    """Mock Supabase client."""
    
    def __init__(self, *args, **kwargs):
        self.table_mock = MagicMock()
        
    def table(self, table_name):
        """Mock table method."""
        mock = MagicMock()
        # Setup fluent interface
        mock.select.return_value = mock
        mock.insert.return_value = mock
        mock.update.return_value = mock
        mock.eq.return_value = mock
        mock.order.return_value = mock
        mock.execute.return_value = MagicMock(data=[])
        return mock


# Mock Retell SDK classes
class MockRetellLLM:
    """Mock Retell LLM API."""
    
    async def create(self, *args, **kwargs):
        """Mock create LLM."""
        mock_result = MagicMock()
        mock_result.llm_id = "mock-llm-id"
        return mock_result
    
    async def update(self, llm_id, *args, **kwargs):
        """Mock update LLM."""
        return True


class MockRetellAgent:
    """Mock Retell Agent API."""
    
    async def create(self, *args, **kwargs):
        """Mock create agent."""
        mock_result = MagicMock()
        mock_result.agent_id = "mock-agent-id"
        mock_result.agent_name = kwargs.get('agent_name', 'Mock Agent')
        return mock_result


class MockRetellCall:
    """Mock Retell Call API."""
    
    async def create_web_call(self, *args, **kwargs):
        """Mock create web call."""
        mock_result = MagicMock()
        mock_result.call_id = "mock-retell-call-id"
        mock_result.access_token = "mock-access-token"
        return mock_result
    
    async def create_phone_call(self, *args, **kwargs):
        """Mock create phone call."""
        mock_result = MagicMock()
        mock_result.call_id = "mock-retell-call-id"
        return mock_result


class MockAsyncRetell:
    """Mock AsyncRetell client."""
    
    def __init__(self, *args, **kwargs):
        self.llm = MockRetellLLM()
        self.agent = MockRetellAgent()
        self.call = MockRetellCall()


# Mock OpenAI classes
class MockChatCompletionMessage:
    """Mock OpenAI chat completion message."""
    
    def __init__(self, content='{}'):
        self.content = content


class MockChatCompletionChoice:
    """Mock OpenAI chat completion choice."""
    
    def __init__(self, message=None):
        self.message = message or MockChatCompletionMessage()


class MockChatCompletion:
    """Mock OpenAI chat completion."""
    
    def __init__(self):
        self.choices = [MockChatCompletionChoice()]


class MockChatCompletions:
    """Mock OpenAI chat completions API."""
    
    async def create(self, *args, **kwargs):
        """Mock create completion."""
        return MockChatCompletion()


class MockChat:
    """Mock OpenAI chat API."""
    
    def __init__(self):
        self.completions = MockChatCompletions()


class MockAsyncOpenAI:
    """Mock AsyncOpenAI client."""
    
    def __init__(self, *args, **kwargs):
        self.chat = MockChat()


# Create mock modules
class MockSupabaseModule:
    """Mock supabase module."""
    Client = MockSupabaseClient
    
    @staticmethod
    def create_client(*args, **kwargs):
        return MockSupabaseClient()


class MockRetellModule:
    """Mock retell module."""
    AsyncRetell = MockAsyncRetell
    Retell = MockAsyncRetell  # Alias in case both are used


class MockOpenAIModule:
    """Mock openai module."""
    AsyncOpenAI = MockAsyncOpenAI
    OpenAI = MockAsyncOpenAI  # Also provide sync version


# Install mocks into sys.modules before any application imports
sys.modules['supabase'] = MockSupabaseModule()
sys.modules['retell'] = MockRetellModule()
sys.modules['openai'] = MockOpenAIModule()


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """
    Automatically mock required environment variables for all tests.
    This ensures tests don't fail due to missing environment configuration.
    """
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("RETELL_API_KEY", "test-retell-key")
    monkeypatch.setenv("RETELL_WEBHOOK_SECRET", "test-webhook-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "https://test.ngrok.io")


@pytest.fixture
def mock_supabase_client():
    """Provide a mock Supabase client for tests."""
    return MockSupabaseClient()


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client for tests."""
    return MockAsyncOpenAI()


@pytest.fixture
def mock_retell_client():
    """Provide a mock Retell client for tests."""
    return MockAsyncRetell()
