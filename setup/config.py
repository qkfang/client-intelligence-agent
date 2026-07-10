"""Shared configuration for the client intelligence setup scripts.

Loads settings from environment variables (see .env.sample) and exposes
the Azure Search / Azure OpenAI credentials used by every script in this
folder. Azure AD (DefaultAzureCredential) is used by default; API keys are
only used when explicitly provided.
"""

import os

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv(override=True)


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


AZURE_SEARCH_ENDPOINT = _required("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "client-intelligence-docs")
AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME = os.environ.get(
    "AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME", "client-intelligence-knowledge-source"
)
AZURE_SEARCH_KNOWLEDGE_BASE_NAME = os.environ.get(
    "AZURE_SEARCH_KNOWLEDGE_BASE_NAME", "client-intelligence-knowledge-base"
)

AZURE_OPENAI_ENDPOINT = _required("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
AZURE_OPENAI_EMBEDDING_MODEL = os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT", "gpt-5.4")
AZURE_OPENAI_CHATGPT_MODEL_NAME = os.environ.get("AZURE_OPENAI_CHATGPT_MODEL_NAME", "gpt-5.4")

AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY") or None
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY") or None


def get_search_credential() -> TokenCredential | AzureKeyCredential:
    """Return an API key credential when configured, otherwise Azure AD."""
    if AZURE_SEARCH_API_KEY:
        return AzureKeyCredential(AZURE_SEARCH_API_KEY)
    return DefaultAzureCredential()
