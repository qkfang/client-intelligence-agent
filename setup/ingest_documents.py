"""Ingest the mock client intelligence documents into the search index.

Splits each document into paragraph-sized chunks, generates embeddings and
uploads them to the index created by create_search_index.py.

Run after create_search_index.py: python setup/ingest_documents.py
"""

from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from openai import AzureOpenAI

import config

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"
MAX_CHUNK_CHARS = 800


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def build_openai_client() -> AzureOpenAI:
    if config.AZURE_OPENAI_API_KEY:
        return AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version="2024-10-21",
        )
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )


def main() -> None:
    openai_client = build_openai_client()
    search_client = SearchClient(
        endpoint=config.AZURE_SEARCH_ENDPOINT,
        index_name=config.AZURE_SEARCH_INDEX_NAME,
        credential=config.get_search_credential(),
    )

    documents = []
    for file_path in sorted(MOCK_DATA_DIR.glob("*.txt")):
        document_id = file_path.stem
        title = document_id.replace("_", " ").title()
        text = file_path.read_text(encoding="utf-8")

        for index, snippet in enumerate(chunk_text(text)):
            embedding = openai_client.embeddings.create(
                input=snippet,
                model=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            ).data[0].embedding

            documents.append(
                {
                    "chunk_id": f"{document_id}-{index}",
                    "document_id": document_id,
                    "title": title,
                    "snippet": snippet,
                    "blob_path": file_path.name,
                    "content_vector": embedding,
                }
            )

    search_client.upload_documents(documents)
    print(f"Ingested {len(documents)} chunks from {MOCK_DATA_DIR.name} into '{config.AZURE_SEARCH_INDEX_NAME}'.")


if __name__ == "__main__":
    main()
