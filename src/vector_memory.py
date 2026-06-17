import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


class VectorMemory:
    def __init__(self):
        # Lightweight embedding config
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},  # force lightweight CPU mode
            encode_kwargs={"normalize_embeddings": True}
        )

        self.index_path = "vector_index"
        self.vectorstore = self._load_store()

    def _load_store(self):
        if os.path.exists(self.index_path):
            try:
                return FAISS.load_local(
                    self.index_path,
                    self.embedding,
                    allow_dangerous_deserialization=True
                )
            except Exception:
                return None
        return None

    def add(self, role: str, content: str):
        doc = Document(
            page_content=content.strip(),
            metadata={"role": role}
        )

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents([doc], self.embedding)
        else:
            self.vectorstore.add_documents([doc])

        # Save only when needed (still simple but safer)
        self.vectorstore.save_local(self.index_path)

    def search(self, query: str, k: int = 4) -> str:
        if not self.vectorstore:
            return ""

        results = self.vectorstore.similarity_search(query, k=k)

        return "\n".join(
            f"{doc.metadata.get('role', 'UNKNOWN').upper()}: {doc.page_content}"
            for doc in results
        )