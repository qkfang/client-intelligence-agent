"""Create the AI Search knowledge source over the client intelligence index.

Run after ingest_documents.py: python setup/create_knowledge_source.py
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)

import config


def main() -> None:
    index_client = SearchIndexClient(endpoint=config.AZURE_SEARCH_ENDPOINT, credential=config.get_search_credential())

    knowledge_source = SearchIndexKnowledgeSource(
        name=config.AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME,
        description="Client intelligence documents: onboarding, KYC/AML, entity resolution and financial review",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=config.AZURE_SEARCH_INDEX_NAME,
            source_data_fields=[
                SearchIndexFieldReference(name="blob_path"),
                SearchIndexFieldReference(name="title"),
                SearchIndexFieldReference(name="snippet"),
            ],
            search_fields=[SearchIndexFieldReference(name="snippet")],
            semantic_configuration_name="client-docs-semantic-config",
        ),
    )

    index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Knowledge source '{config.AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME}' created or updated.")


if __name__ == "__main__":
    main()
