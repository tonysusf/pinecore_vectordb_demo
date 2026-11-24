# Pinecone semantic search demo

Search four sample records by meaning from the terminal. The script prints the top three matches and their similarity scores.

## Run it

Use Python 3.10 or newer and a [Pinecone API key](https://app.pinecone.io/).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'pinecone>=10.1.0'
export PINECONE_API_KEY='your-api-key'
python demo.py "a quiet place to read"
python demo.py "where can I get my bike fixed?"
```

The first query should rank the library highest. The second should rank the bicycle repair shop highest.

## How it works

The script creates the `tony-index-demo` index if needed. Its schema has a single `text` field with automatic embedding. The script puts the built-in records in the `namespace-demo` namespace, waits for them to become searchable, and sends your phrase to Pinecone. Pinecone embeds both the records and the query.

The records use stable IDs so rerunning the script updates the same records. The index stays in your Pinecone project between runs.

[Pinecone quickstart](https://docs.pinecone.io/guides/get-started/quickstart)
