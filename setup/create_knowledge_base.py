"""Create the AI Search knowledge base for client intelligence retrieval.

Combines the knowledge source with an Azure OpenAI chat model so agents can
query it with agentic retrieval and answer synthesis.

Run after create_knowledge_source.py: python setup/create_knowledge_base.py
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizerParameters,
    KnowledgeBase,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceReference,
)

import config


def main() -> None:
    index_client = SearchIndexClient(endpoint=config.AZURE_SEARCH_ENDPOINT, credential=config.get_search_credential())

    aoai_params = AzureOpenAIVectorizerParameters(
        resource_url=config.AZURE_OPENAI_ENDPOINT,
        deployment_name=config.AZURE_OPENAI_CHATGPT_DEPLOYMENT,
        model_name=config.AZURE_OPENAI_CHATGPT_MODEL_NAME,
        api_key=config.AZURE_OPENAI_API_KEY,
    )

    knowledge_base = KnowledgeBase(
        name=config.AZURE_SEARCH_KNOWLEDGE_BASE_NAME,
        models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
        knowledge_sources=[KnowledgeSourceReference(name=config.AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME)],
    )

    index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"Knowledge base '{config.AZURE_SEARCH_KNOWLEDGE_BASE_NAME}' created or updated.")


if __name__ == "__main__":
    main()
