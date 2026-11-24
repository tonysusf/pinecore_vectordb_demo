"""Search a small set of sample documents by meaning using Pinecone."""

import argparse
import os
import sys
import time

INDEX_NAME = "tony-index-demo"
NAMESPACE = "namespace-demo"
DOCUMENTS = [
    {"_id": "library", "text": "A peaceful library with comfy chairs."},
    {"_id": "bakery", "text": "A bakery that sells fresh sourdough every morning."},
    {"_id": "trail", "text": "A steep hiking trail with views of the mountains."},
    {"_id": "bikes", "text": "A repair shop that fixes bicycles and replaces flat tires."},
]


def search(api_key, query):
    from pinecone import Pinecone, SchemaBuilder

    pc = Pinecone(api_key=api_key)
    if not pc.indexes.exists(name=INDEX_NAME):
        schema = SchemaBuilder().add_string_field("text", embed={}).build()
        pc.indexes.create(name=INDEX_NAME, schema=schema)

    deadline = time.monotonic() + 120
    while not pc.indexes.describe(name=INDEX_NAME).status.ready:
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Index {INDEX_NAME!r} is still starting. Try again shortly.")
        time.sleep(2)

    index = pc.index(name=INDEX_NAME)
    index.documents.upsert(namespace=NAMESPACE, documents=DOCUMENTS)

    sample_ids = {document["_id"] for document in DOCUMENTS}
    deadline = time.monotonic() + 30
    while True:
        result = index.documents.search(
            namespace=NAMESPACE,
            top_k=len(DOCUMENTS),
            score_by=[{"type": "embed", "fields": ["text"], "query": query}],
            include_fields=["text"],
        )
        if sample_ids.issubset(match.id for match in result.matches):
            return result.matches[:3]
        if time.monotonic() >= deadline:
            raise TimeoutError("Sample documents are still being indexed. Try again shortly.")
        time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="A phrase to search for")
    args = parser.parse_args()
    query = args.query.strip()
    if not query:
        parser.error("enter a non-empty search phrase")

    api_key = os.environ.get("PINECONE_API_KEY", "").strip()
    if not api_key:
        parser.error("set PINECONE_API_KEY before running the demo")

    try:
        matches = search(api_key, query)
    except Exception as error:
        print(f"Demo failed: {str(error).replace(api_key, '[redacted]')}", file=sys.stderr)
        return 1

    for rank, match in enumerate(matches, start=1):
        print(f"{rank}. {match.text} (score: {match.score:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
