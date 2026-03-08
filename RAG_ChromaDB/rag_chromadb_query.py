import os
import chromadb
from chromadb.utils import embedding_functions
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Setup ─────────────────────────────────────────────────────────────────────
chroma  = chromadb.PersistentClient(path="./test_chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"   # small, fast, runs fully offline
)
collection = chroma.get_or_create_collection(
    name="docs_1",
    embedding_function=embedder
)

claude = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

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
        system=f"""You are a security audit assistant. If the answer isn't there, say so.
{context}""",
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Then query freely
    #print(ask("What ports must be blocked on perimeter firewalls?"))
    #print(ask("What is the password rotation policy?"))
    #print(ask("Which CIS controls apply to SSH hardening?"))
    #print(ask("What document describes the password policy?"))
    #print(ask("Sumarize how the pptx presentation is related with the audit report docx?"))
    print(ask("Provide executive summary from the audit report."))
