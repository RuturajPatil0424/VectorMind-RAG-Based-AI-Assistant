import os
import json
import requests
import faiss
import numpy as np
from tqdm import tqdm


class BGEVectorStore:
    def __init__(
        self,
        model_name="bge-m3",
        ollama_url="http://localhost:11434/api/embed",
        dim=1024,
        index_path="src/vector_store"
    ):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.dim = dim
        self.index_path = index_path

        self.index = faiss.IndexFlatIP(dim)  # cosine similarity
        self.metadata = []

    # EMBEDDING 
    def embed_batch(self, texts):
        response = requests.post(
            self.ollama_url,
            json={
                "model": self.model_name,
                "input": texts
            },
            timeout=300
        )

        embeddings = np.array(response.json()["embeddings"], dtype="float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        return embeddings

    # INGEST 
    def add_documents(self, records, batch_size=32):
        """
        records: list of dicts with 'embedding_text'
        """
        for i in tqdm(range(0, len(records), batch_size), desc="Embedding"):
            batch = records[i:i + batch_size]
            texts = [r["embedding_text"] for r in batch]

            embeddings = self.embed_batch(texts)

            self.index.add(embeddings)
            self.metadata.extend(batch)

    # SAVE 
    def save(self):
        os.makedirs(self.index_path, exist_ok=True)

        faiss.write_index(
            self.index,
            os.path.join(self.index_path, "index.faiss")
        )

        with open(os.path.join(self.index_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    # LOAD 
    def load(self):
        self.index = faiss.read_index(
            os.path.join(self.index_path, "index.faiss")
        )

        with open(os.path.join(self.index_path, "metadata.json"), "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    # SEARCH 
    def search(self, query, top_k=5):
        query_embedding = self.embed_batch([query])
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            record = self.metadata[idx].copy()
            record["score"] = float(score)
            results.append(record)

        return results

    def search_vector_db(self, query: str, top_k: int = 5,score_threshold: float = 0.25):
        # Load vector database
        db = BGEVectorStore(index_path="src/vector_db")
        db.load()

        # Perform semantic search
        results = db.search(query, top_k=top_k)

        # Filter weak matches
        filtered_results = [
            r for r in results
            if r["score"] >= score_threshold
        ]

        return filtered_results
