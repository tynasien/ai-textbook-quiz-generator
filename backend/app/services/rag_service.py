
import re
import uuid
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "storage" / "chroma" # создаются папки
# ChromaDB - сохраняет файлы базы данных в диск

CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# компактная, но мощная мультиязычная модель. понимает слова и текста
_embedding_model = None


def get_embedding_model():
    """Загружает модель только при первом обращении."""
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    return _embedding_model

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name="textbook_chunks",
    metadata={"hnsw:space": "cosine"},
)


def split_text(text: str, chunk_size: int = 1200,
# функция разбивает текст на фрагменты, которые перекрываются друг с другом. Это нужно для того, чтобы при поиске по смыслу не терялась информация между фрагментами.   
               overlap: int = 200) -> list[str]:
    """Разбивает текст на перекрывающиеся фрагменты."""

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def index_textbook(text: str, filename: str) -> dict:
# функция вызывается, когда пользователь загружает новый документ
    """Сохраняет фрагменты учебника в векторной базе."""

    chunks = split_text(text)

    if not chunks:
        raise ValueError("В учебнике не найден текст.")

    document_id = str(uuid.uuid4())

    embeddings = get_embedding_model().encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    ids = [
        f"{document_id}_{i}"
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ],
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_count": len(chunks),
        "message": "Учебник добавлен в базу знаний.",
    }


def search_textbook(
# функция ищет релевантные куски текста в базе
    query: str,
    document_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Ищет фрагменты, наиболее близкие по смыслу к запросу."""

    query = query.strip()

    if not query:
        raise ValueError("Введите поисковый запрос.")

    if collection.count() == 0:
        return []

    query_embedding = get_embedding_model().encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    filters = (
        {"document_id": document_id}
        if document_id
        else None
    )

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        where=filters,
        include=["documents", "metadatas", "distances"],
    )

    found = []

    for i, chunk in enumerate(results["documents"][0]):
        found.append({
            "text": chunk,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return found
