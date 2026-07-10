"""Run the full client intelligence setup: index, ingestion, knowledge
source and knowledge base, in order.

Usage: python setup/run_setup.py
"""

import create_knowledge_base
import create_knowledge_source
import create_search_index
import ingest_documents


def main() -> None:
    create_search_index.main()
    ingest_documents.main()
    create_knowledge_source.main()
    create_knowledge_base.main()


if __name__ == "__main__":
    main()
