import os
import chromadb
from chromadb.utils import embedding_functions
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Setup ─────────────────────────────────────────────────────────────────────
chroma  = chromadb.PersistentClient(path="./chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"   # small, fast, runs fully offline
)
collection = chroma.get_or_create_collection(
    name="audit_docs",
    embedding_function=embedder
)

claude = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# ── 1. Chunking ───────────────────────────────────────────────────────────────
def chunk_text(text, source, chunk_size=100, overlap=20):
    words  = text.split()
    chunks, ids, metas = [], [], []
    for i, start in enumerate(range(0, len(words), chunk_size - overlap)):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk:
            chunks.append(chunk)
            ids.append(f"{source}_chunk_{i}")
            metas.append({"source": source})   # metadata for filtering later
    return chunks, ids, metas

# ── 2. Index documents ────────────────────────────────────────────────────────
def index_document(filepath):
    with open(filepath) as f:
        text = f.read()
    chunks, ids, metas = chunk_text(text, source=filepath)
    collection.add(documents=chunks, ids=ids, metadatas=metas)
    print(f"Indexed {len(chunks)} chunks from {filepath}")

# ── 3. Retrieve + Ask ─────────────────────────────────────────────────────────
def ask(question, top_k=3):
    # Retrieve relevant chunks
    results = collection.query(query_texts=[question], n_results=top_k)
    chunks  = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    # Build context
    context = "\n---\n".join(
        f"[{src}]\n{chunk}" for src, chunk in zip(sources, chunks)
    )

    # Ask Claude
    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=f"""You are a security audit assistant.
Answer based ONLY on the excerpts below. If the answer isn't there, say so.

{context}""",
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Index your docs once
    #index_document("firewall_policy.txt")
    #index_document("access_control.txt")
    #index_document("cis_benchmark_notes.txt")
    #index_document("vulnerability_mgmt.txt")

    # Then query freely
    print(ask("What ports must be blocked on perimeter firewalls?"))
    print(ask("What is the password rotation policy?"))
    print(ask("Which CIS controls apply to SSH hardening?"))
