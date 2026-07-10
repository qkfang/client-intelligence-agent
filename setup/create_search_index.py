"""Create the AI Search index used to store client intelligence documents.

Run this first: python setup/create_search_index.py
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

import config

VECTOR_PROFILE_NAME = "client-docs-vector-profile"
VECTOR_ALGORITHM_NAME = "client-docs-hnsw"
VECTORIZER_NAME = "client-docs-vectorizer"
SEMANTIC_CONFIGURATION_NAME = "client-docs-semantic-config"
EMBEDDING_DIMENSIONS = 3072  # text-embedding-3-large


def build_index() -> SearchIndex:
    fields = [
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="snippet", type=SearchFieldDataType.String),
        SimpleField(name="blob_path", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE_NAME,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=VECTOR_ALGORITHM_NAME)],
        profiles=[
            VectorSearchProfile(
                name=VECTOR_PROFILE_NAME,
                algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
                vectorizer_name=VECTORIZER_NAME,
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name=VECTORIZER_NAME,
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=config.AZURE_OPENAI_ENDPOINT,
                    deployment_name=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                    model_name=config.AZURE_OPENAI_EMBEDDING_MODEL,
                    api_key=config.AZURE_OPENAI_API_KEY,
                ),
            )
        ],
    )

    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name=SEMANTIC_CONFIGURATION_NAME,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="snippet")],
                ),
            )
        ],
        default_configuration_name=SEMANTIC_CONFIGURATION_NAME,
    )

    return SearchIndex(
        name=config.AZURE_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )


def main() -> None:
    index_client = SearchIndexClient(endpoint=config.AZURE_SEARCH_ENDPOINT, credential=config.get_search_credential())
    index_client.create_or_update_index(build_index())
    print(f"Search index '{config.AZURE_SEARCH_INDEX_NAME}' created or updated.")


if __name__ == "__main__":
    main()
