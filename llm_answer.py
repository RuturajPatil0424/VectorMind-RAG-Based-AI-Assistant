import requests

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


def ask_llm_with_context(
    user_query: str,
    matches: list,
    llm_model: str = "llama3.1"
):
    """
    user_query : str
    matches    : list of retrieved vector DB records
    """

    # ---------------- BUILD CONTEXT ----------------
    context_blocks = []
    for i, r in enumerate(matches, 1):
        text = r.get("paragraph_text", r["embedding_text"])
        source = r.get("source_name", "unknown")
        context_blocks.append(f"[{i}] {text} (Source: {source})")

    context_text = "\n\n".join(context_blocks)

    # ---------------- PROMPT ----------------
    prompt = f"""
You are a helpful AI assistant.
Answer the user's question using ONLY the reference context below.
If the answer is not present in the context, say "I don't know".

### Reference Context:
{context_text}

### User Question:
{user_query}

### Answer:
"""

    # ---------------- CALL LLM ----------------
    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": llm_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()
    return response.json()["message"]["content"].strip()
