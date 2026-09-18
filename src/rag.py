from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


class MeetingRAG:
    """Retrieval system for meeting transcripts."""

    def __init__(self, data_dir="data/meetings"):
        self.data_dir = Path(data_dir)

        print("Loading embedding model...")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        self.documents = []
        self.index = None

        self.ingest()

    def ingest(self):
        """Load meeting transcripts and build the vector index."""
        files = sorted(self.data_dir.glob("*.txt"))

        if not files:
            raise RuntimeError(
                f"No meeting transcripts found in {self.data_dir}"
            )

        for file in files:
            text = file.read_text(encoding="utf-8")

            for chunk in self._chunk(text):
                self.documents.append(
                    {
                        "source": file.name,
                        "text": chunk,
                    }
                )

        texts = [document["text"] for document in self.documents]

        embeddings = self.encoder.encode(
            texts,
            normalize_embeddings=True,
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        print(
            f"Ingested {len(files)} meetings "
            f"into {len(self.documents)} chunks."
        )

    @staticmethod
    def _chunk(text, size=120):
        """Split transcript text into small word-based chunks."""
        words = text.split()

        return [
            " ".join(words[i:i + size])
            for i in range(0, len(words), size)
        ]

    def search(self, query, k=3):
        """Return the most relevant transcript chunks."""
        if self.index is None:
            raise RuntimeError("RAG index has not been initialized.")

        embedding = self.encoder.encode(
            [query],
            normalize_embeddings=True,
        )

        scores, indices = self.index.search(
            embedding,
            min(k, len(self.documents)),
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            document = self.documents[index]

            results.append(
                {
                    "source": document["source"],
                    "text": document["text"],
                    "score": float(score),
                }
            )

        return results
